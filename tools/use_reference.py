#!/usr/bin/env python3
"""備援：把講師寫好的腳本拿來用，讓你可以繼續往下做。

用法：python3 tools/use_reference.py            兩支都拿
      python3 tools/use_reference.py srt_strip  只拿「拿掉時間軸」
      python3 tools/use_reference.py fix_terms  只拿「校正專有名詞」

什麼時候用：請 AI 寫了三次，G1 還是紅；或你想先往下走、回家再研究。
它會把 reference/ 裡的腳本複製到 tools/。你原本寫的那一支不會被刪掉，會改名成 *.mine.py 留著對照。
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAMES = ["srt_strip", "fix_terms"]


def main() -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    want = [a for a in sys.argv[1:] if not a.startswith("-")] or NAMES
    bad = [n for n in want if n not in NAMES]
    if bad:
        print(f"[FAIL] 不認識的腳本：{'、'.join(bad)}（只有 srt_strip 和 fix_terms）")
        return 2
    for n in want:
        src, dst = ROOT / "reference" / f"{n}.py", ROOT / "tools" / f"{n}.py"
        if not src.is_file():
            print(f"[FAIL] 找不到 reference/{n}.py")
            return 1
        if dst.is_file() and dst.read_bytes() != src.read_bytes():
            keep = ROOT / "tools" / f"{n}.mine.py"
            shutil.copyfile(dst, keep)
            print(f"[PASS] 你原本的 tools/{n}.py 另存成 tools/{n}.mine.py（留著對照，不會被執行）")
        shutil.copyfile(src, dst)
        print(f"[PASS] 已把講師的版本放到 tools/{n}.py，現在可以跑 python3 tools/{n}.py")
    print("記得在 loop_log.md 記一行：哪一支用了備援、你的版本卡在哪裡。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
