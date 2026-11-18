# NTUT 工作坊｜第一堂：把一段字幕做成好學生筆記

臺北科技大學 AI Agent 實作工作坊第一堂（2026-11-23）的專案。

今天只學一件事：**把一個大任務拆成一步一步**，每一步都寫得出四件事：讀什麼、誰來做、做出什麼、怎麼檢查。材料是一場三分鐘閃講的字幕檔。做出來的東西，是一份沒有少掉任何一句話、讀得進去的好學生筆記，加上你自己寫的理解。

- 上課簡報：<https://goodedunote.web.app/prepare/session1.html>（這個專案的 `slides/` 裡也有一份）
- 實作頁（每一步的指令與提示詞都可以複製）：<https://goodedunote.web.app/prepare/session1-lab.html>
- 課前準備（安裝 Python、Git、AI 工具）：<https://goodedunote.web.app/prepare.html>

## 怎麼開始

1. 把專案複製到你的電腦（clone）。在終端機進到你想放的資料夾，例如桌面的 `ntut-workshop`：

   ```
   git clone https://github.com/shuotao/ntut.git
   ```

2. 用 VS Code 打開 `ntut` 資料夾（檔案 → 開啟資料夾），再開一個終端機（終端機 → 新增終端機）。
3. 看一次紅燈。現在什麼都還沒做，所以九道檢查只有一道是綠的，這是正確的起點：

   ```
   python3 tools/check.py
   ```

   最後一行應該是 `RESULT: RED (1/9)`。Windows 請把 `python3` 換成 `py`。

4. 在這個資料夾啟動你的 AI 工具（`claude`、`codex`、`agy` 或 `copilot`），貼上第一句話：

   > 請先讀 CLAUDE.md、README.md 與 spec.md，然後用三句話告訴我：（一）這個專案要產出什麼；（二）哪些檔案絕對不能改；（三）我們接下來的第一步是什麼。先不要動任何檔案。

5. 接下來照[實作頁](https://goodedunote.web.app/prepare/session1-lab.html)的 S1 到 S4 做。所有提示詞也收在這個專案的 [`prompts.md`](prompts.md)。

之後老師更新了內容，在 `ntut` 資料夾裡跑 `git pull` 就會拿到。你自己做出來的檔案不會被動到。

## 資料夾裡有什麼

| 路徑 | 是什麼 | 誰可以改 |
|---|---|---|
| `CLAUDE.md` | 給 AI 看的班規。這個專案唯一的規則檔 | 沒有人 |
| `AGENTS.md`、`GEMINI.md`、`.github/copilot-instructions.md` | 只有一行，指向 `CLAUDE.md`。不同的 AI 工具會找不同的檔名 | 沒有人 |
| `spec.md` | 筆記的規格：要做出什麼、每一步的規則 | 沒有人 |
| `scripts_spec.md` | 兩支腳本的規格：你請 AI 寫腳本時的訂單 | 沒有人 |
| `prompts.md` | 今天用到的每一段提示詞，照順序 | 沒有人 |
| `source/transcript.srt` | 來源：閃講的字幕檔，51 段，有聽錯的專有名詞 | 沒有人（唯讀） |
| `data/corrections.json` | 校正用語清單：聽錯的詞 → 對的詞，25 條 | 你確認之後可以加 |
| `tools/check.py` | 九道閘門 G0 到 G8 | 沒有人 |
| `tools/render.py` | 把現在有的檔案做成一頁網頁 `site/index.html` | 沒有人 |
| `tools/plan_check.py` | 檢查計畫 `plan.md` 的格式 | 沒有人 |
| `tools/use_reference.py` | 備援：把講師寫好的腳本拿來用 | 沒有人 |
| `reference/` | 講師寫好的兩支腳本。**先不要打開**，見下面「雙軌」 | 沒有人 |
| `slides/` | 第一堂的簡報。用瀏覽器打開 `slides/session1.html` | 沒有人 |

你會做出來的檔案：`tools/srt_strip.py`、`tools/fix_terms.py`（S1）、`data/cues*.json`（S1）、`plan.md`（S2）、`notes/cleaned.md`、`notes/notes.md`（S3）、`site/index.html`、`loop_log.md`、`understanding.md`（S4）。

## 今天的五關

| 關 | 做什麼 | 誰做 | 怎麼確認 |
|---|---|---|---|
| S0 | 把專案 clone 下來，AI 開在這個資料夾，先讀班規 | 你 | `check.py` 是 RED (1/9) |
| S1 | 請 AI 寫兩支腳本：拿掉時間軸、校正專有名詞。然後自己讀 51 段字幕 | AI 寫腳本，腳本做事，你驗收 | `check.py --only G0,G1` 是 GREEN (2/2) |
| S2 | 請 AI 擬訂計畫，你來審 | AI 擬，你審 | `plan_check.py` 是 GREEN (1/1) |
| S3 | 把字幕變回一篇文章；再加名詞補充與立場筆記（用你的身份寫視角） | AI | 字數沒少、每一段都還在、原文沒被動到 |
| S4 | 紅燈修到過（最多三輪），自己讀一遍，親手寫理解 | AI 修，你寫 | `check.py` 是 GREEN (9/9) |

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

它會把 `reference/` 裡講師的版本放進 `tools/`，你寫的那一支改名成 `*.mine.py` 留著對照。用了備援不是失敗：今天要學的是怎麼把訂單寫清楚、怎麼檢查，不是比誰的 AI 厲害。

## 九道閘門

`python3 tools/check.py` 每一道印一行，最後一行是 `RESULT: GREEN` 或 `RESULT: RED`。紅燈不是壞掉，是它幫你抓到問題。

| 閘門 | 檢查什麼 |
|---|---|
| G0 | 字幕檔沒被改 |
| G1 | 字幕文字是腳本做的，而且和標準答案一段一段都一樣 |
| G2 | 文章的字數落在字幕的 95% 到 105%（沒有被濃縮） |
| G3 | 51 段字幕每一段都還在 |
| G4 | 沒有「講者提到……」這一類摘要句 |
| G5 | 補述沒有動到全文 |
| G6 | 每一塊補述都有標記（📖 名詞補充、🎯 身份視角） |
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
