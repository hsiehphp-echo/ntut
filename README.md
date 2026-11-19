# NTUT 工作坊｜第一堂：把一段字幕做成好學生筆記

臺北科技大學 AI Agent 實作工作坊第一堂（2026-11-23）的專案。

今天只學一件事：**把一個大任務拆成一步一步**，每一步都寫得出四件事：讀什麼、誰來做、做出什麼、怎麼檢查。材料是一場三分鐘閃講的字幕檔。做出來的東西，是一份沒有少掉任何一句話、讀得進去的好學生筆記，加上你自己寫的理解。

- 上課簡報：<https://goodedunote.web.app/prepare/session1.html>（這個專案的 `slides/` 裡也有一份）
- 實作頁（每一步的指令與提示詞都可以複製）：<https://goodedunote.web.app/prepare/session1-lab.html>
- 課前準備（安裝 Python、Git、AI 工具）：<https://goodedunote.web.app/prepare.html>

## 怎麼開始

1. 把專案複製到你的電腦（clone）。在終端機進到你想放的資料夾，例如桌面的 `ntut-workshop`，然後執行下面兩行（第一行會多出一個 `ntut` 資料夾，第二行進到裡面）：

   ```
   git clone https://github.com/shuotao/ntut.git
   cd ntut
   ```

2. 用 VS Code 打開 `ntut` 資料夾（檔案 → 開啟資料夾），再開一個終端機（終端機 → 新增終端機）。Windows 的終端機預設是 PowerShell：指令一行一行貼、一行一行跑，不要用 `&&` 把兩個指令串在一起。
3. 看一次紅燈。現在什麼都還沒做，所以九道檢查只有一道是綠的，這是正確的起點：

   ```
   py tools/check.py
   ```

   最後一行應該是 `RESULT: RED (1/9)`。如果 Windows 說找不到 `py`，就改成 `python tools/check.py`；不要打 `python3`，在 Windows 上它常會跳出 Microsoft Store。macOS 用 `python3 tools/check.py`。下面所有指令裡的 `python3`，Windows 都照這樣換成 `py`（或 `python`）。

4. 在這個資料夾啟動你的 AI 工具（`claude`、`codex`、`agy` 或 `copilot`），貼上第一句話：

   > 請先讀 CLAUDE.md、README.md 與 spec.md，然後用三句話告訴我：（一）這個專案要產出什麼；（二）哪些檔案絕對不能改；（三）我們接下來的第一步是什麼。先不要動任何檔案。

