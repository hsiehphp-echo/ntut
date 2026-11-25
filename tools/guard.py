#!/usr/bin/env python3
"""守衛（guard）：只看、只報告，不還原任何東西。（Windows 把 python3 換成 py）
  python3 tools/guard.py                  比對 spec.md、tools/check.py、tools/round.py 有沒有被動過
  python3 tools/guard.py audit <資料夾>    跑完之後的稽核：關卡真的跑了幾次、紀錄對不對、誰做了什麼
印出 GUARD: OK / GUARD: VIOLATION ...，或 AUDIT: OK / AUDIT: 有 n 件事要看。只有 OK 的結束碼是 0。"""
import hashlib
import json
import os
import re
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 這三個值由老師的 make_l2_packs.py 寫進來（換行符號先統一再算，編輯器改成 CRLF 不會誤報）。
EXPECT = {"spec.md": "a036ea51327e23d83113e21e3ab32c01c0de5de6100c210ad1a0e6ade722dd8c",
          "tools/check.py": "30e0a7b03056af400565372faf0a8e0c1eefd87e301c33bf459f75c7f707ea1f",
          "tools/round.py": "ed4ccd73b287210931c24a0a89e3aec5cd87ec0c8bc6f4980af89751563172ce"}
FILES = ("shopping.md", "menu.json", "menu.html")
SCORE = re.compile(r"(?:品味|驗收|總分)[^\n0-9]*?(\d+)\s*/\s*10")
ANY10 = re.compile(r"(\d+)\s*/\s*10")


def read_score(text, review=False):
    """「品味：8/10」的 8（也讀「總分：8/10」、全形的「８／１０」）。review=True（驗收的回答）時，什麼標籤都沒有，就取前三行裡第一個 N/10。"""
    t = unicodedata.normalize("NFKC", text or "")
    m = SCORE.search(t)
    if not m and review:
        m = ANY10.search("\n".join(t.splitlines()[:3]))
    return m.group(1) if m else None


def score(text, review=False):
    return read_score(text, review)


