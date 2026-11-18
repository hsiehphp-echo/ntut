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
- 不准為了讓檢查變綠而修改檢查本身（`tools/` 裡的檢查程式、`tests/`）。如果你認為檢查錯了，寫一段 `GATE DISPUTE` 說明，交給學生決定。
- 回報結果時附上你實際跑過的指令與完整輸出；不要只說「我檢查過了」。

## 停止條件

- 缺少必要資料 → 停下來，寫清楚缺什麼，不要自己補寫或編造。
- 同一個工具連續兩次執行失敗 → 停下來，留下錯誤訊息。
- 修正最多三輪；三輪後仍未全綠 → 停下來，把卡住的地方交還給學生。
- 學生隨時可以說「停」。



---

# 第一堂專案：把一段字幕做成好學生筆記

本專案把一場三分鐘閃講的字幕檔（`source/transcript.srt`）照好學生筆記的切分做成一份筆記：拿掉時間軸、校正專有名詞、把字幕變回一篇文章、加上名詞補充與立場筆記（用學生指定的身份寫視角），最後由學生親手寫下理解。目標不是做得快，而是每一步交給下一步的時候，講者的話一句都沒有少。

## 檔案地圖

| 路徑 | 是什麼 | 誰可以改 |
|---|---|---|
| `source/transcript.srt` | 來源：帶時間軸的字幕檔（51 段，有聽錯的專有名詞） | 沒有人（唯讀） |
| `data/corrections.json` | 校正用語清單（聽錯的詞 → 對的詞） | 只有學生本人確認後才加；AI 可以提議，不可以自己加 |
| `scripts_spec.md` | 兩支腳本的規格（輸入、輸出格式、規則） | 沒有人 |
| `tools/srt_strip.py`、`tools/fix_terms.py` | S1 由 AI 照 `scripts_spec.md` 寫出來的兩支腳本（一開始不存在） | AI 寫，學生用 G1 驗收 |
| `reference/` | 講師寫好的同兩支腳本，是備援 | 沒有人；**AI 不可以打開、不可以讀、不可以照抄**，除非學生明確說「用備援」 |
| `data/cues.json`、`data/raw.txt` | 拿掉時間軸之後的字幕文字，由 `tools/srt_strip.py` 產生 | 只能由腳本重產生 |
| `data/cues_fixed.json`、`data/fixed.txt` | 套用校正用語之後的字幕文字，由 `tools/fix_terms.py` 產生 | 只能由腳本重產生 |
| `notes/cleaned.md` | 把字幕變回的一篇文章（只有講者的話） | AI 寫，人審 |
| `notes/notes.md` | 全文加上補述區塊（📖 名詞補充、🎯 身份視角） | AI 寫，人審 |
| `plan.md` | 步驟計畫（每步四欄：輸入／工具／輸出／檢查） | AI 寫，人確認 |
| `understanding.md` | 我的理解 | 只有學生本人（AI 絕不可寫、不可改、不可補） |
| `loop_log.md` | 修正迴圈紀錄（最多三輪） | 人與 AI |
| `site/index.html` | 網頁，由 `tools/render.py` 產生 | 只能由腳本產生 |
| `tools/` 其他檔案 | render.py、check.py、plan_check.py、gsn.py、use_reference.py | 沒有人（不要為了變綠改它） |
| `spec.md` | 筆記必須包含什麼、每一步的規則 | 沒有人 |

## 第一堂的規則

