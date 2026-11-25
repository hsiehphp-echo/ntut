"""呼叫學生自己的 AI 命令列工具（headless，一次一個任務）。
給 ask.py 用（主對話的 AI 執行 ask.py，去叫另一個模型或另一家）。重點：
- 不用 shell，不用 bash；命令用「參數清單」，提示一律從標準輸入送進去（中文和引號在 Windows 命令列上很容易壞）。
- 結束碼 0 不代表做完：呼叫的人要自己檢查檔案。
- 每一次呼叫都有時間上限。"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TOOLS = ("claude", "codex", "agy", "copilot")
NAME_ZH = {"claude": "Claude Code", "codex": "Codex CLI", "agy": "Antigravity CLI (agy)", "copilot": "GitHub Copilot CLI", "replay": "重播"}
# 單一迴圈（動手 A、C）的預設：最便宜的選擇。空的就用你帳號預設的模型。
SOLO_DEFAULT = {
    "claude": {"model": "haiku", "effort": ""},
    "codex": {"model": "gpt-6.1-terra", "effort": "low"},
    "agy": {"model": "", "effort": ""},
    "copilot": {"model": "", "effort": ""},
}
MODEL_REFUSED = re.compile(r"model_not_found|is not available|not available;|unrecognized_model|not supported when using|requested model is not supported|unknown model|invalid model", re.I)


def find(tool):
    """用 shutil.which 找可執行檔（Windows 會自動試 .exe、.cmd）。找不到回傳 None。"""
    return shutil.which(tool)


def build_argv(tool, exe, write=True, model="", effort="", image="", timeout=180, usage_file="", chef=False):
    if tool == "claude":
        # stream-json：一行一個事件。中途被中斷，也還留得下它已經用了哪些模型、多少 tokens。
        a = [exe, "-p", "--output-format", "stream-json", "--verbose", "--max-budget-usd", "2" if chef else "1"]
        if model:
            a += ["--model", model]
        if effort:
            a += ["--effort", effort]
        if write:
            a += ["--permission-mode", "acceptEdits"]
            a += ["--allowedTools", "Read,Write,Edit,Agent" if chef else "Read,Write,Edit"]
        else:
            a += ["--allowedTools", "Read"]
        return a
    if tool == "codex":
        a = [exe, "exec", "--skip-git-repo-check", "--ephemeral"]
        if image:
            a += ["-i", image]
        if model:
            a += ["-m", model]
        if effort:
            a += ["-c", "model_reasoning_effort=" + effort]
        a += ["-s", "workspace-write" if write else "read-only", "-"]
        return a
    if tool == "agy":
        a = [exe, "--input-format", "text", "--output-format", "json", "--print-timeout", "%ds" % int(timeout)]
        if model:
            a += ["--model", model]
        return a
    if tool == "copilot":
        a = [exe, "-s", "--no-ask-user"]
        if write:
            a += ["--allow-tool", "write"]
        if usage_file:
            a += ["--usage-output-file", usage_file]
        if image:
            a += ["--attachment", image]
        return a
    raise ValueError("不認識的工具：%s" % tool)


def _usage(tool, out, err, usage_file, partial=None):
    """回傳 (cost dict 或 None, 實際用到的模型清單, 文字)。讀不到就回 None，不猜。
    partial：被中斷的呼叫，看得到多少就記多少（例如 tokens）。"""
    cost, models, text = None, [], out
    partial = {} if partial is None else partial
    try:
        if tool == "claude":
            final, seen, toks, said = None, set(), 0, []
            for line in out.splitlines():
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    j = json.loads(line)
                except ValueError:
                    continue
                if j.get("type") == "result":
                    final = j
                elif j.get("type") == "assistant" and isinstance(j.get("message"), dict):
                    m = j["message"]
                    if m.get("model"):
                        seen.add(m["model"])
                    u = m.get("usage") or {}
                    toks += sum(v for k, v in u.items() if k.endswith("_tokens") and isinstance(v, int))
                    for c in m.get("content") or []:
                        if isinstance(c, dict) and c.get("type") == "text" and not j.get("parent_tool_use_id"):
                            said.append(c.get("text", ""))
            if final is not None:
                if isinstance(final.get("total_cost_usd"), (int, float)):
                    cost = {"unit": "usd", "value": round(float(final["total_cost_usd"]), 4)}
                models = sorted((final.get("modelUsage") or {}).keys()) or sorted(seen)
                text = final.get("result", "") if isinstance(final.get("result"), str) else "\n".join(said)
            else:   # 被中斷：沒有帳單那一行，只留得下模型和 tokens（不換算成美元，不猜）
                models = sorted(seen)
                text = "\n".join(said)
                if toks:
                    partial["tokens"] = toks
        elif tool == "agy":
            j = json.loads(out)
            if isinstance(j.get("response"), str):
                text = j["response"]
            u = j.get("usage") or {}
            if isinstance(u.get("total_tokens"), int):
                cost = {"unit": "tokens", "value": u["total_tokens"]}
        elif tool == "codex":
            m = re.search(r"tokens used\s*[:\n]?\s*([\d,]+)", err + "\n" + out)
            if m:
                cost = {"unit": "tokens", "value": int(m.group(1).replace(",", ""))}
            m = re.search(r"^model:\s*(\S+)", err + "\n" + out, re.M)
            if m:
                models = [m.group(1)]
        elif tool == "copilot" and usage_file and os.path.isfile(usage_file):
            with open(usage_file, encoding="utf-8-sig") as f:
                j = json.load(f)
            if isinstance(j.get("totalNanoAiu"), (int, float)):
                cost = {"unit": "ai_credits", "value": round(j["totalNanoAiu"] / 1e9, 3)}
            ms = j.get("models") or j.get("perModel") or {}
            if isinstance(ms, dict):
                models = sorted(ms.keys())
    except Exception:
        pass
    return cost, models, text


def _kill_tree(p):
    """逾時時把整串程式都結束。Windows 上 .cmd 外殼底下還有 node，只殺外殼的話，管線會一直開著。"""
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True, timeout=15)
        else:
            p.kill()
    except Exception:
        try:
            p.kill()
        except Exception:
            pass


def _run_once(argv, prompt, cwd, timeout):
    t0 = time.time()

    def s(x):
        return x.decode("utf-8", "replace") if isinstance(x, bytes) else (x or "")
    try:
        kw = {}
        if os.name == "nt":
            kw["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             encoding="utf-8", errors="replace", cwd=cwd, **kw)
    except OSError as e:
        return {"rc": -2, "out": "", "err": "無法啟動：%s" % e, "timeout": False, "seconds": time.time() - t0}
    try:
        out, err = p.communicate(prompt, timeout=timeout)
        return {"rc": p.returncode, "out": out or "", "err": err or "", "timeout": False, "seconds": time.time() - t0}
    except subprocess.TimeoutExpired as e:
        out, err = s(e.stdout), s(e.stderr)
        _kill_tree(p)
        try:
            o2, e2 = p.communicate(timeout=10)
            out, err = o2 or out, e2 or err
        except Exception:
            pass
        return {"rc": -1, "out": out, "err": err, "timeout": True, "seconds": time.time() - t0}


CODEX_NOTE = ("（給 Codex：讀檔和寫檔請用你平常的方式，包含用 cat 讀 CLAUDE.md、用 apply_patch 寫檔，這些不算執行程式。"
              "卡上的「不要執行任何程式」是指不要執行 tools/ 裡的程式，也不要自己寫程式來跑。不要停下來問，直接做完。）\n\n")


def call(tool, prompt, cwd=".", write=True, model="", effort="", image="", timeout=180, usage_file="",
         chef=False, tick=None, notify=None):
    """呼叫一次。回傳 dict：rc, out, err, timeout, seconds, cost, models, text, fell_back, argv。
    tick(秒數)：等待時每 10 秒被叫一次，讓畫面有動靜。notify(文字)：要告訴學生的訊息。"""
    exe = find(tool)
    if not exe:
        return {"rc": -3, "out": "", "err": "找不到 %s" % tool, "timeout": False, "seconds": 0.0, "cost": None,
                "models": [], "text": "", "fell_back": False, "argv": [], "missing": True}
    if tool == "codex":
        prompt = CODEX_NOTE + prompt
    if tool == "agy" and image:
        prompt = prompt.rstrip("\n") + "\n@" + image + "\n"
    img_arg = image if tool in ("codex", "copilot") else ""
    result = {}

    def work(m, e):
        argv = build_argv(tool, exe, write, m, e, img_arg, timeout, usage_file, chef)
        result["argv"] = argv
        result["r"] = _run_once(argv, prompt, cwd, timeout + 15 if tool == "agy" else timeout)

    def run_with_heartbeat(m, e):
        th = threading.Thread(target=work, args=(m, e), daemon=True)
        th.start()
        waited = 0
        while th.is_alive():
            th.join(10)
            waited += 10
            if th.is_alive() and tick:
                tick(waited)
        return result["r"]

    fell = False
    r = run_with_heartbeat(model, effort)
    if r["rc"] not in (0, -1) and model and MODEL_REFUSED.search(r["out"] + "\n" + r["err"]):
        if notify:
            notify("這個帳號不能用 %s，改用帳號預設的模型再試一次" % model)
        fell = True
        r = run_with_heartbeat("", effort if tool == "codex" else "")
    partial = {}
    cost, models, text = _usage(tool, r["out"], r["err"], usage_file, partial)
    r.update({"cost": cost, "models": models, "text": text, "fell_back": fell, "argv": result.get("argv", []),
              "partial_tokens": partial.get("tokens")})
    return r


def fmt_cost(c):
    if not c:
        return "讀不到花費"
    if c["unit"] == "usd":
        return "%.3f 美元" % c["value"]
    if c["unit"] == "tokens":
        return "{:,} tokens".format(c["value"])
    if c["unit"] == "ai_credits":
        return "%.3f AI credits" % c["value"]
    return str(c)


def add_cost(total, c):
    if not c:
        return total
    if total is None:
        return dict(c)
    if total["unit"] == c["unit"]:
        total = {"unit": total["unit"], "value": round(total["value"] + c["value"], 4)}
    return total
