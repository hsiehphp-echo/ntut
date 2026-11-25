#!/usr/bin/env python3
"""一輪關卡。這是目標文件裡唯一的關卡指令，由 AI 自己執行。（Windows 把 python3 換成 py）
  python3 tools/round.py <資料夾> --max N     跑一輪：守衛、關卡、記一筆、說下一步
  python3 tools/round.py <資料夾> --archive   把這個資料夾改名成 <資料夾>.old1（不刪任何東西）
第一次在還沒有菜單的資料夾跑，是「起點」，不算一輪。最後兩行是 ROUND: 和 NEXT:。
紅燈或綠燈，結束碼都是 0（結果寫在畫面上）；已經跑滿輪數是 4；指令寫錯是 2。"""
import hashlib
import json
import os
import re
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
# 這兩個值由老師的 make_l2_packs.py 寫進來（換行符號先統一再算）。
EXPECT = {"spec.md": "a036ea51327e23d83113e21e3ab32c01c0de5de6100c210ad1a0e6ade722dd8c",
          "tools/check.py": "30e0a7b03056af400565372faf0a8e0c1eefd87e301c33bf459f75c7f707ea1f"}
WATCH = ("spec.md", "tools/check.py", "tools/guard.py", "tools/round.py", "taste.md")
FILES = ("shopping.md", "menu.json", "menu.html")


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


def chain(prev, rec):
    body = {k: v for k, v in rec.items() if k != "chain"}
    return hashlib.sha256((prev + json.dumps(body, sort_keys=True, ensure_ascii=False)).encode("utf-8")).hexdigest()[:16]


def main(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        print(__doc__)
        return 2
    d = argv[1].replace("\\", "/").rstrip("/")
    mx = 3
    if "--max" in argv:
        try:
            mx = int(argv[argv.index("--max") + 1])
        except (ValueError, IndexError):
            print("--max 後面要寫一個整數，例如 --max 3")
            return 2
    os.chdir(ROOT)
    if not re.fullmatch(r"runs/[\w.-]+", d) or ".." in d:
        print("資料夾要寫成 runs/名字（例如 runs/a），只能在 runs/ 底下。")
        return 2
    if "--archive" in argv:
        n = 1
        while os.path.exists("%s.old%d" % (d, n)):
            n += 1
        if os.path.isdir(d):
            os.rename(d, "%s.old%d" % (d, n))
            print("已改名成 %s.old%d（沒有刪除任何東西）" % (d, n))
        else:
            print("沒有 %s，不用改名。" % d)
        return 0
    os.makedirs(d, exist_ok=True)
    gp = os.path.join(d, "gate.jsonl")
    recs = read_jsonl(gp)
    done = [r for r in recs if r.get("round", 0) >= 1]
    if len(done) >= mx:
        print("ROUND: LIMIT 已經跑滿 %d 輪，這一次沒有檢查" % mx)
        print("NEXT: 停。在 log.md 寫好最後一輪，回報還沒過的項目。")
        return 4

    # 1. 守衛
    cur = {k: digest(k) for k in WATCH}
    bad = ["%s 被改過或不見了" % rel for rel, want in EXPECT.items() if cur[rel] != want]
    if recs:
        for rel in ("tools/round.py", "tools/guard.py", "taste.md"):
            if cur[rel] != recs[0]["hashes"].get(rel):
                bad.append("%s 在這次開始之後被改過" % rel)
    has_files = any(os.path.isfile(os.path.join(d, f)) for f in FILES)
    is_start = not recs and not has_files
    sp, mp = os.path.join(d, "shopping.md"), os.path.join(d, "menu.json")
    order_ok = True
    if not any(r.get("saw_menu") for r in recs) and os.path.exists(mp):   # 第一次看到 menu.json 的那一輪比先後
        if not os.path.exists(sp) or os.path.getmtime(sp) > os.path.getmtime(mp) + 0.001:
            order_ok = False
            bad.append("shopping.md 沒有比 menu.json 先寫")
    print("GUARD: OK" if not bad else "GUARD: VIOLATION " + "；".join(bad))

    # 2. 關卡（tools/check.py，原封不動）
    p = subprocess.run([sys.executable, os.path.join(HERE, "check.py"), d], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    text = p.stdout
    sys.stdout.write(text if text.endswith("\n") else text + "\n")
    m = re.search(r"RESULT: (GREEN|RED) \((\d+)/(\d+)\)", text)
    color, ok, total = (m.group(1), int(m.group(2)), int(m.group(3))) if m else ("RED", 0, 8)
    if not m:   # 關卡自己當掉了：沒有 RESULT 那一行。把錯誤的最後一行印出來，讓 AI 有一行可以讀
        last = (p.stderr or "").strip().splitlines()[-1:] or ["（沒有錯誤訊息）"]
        print("[FAIL] 關卡沒有跑完（程式出錯，多半是 menu.json 的內容不對）：%s" % last[0][:200])
        print("RESULT: RED (0/8)")
    fails = re.findall(r"\[FAIL\] (M\d)", text)
    if bad:
        color = "RED"

    # 3. 記一筆（gate.jsonl，每一行接著上一行的雜湊），每一輪的檔案備份到 round<N>/
    n = 0 if is_start else len(done) + 1
    rec = {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "round": n, "max": mx, "color": color, "passed": ok, "total": total,
           "fails": fails, "guard": "OK" if not bad else "VIOLATION", "guard_detail": bad, "order_ok": order_ok,
           "saw_menu": os.path.exists(mp), "hashes": cur,
           "files": {f: digest(os.path.join(d, f))[:16] for f in FILES}}
    rec["chain"] = chain(recs[-1]["chain"] if recs else "0", rec)
    with open(gp, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    if n >= 1:
        rd = os.path.join(d, "round%d" % n)
        os.makedirs(rd, exist_ok=True)
        for f in FILES:
            if os.path.isfile(os.path.join(d, f)):
                shutil.copyfile(os.path.join(d, f), os.path.join(rd, f))

    # 4. 兩行結論
    if is_start:
        print("ROUND: 0（起點）%s (%d/%d)" % (color, ok, total))
        print("NEXT: 這是起點，不算一輪。先寫 shopping.md，再寫 menu.json 和 menu.html，然後再執行一次這個指令。")
        return 0
    print("ROUND: %d/%d %s (%d/%d)" % (n, mx, color, ok, total))
    if bad:
        print("NEXT: 守衛說有地方不對。在 log.md 寫明這件事；不要再改 tools/、spec.md、taste.md。")
    elif n >= mx:
        print("NEXT: 這是最後一輪（上限 %d）。在 log.md 記下這一輪，然後停，回報還沒過的項目。" % mx)
    elif color == "GREEN" and not any(r.get("color") == "GREEN" for r in done):
        print("NEXT: 第一次全綠。在 log.md 記下這一輪，再做一輪品味：只改品味最弱的一條，關卡要保持綠燈，再執行這個指令。")
    elif color == "GREEN":
        print("NEXT: 全綠。在 log.md 記下這一輪；品味到 8 分以上就停，不到就改最弱的一條再跑。")
    else:
        print("NEXT: 在 log.md 記下這一輪，只修 [FAIL] 的那幾行，再執行這個指令。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
