# CLAUDE.md — 本專案唯一的規則檔

> For AI agents (Claude Code, Codex CLI, Antigravity CLI (agy), GitHub Copilot): this file is the single source of rules for this project. AGENTS.md, GEMINI.md and .github/copilot-instructions.md only point here. Read this whole file before acting. Propose a plan first and wait for the student to say 「開始」 unless the student's prompt explicitly says to proceed. Reply to the student in Traditional Chinese (zh-TW) with full-width punctuation.

## 三層分開，永遠看得出來

1. **來源原文**：專案裡標明唯讀的來源檔（位置見下面的專案說明）。任何人、任何代理都不准修改。
2. **AI 補述**：AI 加上去的解釋、外部查證，只能寫進指定的位置（見下面的專案說明），不能混進原文。
3. **自己的理解**：學生親手寫的內容（例如 `understanding.md`），AI 不代寫。

## 鐵律

- 確定性的工作交給 `tools/` 裡的腳本；只有需要判斷的步驟由 AI 做。
- AI 可以寫哪些檔案，以下面專案說明裡的「檔案地圖」為準；地圖沒列的不寫、不改。網頁一律由腳本產生。
- 每一個內容單位都要能追回來源。
- 不准為了讓檢查變綠而修改檢查本身（`tools/` 裡的檢查程式；專案裡有 `tests/` 的話也一樣）。如果你認為檢查錯了，寫一段 `GATE DISPUTE` 說明，交給學生決定。
- 回報結果時附上你實際跑過的指令與完整輸出；不要只說「我檢查過了」。

## 停止條件

- 缺少必要資料 → 停下來，寫清楚缺什麼，不要自己補寫或編造。
- 同一個工具連續兩次執行失敗 → 停下來，留下錯誤訊息。
- 修正最多三輪；三輪後仍未全綠 → 停下來，把卡住的地方交還給學生。
- 學生隨時可以說「停」。


---

# 第二堂專案：目標文件進去，一桌菜出來

本專案做一件事：學生貼上一份「目標文件」（`goals/` 裡也有同樣的檔案），你照文件做出一桌四道菜的午餐，交三個檔案。做得對不對，由關卡判斷，不是你：你自己執行 `tools/round.py`，它會跑守衛和關卡 `tools/check.py`，並把結果記下來。

> **目標文件寫了「請直接開始，做到完」，就不用先提計畫，也不用等學生說「開始」，也不要停下來問。** 這一條蓋過上面「先提計畫」那一條。
> **目標文件寫的輪數，蓋過上面「修正最多三輪」。** 文件寫最多幾輪，就最多幾輪。關卡紅燈是正常的結果，不是「工具執行失敗」。

> **指令寫法**：文件裡的 `python3 …` 是 macOS 的寫法。「指令照抄」只有這一個例外：Windows 請改用 `py …`；找不到 `py` 就用 `python …`；不要用 `python3`（Windows 上常會打開 Microsoft Store）。PowerShell 5.1 不支援 `&&`，指令要一行一行執行。

## 你可以執行的程式

`tools/round.py`（跑一輪關卡）、`tools/ask.py`（叫另一個 AI 做一件事）、`tools/compare.py`（印比較表），以及你自己寫在 `mytools/` 的小程式（目標文件的【工具】說什麼時候該做）。**不要打開、讀、修改 `tools/` 裡的任何檔案**，也不要執行別的程式。不要用 python3 -c 執行一小段程式；要算的事寫成 `mytools/` 裡的檔案。不要用提問的工具問我：要我確認的事，寫進 log.md 的「變更提案」。

執行 mytools/ 裡的程式，只寫 python3 mytools/檔名.py 加資料夾這一種寫法：前面不加 -I 或別的旗標，也不要用 ; 或 && 和別的指令接在一起。（Windows 一樣把 python3 換成 py。）

## 檔案地圖

