#!/usr/bin/env python3
"""午餐菜單的關卡（gate）。
用法：python3 tools/check.py [資料夾，預設 runs/a]      （Windows 把 python3 換成 py）
八條規則的說明在 spec.md。這裡沒有藏起來的上限：預算是 menu.json 裡你自己記下的那一個。
每條規則印一行：[PASS] M1 ✅ ... 或 [FAIL] M1 ❌ ...；最後一行 RESULT: GREEN (8/8) 或 RESULT: RED (n/8)。
全綠結束碼是 0，否則是 1。這支程式不能被 AI 改（守衛會檢查）。"""
import json
import os
import re
import sys
from html.parser import HTMLParser

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 這裡沒有藏起來的數字：預算是使用者說的、AI 自己記下來的那一個；時間要說得通；價錢要有依據。
N = 4
CATS = ["飯", "肉", "菜", "湯"]
NAMES = {
    "M1": "盤數和人數", "M2": "預算", "M3": "飯肉菜湯", "M4": "時間說得通",
    "M5": "食材不重複", "M6": "每道菜都有做法", "M7": "menu.html 有菜名和幣別", "M8": "採購清單對得上、價錢有依據",
}
DATE = re.compile(r"(19|20)\d\d\s*[-/.年]\s*\d{1,2}")


def shopping_items(s):
    """採購清單的每一行「- 食材｜買多少｜約幾元｜依據」→ [(行號, 食材, 價錢或 None, 依據)]。"""
    out = []
    for no, line in enumerate(s.splitlines(), 1):
        t = line.strip()
        if not re.match(r"^[-*]\s", t):
            continue
        parts = [x.strip() for x in re.split(r"[｜|]", t[1:].strip())]
        if len(parts) < 2:
            continue
        name = parts[0]
        price = None
        if len(parts) >= 3:
            m = re.search(r"(\d[\d,]*)\s*元", parts[2]) or re.fullmatch(r"\D*?(\d[\d,]*)\D*", parts[2])
            if m:
                price = int(m.group(1).replace(",", ""))
        basis = "｜".join(parts[3:]).strip() if len(parts) >= 4 else ""
        out.append((no, name, price, basis))
    return out


def read_text(path):
    with open(path, encoding="utf-8-sig") as f:
        return f.read()


def text_or_none(path):
    try:
        return read_text(path)
    except (UnicodeDecodeError, OSError):
        return None


class _Visible(HTMLParser):
    """網頁上看得到的字：不算註解、程式、樣式、屬性，也不算藏起來的元素（hidden、aria-hidden="true"、display:none）。"""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack = [], []

    def handle_starttag(self, tag, attrs):
        if tag in self.VOID:
            return
        a = {k: (v or "") for k, v in attrs}
        hide = (tag in ("script", "style", "template") or "hidden" in a or a.get("aria-hidden", "").lower() == "true"
                or re.search(r"display\s*:\s*none|visibility\s*:\s*hidden", a.get("style", ""), re.I))
        self.stack.append((tag, bool(hide)))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not any(h for _, h in self.stack):
            self.out.append(data)


