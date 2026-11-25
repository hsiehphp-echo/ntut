#!/usr/bin/env python3
"""換課：同一個 ntut 資料夾，在第二堂和第一堂之間切換。（Windows 把 python3 換成 py，沒有 py 就用 python）
  python3 tools/switch_lesson.py 1    想複習第一堂：先把第二堂的版本存進 lesson2_keep/，再把 lesson1_backup/ 的第一堂原檔放回原位
  python3 tools/switch_lesson.py 2    複習完，回到第二堂：先把第一堂的版本存回 lesson1_backup/，再把 lesson2_keep/ 的第二堂版本放回原位
只複製，不刪除任何檔案。換完會自己跑一次那一堂的檢查，印出最後一行。最後一行是 SWITCH: OK … 或 SWITCH: 停 …。
換完請離開 AI 對話、重新開一個：AI 開始時讀的是當時的 CLAUDE.md。"""
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKUP = "lesson1_backup"
KEEP = "lesson2_keep"
# 第一堂和第二堂同名、會衝突的檔案（路徑在三個地方都一樣：原位、lesson1_backup/、lesson2_keep/）
FILES = ["CLAUDE.md", "README.md", "spec.md", "tools/check.py"]
MARK = {1: "# 第一堂專案", 2: "# 第二堂專案"}
PY = "py" if sys.platform == "win32" else "python3"


def p(*parts):
    return os.path.join(ROOT, *parts)


def which():
    try:
        with open(p("CLAUDE.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    got = [n for n, m in MARK.items() if m in text]
    return got[0] if len(got) == 1 else None


def copy(src_dir, dst_dir, label):
    for rel in FILES:
        src = p(src_dir, *rel.split("/")) if src_dir else p(*rel.split("/"))
        dst = p(dst_dir, *rel.split("/")) if dst_dir else p(*rel.split("/"))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"  {(src_dir + '/' if src_dir else '') + rel} → {(dst_dir + '/' if dst_dir else '') + rel}")
    print(f"SWITCH: {label}")


def last_line(args):
    r = subprocess.run([sys.executable] + args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [x for x in (r.stdout or "").splitlines() if x.strip()] or \
        [x for x in (r.stderr or "").splitlines() if x.strip()] or ["（沒有輸出）"]
    return lines[-1]


def main():
    want = sys.argv[1] if len(sys.argv) > 1 else ""
    if want not in ("1", "2"):
        print(__doc__)
        print("SWITCH: 停：請在後面寫 1（換成第一堂）或 2（換回第二堂）")
        return 2
    want = int(want)
    if not os.path.isdir(p(BACKUP)):
        print(f"SWITCH: 停：找不到 {BACKUP}/。這個資料夾不是用 git pull 更新過的 ntut（壓縮檔沒有第一堂的檔案）。")
        return 1
    now = which()
    if now is None:
        print("SWITCH: 停：看不出現在是第幾堂（CLAUDE.md 被改過，或不見了）。什麼都沒有動。請把這一行貼給老師。")
        return 1
    if now == want:
        print(f"SWITCH: 停：現在已經是第{'一二'[want - 1]}堂了，什麼都沒有動。")
        return 1
    if want == 1:
        missing = [r for r in FILES if not os.path.isfile(p(BACKUP, *r.split("/")))]
        if missing:
            print(f"SWITCH: 停：{BACKUP}/ 裡少了 {'、'.join(missing)}，什麼都沒有動。")
            return 1
        print(f"一、先把第二堂的版本存進 {KEEP}/：")
        copy("", KEEP, f"第二堂的 {len(FILES)} 個檔案已存進 {KEEP}/")
        print(f"二、把第一堂的原檔放回原位：")
        copy(BACKUP, "", f"第一堂的 {len(FILES)} 個檔案已放回原位")
        print(f"三、第一堂的檢查（{PY} tools/check.py）最後一行：")
        print("  " + last_line([os.path.join("tools", "check.py")]))
        print("SWITCH: OK，現在是第一堂。請離開 AI 對話，重新開一個，它才會讀到第一堂的 CLAUDE.md。"
              f"複習完，貼「回到第二堂」那一段（或自己打 {PY} tools/switch_lesson.py 2）。")
        return 0
    missing = [r for r in FILES if not os.path.isfile(p(KEEP, *r.split("/")))]
    if missing:
        print(f"SWITCH: 停：{KEEP}/ 裡少了 {'、'.join(missing)}，什麼都沒有動。請用 git checkout -- {' '.join(missing)} 拿回老師的版本。")
        return 1
    print(f"一、先把第一堂的版本（含你複習時改的地方）存回 {BACKUP}/：")
    copy("", BACKUP, f"第一堂的 {len(FILES)} 個檔案已存回 {BACKUP}/")
    print(f"二、把第二堂的版本放回原位：")
    copy(KEEP, "", f"第二堂的 {len(FILES)} 個檔案已放回原位")
    print(f"三、第二堂的守衛（{PY} tools/guard.py）和起點關卡（{PY} tools/check.py runs/a）最後一行：")
    print("  " + last_line([os.path.join("tools", "guard.py")]))
    print("  " + last_line([os.path.join("tools", "check.py"), "runs/a"]))
    print("SWITCH: OK，現在是第二堂。請離開 AI 對話，重新開一個，它才會讀到第二堂的 CLAUDE.md。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