| 路徑 | 是什麼 | 誰可以改 |
|---|---|---|
| `spec.md` | 規格：要交什麼、menu.json 的格式、八條規則的名字 | 沒有人 |
| `taste.md` | 品味五條（吃的人會不會滿意） | 只有學生，而且要在開始跑之前 |
| `goals/` | 目標文件，和學生自己寫的 `my_goal.md` | 只有學生 |
| `cards/`、`.claude/agents/`、`.codex/agents/`、`.agents/agents/`、`team.json` | 交給幫手（subagent 或別家）的任務卡與角色檔 | 沒有人 |
| `inputs/` | 第三關的材料（一份英文食譜、一張冰箱圖）；第一、二關不要讀 | 沒有人（唯讀） |
| `mytools/` | 你自己做的小程式（例如加總價錢），每一輪重跑 | 做事的 AI 寫 |
| `tools/` | 關卡、守衛、呼叫別家的程式、重播的紀錄 | **沒有人** |
| `runs/<名字>/shopping.md`、`menu.json`、`menu.html` | 採購清單、菜單、網頁 | 做菜的 AI 寫 |
| `runs/<名字>/log.md` | 每一輪的紀錄（格式在目標文件裡） | 主對話的 AI 寫，要照實寫 |
| `runs/<名字>/plan.md`、`fridge.md`、`recipe_zh.md` | 第三關：任務佈局、看圖的結果、翻譯的結果 | 主對話寫佈局；看圖、翻譯由別家寫 |
| `runs/<名字>/gate.jsonl`、`round<N>/`、`calls.jsonl` | 關卡和呼叫別家時，程式自己寫的紀錄與每輪備份 | 只有 `tools/round.py`、`tools/ask.py` |
| `runs/<名字>/fix.md` | 第二關：主廚交給幫手的「照這幾行改」（`tools/ask.py --feedback`） | 主對話寫 |
| `runs/<名字>/review_r<N>.md` | 驗收的回答，原樣存下來 | 驗收；主對話不能改它的分數 |
| `eval.md` | 比較表與學生自己的結論 | 表由 `tools/compare.py` 填；其他幾行**只有學生本人寫**，AI 不代寫 |

## 第二堂的規則

1. 只寫目標文件指定的檔案，寫在指定的資料夾裡（和 `mytools/`）。不要刪除任何檔案。`tools/round.py` 和 `tools/ask.py` 會自己在 `runs/<名字>/` 記紀錄（`gate.jsonl`、`round<N>/`、`calls.jsonl`），這是正常的，不算你寫的檔案。
2. 關卡沒有藏起來的數字：預算是你從使用者的話讀出來、記在 `menu.json` 的那一個。關卡沒過時，會印出「哪一項、現在多少、要多少」，照那幾行修。
3. 先寫 `shopping.md`，再寫 `menu.json`，最後寫 `menu.html`。
4. 不要為了讓關卡變綠，把一桌菜變得不像一頓飯。
5. 紀錄要照實：關卡跑了幾次、結果是什麼，以 `tools/round.py` 印出來的為準。學生會用 `python3 tools/guard.py audit` 對帳。

## 同一個資料夾裡的第一堂（只有用 git pull 拿到的 `ntut` 才有）

這個資料夾也是第一堂的專案，第一堂已經上完。第一堂留下來的東西（`source/`、`data/`、`reference/`、`slides/`、`notes/`、`site/`，最上層的 `plan.md`、`loop_log.md`、`understanding.md`，`prompts.md`、`scripts_spec.md`，和 `tools/` 裡的 `render.py`、`plan_check.py`、`gsn.py`、`use_reference.py`）第二堂用不到：不要讀、不要改、不要刪。
第一堂和第二堂同名、會衝突的檔案（`CLAUDE.md`、`README.md`、`spec.md`、`tools/check.py`），第一堂的原版放在 `lesson1_backup/`，路徑和原來一樣。第二堂照這一份 `CLAUDE.md`，不要讀 `lesson1_backup/`。
學生想複習第一堂，會貼一段寫了 `tools/switch_lesson.py` 的文字：只有這個時候，照那段文字執行它寫的那一行。換檔案是那支程式的事，你不要自己複製、移動或刪除檔案。用壓縮檔拿到的資料夾沒有 `lesson1_backup/`，也沒有這支程式，不用找。
