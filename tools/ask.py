#!/usr/bin/env python3
"""叫另一個 AI（或另一家）只做一件事，不開對話（headless）。目標文件裡由主對話的 AI 執行，不是你。
用法（Windows 把 python3 換成 py）：
  python3 tools/ask.py --tool claude|codex|agy|copilot --card cards/see.md [--image inputs/fridge.png] --name c [--round 1]
  python3 tools/ask.py --tool claude --role shopper|recipe|inspector --name b --say "一句話" [--round 1] [--feedback runs/b/fix.md]
  --feedback：把那個檔案的內容（沒過的那幾行、要改的地方）接在任務卡後面一起交過去（--card 也可以用）。
  --role shopper 或 recipe：runs/<名字>/log.md 第一行是「第五條品味：…」時，也一起交過去。
最後一行：ASK: OK <檔案>，或 ASK: NO FILE / TIMEOUT / TOOL NOT FOUND。只有 OK 的結束碼是 0。
每叫一次，就在 runs/<名字>/calls.jsonl 記一行（哪一家、做什麼、哪個模型、幾秒、結果）。"""
import argparse
import json
import os
import re
import sys
import time
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agents  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(HERE)
# 卡 -> 做完應該出現的檔案。REVIEW 是唯讀的卡：回答的文字由這支程式原樣存成 review_r<N>.md。
CARDS = {"hello.md": "hello.txt", "see.md": "fridge.md", "translate.md": "recipe_zh.md", "design.md": "menu.html",
         "review.md": "REVIEW", "b_inspector.md": "REVIEW", "b_shopper.md": "shopping.md", "b_recipe.md": "menu.json"}
SCORE = re.compile(r"(?:品味|驗收|總分)[^\n0-9]*?(\d+)\s*/\s*10")
ANY10 = re.compile(r"(\d+)\s*/\s*10")


def read_score(text, review=False):
    """「品味：8/10」的 8（也讀「總分：8/10」、全形的「８／１０」）。review=True（驗收的回答）時，什麼標籤都沒有，就取前三行裡第一個 N/10。"""
    t = unicodedata.normalize("NFKC", text or "")
    m = SCORE.search(t)
    if not m and review:
        m = ANY10.search("\n".join(t.splitlines()[:3]))
    return m.group(1) if m else None


def has_score(text):
    return read_score(text, True) is not None


ROLE_CARD = {"shopper": "cards/b_shopper.md", "recipe": "cards/b_recipe.md", "inspector": "cards/b_inspector.md"}