0. AI 只寫這些檔案：筆記檔（`notes/` 裡的 Markdown）、`plan.md`、`loop_log.md`，以及 S1 指定的兩支腳本（`tools/srt_strip.py`、`tools/fix_terms.py`，規格在 `scripts_spec.md`）。其他工具不寫、不改；網頁一律由 `tools/render.py` 產生。
1. **零省略**：`notes/cleaned.md` 要保留字幕裡講者說的每一句話。不摘要、不濃縮、不改寫、不改成第三人稱（不要寫「講者提到……」）。
2. 寫 `notes/cleaned.md` 時，只讀 `data/cues_fixed.json`（或 `data/fixed.txt`），不要讀 `source/transcript.srt`。時間軸是腳本管的，你不需要看到它。
3. 寫 `notes/cleaned.md` 可以做的只有：補全形標點、在句子之間補接續詞與承接、合併成段落並依語意分段、在段落之間加 `## ` 小標題、去掉只當發語詞的贅字。
4. 看到你覺得是聽錯的專有名詞，不要自己改。列出來告訴學生，由學生決定要不要加進 `data/corrections.json`，再由 `tools/fix_terms.py` 替換。
5. `notes/notes.md` 的正文必須和 `notes/cleaned.md` 一字不差。你加的話只能放在以 `>` 開頭的補述區塊裡，區塊上下各空一行。
6. 補述區塊只有兩種：`> 📖 **名詞補充：術語**` 與 `> 🎯 **某某視角**`。格式照 `spec.md`。
7. 身份視角的「某某」由學生指定。學生沒說，就先問，不要自己挑一個。整份筆記用同一個身份。
8. 名詞補充只寫你確定的內容。不確定的術語寫「這個詞我不確定，請你查證」，不要編。
9. 不要替講者下結論。看不出來的就留給學生寫進「我還不懂」。
10. 不要手改 `site/`，改完檔案後跑 `python3 tools/render.py`。Windows 的學生請把 `python3` 換成 `py`。
11. **`understanding.md` 只有學生本人親手寫。AI 絕不可以建立、撰寫、修改或補充它，也不可以想辦法讓 G8 變綠**（包括產生草稿、範本、換個檔名、改 `check.py`）。G8 紅燈不是你的工作：回報「G8 要等學生自己寫」就好。
12. `data/cues.json`、`data/cues_fixed.json` 只能由腳本產生；G1 會用講師的版本重做一次、一段一段比對，手改一個字就會紅燈。G1 紅燈時修腳本，不要手改 `data/`。
13. 寫 `tools/srt_strip.py`、`tools/fix_terms.py` 時：只照 `scripts_spec.md` 寫，只用 Python 標準函式庫，不要打開 `reference/`。最多修三次；三次後 G1 仍紅就停下來，告訴學生可以執行 `python3 tools/use_reference.py` 用備援往下做。不要自己去執行它。

## 閘門與指令

- 先跑 G0–G7：`python3 tools/check.py --before-understanding`（只跑 G0 到 G7，不含 G8）。這是你和學生一起把紅燈修到全綠的階段，全綠後只代表「G0–G7 共八道閘門過了」，還不算完成。
- 全部閘門：`python3 tools/check.py`（G0 到 G8 全綠、exit code 0 才算完成）。完整檢查只在學生親手寫完 `understanding.md` 之後才有意義。
- 只跑部分：`python3 tools/check.py --only G0,G1`。
- G0 字幕檔沒被改、G1 字幕文字是腳本做的、G2 字數落在 95% 到 105%、G3 每一段字幕都還在、G4 沒有摘要句、G5 補述沒有動到全文、G6 補述都有標記、G7 網頁與檔案同步、G8 understanding.md（學生寫）。
- 計畫檢查：`python3 tools/plan_check.py`。

## 順序（S4 的收尾）

1. 你（AI）修 `notes/` 裡的檔案，直到 `python3 tools/check.py --before-understanding` 是 GREEN（8/8），最多三輪，每一輪記在 `loop_log.md`。修的時候對照 `data/fixed.txt` 把原話補回來，不要為了過關去改字幕文字、校正用語或檢查程式。改了 `notes/cleaned.md` 的正文，`notes/notes.md` 的正文要跟著一樣。每一輪修完先跑 `python3 tools/render.py` 再檢查。
2. 停下來，告訴學生：換你了，請自己把筆記讀一遍，親手寫 `understanding.md`（至少 150 字、有一行以「我還不懂：」開頭）。你不寫、不改、不給草稿。
3. 學生寫完 `understanding.md` 之後，先跑 `python3 tools/render.py`（網頁會多出「我的理解」；不重新產生，G7 會因為不同步而紅燈），再跑完整的 `python3 tools/check.py`，G0 到 G8 全綠（GREEN 9/9）才算完成。如果只剩 G8 紅燈，那是學生的作業，不要試圖修。
- 回報時貼出你實際跑的指令與完整輸出。