5. 接下來照[實作頁](https://goodedunote.web.app/prepare/session1-lab.html)的 S1 到 S4 做。所有提示詞也收在這個專案的 [`prompts.md`](prompts.md)。

之後老師更新了內容，在 `ntut` 資料夾裡跑 `git pull` 就會拿到。你自己做出來的檔案不會被動到。唯一的例外：如果你自己在 `data/corrections.json` 加過校正用語，而老師也更新了這個檔案，`git pull` 會說有衝突。這時先把你加的那幾條抄下來，執行 `git checkout data/corrections.json` 還原，再 `git pull`，然後把你的那幾條加回去。

## 現在資料夾裡有什麼

你剛 clone 下來，在 VS Code 左邊看到的就是下面這些，不多也不少（隱藏的 `.git` 不算）。

| 路徑 | 是什麼 | 誰可以改 |
|---|---|---|
| `README.md` | 這份說明 | 沒有人 |
| `CLAUDE.md` | 給 AI 看的班規。這個專案唯一的規則檔 | 沒有人 |
| `AGENTS.md`、`GEMINI.md`、`.github/copilot-instructions.md` | 只有一行，指向 `CLAUDE.md`。不同的 AI 工具會找不同的檔名 | 沒有人 |
| `spec.md` | 筆記的規格：要做出什麼、每一步的規則 | 沒有人 |
| `scripts_spec.md` | 兩支腳本的規格（輸入、輸出格式、規則）：你請 AI 寫腳本時的訂單 | 沒有人 |
| `prompts.md` | 今天用到的每一段提示詞，照順序 | 沒有人 |
| `source/transcript.srt` | 來源：閃講的字幕檔，51 段，有聽錯的專有名詞 | 沒有人（唯讀） |
| `data/corrections.json` | 校正用語清單：聽錯的詞 → 對的詞，25 條。`data/` 裡現在只有這一個檔案 | 你確認之後可以加 |
| `tools/check.py` | 九道閘門 G0 到 G8 | 沒有人 |
| `tools/render.py` | 把現在有的檔案做成一頁網頁 `site/index.html` | 沒有人 |
| `tools/plan_check.py` | 檢查計畫 `plan.md` 的格式 | 沒有人 |
| `tools/gsn.py` | 給 `check.py` 和 `render.py` 用的小函式 | 沒有人 |
| `tools/use_reference.py` | 備援：把老師寫好的腳本拿來用 | 沒有人 |
| `reference/srt_strip.py`、`reference/fix_terms.py` | 老師寫好的兩支腳本。**先不要打開**，見下面「雙軌」 | 沒有人 |
| `slides/` | 第一堂的簡報。用瀏覽器打開 `slides/session1.html` | 沒有人 |
| `LICENSE`、`.gitignore`、`.gitattributes` | 授權與 git 的設定 | 沒有人 |

`tools/` 裡現在**沒有** `srt_strip.py` 和 `fix_terms.py`：那兩支是 S1 要請 AI 寫的。這個資料夾也**還沒有** `notes/`、`site/`，`data/` 裡也還沒有字幕文字。找不到它們不是你弄丟了，下一節說它們什麼時候出現。

## 之後才會出現的檔案，由哪一步做出來

| 檔案 | 什麼時候出現 | 誰做出來的 |
|---|---|---|
| `tools/srt_strip.py` | S1 第一支腳本 | AI 照 `scripts_spec.md` 寫（或 `use_reference.py` 放進來） |
| `data/cues.json`、`data/raw.txt` | 跑完 `tools/srt_strip.py` 之後 | `tools/srt_strip.py`。`cues.json` 給程式讀，`raw.txt` 給你讀，一段一行 |
| `tools/fix_terms.py` | S1 第二支腳本 | AI 照 `scripts_spec.md` 寫（或 `use_reference.py` 放進來） |
| `data/cues_fixed.json`、`data/fixed.txt` | 跑完 `tools/fix_terms.py` 之後 | `tools/fix_terms.py`。格式和 `cues.json`、`raw.txt` 一樣，但已經換成對的專有名詞 |
| `site/index.html` | 第一次跑 `tools/render.py` 之後（S1 做完就可以跑，之後每次檔案有改都要重跑） | `tools/render.py`（`site/` 資料夾也是這時才有） |
| `plan.md` | S2 | AI 寫，你審。`python3 tools/plan_check.py` 檢查格式 |
| `notes/cleaned.md` | S3 第一件事：把字幕變回一篇文章 | AI（`notes/` 資料夾也是這時才有） |
| `notes/notes.md` | S3 第二件事：加上名詞補充與立場筆記 | AI |
| `loop_log.md` | S4 的修正迴圈，每一輪記一行；S1 用了備援也記一行 | AI 或你（沒有工具會自動建立它，沒有就新增一個） |
| `understanding.md` | S4 最後 | **你親手寫**，AI 不代筆 |
| `tools/srt_strip.mine.py`、`tools/fix_terms.mine.py` | 只有你先寫了自己的腳本、後來又用了備援才會有 | `use_reference.py` 把你原本的那一支改名留下 |

`data/cues.json` 和 `data/cues_fixed.json` 的格式（鍵名、每一段的欄位）寫在 [`scripts_spec.md`](scripts_spec.md) 裡。除了 `understanding.md`，這些檔案都是腳本或 AI 做出來的，你不用自己動手建立。

## 今天的五關

| 關 | 做什麼 | 誰做 | 怎麼確認 |
|---|---|---|---|
| S0 開起來 | 把專案 clone 下來，AI 開在這個資料夾，先讀班規 | 你 | `check.py` 是 RED (1/9) |
| S1 請 AI 寫腳本 | 請 AI 寫兩支腳本：拿掉時間軸、校正專有名詞。然後自己讀 51 段字幕 | AI 寫腳本，腳本做事，你驗收 | `check.py --only G0,G1` 是 GREEN (2/2) |
| S2 擬訂計畫 | 請 AI 擬訂計畫，你來審 | AI 擬，你審 | `plan_check.py` 是 GREEN (1/1) |
| S3 把字幕變回文章 | 把字幕變回一篇文章（`notes/cleaned.md`）；再加名詞補充與立場筆記（`notes/notes.md`，用你的身份寫的視角） | AI | `--only G0,G1,G2,G3,G4` 是 GREEN (5/5)；`--only G5,G6` 是 GREEN (2/2) |
| S4 跑檢查，寫下你的理解 | 紅燈修到過（最多三輪），自己讀一遍，親手寫下你的理解 | AI 修，你寫 | `check.py` 是 GREEN (9/9) |

## 雙軌：自己請 AI 寫腳本，或用備援

S1 的兩支腳本一開始不存在。你要用提示詞請 AI 照 [`scripts_spec.md`](scripts_spec.md) 寫出來。

**怎麼把訂單寫清楚。** 只說「幫我寫一支程式把字幕的時間拿掉」，每個人的 AI 會寫出不一樣的東西。訂單要寫六件事：

| 訂單上要寫 | 在問什麼 |
|---|---|
| 輸入 | 讀哪個檔案 |
| 工具 | 可以用什麼 |
| 輸出 | 留下哪個檔案、長什麼樣子 |
| 檢查 | 怎麼知道寫對了 |
| 邊界 | 哪些東西不准碰 |
| 停止 | 做到哪裡停、修幾次算了 |

**怎麼確定大家的腳本都一樣。** 不比程式碼，比結果。每個人的 AI 寫出來的程式碼都不一樣，但閘門 G1 會拿你的腳本做出來的 51 段文字，和同一份標準答案一段一段比。G1 綠燈，代表你的結果和全班完全相同。

**寫了三次還是紅。** 把 G1 的訊息貼回給 AI 修，最多三次。三次還紅，或你用的 AI 寫不出來，就用備援往下走：

```
python3 tools/use_reference.py
```

Windows 請打 `py tools/use_reference.py`。它會把 `reference/` 裡老師的版本放進 `tools/`，你寫的那一支改名成 `*.mine.py` 留著對照。用了備援不是失敗：今天要學的是怎麼把訂單寫清楚、怎麼檢查，不是比誰的 AI 厲害。

## AI 動手前要不要問你：四種啟動方式

AI 要寫檔或跑指令之前，會先問你可不可以。每一家工具都可以在啟動時決定「要問到什麼程度」。上課時老師會說用哪一種。

| 工具 | 直接打指令時 | 改檔不問，指令照問 | 工具自己判斷 | 完全不問 |
|---|---|---|---|---|
| Claude Code | 新版（2.1.283 起）會自己判斷。要每一步都問：`claude --permission-mode default` | `claude --permission-mode acceptEdits` | `claude --permission-mode auto` | `claude --dangerously-skip-permissions` |
| Antigravity CLI（agy） | 新版（1.5.7 起）用個人帳號時會自己判斷，其他情況每一步都問 | `agy --mode accept-edits` | `agy --mode auto` | `agy --dangerously-skip-permissions` |
| Codex CLI | 官方文件沒有寫明 | 沒有對等的啟動方式 | `codex --approve-for-me` | `codex --yolo` |
| GitHub Copilot | 每一步都問 | `copilot --allow-tool='write'` | `copilot --assisted-approval` | `copilot --yolo` |

- **改檔不問，指令照問**：建立與修改檔案直接做；要跑指令時還是先問你。
- **工具自己判斷**：工具裡另外有一層，判斷這個動作安不安全。它覺得安全就直接做，覺得有風險才問你。問得最少，但什麼時候問不固定。
- **完全不問**：只適合用完就丟的測試環境，上課不用。

依各家官方文件整理（2026-11-18 查核），之後各家可能再改：[Claude Code](https://code.claude.com/docs/en/permission-modes)、[Antigravity CLI](https://antigravity.google/docs/cli/modes)、[Codex CLI](https://developers.openai.com/codex/cli/reference)、[GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-cli/allowing-tools)。

**會不會刪掉我的檔案？**

- 不問的範圍越大，越有可能。在專案資料夾裡面，「改檔不問」和「工具自己判斷」都可能直接覆蓋或刪除檔案，不會先問你。官方文件自己也寫：自己判斷的模式只是減少詢問，不保證安全。
- 專案資料夾外面比較安全。這幾家預設都把 AI 的活動範圍限制在你打開的那個資料夾。所以請一定在 `ntut` 資料夾裡啟動 AI，不要在桌面或使用者資料夾啟動。
- 從 GitHub clone 下來的檔案救得回來（`git checkout .` 或重新 clone）。你自己做出來的檔案救不回來，尤其是你親手寫的 `understanding.md`。寫完請另外複製一份到別的地方。
- 這個專案的班規（`CLAUDE.md`）有寫「不要刪除任何檔案」。這是對 AI 的要求，不是技術上的保證。

## 九道閘門

`python3 tools/check.py`（Windows：`py tools/check.py`）每一道印一行，最後一行是 `RESULT: GREEN` 或 `RESULT: RED`，括號裡是過了幾道。紅燈不是壞掉，是它幫你抓到問題。

| 閘門 | 檢查什麼 |
|---|---|
| G0 | 字幕檔沒被改 |
| G1 | 字幕文字是腳本做的，而且和標準答案一段一段都一樣 |
| G2 | 文章的字數落在字幕的 95% 到 105%（沒有被濃縮） |
| G3 | 51 段字幕每一段都還在 |
| G4 | 沒有「講者提到……」這一類摘要句 |
| G5 | 補述沒有動到全文 |
| G6 | 每一塊補述都有標記（📖 名詞補充、🎯 立場筆記） |
| G7 | 網頁和檔案同步 |
| G8 | `understanding.md` 是你親手寫的 |

只跑其中幾道：`python3 tools/check.py --only G0,G1`。寫理解之前先跑前八道：`python3 tools/check.py --before-understanding`。

## 三條鐵律

1. 講者的話一句都不能少。不摘要、不濃縮、不改寫。
2. AI 加的話要另外放，標明不是原文。
3. 你的理解自己寫，AI 不代筆。

## 卡住了

每一關都有一包「做到那一關結束」的起始包，連結在[實作頁](https://goodedunote.web.app/prepare/session1-lab.html)每一關最下面的「卡住了？」。下載、解壓、照包裡 README 的「下一步」接著做。

## 授權與來源

文字 CC BY 4.0，程式碼 MIT。來源：好學生筆記、說話與聽話（江碩濤）。字幕檔是講者本人 2026 年 7 月閃講的語音辨識結果，刻意保留辨識錯誤作為教材。
