#!/usr/bin/env python3
"""比較表：同一道關卡，把 runs/ 底下每一次的結果排成一張表，填進 eval.md（表以外的字不動）。
用法（Windows 把 python3 換成 py）：
  python3 tools/compare.py           印出表，並更新 eval.md
  python3 tools/compare.py --check   檢查：至少兩次結果，而且「我的結論：」你自己寫了 10 個字以上（EVAL: OK）
表的每一欄都從 tools/round.py 寫的 gate.jsonl、shopping.md、log.md 和驗收的檔案讀出來；花費讀不到（對話裡的用量只有工具自己知道），請自己抄進 eval.md。"""
import glob
import json
import os
import re
import sys
import time
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check import DATE, shopping_items   # 和關卡用同一個讀法
START, END = "<!-- table:start -->", "<!-- table:end -->"
SCORE = re.compile(r"(?:品味|驗收|總分)[^\n0-9]*?(\d+)\s*/\s*10")
ANY10 = re.compile(r"(\d+)\s*/\s*10")


def read_score(text, review=False):
    """「品味：8/10」的 8（也讀「總分：8/10」、全形的「８／１０」）。review=True（驗收的回答）時，什麼標籤都沒有，就取前三行裡第一個 N/10。"""
    t = unicodedata.normalize("NFKC", text or "")
    m = SCORE.search(t)
    if not m and review:
        m = ANY10.search("\n".join(t.splitlines()[:3]))
    return m.group(1) if m else None


def read_text(path):
    """先用 UTF-8 讀；Windows 的編輯器存成 Big5（cp950）也讀得進來。"""
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "cp950"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    raise SystemExit("EVAL: 讀不懂 %s 的編碼。請在 VS Code 右下角把編碼改成 UTF-8（Save with Encoding → UTF-8），存檔再跑一次。" % os.path.relpath(path, ROOT))


def maybe(path):
    try:
        return read_text(path)
    except (OSError, SystemExit):
        return ""


def ts(s):
    return time.mktime(time.strptime(s, "%Y-%m-%dT%H:%M:%S"))


def rows():
    out = []
    for gp in sorted(glob.glob(os.path.join(ROOT, "runs", "*", "gate.jsonl"))):
        d = os.path.dirname(gp)
        name = os.path.basename(d)
        if re.search(r"\.old\d+$", name):
            continue
        recs = [json.loads(l) for l in maybe(gp).splitlines() if l.strip()]
        rounds = [r for r in recs if r.get("round", 0) >= 1]
        if not rounds:
            continue
        last = rounds[-1]
        src = {}
        if os.path.isfile(os.path.join(d, "source.json")):
            src = json.loads(maybe(os.path.join(d, "source.json")) or "{}")
        tag = {"replay": "（重播）", "teacher": "（老師的紀錄）"}.get(src.get("by"), "")
        secs = src.get("span") if src.get("by") == "replay" and src.get("span") is not None else round(ts(last["t"]) - ts(recs[0]["t"]))
        rv = maybe(os.path.join(d, "review_r%d.md" % last["round"]))
        if rv:
            m = read_score(rv, True)
            taste = ("%s/10" % m if m else "讀不到") + "（驗收）"
        else:
            m = SCORE.findall(unicodedata.normalize("NFKC", maybe(os.path.join(d, "log.md"))))
            taste = ("%s/10" % m[-1] if m else "沒寫") + "（自評）"
        calls = [json.loads(l) for l in maybe(os.path.join(d, "calls.jsonl")).splitlines() if l.strip()]
        out.append("| %s%s | %s %d/%d | %d 輪 | %s 秒%s | %s | %s | %s | %s |" % (
            name, tag, last["color"], last["passed"], last["total"], len(rounds), secs, "（錄的）" if src.get("by") == "replay" else "",
            taste, sourced(d), forks(d), ("%d 次" % len(calls)) if calls else "沒有"))
    return out


def sourced(d):
    """採購清單裡，有來源和日期的價錢有幾個（家裡已有、0 元的不算）。"""
    items = [(p, b) for (_, _, p, b) in shopping_items(maybe(os.path.join(d, "shopping.md"))) if p]
    if not items:
        return "沒有"
    return "%d/%d" % (sum(1 for p, b in items if DATE.search(b) and "估計" not in b), len(items))


def forks(d):
    """log.md 裡「岔路：」寫了東西（不是「無」）的有幾輪。"""
    lines = re.findall(r"(?m)^\s*岔路[:：]\s*(.*)$", maybe(os.path.join(d, "log.md")))
    return "%d 輪" % sum(1 for x in lines if x.strip() and not x.strip().startswith("無"))


def conclusion(text):
    m = re.search(r"我的結論：(.*)", text)
    return m.group(1).strip() if m else ""


def main(argv):
    path = os.path.join(ROOT, "eval.md")
    text = read_text(path)
    r = rows()
    if "--check" in argv:
        if len(r) < 2:
            print("EVAL: 還沒有兩次結果（先跑 a 和 b）")
            return 1
        if conclusion(text).startswith("（範例）"):
            print("EVAL: 這一行還是老師的範例，請換成你自己的話（把「我的結論：」後面的字整個換掉）")
            return 1
        if len(conclusion(text)) < 10:
            print("EVAL: 還沒寫結論（在 eval.md 的「我的結論：」後面，用你自己的話寫至少 10 個字）")
            return 1
        print("EVAL: OK")
        return 0
    table = ["| 名字 | 最後一次關卡 | 輪數 | 起點到最後一次關卡 | 品味（誰評的） | 價錢有出處 | 記了岔路 | 叫別家 |",
             "|---|---|---|---|---|---|---|---|"] + (r or ["| （還沒有跑完一輪的資料夾） | | | | | | | |"])
    print("\n".join(table))
    if START in text and END in text:
        a, b = text.index(START) + len(START), text.index(END)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text[:a] + "\n" + "\n".join(table) + "\n" + text[b:])
        print("\n（已更新 eval.md 的表；你寫的字沒有動。花多少只有工具自己知道：訂閱的人看不到金額。Claude Code：開新對話前、做完各打一次 /usage，把「Current session」的 % 相減，寫進 eval.md 的「b 花了多少」那一行；其他工具：那一行照 eval.md 上面寫的做。）")
    else:
        print("\neval.md 裡找不到表的位置（%s 與 %s），所以沒有更新。" % (START, END))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
