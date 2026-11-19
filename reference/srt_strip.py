"""備援腳本（老師的版本）：把字幕檔的時間軸拿掉，只留下每一段講者說的話。

用法：python3 tools/srt_strip.py
讀：source/transcript.srt（唯讀，不會被改）
寫：data/cues.json（給程式讀）、data/raw.txt（給人讀，一段一行）
規格見 scripts_spec.md 的「腳本一」。只用標準函式庫。
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TIME = re.compile(r"^\s*\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[,.]\d{1,3}")


def parse_srt(text: str):
    """回傳 [{'n': 1, 'text': '…'}, …]。一段字幕＝時間軸那一行之後、到下一個空行之前的文字。"""
    cues, cur, seen_time = [], [], False
    for ln in text.replace("\r\n", "\n").replace("\r", "\n").split("\n") + [""]:
        s = ln.strip()
        if TIME.match(s):
            seen_time, cur = True, []
            continue
        if not s:
            if seen_time and cur:
                cues.append(" ".join(cur))
            cur, seen_time = [], False
            continue
        if seen_time:
            cur.append(s)
    return [{"n": i + 1, "text": unicodedata.normalize("NFC", t)} for i, t in enumerate(cues)]


def build(root: Path):
    text = (root / "source" / "transcript.srt").read_text(encoding="utf-8-sig")
    return {"cues": parse_srt(text)}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    src = ROOT / "source" / "transcript.srt"
    if not src.is_file():
        print("[FAIL] 找不到 source/transcript.srt（你是不是不在有 CLAUDE.md 的那個資料夾？）")
        return 1
    d = build(ROOT)
    if not d["cues"]:
        print("[FAIL] source/transcript.srt 裡沒有讀到任何字幕")
        return 1
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "cues.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "data" / "raw.txt").write_text("".join(f"{c['n']:>3}  {c['text']}\n" for c in d["cues"]), encoding="utf-8", newline="\n")
    print(f"[PASS] {len(d['cues'])} 段字幕 -> data/cues.json、data/raw.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
