# Windows → Mac 交接（2026-11-18）

> 給 Mac 上的 AI：這份是 Windows 驗收後留下的交接。請先讀完，照「待辦」做；全部做完後刪掉整個 `.handoff/` 資料夾，再 commit、push 到 main。學生 11/23 會 clone main，請在那之前完成。

## 一、統一說法（請沿用，不要改回去）

- Windows 的 Python 指令：**用 `py`，沒有 `py` 就用 `python`，不要打 `python3`**（Windows 上 `python3` 常會跳出 Microsoft Store）。
  - python.org 安裝：有 `py`；`python` 只有勾了「Add to PATH」才有。
  - Microsoft Store 安裝：有 `python`，**沒有 `py`**。
- macOS 照舊寫 `python3`。
- VS Code 在 Windows 的預設終端機是 Windows PowerShell 5.1：**不支援 `&&`／`||`**，指令一行一行貼。

## 二、已完成（這次 commit 的內容）

**腳本（`tools/`、`reference/`）**
- 所有檔案讀寫明確用 UTF-8；`sys.stdout.reconfigure(encoding="utf-8")` 移到 `parse_args()` 之前（cp950 主控台下 `--help` 不再當掉，Git Bash 不再亂碼）。
- 學生的檔案不是 UTF-8（記事本存成 ANSI/Big5）或 JSON 壞掉時：`check.py`、`render.py`、`plan_check.py` 改成亮紅燈並用中文說明，不再噴 traceback。
- 提示訊息裡的指令改用常數 `PY = "py" if sys.platform == "win32" else "python3"`，Windows 顯示 `py tools/...`，Mac 顯示 `python3 tools/...`。
- 閘門標準沒有放寬；CRLF、BOM 原本就不會讓閘門變紅（`gsn.read_text` 已處理），已驗證。

**文件**
- README、CLAUDE.md、prompts.md、spec.md、scripts_spec.md 套用上面的統一說法；README 在 clone 後補 `cd ntut`。
- prompts.md：每段含指令的 prompt 都告訴 AI 在 Windows 怎麼呼叫 Python；修正 S1「只新增一個檔案」與輸出要產生 `data/` 檔案的矛盾。
- scripts_spec.md：要求開檔寫 `encoding="utf-8"`（讀可用 `utf-8-sig`）、寫檔用 `newline="\n"`。
- AGENTS.md、GEMINI.md 改成與 copilot-instructions.md 一樣的一句話。

**簡報（`slides/`）**
- `deck.css` 字型補上微軟正黑體、Consolas、Segoe UI Emoji；`deck.js` 只改了過時的檔頭註解。
- 用無頭 Edge 以 file:// 開過，沒有錯誤；音檔、圖片路徑與大小寫都正確。

## 三、驗收紀錄（Windows 11、Python 3.14、PowerShell、未設 PYTHONUTF8）

兩份乾淨副本各跑一次：筆記檔用 LF 一次、用 CRLF+BOM 一次，結果相同。

```
python tools/check.py                         → RESULT: RED (1/9)
python tools/use_reference.py ; python tools/srt_strip.py ; python tools/fix_terms.py
python tools/check.py --only G0,G1            → RESULT: GREEN (2/2)
python tools/plan_check.py                    → RESULT: GREEN (1/1)
python tools/render.py
python tools/check.py --before-understanding  → RESULT: GREEN (8/8)
（寫 understanding.md，不重產網頁）python tools/check.py → RESULT: RED (8/9)，只有 G7
python tools/render.py ; python tools/check.py → RESULT: GREEN (9/9)
cmd /c "chcp 950 & python tools\check.py"     → RESULT: GREEN (9/9)
Git Bash: python tools/check.py               → RESULT: GREEN (9/9)，emoji 正常
```

## 四、待辦（Windows 這邊做不到，請在 Mac 上處理）

1. **外部網頁的原始 HTML 放進 repo，然後修正**
   - `https://goodedunote.web.app/prepare/session1-lab.html`（實作頁）、`https://goodedunote.web.app/prepare.html`（課前準備）的原始檔不在這個 repo，Windows 這邊改不到。
   - 請把原始檔加進 repo（位置由老師決定，例如 `site_src/`），然後：
     - 實作頁有 30 多處 `python3 …`，目前只有一句「Windows 把 python3 改成 py」。改成統一說法：「Windows：用 `py`（沒有 `py` 就用 `python`）」。
     - 檢查有沒有 `&&`、`export`、`rm -rf`、`cat` 這類 PowerShell 5.1 不能照貼的指令，補上 Windows 寫法。
     - 實作頁上的提示詞要和 `prompts.md` 新版一字一致（新版加了 Windows 怎麼呼叫 Python 的句子，S1 邊界那句也改了）。
     - 課前準備頁的 Python 安裝說明：python.org 安裝時提醒勾選「Add python.exe to PATH」；說明 Store 版沒有 `py`。
   - 改完重新部署 goodedunote.web.app（若部署流程在 Mac 上）。

2. **`slides/session1.html:59` 標籤與內容不符**
   - 標成「逐字稿，完整保留」，但和 `source/transcript.srt` 比，51 段裡有 23 段被改寫或刪掉（例如「這就是我為大家分享的一個功能。」不見了）。這和課程「零省略」的主旨衝突。
   - 請老師決定：改標籤（例如「潤飾版」），或換成完整原文。

3. **shebang 與 `py` 啟動器（需要一台有 `py` 的 Windows 機器驗證）**
   - 腳本第一行是 `#!/usr/bin/env python3`。`py script.py` 會讀 shebang，遇到 `/usr/bin/env` 會去 PATH 找 `python3`，可能找到 Microsoft Store 的空殼。
   - 這台 Windows 沒有 `py`，無法驗證。若有問題，建議把 shebang 改成 `#!/usr/bin/env python`，Mac 上 `python3 tools/check.py` 不受影響。

4. **小問題**
   - `CLAUDE.md`「鐵律」提到 `tests/`，但 repo 沒有這個資料夾：拿掉或改成只寫 `tools/` 的檢查程式。
   - `README.md`「之後老師更新了內容，跑 `git pull` …你自己做出來的檔案不會被動到」：學生改過 `data/corrections.json` 時，如果老師也更新了它，pull 會衝突。建議加一句說明。

5. **收尾**
   - 修改時保留第二節的 Windows 修正：UTF-8 讀寫、`PY` 常數、`py`／`python` 說法。
   - 改到 `tools/` 的話，Mac 上至少跑一次完整流程到 `RESULT: GREEN (9/9)`，乾淨 clone 要是 `RESULT: RED (1/9)`。
   - 刪掉 `.handoff/`，commit、push 到 main。
