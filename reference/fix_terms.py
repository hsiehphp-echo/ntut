#!/usr/bin/env python3
"""備援腳本（講師的版本）：照「校正用語」清單，把語音辨識聽錯的專有名詞換成對的。

用法：python3 tools/fix_terms.py
讀：data/cues.json、data/corrections.json（清單由人確認）
寫：data/cues_fixed.json（給程式讀）、data/fixed.txt（給人讀，一段一行）
規格見 scripts_spec.md 的「腳本二」。只用標準函式庫。
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_corrections(p: Path):
    d = json.loads(p.read_text(encoding="utf-8-sig"))
    if not isinstance(d, list):
        raise ValueError("校正用語要是一個清單")
    out = []
    for i, c in enumerate(d, 1):
        if not isinstance(c, dict) or not str(c.get("wrong", "")).strip() or "right" not in c:
            raise ValueError(f"第 {i} 條校正用語缺少 wrong 或 right")
        out.append((str(c["wrong"]), str(c["right"])))
    return out


def apply_corrections(cues, pairs):
    """長的詞先換；已經換過的地方不會被後面的詞再換一次。回傳（新字幕, 每個詞換了幾處）。"""
    order = sorted(pairs, key=lambda x: -len(x[0]))
    hits = {w: 0 for w, _ in pairs}
    out = []
    for c in cues:
        t, marks = c["text"], []
        for w, r in order:
            n = t.count(w)
            if n:
                hits[w] += n
                key = f"\u0000{len(marks)}\u0000"
                marks.append((key, r))
                t = t.replace(w, key)
        for key, r in marks:
            t = t.replace(key, r)
        out.append({"n": c["n"], "text": t})
    return out, hits


def build(root: Path):
    cues = json.loads((root / "data" / "cues.json").read_text(encoding="utf-8-sig"))["cues"]
    fixed, hits = apply_corrections(cues, load_corrections(root / "data" / "corrections.json"))
    return {"cues": fixed}, hits


def main() -> int:
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    if not (ROOT / "data" / "cues.json").is_file():
        print("[FAIL] 還沒有 data/cues.json（請先跑 python3 tools/srt_strip.py）")
        return 1
    if not (ROOT / "data" / "corrections.json").is_file():
        print("[FAIL] 找不到 data/corrections.json（校正用語清單）")
        return 1
    try:
        d, hits = build(ROOT)
    except ValueError as e:
        print(f"[FAIL] data/corrections.json 讀不懂：{e}")
        return 1
    (ROOT / "data" / "cues_fixed.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "data" / "fixed.txt").write_text("".join(f"{c['n']:>3}  {c['text']}\n" for c in d["cues"]), encoding="utf-8", newline="\n")
    for w, n in hits.items():
        if n == 0:
            print(f"[WARN] 清單裡的「{w}」在字幕裡找不到，這一條沒有用到")
    print(f"[PASS] 套用 {len(hits)} 條校正用語，共換掉 {sum(hits.values())} 處；{len(d['cues'])} 段字幕 -> data/cues_fixed.json、data/fixed.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
