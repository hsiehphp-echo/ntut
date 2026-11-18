"""腳本：把現在有的檔案做成一頁可以讀的網頁 site/index.html。

用法：python3 tools/render.py [--root DIR]
讀：data/、notes/、understanding.md（有什麼就用什麼）
寫：site/index.html（只能由這支腳本產生，不要手改）

網頁上三種人的話分開放：
  實線框　講者的話（原文，一個字都不改）
  虛線框　AI 補述（非原文）：名詞補充、身份視角
  波浪線　你的理解（你親手寫的）
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

PY = "py" if sys.platform == "win32" else "python3"  # 提示訊息裡的指令寫法

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gsn  # noqa: E402

CSS = """
:root{color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:#000;color:#fff;font:400 19px/1.9 "Noto Sans TC","PingFang TC","Microsoft JhengHei",system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:48px 24px 96px}
h1{font-size:40px;line-height:1.3;font-weight:900;margin:0 0 8px}
h2{font-size:26px;font-weight:900;margin:56px 0 16px;padding-top:20px;border-top:1px solid #3a3a3a}
h3{font-size:22px;font-weight:900;margin:36px 0 8px}
p{margin:0 0 18px}
.lead{color:#8f8f8f;margin-bottom:28px}
table{border-collapse:collapse;width:100%;font-size:17px;margin:8px 0 8px}
th,td{text-align:left;padding:8px 14px 8px 0;border-top:1px solid #3a3a3a;font-weight:400;vertical-align:top}
th{color:#8f8f8f;font-size:14px;letter-spacing:.12em}
.yes{font-weight:900}.no{color:#8f8f8f}
.legend{display:flex;flex-wrap:wrap;gap:12px 28px;font-size:16px;color:#cfcfcf;margin:18px 0 0}
.legend span{display:inline-flex;align-items:center;gap:10px}
.legend i{display:inline-block;width:44px;border-top:3px solid #fff}
.legend i.d{border-top-style:dashed}
.legend i.w{border:0;height:10px;background:repeating-radial-gradient(circle at 6px 14px,transparent 0 7px,#fff 7px 9px,transparent 9px 12px) 0 0/12px 10px}
.src{border-left:3px solid #fff;padding:2px 0 2px 20px;margin:0 0 22px}
.src p:last-child{margin-bottom:0}
.add{border:2px dashed #8f8f8f;padding:14px 20px 16px;margin:0 0 26px;font-size:17px;line-height:1.8;color:#e6e6e6}
.add .tag{display:block;font-size:13px;letter-spacing:.14em;color:#8f8f8f;margin-bottom:4px}
.add p{margin:0 0 6px}.add ul{margin:6px 0 0;padding-left:22px}
.mine{padding:18px 0 4px;margin:0;border-top:3px solid #fff;border-image:repeating-linear-gradient(90deg,#fff 0 10px,transparent 10px 16px) 3}
.cue{display:grid;grid-template-columns:44px 1fr;gap:0 8px;margin:0 0 6px}
.cue b{color:#8f8f8f;font-weight:400;font-size:14px;padding-top:5px}
.empty{color:#8f8f8f}
footer{margin-top:64px;color:#5c5c5c;font-size:14px}
"""


def esc(s):
    return html.escape(str(s), quote=False)


def inline(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(s))


def load(root, rel):
    p = root / rel
    if not p.is_file():
        return None
    try:
        return gsn.read_text(p)
    except UnicodeDecodeError:
        # Windows 的編輯器可能存成 ANSI（cp950）；檔案一律要是 UTF-8。
        raise ValueError(f"{rel} 不是 UTF-8 編碼（請在編輯器裡改用 UTF-8 另存；Windows 記事本的「編碼」選 UTF-8）") from None


def block_html(lines):
    head = lines[0]
    kind = "名詞補充" if head.startswith("📖") else "身份視角" if head.startswith("🎯") else "補述"
    out = [f'<aside class="add"><span class="tag">AI 補述（非原文）・{kind}</span>']
    items = []
    for ln in lines:
        if ln.startswith(("- ", "* ")):
            items.append(f"<li>{inline(ln[2:])}</li>")
            continue
        if items:
            out.append("<ul>" + "".join(items) + "</ul>")
            items = []
        out.append(f"<p>{inline(ln)}</p>")
    if items:
        out.append("<ul>" + "".join(items) + "</ul>")
    out.append("</aside>")
    return "\n".join(out)


def notes_html(md):
    out, quote = [], []

    def flush():
        if quote:
            b = [x for x in quote if x]
            if b:
                out.append(block_html(b))
            quote.clear()

    for ln in md.split("\n"):
        s = ln.strip()
        if s.startswith(">"):
            quote.append(s[1:].strip())
            continue
        flush()
        if not s:
            continue
        if s.startswith("## "):
            out.append(f"<h3>{inline(s[3:])}</h3>")
        elif s.startswith("#"):
            out.append(f"<h3>{inline(s.lstrip('#').strip())}</h3>")
        else:
            out.append(f'<div class="src"><p>{inline(s)}</p></div>')
    flush()
    return "\n".join(out)


def cues_html(cues):
    return "\n".join(f'<div class="cue"><b>{c["n"]}</b><span>{esc(c["text"])}</span></div>' for c in cues)


def render(root: Path) -> str:
    def cues_of(rel):
        t = load(root, rel)
        if t is None:
            return None
        try:
            d = json.loads(t)
            return d["cues"] if isinstance(d.get("cues"), list) else None
        except (ValueError, AttributeError, KeyError):
            return None

    raw, fixed = cues_of("data/cues.json"), cues_of("data/cues_fixed.json")
    cleaned, notes, mine = load(root, "notes/cleaned.md"), load(root, "notes/notes.md"), load(root, "understanding.md")
    src_n = sum(gsn.count(c["text"]) for c in fixed) if fixed else 0
    rows = [
        ("1", "拿掉時間軸", "腳本", f"{len(raw)} 段字幕" if raw else None),
        ("2", "校正專有名詞", "人確認，腳本替換", f"{src_n} 個字" if fixed else None),
        ("3", "把字幕變回一篇文章", "AI，腳本檢查字數",
         f"{sum(gsn.count(p) for p in gsn.body_paragraphs(cleaned))} 個字" if cleaned else None),
        ("4", "名詞補充與身份視角", "AI，腳本檢查原文沒被動",
         f"{len(gsn.quote_blocks(notes))} 塊補述" if notes else None),
        ("5", "我的理解", "你親手寫", "有" if mine else None),
    ]
    tr = "".join(
        f'<tr><td>{n}</td><td>{esc(a)}</td><td>{esc(b)}</td>'
        f'<td class="{"yes" if v else "no"}">{esc(v) if v else "還沒有"}</td></tr>' for n, a, b, v in rows)
    if notes:
        title, body = "好學生筆記：全文與補述", notes_html(notes)
    elif cleaned:
        title, body = "全文（還沒有補述）", notes_html(cleaned)
    elif fixed:
        title, body = "字幕文字（已校正專有名詞，還沒有變成文章）", cues_html(fixed)
    elif raw:
        title, body = "字幕文字（剛拿掉時間軸，還沒校正）", cues_html(raw)
    else:
        title, body = "還沒有內容", f'<p class="empty">請先跑 {PY} tools/srt_strip.py</p>'
    if mine:
        paras = "".join(f"<p>{inline(p)}</p>" for p in mine.split("\n") if p.strip() and not p.startswith("#"))
        mine_html = f'<div class="mine">{paras}</div>'
    else:
        mine_html = '<p class="empty">還沒有。這一段只有你能寫：請自己建立 understanding.md。</p>'
    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>我的好學生筆記</title>
<style>{CSS}</style>
</head>
<body>
<main>
<h1>我的好學生筆記</h1>
<p class="lead">來源：閃講〈好學生筆記〉的字幕檔。原文一個字都不改，補述另外放，理解自己寫。</p>
<table>
<thead><tr><th></th><th>步驟</th><th>誰做</th><th>現在</th></tr></thead>
<tbody>{tr}</tbody>
</table>
<div class="legend"><span><i></i>講者的話</span><span><i class="d"></i>AI 補述（非原文）</span><span><i class="w"></i>你的理解</span></div>
<h2>{esc(title)}</h2>
{body}
<h2>我的理解</h2>
{mine_html}
<footer>這一頁由 tools/render.py 產生，請不要手改。檔案改了之後，重跑一次就會更新。</footer>
</main>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    a = ap.parse_args()
    root = Path(a.root).resolve()
    try:
        page = render(root)
    except ValueError as e:
        print(f"[FAIL] {e}")
        return 1
    (root / "site").mkdir(exist_ok=True)
    (root / "site" / "index.html").write_text(page, encoding="utf-8", newline="\n")
    print("[PASS] 已產生：site/index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
