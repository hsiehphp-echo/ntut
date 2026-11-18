"""檢查 plan.md：至少 5 個編號步驟，每步有 輸入／工具／輸出／檢查 四欄。

用法：python3 tools/plan_check.py [--root DIR]
步驟寫法（任一種）：「1.」「1、」「1)」開頭，或「### 步驟 1」標題；欄位寫成「- 輸入：…」。
輸出 [PASS]/[FAIL] 與 RESULT: GREEN|RED；只有綠燈 exit 0。
"""
import argparse
import re
import sys
from pathlib import Path

FIELDS = ["輸入", "工具", "輸出", "檢查"]
START = re.compile(r"^\s*(?:#{2,4}\s*(?:步驟\s*)?(\d+)\b|(?:步驟\s*)?(\d+)\s*[.、)）:：])")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    a = ap.parse_args()
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        "✅❌".encode(enc)
        em = True
    except Exception:
        em = False
    p = Path(a.root) / "plan.md"
    if not p.is_file():
        print(f"[FAIL] {'❌ ' if em else ''}找不到 plan.md")
        print("RESULT: RED (0/1)")
        return 1
    try:
        text = p.read_text(encoding="utf-8-sig")  # 編輯器可能加 BOM、用 \r\n，都要能讀
    except UnicodeDecodeError:
        print(f"[FAIL] {'❌ ' if em else ''}plan.md 不是 UTF-8 編碼（請在編輯器裡改用 UTF-8 另存）")
        print("RESULT: RED (0/1)")
        return 1
    steps, cur = [], None
    for ln in text.splitlines():
        m = START.match(ln)
        if m:
            cur = {"n": m.group(1) or m.group(2), "t": []}
            steps.append(cur)
        if cur is not None:
            cur["t"].append(ln)
    problems = []
    if len(steps) < 5:
        problems.append(f"只有 {len(steps)} 個步驟，至少要 5 個")
    for s in steps:
        body = "\n".join(s["t"])
        miss = [f for f in FIELDS if not re.search(rf"{f}\s*[：:]\s*\S", body)]
        if miss:
            problems.append(f"步驟 {s['n']} 缺少或留空：{'、'.join(miss)}")
    if problems:
        print(f"[FAIL] {'❌ ' if em else ''}" + "；".join(problems[:5]))
        print("RESULT: RED (0/1)")
        return 1
    print(f"[PASS] {'✅ ' if em else ''}plan.md 有 {len(steps)} 個步驟，每步都有輸入／工具／輸出／檢查")
    print("RESULT: GREEN (1/1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