def digest(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()
    except OSError:
        return "不存在"


def read_jsonl(p):
    out = []
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    except (OSError, ValueError):
        pass
    return out


def read(p):
    try:
        with open(p, encoding="utf-8-sig") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def chain(prev, rec):
    body = {k: v for k, v in rec.items() if k != "chain"}
    return hashlib.sha256((prev + json.dumps(body, sort_keys=True, ensure_ascii=False)).encode("utf-8")).hexdigest()[:16]


def basic():
    return ["%s 被改過或不見了" % r for r, w in EXPECT.items() if digest(r) != w]


def audit(d):
    d = d.replace("\\", "/").rstrip("/")
    os.chdir(ROOT)
    todo, notes = [], []
    print("稽核 %s（對帳：紀錄和關卡自己記的對不對得上；防得了粗心，防不了存心）" % d)
    recs = read_jsonl(os.path.join(d, "gate.jsonl"))
    if not recs:
        print("關卡紀錄：沒有。這個資料夾沒有用 tools/round.py 跑過。")
        print("　- 沒有關卡紀錄（gate.jsonl）")
        print("AUDIT: 有 1 件事要看")
        return 1
    prev = "0"
    for r in recs:
        if chain(prev, r) != r.get("chain"):
            todo.append("gate.jsonl 的紀錄對不上：有人改過或刪過其中一行")
            break
        prev = r["chain"]
    bad = basic()
    for rel in ("tools/guard.py", "taste.md"):
        if digest(rel) != recs[0]["hashes"].get(rel):
            bad.append("%s 在這次開始之後被改過" % rel)
    print("守衛：" + ("OK" if not bad else "VIOLATION " + "；".join(bad)))
    todo += bad
    rounds = [r for r in recs if r["round"] >= 1]
    print("關卡跑了 %d 次（起點不算一輪）：" % len(recs))
    for r in recs:
        print("　%s　%s　%s %d/%d　沒過：%s　守衛：%s" % (
            r["t"][11:], "起點　" if r["round"] == 0 else "第 %d 輪" % r["round"], r["color"], r["passed"], r["total"],
            "、".join(r["fails"]) or "無", r["guard"]))
        if r["guard"] != "OK":
            todo.append("%s的守衛是 VIOLATION：%s" % ("起點" if r["round"] == 0 else "第 %d 輪" % r["round"], "；".join(r.get("guard_detail") or [])))
    if recs[0]["round"] != 0:
        notes.append("沒有起點：第一次跑關卡時，資料夾裡已經有菜單了")
    if not rounds:
        todo.append("關卡只跑了起點，沒有跑完任何一輪")
    greens = [r for r in rounds if r["color"] == "GREEN"]
    if greens:
        g = greens[0]
        if not [r for r in rounds if r["round"] > g["round"]] and g["round"] < g.get("max", 99):
            todo.append("關卡第一次綠燈（第 %d 輪）之後，沒有再做品味的那一輪（文件要求至少再做一輪）" % g["round"])
    if rounds and rounds[0]["color"] == "GREEN":
        notes.append("第 1 輪就全綠：關卡只查規定，這很常見。看綠燈之後那一輪它改了什麼")
    if greens:
        back = [r for r in rounds if r["round"] > greens[0]["round"] and r["color"] == "RED"]
        if back:
            todo.append("第 %d 輪已經綠燈，第 %s 輪又變成紅燈（文件說：綠燈的版本，不要為了品味改成紅燈）" % (
                greens[0]["round"], "、".join(str(r["round"]) for r in back)))
    if any(r.get("order_ok") is False for r in recs) and not any("shopping.md 沒有比" in t for t in todo):
        todo.append("shopping.md 沒有比 menu.json 先寫")
    if rounds:
        for f in FILES:
            if digest(os.path.join(d, f))[:16] != rounds[-1]["files"].get(f):
                todo.append("最後一次關卡之後，%s 又被改過（現在的檔案沒有過關卡）" % f)
    # log.md：每一輪一段，「關卡：」要和紀錄一樣
    log = read(os.path.join(d, "log.md"))
    found = {}
    if log is None:
        todo.append("沒有 log.md")
    else:
        secs = re.split(r"(?m)^#+\s*第\s*(\d+)\s*輪\s*$", log)
        for i in range(1, len(secs) - 1, 2):
            if int(secs[i]) in found:
                todo.append("log.md 的「第 %d 輪」寫了兩段（關卡只記了一次）" % int(secs[i]))
            found[int(secs[i])] = secs[i + 1]
    team = os.path.basename(d) in ("b", "c") or os.path.isfile(os.path.join(d, "review_r1.md"))
    for r in rounds:
        s = found.get(r["round"])
        if s is None:
            if log is not None:
                todo.append("log.md 沒有第 %d 輪的那一段" % r["round"])
            continue
        m = re.search(r"關卡[:：].*?(\d+)/(\d+)\s+(GREEN|RED)\s+\((\d+)/(\d+)\)", unicodedata.normalize("NFKC", s))
        if not m:
            todo.append("log.md 第 %d 輪的「關卡：」沒有原樣貼 ROUND 那一行" % r["round"])
        elif (int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4))) != (r["round"], r.get("max", int(m.group(2))), r["color"], r["passed"]):
            todo.append("log.md 第 %d 輪寫的關卡結果和真正的紀錄不同（寫 %s/%s %s %s/8，紀錄是 %d/%s %s %d/8）" % (
                r["round"], m.group(1), m.group(2), m.group(3), m.group(4), r["round"], r.get("max", "?"), r["color"], r["passed"]))
        own = score(s)
        rv = read(os.path.join(d, "review_r%d.md" % r["round"])) if team else None
        other = score(rv, True) if rv else None
        if team:
            print("　第 %d 輪品味：驗收給 %s；log.md 寫 %s" % (r["round"], (other + "/10") if other else ("讀不到" if rv else "沒有"),
                                                         (own + "/10") if own else "沒寫"))
            if rv is None:
                todo.append("第 %d 輪沒有驗收的回答 review_r%d.md" % (r["round"], r["round"]))
            elif not other:
                todo.append("第 %d 輪的驗收回答 review_r%d.md 讀不到分數（要有「品味：幾分/10」）" % (r["round"], r["round"]))
            elif own and other != own:
                todo.append("第 %d 輪 log.md 寫的分數（%s）和驗收給的（%s）不同" % (r["round"], own, other))
        else:
            print("　第 %d 輪品味（它給自己的）：%s" % (r["round"], (own + "/10") if own else "沒寫"))
            if not own:
                todo.append("log.md 第 %d 輪沒有品味分數" % r["round"])
    for k in sorted(found):
        if k > len(rounds):
            todo.append("log.md 寫了第 %d 輪，可是關卡只跑了 %d 輪（多出來的那一段沒有真的跑關卡）" % (k, len(rounds)))
    # 價錢的依據和岔路：只列出來給人看，不算對錯（關卡查有沒有寫，這裡讓你看寫了什麼）
    shop = read(os.path.join(d, "shopping.md")) or ""
    based = [l.strip() for l in shop.splitlines() if re.match(r"^\s*[-*]\s", l) and l.count("｜") + l.count("|") >= 3]
    est = sum(1 for l in based if "估計" in l.split("｜")[-1])
    print("　價錢的依據：%d 行，寫「估計」的 %d 行（打開 shopping.md 看最後一欄）" % (len(based), est))
    fk = [x.strip() for x in re.findall(r"(?m)^\s*岔路[:：]\s*(.*)$", log or "") if x.strip() and not x.strip().startswith("無")]
    print("　記下的岔路：%d 輪" % len(fk) + ("；第一個：" + fk[0][:60] if fk else ""))
    # 叫別家（tools/ask.py 記的）
    for c in read_jsonl(os.path.join(d, "calls.jsonl")):
        print("　叫別家：%s　%s　模型 %s　%s 秒　%s" % (c.get("tool"), c.get("what"), c.get("model") or "帳號預設",
                                                c.get("seconds"), c.get("result")))
        if c.get("result") != "OK":
            notes.append("叫 %s 做 %s 沒有成功一次（%s）" % (c.get("tool"), c.get("what"), c.get("result")))
    if rounds and rounds[-1]["color"] == "RED":
        if rounds[-1]["round"] >= rounds[-1].get("max", 99):
            notes.append("最後一輪是紅燈，而且輪數跑滿了：這是正確的停法，不是失敗")
        else:
            todo.append("最後一輪是紅燈，輪數也還沒跑滿：它沒照【停止】做完")
    for t in notes:
        print("　注意：" + t)
    if todo:
        print("要看的事：")
        for t in todo:
            print("　- " + t)
        print("AUDIT: 有 %d 件事要看" % len(todo))
        return 1
    print("AUDIT: OK")
    return 0


def main(argv):
    if len(argv) > 2 and argv[1] == "audit":
        return audit(argv[2])
    if len(argv) > 1:
        print(__doc__)
        return 2
    bad = basic()
    if bad:
        print("GUARD: VIOLATION " + "；".join(bad))
        return 3
    print("GUARD: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