def log_call(folder, rec):
    try:
        with open(os.path.join(folder, "calls.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True, choices=list(agents.TOOLS))
    ap.add_argument("--card", default="")
    ap.add_argument("--role", default="", choices=["", "shopper", "recipe", "inspector"])
    ap.add_argument("--say", default="")
    ap.add_argument("--image", default="")
    ap.add_argument("--name", default="")
    ap.add_argument("--model", default="")
    ap.add_argument("--round", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=100)
    ap.add_argument("--feedback", default="")
    a = ap.parse_args()
    os.chdir(ROOT)
    card = (a.card or ROLE_CARD.get(a.role, "")).replace("\\", "/")
    base = os.path.basename(card)
    name = a.name or ("hello" if base == "hello.md" else "ask")
    folder = "runs/" + name
    if not card or not os.path.isfile(card):
        print("找不到任務卡 %s。請確認你在解壓縮出來的資料夾裡（看得到 tools 和 cards）。" % (card or "（沒有指定 --card 或 --role）"))
        print("ASK: NO FILE（沒有任務卡）")
        return 2
    out_file = CARDS.get(base)
    review = out_file == "REVIEW"
    os.makedirs(folder, exist_ok=True)
    target = os.path.join(folder, ("review_r%d.md" % a.round) if review else out_file) if out_file else None
    rel = target.replace(os.sep, "/") if target else ""
    what = a.role or base
    if not agents.find(a.tool):
        print("這台電腦找不到 %s。" % agents.NAME_ZH[a.tool])
        print("ASK: TOOL NOT FOUND %s" % a.tool)
        log_call(folder, {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": a.tool, "what": what, "model": "", "seconds": 0, "result": "TOOL NOT FOUND"})
        return 2
    if not a.image and base == "see.md":
        a.image = "inputs/fridge.png"   # 看圖的卡，沒指定圖就用起始包裡的冰箱圖
    if a.image and not os.path.isfile(a.image):
        print("找不到圖檔 %s。請在解壓縮出來的資料夾裡跑，並確認 inputs 裡有這張圖。" % a.image)
        print("ASK: NO FILE（沒有圖檔）")
        return 2
    with open(card, encoding="utf-8-sig") as f:
        text = f.read().replace("{資料夾}", folder).replace("{圖檔}", a.image or "inputs/fridge.png").replace("{一句話}", a.say)
    if a.say and "{一句話}" not in open(card, encoding="utf-8-sig").read():   # 角色卡沒有空格放那句話：接在後面，連同資料夾
        text = text.rstrip() + "\n\n資料夾：%s\n使用者說的話：%s\n" % (folder, a.say)
    if a.role in ("shopper", "recipe"):   # 第五條品味：主廚寫在 log.md 的第一行，這裡一起交過去
        try:
            with open(os.path.join(folder, "log.md"), encoding="utf-8-sig") as f:
                first = f.readline().strip()
            if first.startswith("第五條品味"):
                text = text.rstrip() + "\n\n" + first + "\n"
        except (OSError, UnicodeDecodeError):
            pass
    if a.feedback:
        try:
            with open(a.feedback, encoding="utf-8-sig") as f:
                fb = f.read().strip()
        except (OSError, UnicodeDecodeError):
            print("找不到或讀不懂 --feedback 的檔案 %s。" % a.feedback)
            print("ASK: NO FILE（沒有 --feedback 的檔案）")
            return 2
        text = text.rstrip() + "\n\n主廚要你照下面這幾行改（上一輪沒過的地方）：\n" + fb + "\n"
    model, effort = a.model, ""
    if a.role and not a.model:
        try:
            with open("team.json", encoding="utf-8-sig") as f:
                t = json.load(f).get(a.tool, {}).get(a.role, {})
            model, effort = t.get("model", ""), t.get("effort", "")
        except (OSError, ValueError):
            pass
    elif not a.model:
        d = agents.SOLO_DEFAULT[a.tool]
        model, effort = d["model"], d["effort"]
    print("工具：%s　模型：%s　任務卡：%s" % (agents.NAME_ZH[a.tool], model or "帳號預設", card))
    print("（AI 正在做，通常 10 到 90 秒）", flush=True)
    result, res = "NO FILE", None
    for attempt in (1, 2):
        t0 = time.time()
        res = agents.call(a.tool, text, cwd=ROOT, write=not review, model=model, effort=effort, image=a.image, timeout=a.timeout,
                          tick=lambda n: print("　（已等 %d 秒）" % n, flush=True), notify=lambda s: print("　" + s, flush=True))
        print("用了 %d 秒　花費 %s" % (round(res["seconds"]), agents.fmt_cost(res["cost"])), flush=True)
        if res["timeout"]:
            print("超過 %d 秒沒有做完。" % a.timeout)
            result = "TIMEOUT"
            break
        if res["rc"] != 0:
            tail = (res["err"] or res["out"]).strip().splitlines()[-3:]
            print("工具結束碼 %s。最後幾行：" % res["rc"])
            for line in tail:
                print("　" + line[:200])
        if review and res["rc"] == 0 and (res["text"] or "").strip():
            if has_score(res["text"]):
                with open(target, "w", encoding="utf-8", newline="\n") as f:
                    f.write(res["text"].strip() + "\n")
            else:
                print("它回答了，但讀不到「品味：幾分/10」那一行，不算驗收。")
        fresh = bool(target) and os.path.isfile(target) and os.path.getmtime(target) >= t0 - 2 and os.path.getsize(target) > 0
        if res["rc"] == 0 and (not target or fresh):
            result = "OK"
            break
        said = [l for l in (res["text"] or "").strip().splitlines() if l.strip()][-3:]
        if said:
            print("AI 最後說的話：")
            for line in said:
                print("　" + line[:200])
        if attempt == 1:
            print("第一次沒有成功（%s 沒有寫出來，或工具結束碼不是 0），再試一次。" % rel, flush=True)
    if result == "OK" and base == "hello.md":
        with open(target, encoding="utf-8-sig") as f:
            if "今天午餐吃蛋炒飯" not in f.read():
                print("檔案有了，但裡面不是要求的那一句。")
                result = "NO FILE"
    log_call(folder, {"t": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": a.tool, "what": what, "model": model or "帳號預設",
                      "seconds": round(res["seconds"]), "result": result, "models_seen": res.get("models") or []})
    if result == "OK":
        print("ASK: OK %s" % (rel or "（沒有指定要檢查的檔案）"))
        return 0
    if result == "TIMEOUT":
        print("ASK: TIMEOUT %s" % rel)
    else:
        print("沒有成功：%s 沒有寫出來，或工具結束碼不是 0。" % rel)
        print("ASK: NO FILE %s" % rel)
    return 1


if __name__ == "__main__":
    sys.exit(main())
