#!/usr/bin/env python3
"""好學生筆記的閘門 G0–G8：每一步交給下一步之前，先確認上一步的成果還在。

用法：python3 tools/check.py [--only G1,G2 | --before-understanding] [--root DIR]
  --before-understanding  只跑 G0–G7（不含 G8）。學生還沒親手寫 understanding.md 時，
                          先用它和 AI 把 G0–G7 共八道閘門修到全綠；全綠後學生自己寫理解，
                          寫完先跑 python3 tools/render.py（網頁會多出「我的理解」，不重產 G7 會紅），
                          最後再跑不帶參數的完整檢查。
每道閘門印一行：[PASS] G1 ✅ ... 或 [FAIL] G2 ❌ ...；最後 RESULT: GREEN|RED (x/y)。
只有全綠才 exit 0。不要為了變綠而修改本檔；覺得閘門錯了，寫 GATE DISPUTE 交給人決定。
只用標準函式庫，Python 3.10 以上。

  G0 字幕檔沒被改        source/transcript.srt 的指紋和寫死的基準一樣
  G1 字幕文字是腳本做的  data/cues.json、data/cues_fixed.json 和標準答案一段一段都一樣
  G2 字數沒有變少        notes/cleaned.md 的字數落在字幕的 95% 到 105%
  G3 每一段字幕都還在    51 段字幕，每一段都能在 cleaned.md 裡找到
  G4 沒有摘要句          cleaned.md 沒有「講者提到」這一類第三人稱的摘要
  G5 補述沒有動到全文    notes/notes.md 拿掉補述之後，和 cleaned.md 一字不差
  G6 補述都有標記        每一塊補述都標明是名詞補充（📖）或某個身份的視角（🎯）
  G7 網頁和檔案同步      site/index.html 是腳本用現在的檔案產生的
  G8 你的理解            understanding.md 由學生親手寫
"""
import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path

PY = "py" if sys.platform == "win32" else "python3"  # 提示訊息裡的指令寫法

ROOT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
ROOT_REF = ROOT / "reference"
sys.path.insert(0, str(TOOLS))
import gsn  # noqa: E402

# G0 的基準寫死在程式裡（tools/ 唯讀），不是從專案裡別的檔案讀來的。
SOURCE_SHA1 = "d29aeb0c60e0dd63325c43d099b39c9bd3ae929c"
LOW, HIGH = 0.95, 1.05
MIN_COVER = 0.6          # 一段字幕至少要有六成的字還找得到，才算「還在」
BANNED = ["講者介紹", "講者提到", "講者表示", "講者認為", "講者指出", "講者分享", "講者說明", "講者強調",
          "本段討論", "本段說明", "這一段討論", "第一部分提到", "第一部分討論", "接著討論", "總結來說", "綜上所述"]
KINDS = {"📖": "名詞補充", "🎯": "視角", "📝": "學習摘要", "💡": "核心洞察"}
MIN_TERM, MIN_VIEW = 2, 2
_TAG = re.compile(r"<[^>]*>?")


def show(v, n: int = 24) -> str:
    t = " ".join(_TAG.sub("", str(v)).replace("<", "").replace(">", "").split())
    return (t[:n] + "…") if len(t) > n else (t or "（空）")


class Ctx:
    def __init__(self, root: Path):
        self.root = root
        self.bad = {}
        self._c = {}

    def text(self, rel):
        p = self.root / rel
        if not p.is_file():
            return None
        try:
            return gsn.read_text(p)
        except UnicodeDecodeError:
            # Windows 的編輯器可能存成 ANSI（cp950）；這不是內容錯，但檔案一律要是 UTF-8。
            raise ValueError(f"{rel} 不是 UTF-8 編碼（請在編輯器裡改用 UTF-8 另存；Windows 記事本的「編碼」選 UTF-8）") from None

    def load(self, rel):
        if rel in self._c:
            return self._c[rel]
        v, t = None, self.text(rel)
        if t is not None:
            try:
                v = json.loads(t)
            except ValueError as e:
                self.bad[rel] = str(e)
        self._c[rel] = v
        return v

    def fixed_cues(self):
        d = self.load("data/cues_fixed.json")
        return d.get("cues") if isinstance(d, dict) and isinstance(d.get("cues"), list) else None


