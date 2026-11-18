"""檢查與產生網頁共用的小函式：數字數、拆出正文與補述區塊。只用標準函式庫。
"""
import json
import re
import unicodedata
from pathlib import Path


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def NFC(s) -> str:
    return unicodedata.normalize("NFC", str(s))


def letters(s: str) -> str:
    """只留下「字」：中文字、英文字母、數字。空白與標點都不算，大小寫視為相同。"""
    return "".join(c for c in unicodedata.normalize("NFC", str(s)).lower() if unicodedata.category(c)[0] in "LN")


def count(s: str) -> int:
    return len(letters(s))


def body_paragraphs(md: str):
    """一份筆記的「正文」：不含標題（#）與補述區塊（> 開頭）。回傳段落清單。"""
    return [ln.strip() for ln in md.replace("\r\n", "\n").split("\n")
            if ln.strip() and not ln.lstrip().startswith((">", "#"))]


def quote_blocks(md: str):
    """補述區塊：連續以 > 開頭的行算一塊。回傳每一塊的行清單（去掉 > ）。"""
    blocks, cur = [], []
    for ln in md.replace("\r\n", "\n").split("\n"):
        if ln.lstrip().startswith(">"):
            cur.append(ln.lstrip()[1:].strip())
        else:
            if cur:
                blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return [[x for x in b if x] for b in blocks if any(b)]


def dump(p: Path, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
