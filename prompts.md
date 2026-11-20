# 今天用到的提示詞

照順序。每一段都是「貼給 AI」的內容，所有 AI 工具相同。貼之前先想：這一段在叫 AI 做什麼？貼完我要看什麼？
實作頁上每一段前面都有小卡說明：<https://goodedunote.web.app/prepare/session1-lab.html>
提示詞裡提到的檔案，有些要做到那一步才會有（例如 `data/raw.txt`、`notes/cleaned.md`）。哪個檔案由哪一步做出來，看 `README.md` 的「之後才會出現的檔案」。

Windows 的同學：提示詞裡的 `python3` 不用自己改，有指令的每一段都已經寫了一句告訴 AI 在 Windows 要用 `py`（沒有就用 `python`）。Windows 請在命令提示字元（cmd）操作。

## S0 開起來

**第一句話**

```text
請先讀 CLAUDE.md、README.md 與 spec.md，然後用三句話告訴我：（一）這個專案要產出什麼；（二）哪些檔案絕對不能改；（三）我們接下來的第一步是什麼。先不要動任何檔案。
```

## S1 請 AI 寫腳本

**請 AI 寫第一支腳本：拿掉時間軸**

```text
請寫一支腳本 tools/srt_strip.py，把字幕檔的時間軸拿掉。規格在 scripts_spec.md 的「腳本一」，請先讀它和 CLAUDE.md。
輸入：source/transcript.srt（唯讀，不能改）。
工具：Python 標準函式庫，不安裝任何套件。
輸出：data/cues.json 與 data/raw.txt，格式照規格，鍵名一字不改。
檢查：寫完先執行 python3 tools/srt_strip.py，再執行 python3 tools/check.py --only G0,G1，把兩次的完整輸出貼給我。（Windows 請用 py 代替 python3，沒有 py 就用 python；Windows 用命令提示字元（cmd），指令分開跑。）
邊界：不要打開 reference/；不要改 source/、tools/ 裡已有的檔案；程式只新增 tools/srt_strip.py 這一支（data/cues.json 與 data/raw.txt 是腳本跑出來的）。
停止：G1 提示「還沒套校正用語」就代表這一支過了，請停下來。如果 G1 說某一段不一樣，修正腳本再跑，最多三次；三次還不過就停下來，把訊息交給我。
```

**請 AI 寫第二支腳本：校正專有名詞**

```text
請寫第二支腳本 tools/fix_terms.py，照校正用語清單把聽錯的專有名詞換成對的。規格在 scripts_spec.md 的「腳本二」。
輸入：data/cues.json、data/corrections.json（都不能改）。
工具：Python 標準函式庫，不安裝任何套件。
輸出：data/cues_fixed.json 與 data/fixed.txt，格式照規格。
規則：長的詞先換；換過的地方不能再被別條規則換一次；清單以外的字一個都不動。
檢查：寫完先執行 python3 tools/fix_terms.py，再執行 python3 tools/check.py --only G0,G1，把兩次的完整輸出貼給我。（Windows 請用 py 代替 python3，沒有 py 就用 python；Windows 用命令提示字元（cmd），指令分開跑。）
邊界：不要打開 reference/；程式只新增 tools/fix_terms.py 這一支（data/cues_fixed.json 與 data/fixed.txt 是腳本跑出來的）。
停止：看到 RESULT: GREEN (2/2) 就停下來。如果 G1 說某一段不一樣，修正腳本再跑，最多三次；三次還不過就停下來，把訊息交給我。
```

**選配：請 AI 找還有沒有聽錯的詞（兩支腳本都跑完、有了 data/raw.txt 才貼）**

```text
請讀 data/raw.txt 與 data/corrections.json。字幕是語音辨識做的，裡面有聽錯的專有名詞。請列出你覺得還有哪些詞可能聽錯、但清單裡還沒有的，每個寫出第幾段、原來的字、你猜是什麼、你有多確定。只列出來給我判斷，不要改任何檔案。
```

## S2 擬訂計畫

**請 AI 提出計畫**

