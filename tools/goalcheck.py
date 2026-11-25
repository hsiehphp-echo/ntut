#!/usr/bin/env python3
"""目標文件的檢查：七個必要的部分都寫了沒有，加上兩個讓它自己發現問題的部分（加分，沒寫不算錯）。（Windows 把 python3 換成 py）
  python3 tools/goalcheck.py                    檢查 goals/my_goal.md
  python3 tools/goalcheck.py goals/goal_a.md    檢查別的目標文件
它只看每個部分有沒有寫、【停止】有沒有寫數字；寫得好不好，它不判斷，那要你和同學判斷。
一個部分一行，最後一行 GOAL: OK 或 GOAL: 還有 n 個部分沒寫。
加分的兩個部分：【自我檢查】（每一輪用使用者的眼睛問自己什麼）、【工具】（哪些事先做成程式、每一輪重跑）。"""
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = ["目標", "品質標準與品味", "規則", "關卡", "每一輪的紀錄", "停止"]
BONUS = ["自我檢查", "工具"]
GUIDE = re.compile(r"^（[^（）]*(?:（[^（）]*）[^（）]*)*）$")   # 範本裡的引導問題：整行都在全形括號裡


def body(lines):
    kept = [l.strip() for l in lines if l.strip() and not GUIDE.match(l.strip())]
    return "\n".join(kept)


def main(argv):
    rel = argv[1] if len(argv) > 1 else "goals/my_goal.md"
    path = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    try:
        with open(path, encoding="utf-8-sig") as f:
            text = f.read()
    except OSError:
        print("找不到 %s。請確認你在起始包的資料夾裡。" % rel)
        print("GOAL: 找不到檔案")
        return 2
    except UnicodeDecodeError:
        print("讀不懂 %s 的編碼。請在 VS Code 右下角把編碼改成 UTF-8，存檔再跑一次。" % rel)
        print("GOAL: 讀不懂編碼")
        return 2
    lines = text.splitlines()
    heads = {}
    for i, l in enumerate(lines):
        m = re.match(r"^\s*(?:#+\s*)?【([^】]+)】\s*$", l)
        if m:
            heads[m.group(1)] = i
    first = min(heads.values()) if heads else len(lines)
    rows = [("做到完（第一行）", bool(body(lines[:first])), "第一行寫清楚：直接開始、做到完、不要停下來問")]
    order = sorted(heads.items(), key=lambda kv: kv[1])
    for p in PARTS:
        if p not in heads:
            rows.append(("【%s】" % p, False, "找不到【%s】這個標題" % p))
            continue
        i = heads[p]
        nxt = [j for _, j in order if j > i]
        b = body(lines[i + 1:(nxt[0] if nxt else len(lines))])
        if p == "停止" and b and not re.search(r"[0-9０-９一二兩三四五六七八九十]", b):
            rows.append(("【停止】", False, "寫了，但沒有數字：最多幾輪？"))
            continue
        rows.append(("【%s】" % p, bool(b), "還沒寫（括號裡的問題要換成你的答案）"))
    miss = 0
    print("檢查 %s" % rel)
    for name, ok, why in rows:
        print("　%s %s%s" % ("[OK]  " if ok else "[還沒]", name, "" if ok else "：" + why))
        miss += 0 if ok else 1
    for p in BONUS:
        i = heads.get(p)
        nxt = [j for _, j in order if i is not None and j > i]
        b = body(lines[i + 1:(nxt[0] if nxt else len(lines))]) if i is not None else ""
        print("　%s 【%s】%s" % ("[加分]" if b else "[可加]", p, "" if b else "：沒寫不算錯；寫了，它比較會自己發現問題"))
    if miss:
        print("GOAL: 還有 %d 個部分沒寫" % miss)
        return 1
    print("GOAL: OK（七個必要的部分都寫了；寫得好不好，請同學或 AI 幫你看）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
