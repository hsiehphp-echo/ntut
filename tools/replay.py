#!/usr/bin/env python3
"""重播：沒有能用的 AI 工具時用。不呼叫 AI。（Windows 把 python3 換成 py）
  python3 tools/replay.py a      重播動手 A（也可以是 b、c）
  python3 tools/replay.py a --name a2   放到別的資料夾
它把老師的 AI 照同一份目標文件真的寫出來的檔案，一輪一輪放進 runs/<名字>，每一輪都用真的 tools/round.py
（守衛和關卡）檢查一次，最後放進那一次 AI 自己寫的 log.md。之後的稽核、比較，和大家一樣做。
最後一行：REPLAY: OK runs/<名字>（幾輪），或 REPLAY: 沒有這一段的紀錄。"""
import json
import os
import shutil
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BEFORE = ("plan.md", "fridge.md", "recipe_zh.md")   # 第 1 輪之前就有的檔案（C 的任務佈局、看圖、翻譯）


def gate(folder, mx):
    p = subprocess.run([sys.executable, os.path.join(HERE, "round.py"), folder, "--max", str(mx)], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.stdout.strip().splitlines()


def main(argv):
    if len(argv) < 2 or argv[1] not in ("a", "b", "c"):
        print(__doc__)
        return 2
    stage = argv[1]
    name = argv[argv.index("--name") + 1] if "--name" in argv and argv.index("--name") + 1 < len(argv) else stage
    src = os.path.join(HERE, "fixtures", stage)
    try:
        with open(os.path.join(src, "meta.json"), encoding="utf-8") as f:
            meta = json.load(f)
    except OSError:
        print("REPLAY: 沒有這一段的紀錄（tools/fixtures/%s）" % stage)
        return 1
    os.chdir(ROOT)
    folder = "runs/" + name
    if os.path.isdir(folder) and os.listdir(folder):
        n = 1
        while os.path.exists("%s.old%d" % (folder, n)):
            n += 1
        os.rename(folder, "%s.old%d" % (folder, n))
        print("舊的 %s 已改名成 %s.old%d（沒有刪除任何東西）" % (folder, folder, n))
    os.makedirs(folder, exist_ok=True)
    print("重播：%s 用 %s，照 goals/goal_%s.md 真的跑出來的檔案（%s，老師的電腦）。這一次沒有呼叫 AI；守衛和關卡是真的。"
          % (meta["tool_label"], meta["model_label"], stage, meta["date"]))
    mx = meta.get("max", 3)
    out = gate(folder, mx)
    print("起點　　" + out[-2])
    for f in BEFORE:
        if os.path.isfile(os.path.join(src, f)):
            shutil.copyfile(os.path.join(src, f), os.path.join(folder, f))
    k = 1
    t = time.time() - 60
    while os.path.isdir(os.path.join(src, "round%d" % k)):
        rd = os.path.join(src, "round%d" % k)
        for i, f in enumerate(("shopping.md", "menu.json", "menu.html")):
            if os.path.isfile(os.path.join(rd, f)):
                shutil.copyfile(os.path.join(rd, f), os.path.join(folder, f))
                os.utime(os.path.join(folder, f), (t + i, t + i))   # 照當時的順序：先採購清單，再菜單
        out = gate(folder, mx)
        fails = [l.strip() for l in out if l.strip().startswith("[FAIL]")]
        print("第 %d 輪　%s　%s" % (k, out[0], out[-2]))
        for l in fails:
            print("　　" + l)
        rv = os.path.join(src, "review_r%d.md" % k)
        if os.path.isfile(rv):
            shutil.copyfile(rv, os.path.join(folder, "review_r%d.md" % k))
        k += 1
        t += 10
    for f in ("log.md", "calls.jsonl"):
        if os.path.isfile(os.path.join(src, f)):
            shutil.copyfile(os.path.join(src, f), os.path.join(folder, f))
    tt = meta.get("times") or []
    fmt = "%Y-%m-%dT%H:%M:%S"
    span = round(time.mktime(time.strptime(tt[-1], fmt)) - time.mktime(time.strptime(tt[0], fmt))) if len(tt) > 1 else None
    with open(os.path.join(folder, "source.json"), "w", encoding="utf-8") as f:
        json.dump({"by": "replay", "tool": meta["tool_label"], "model": meta["model_label"], "date": meta["date"],
                   "seconds": meta["seconds"], "span": span}, f, ensure_ascii=False)
    print("log.md 是那一次 AI 自己寫的，原樣放進來。" + ("當時起點到最後一次關卡花了 %d 秒；" % span if span is not None else "")
          + "整次執行花了 %d 秒（headless，不開對話）。" % meta["seconds"])
    print("REPLAY: OK %s（%d 輪）" % (folder, k - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