```text
請讀 CLAUDE.md、spec.md 與 data/fixed.txt。先不要寫任何筆記或程式。請提出一份步驟計畫，寫進 plan.md，從「拿掉時間軸」一路到「學生寫下自己的理解」：每一步用「1.」「2.」編號並寫一個簡短標題，底下固定四欄，欄名一字不改：「- 輸入：」「- 工具：」「- 輸出：」「- 檢查：」。輸入與輸出寫檔案路徑；工具寫腳本名稱，或寫「AI 的判斷」，或寫「學生本人」；檢查寫 tools/check.py 的哪一道閘門。規則：確定性的工作交給 tools/ 裡的腳本，只有需要判斷的步驟由你來做；每一步只做一件事。寫完後跑 `python3 tools/plan_check.py`（Windows 用 py 代替 python3，沒有 py 就用 python），把結果貼給我，然後停下來等我確認。
```

**審計畫：某一步太大（把 n 換成步驟編號）**

```text
第 n 步太大，請拆成兩步。
```

**審計畫：某一步不該用 AI（把 n 換成步驟編號）**

```text
第 n 步為什麼需要 AI 判斷？如果是機械工作，改成用腳本。
```

## S3 把字幕變回文章

**把字幕變回一篇文章**

```text
請依 CLAUDE.md 與 spec.md「步驟 3」的規則，只讀 data/cues_fixed.json（這是唯一來源，共 51 段字幕），把字幕變回一篇文章，寫進 notes/cleaned.md。你可以做的只有：補全形標點、在句子之間補接續詞與前後承接、把破碎的字幕合併成段落、在段落之間加「## 」小標題。講者說的每一句話都要留著：不刪句子、不濃縮、不改寫、不改成第三人稱。不要加任何補充說明。只寫 notes/cleaned.md，不要碰 source/ 與 data/。寫完跑 `python3 tools/check.py --only G0,G1,G2,G3,G4`（Windows 用 py 代替 python3，沒有 py 就用 python），貼結果。若紅燈，說明原因並修正，最多三輪；三輪仍紅就停下來把問題交給我。
```

**名詞補充**

```text
請依 spec.md「步驟 4」的規則，讀 notes/cleaned.md，寫出 notes/notes.md：先把 notes/cleaned.md 的全文原樣照抄，一個字都不改；再挑 2 到 3 個第一次聽會陌生的術語，在它出現的那一段後面插入名詞補充區塊，第一行寫「> 📖 **名詞補充：術語**」，下面一到三句說明，每一行都以「> 」開頭，區塊上下各空一行。只寫你確定的內容，不確定的術語告訴我，不要編。這一步先不要寫身份視角。只寫 notes/notes.md。
```

**立場筆記（貼之前把第一句括號裡的字換成你的科系或身份）**

```text
我的身份是：（請換成你的科系或身份，例如：資財系學生）。請在 notes/notes.md 裡加上這個身份的視角：挑 2 到 3 段，在段落後面插入一個區塊，第一行寫「> 🎯 **我的身份視角**」（把「我的身份」換成我上面寫的身份），下面三行分別是「> - **類比**：」「> - **應用**：」「> - **連結**：」，用這個身份熟悉的事情來寫。區塊上下各空一行。正文與已經有的名詞補充都不要改。寫完跑 `python3 tools/check.py --only G5,G6`（Windows 用 py 代替 python3，沒有 py 就用 python），貼結果。若紅燈，說明原因並修正，最多三輪。
```

## S4 跑檢查，寫下你的理解

**紅燈時的修正（把 check.py 的完整輸出貼在最後）**

```text
tools/check.py --before-understanding 的輸出如下（貼上）。請只修正 G0 到 G7 紅燈指出的檔案：不要改 source/，不要手改 data/ 裡腳本產生的檔案，不要改 data/corrections.json，不要改 tools/。字幕不見了就對照 data/fixed.txt 把講者的原話補回 notes/cleaned.md，並讓 notes/notes.md 的正文跟著一樣；不要為了過閘門而刪字、湊字或改寫講者的話。絕對不要建立、撰寫或修改 understanding.md，也不要試圖讓 G8 變綠，那是學生自己親手寫的。如果你認為閘門本身錯了，不要硬改，寫一段 GATE DISPUTE 說明給我。修完先跑 python3 tools/render.py，再重跑 python3 tools/check.py --before-understanding（Windows 用 py 代替 python3，沒有 py 就用 python；Windows 用命令提示字元（cmd），兩個指令分開跑）。
```