def visible_text(h):
    p = _Visible()
    try:
        p.feed(h)
        p.close()
    except Exception:
        return re.sub(r"<[^>]+>", " ", h)
    return "".join(p.out)


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def evaluate(d):
    """回傳 {id: (通過?, 說明)}。"""
    res = {}

    def ok(k, msg):
        res[k] = (True, msg)

    def bad(k, msg):
        res[k] = (False, msg)

    mp = os.path.join(d, "menu.json")
    dishes = None
    data = None
    why = ""
    if not os.path.isfile(mp):
        why = "找不到 %s" % mp.replace(os.sep, "/")
    else:
        try:
            data = json.loads(read_text(mp))
            dishes = data["dishes"]
            if not isinstance(dishes, list):
                raise TypeError("dishes 不是清單")
            dishes = [x for x in dishes if isinstance(x, dict)] if all(isinstance(x, dict) for x in dishes) else None
            if dishes is None:
                why = "menu.json 的 dishes 裡每一項都要是一道菜（有 name、category 等欄位）"
        except KeyError as e:
            why = "menu.json 缺少最上層欄位 %s，要有 \"dishes\" 這個清單" % e
        except UnicodeDecodeError:
            why = "menu.json 讀不懂，請存成 UTF-8"
        except json.JSONDecodeError as e:
            why = "menu.json 不是合法的 JSON：大約在第 %d 行第 %d 個字（%s）" % (e.lineno, e.colno, e.msg)
        except Exception as e:
            why = "menu.json 讀不到或格式不對（%s）" % type(e).__name__
    if dishes is None:
        for k in ("M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8"):
            bad(k, "%s：%s" % (NAMES[k], why or "沒有 menu.json 可以對照"))
        return res

    sp = os.path.join(d, "shopping.md")
    stext = text_or_none(sp) if os.path.isfile(sp) else None
    items = shopping_items(stext) if stext is not None else []
    # M1
    sv = data.get("servings") if isinstance(data, dict) else None
    if len(dishes) != N:
        bad("M1", "盤數和人數：現在 %d 道，要剛好 %d 道" % (len(dishes), N))
    elif not (is_int(sv) and sv >= 1):
        bad("M1", "盤數和人數：%d 道；menu.json 要有 servings（幾個人吃，整數）" % len(dishes))
    else:
        ok("M1", "盤數和人數：%d 道，%d 人份" % (len(dishes), sv))
    # M2：預算是 AI 自己從使用者的話讀出來、記在 menu.json 的那一個
    bud = data.get("budget") if isinstance(data, dict) else None
    amount = bud.get("amount") if isinstance(bud, dict) else None
    reading = bud.get("reading") if isinstance(bud, dict) else None
    prices = [x.get("price") for x in dishes]
    known = [p for (_, _, p, _) in items if p is not None]
    if not (is_int(amount) and amount > 0):
        bad("M2", "預算：menu.json 要有 budget.amount（你讀到的預算，整數新台幣元）")
    elif not (isinstance(reading, str) and len(reading.strip()) >= 8):
        bad("M2", "預算：menu.json 要有 budget.reading：用一兩句話寫你怎麼讀使用者說的錢和份量")
    elif not all(is_int(v) and v >= 0 for v in prices):
        bad("M2", "預算：每道菜的 price 都要是 0 以上的整數（新台幣元）")
    elif stext is None or not items:
        bad("M2", "預算：讀不到採購清單的價錢（先看 M8）")
    elif len(known) != len(items):
        bad("M2", "預算：採購清單有 %d 行讀不到價錢（先看 M8）" % (len(items) - len(known)))
    elif sum(known) > amount:
        bad("M2", "預算：採購清單總共 %d 元，你記下的預算 %d 元（新台幣），多了 %d 元" % (sum(known), amount, sum(known) - amount))
    else:
        ok("M2", "預算：採購清單總共 %d 元，你記下的預算 %d 元（新台幣）" % (sum(known), amount))
    # M4：幾道菜可以同時做，所以上桌時間不會比最久的那一道短，也不會比四道加起來長
    mins = [x.get("minutes") for x in dishes]
    tm = data.get("total_minutes") if isinstance(data, dict) else None
    if not mins:
        bad("M4", "時間說得通：menu.json 的 dishes 是空的，沒有菜可以算時間")
    elif not all(is_int(v) and v > 0 for v in mins):
        bad("M4", "時間說得通：每道菜的 minutes 都要是大於 0 的整數（分鐘）")
    elif not is_int(tm):
        bad("M4", "時間說得通：menu.json 要有 total_minutes（從開始做到上桌，整數分鐘）")
    elif tm < max(mins):
        bad("M4", "時間說得通：你寫上桌要 %d 分鐘，可是最久的一道就要 %d 分鐘" % (tm, max(mins)))
    elif tm > sum(mins):
        bad("M4", "時間說得通：你寫上桌要 %d 分鐘，比四道一道一道做（%d 分鐘）還久" % (tm, sum(mins)))
    else:
        ok("M4", "時間說得通：最久的一道 %d 分鐘，四道加起來 %d 分鐘，上桌 %d 分鐘" % (max(mins), sum(mins), tm))
    # M3
    cats = sorted(str(x.get("category", "")) for x in dishes)
    if cats == sorted(CATS):
        ok("M3", "飯肉菜湯：各一道")
    else:
        bad("M3", "飯肉菜湯：現在是 %s，要飯、肉、菜、湯各一道" % ("、".join(cats) or "（沒有）"))
    # M5
    seen, shape = {}, []
    for x in dishes:
        ings = x.get("ingredients")
        if not (isinstance(ings, list) and ings and all(isinstance(i, str) and i.strip() for i in ings)):
            shape.append(str(x.get("name", "?")))
            continue
        for i in sorted({i.strip() for i in ings}):   # 同一道菜寫兩次同一個食材，不算兩道菜重複
            seen.setdefault(i, []).append(str(x.get("name", "?")))
    dup = ["「%s」同時出現在 %s" % (i, "、".join(n)) for i, n in seen.items() if len(n) > 1]
    if shape:
        bad("M5", "食材不重複：「%s」的 ingredients 要是食材名稱的字串清單，例如 [\"豬肉\", \"薑\"]" % "、".join(shape))
    elif dup:
        bad("M5", "食材不重複：" + "；".join(dup))
    else:
        ok("M5", "食材不重複：沒有重複")
    # M6
    thin = [str(x.get("name", "?")) for x in dishes
            if not (isinstance(x.get("steps"), list) and len(x["steps"]) >= 2 and all(isinstance(s, str) and s.strip() for s in x["steps"]))]
    if thin:
        bad("M6", "每道菜都有做法：「%s」的 steps 要至少 2 步，而且不能是空的" % "、".join(thin))
    else:
        ok("M6", "每道菜都有做法：每道至少 2 步")
    # M7
    hp = os.path.join(d, "menu.html")
    if not os.path.isfile(hp):
        bad("M7", "menu.html 有菜名和幣別：menu.html 不存在")
    elif text_or_none(hp) is None:
        bad("M7", "menu.html 有菜名和幣別：menu.html 讀不懂，請存成 UTF-8")
    else:
        h = text_or_none(hp)
        h = visible_text(h)   # 只算網頁上看得到的字：註解、程式、樣式、屬性、藏起來的元素裡的字不算
        names = [str(x.get("name", "")).strip() for x in dishes]
        miss = [n for n in names if n and n not in h]
        if not names:
            bad("M7", "menu.html 有菜名和幣別：menu.json 沒有任何一道菜")
        elif not all(names) or len(set(names)) != len(names):
            bad("M7", "menu.html 有菜名和幣別：menu.json 的菜名要四個都有字，而且不能重複")
        elif miss:
            bad("M7", "menu.html 有菜名和幣別：網頁上看不到這些菜名（藏起來的不算）：" + "、".join(miss))
        elif "新台幣" not in h:
            bad("M7", "menu.html 有菜名和幣別：網頁上看得到的字裡沒有「新台幣」，價錢要寫明是新台幣")
        else:
            ok("M7", "menu.html 有菜名和幣別")
    # M8：每個食材都在清單上；每個價錢都寫了依據（來源和日期，或寫明「估計」）
    if not os.path.isfile(sp):
        bad("M8", "採購清單：shopping.md 不存在")
    elif stext is None:
        bad("M8", "採購清單：shopping.md 讀不懂，請存成 UTF-8")
    elif not items:
        bad("M8", "採購清單：讀不到任何一行「- 食材｜買多少｜約幾元｜依據」")
    else:
        need = []
        for x in dishes:
            if isinstance(x.get("ingredients"), list):
                need += [i.strip() for i in x["ingredients"] if isinstance(i, str) and i.strip()]
        lines = "\n".join(nm for (_, nm, _, _) in items)   # 只看每一行的食材欄，不看說明文字
        miss = sorted({i for i in need if i not in lines})
        noprice = ["第 %d 行「%s」" % (no, nm) for (no, nm, p, _) in items if p is None]
        nobasis = ["第 %d 行「%s」" % (no, nm) for (no, nm, p, b) in items
                   if p is not None and p > 0 and not ("估計" in b or (DATE.search(b) and len(DATE.sub("", b).strip(" ，,、()（）")) >= 2))]
        src = sum(1 for (_, _, p, b) in items if p and DATE.search(b) and "估計" not in b)
        est = sum(1 for (_, _, p, b) in items if p and "估計" in b)
        if miss:
            bad("M8", "採購清單：shopping.md 的「- 食材｜…」那幾行，食材欄找不到：" + "、".join(miss))
        elif noprice:
            bad("M8", "採購清單：讀不到價錢（要寫「約幾元」）：" + "、".join(noprice[:5]))
        elif nobasis:
            bad("M8", "採購清單：這些價錢沒有依據（要寫來源和日期，或寫「估計」）：" + "、".join(nobasis[:5]))
        else:
            ok("M8", "採購清單：%d 行；價錢有來源和日期的 %d 個，寫「估計」的 %d 個" % (len(items), src, est))
    return res


def main(argv):
    d = argv[1] if len(argv) > 1 else "runs/a"
    res = evaluate(d)
    n = 0
    for k in sorted(res):
        passed, msg = res[k]
        n += passed
        print("[PASS] %s ✅ %s" % (k, msg) if passed else "[FAIL] %s ❌ %s" % (k, msg))
    total = len(res)
    if n == total:
        print("RESULT: GREEN (%d/%d)" % (n, total))
        return 0
    print("RESULT: RED (%d/%d)" % (n, total))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