def g0(cx):
    p = cx.root / "source" / "transcript.srt"
    if not p.is_file():
        return False, "找不到 source/transcript.srt（來源字幕檔不見了，請從起始包還原）"
    # Windows 的 Git 可能把換行換成 \r\n；換行不算內容，所以先統一成 \n 再算指紋。
    if hashlib.sha1(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != SOURCE_SHA1:
        return False, "來源字幕檔被改動：source/transcript.srt（請還原，來源唯讀；要改錯字請改 data/corrections.json）"
    return True, "來源字幕檔 source/transcript.srt 的指紋和寫死的基準一致，沒有被改過"


def ref(name):
    """載入 reference/ 裡講師的備援腳本，用來重做一次「標準答案」。"""
    import importlib.util
    p = ROOT_REF / f"{name}.py"
    spec = importlib.util.spec_from_file_location("ref_" + name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def first_diff(have, want, what):
    """比對兩份字幕清單，回傳第一個不一樣的地方（給人看的訊息），一樣就回傳空字串。"""
    if not isinstance(have, list):
        return f"{what} 裡找不到 cues 清單（格式見 scripts_spec.md）"
    if len(have) != len(want):
        return f"{what} 有 {len(have)} 段，應該是 {len(want)} 段"
    for h, w in zip(have, want):
        if not isinstance(h, dict) or h.get("n") != w["n"]:
            return f"{what} 第 {w['n']} 段的編號 n 不對（每一段要有 n 和 text）"
        if gsn.NFC(h.get("text", "")) != w["text"]:
            return f"{what} 第 {w['n']} 段不一樣：你的是「{show(h.get('text', ''), 22)}」，應該是「{show(w['text'], 22)}」"
    return ""


def g1(cx):
    have = cx.load("data/cues.json")
    if have is None:
        if "data/cues.json" in cx.bad:
            return False, f"data/cues.json 不是合法 JSON：{cx.bad['data/cues.json']}（格式見 scripts_spec.md；請修正 tools/srt_strip.py 再重跑，不要手改 data/）"
        return False, f"還沒做 S1：還沒有 data/cues.json（請先執行 {PY} tools/srt_strip.py 把字幕的時間軸拿掉）"
    want = ref("srt_strip").build(cx.root)["cues"]
    d = first_diff(have.get("cues") if isinstance(have, dict) else None, want, "data/cues.json")
    if d:
        return False, d + "（請修正 tools/srt_strip.py 再重跑，不要手改 data/）"
    if not (cx.root / "data" / "corrections.json").is_file():
        return False, "找不到 data/corrections.json（校正用語清單）"
    fixed = cx.load("data/cues_fixed.json")
    if fixed is None:
        if "data/cues_fixed.json" in cx.bad:
            return False, f"data/cues_fixed.json 不是合法 JSON：{cx.bad['data/cues_fixed.json']}（格式見 scripts_spec.md；請修正 tools/fix_terms.py 再重跑，不要手改 data/）"
        return False, f"時間軸拿掉了，還沒套校正用語：還沒有 data/cues_fixed.json（請執行 {PY} tools/fix_terms.py）"
    try:
        wantf, hits = ref("fix_terms").build(cx.root)
    except ValueError as e:
        return False, f"data/corrections.json 讀不懂：{e}"
    d = first_diff(fixed.get("cues") if isinstance(fixed, dict) else None, wantf["cues"], "data/cues_fixed.json")
    if d:
        return False, d + f"（改了校正用語或腳本之後要重跑 {PY} tools/fix_terms.py，不要手改 data/）"
    n = sum(gsn.count(c["text"]) for c in wantf["cues"])
    return True, f"{len(want)} 段字幕的文字和標準答案一段一段都一樣，套了 {len(hits)} 條校正用語，共 {n} 個字"


def _cleaned(cx):
    t = cx.text("notes/cleaned.md")
    if t is None:
        return None, "還沒有 notes/cleaned.md（S3a：請 AI 把字幕變回一篇文章）"
    if not gsn.body_paragraphs(t):
        return None, "notes/cleaned.md 是空的"
    return t, ""


def g2(cx):
    cues = cx.fixed_cues()
    if cues is None:
        return False, "還沒做 S1：沒有 data/cues_fixed.json，沒辦法比字數"
    t, why = _cleaned(cx)
    if t is None:
        return False, why
    src = sum(gsn.count(c["text"]) for c in cues)
    out = sum(gsn.count(p) for p in gsn.body_paragraphs(t))
    r = out / src if src else 0
    msg = f"字幕 {src} 個字，cleaned.md 正文 {out} 個字，是 {r * 100:.1f}%"
    if r < LOW:
        return False, msg + "，少於 95%：內容被刪掉或濃縮了（零省略：每一句原話都要留著）"
    if r > HIGH:
        return False, msg + "，多於 105%：加了原話沒有的內容（補充請放到 notes.md 的補述區塊）"
    return True, msg + "，落在 95% 到 105% 之間"


def coverage(cues, text):
    """每一段字幕還有幾成的字找得到。回傳 [(段號, 比例, 字幕文字)]。"""
    parts = [gsn.letters(c["text"]) for c in cues]
    a, b = "".join(parts), gsn.letters(text)
    hit = [False] * len(a)
    for m in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for i in range(m.a, m.a + m.size):
            hit[i] = True
    out, pos = [], 0
    for c, p in zip(cues, parts):
        n = len(p)
        out.append((c["n"], (sum(hit[pos:pos + n]) / n) if n else 1.0, c["text"]))
        pos += n
    return out


def g3(cx):
    cues = cx.fixed_cues()
    if cues is None:
        return False, "還沒做 S1：沒有 data/cues_fixed.json，沒辦法一段一段對"
    t, why = _cleaned(cx)
    if t is None:
        return False, why
    lost = [(n, r, s) for n, r, s in coverage(cues, "\n".join(gsn.body_paragraphs(t))) if r < MIN_COVER]
    if lost:
        head = "；".join(f"第 {n} 段「{show(s, 18)}」只剩 {r * 100:.0f}%" for n, r, s in lost[:4])
        more = f"（共 {len(lost)} 段）" if len(lost) > 4 else ""
        return False, f"有字幕不見了或被改寫：{head}{more}。請對照 data/fixed.txt 把原話補回 notes/cleaned.md"
    return True, f"{len(cues)} 段字幕都還在 cleaned.md 裡（每一段至少找得到六成的字）"


def g4(cx):
    t, why = _cleaned(cx)
    if t is None:
        return False, why
    body = "\n".join(gsn.body_paragraphs(t))
    bad = [w for w in BANNED if w in body]
    if bad:
        return False, f"cleaned.md 出現摘要式的寫法：{'、'.join(bad[:4])}（要保留講者第一人稱的原話，不要替他轉述）"
    if any(ln.lstrip().startswith(">") for ln in t.split("\n")):
        return False, "cleaned.md 裡有補述區塊（> 開頭的行）：這一份只放講者的話，補述請放到 notes/notes.md"
    heads = [ln for ln in t.split("\n") if ln.startswith("## ")]
    if not heads:
        return False, "cleaned.md 沒有任何小標題（請用「## 」開頭的行，插在段落之間）"
    return True, f"cleaned.md 沒有摘要式的寫法，只有講者的話，有 {len(heads)} 個小標題"


def _notes(cx):
    t = cx.text("notes/notes.md")
    if t is None:
        return None, "還沒有 notes/notes.md（S3b：請 AI 在全文旁邊加名詞補充與你的身份視角）"
    return t, ""


def g5(cx):
    c, why = _cleaned(cx)
    if c is None:
        return False, why
    n, why = _notes(cx)
    if n is None:
        return False, why
    a, b = gsn.body_paragraphs(c), gsn.body_paragraphs(n)
    if a == b:
        return True, f"notes.md 拿掉補述之後，{len(a)} 段正文和 cleaned.md 一字不差"
    for i, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            return False, f"notes.md 的第 {i} 段正文和 cleaned.md 不一樣：「{show(y, 20)}」（補述只能加在段落之間，不能改講者的話）"
    if len(b) < len(a):
        return False, f"notes.md 少了正文：cleaned.md 有 {len(a)} 段，notes.md 只有 {len(b)} 段"
    return False, f"notes.md 多出不是補述的段落：「{show(b[len(a)], 20)}」（AI 加的話要放在 > 開頭的補述區塊裡）"


def g6(cx):
    n, why = _notes(cx)
    if n is None:
        return False, why
    blocks = gsn.quote_blocks(n)
    if not blocks:
        return False, "notes.md 還沒有任何補述區塊（> 開頭的行）"
    cnt = {k: 0 for k in KINDS}
    who = set()
    for b in blocks:
        k = next((k for k in KINDS if b[0].startswith(k)), None)
        if k is None:
            return False, f"有一塊補述沒有標記是哪一種：「{show(b[0], 20)}」（第一行要以 📖 或 🎯 開頭）"
        cnt[k] += 1
        if k == "🎯":
            m = re.search(r"\*\*(.+?)視角\*\*", b[0])
            if not m or not m.group(1).strip():
                return False, f"視角區塊的第一行要寫成「🎯 **你的身份視角**」：「{show(b[0], 20)}」"
            who.add(m.group(1).strip())
        if len(b) < 2:
            return False, f"有一塊補述只有標題、沒有內容：「{show(b[0], 20)}」"
    if cnt["📖"] < MIN_TERM:
        return False, f"名詞補充（📖）只有 {cnt['📖']} 塊，至少要 {MIN_TERM} 塊"
    if cnt["🎯"] < MIN_VIEW:
        return False, f"身份視角（🎯）只有 {cnt['🎯']} 塊，至少要 {MIN_VIEW} 塊"
    if len(who) > 1:
        return False, f"身份視角用了不只一個身份：{'、'.join(sorted(who))}（整份筆記用同一個身份）"
    return True, f"{len(blocks)} 塊補述都有標記：名詞補充 {cnt['📖']} 塊、「{next(iter(who))}」視角 {cnt['🎯']} 塊"


def g7(cx):
    import render
    p = cx.root / "site" / "index.html"
    if not p.is_file():
        return False, f"還沒有 site/index.html（請跑 {PY} tools/render.py）"
    if p.read_bytes().replace(b"\r\n", b"\n").decode("utf-8") != render.render(cx.root):
        return False, f"site/index.html 和現在的檔案不同步（請重跑 {PY} tools/render.py，不要手改 site/）"
    return True, "site/index.html 是腳本用現在的檔案產生的"


def g8(cx):
    t = cx.text("understanding.md")
    if t is None:
        return False, "還沒有 understanding.md（要學生自己親手寫；AI 不代寫，也不要試圖修 G8）"
    if len(re.sub(r"\s", "", t)) < 150:
        return False, "understanding.md 少於 150 字"
    if not re.search(r"^我還不懂：", t, re.M):
        return False, "缺少一行以「我還不懂：」開頭"
    return True, "understanding.md 存在、≥150 字、有「我還不懂：」"


GATES = [("G0", g0), ("G1", g1), ("G2", g2), ("G3", g3), ("G4", g4), ("G5", g5), ("G6", g6), ("G7", g7), ("G8", g8)]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", default="", help="只跑指定的閘門，例如 G0,G1")
    ap.add_argument("--before-understanding", action="store_true", dest="before_u",
                    help="只跑 G0–G7（不含 G8）；用在學生還沒親手寫 understanding.md 的階段")
    ap.add_argument("--root", default=str(ROOT))
    # Windows 把輸出接到管線（Git Bash、AI 工具）時預設不是 UTF-8，會印成亂碼或當掉；先改成 UTF-8，印不出來的字用 ? 代替。
    # 要放在 parse_args 之前，--help 的說明文字才印得出來。
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    a = ap.parse_args()
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "✅❌".encode(enc)
        emoji = True
    except Exception:
        emoji = False
    if a.before_u and a.only:
        print("[FAIL] --before-understanding 和 --only 不能一起用")
        return 2
    want = {x.strip().upper() for x in a.only.split(",") if x.strip()}
    if a.before_u:
        want = {g for g, _ in GATES if g != "G8"}
    unknown = want - {g for g, _ in GATES}
    if unknown:
        print(f"[FAIL] 不認識的閘門：{', '.join(sorted(unknown))}")
        return 2
    cx = Ctx(Path(a.root).resolve())
    ok = tot = 0
    for g, fn in GATES:
        if want and g not in want:
            continue
        try:
            r, msg = fn(cx)
        except Exception as e:  # 資料格式錯誤也要變成紅燈而不是當掉
            r, msg = False, str(e) if type(e) is ValueError else f"資料格式有問題（{type(e).__name__}: {e}）"
        if not r:
            for f in cx.bad:
                if f not in msg:
                    msg += f"；{f} 不是合法 JSON"
        tot += 1
        ok += bool(r)
        mark = ("✅" if r else "❌") if emoji else ""
        print(f"[{'PASS' if r else 'FAIL'}] {g} {mark} {msg}".replace("  ", " "))
    green = ok == tot and tot > 0
    print(f"RESULT: {'GREEN' if green else 'RED'} ({ok}/{tot})")
    if a.before_u and green:
        print("G0–G7 都過了，還沒跑 G8，還不算完成：換你自己讀筆記、親手寫 understanding.md，"
              f"寫完先跑 {PY} tools/render.py，再跑 {PY} tools/check.py")
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
