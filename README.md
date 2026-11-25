# NTUT 工作坊｜第一堂與第二堂的專案

臺北科技大學 AI Agent 實作工作坊的專案資料夾。兩堂課用同一個資料夾：

- **第一堂（2026-11-23，已經上完）**：把一個大任務拆成一步一步。材料是一場閃講的字幕，做成一份好學生筆記。
- **第二堂（2026-11-30）**：寫一份目標文件交給 AI，然後放手，讓它自己跑關卡、自己修，跑到合格為止。題目是「你今天想吃什麼」，做出一桌四道菜的午餐。

第二堂的東西是老師放上來、你用 `git pull` 拿到的。你第一堂做出來的檔案（`data/`、`notes/`、`plan.md`、`understanding.md`、`site/`……）都還在，沒有被動到。

- 第二堂簡報：<https://goodedunote.web.app/prepare/session2.html>
- 第二堂實作頁（每一步的指令與要貼給 AI 的文件都可以複製）：<https://goodedunote.web.app/prepare/session2-lab.html>
- 第一堂簡報與實作頁：<https://goodedunote.web.app/prepare/session1.html>、<https://goodedunote.web.app/prepare/session1-lab.html>

## 第二堂從這裡開始

1. 在 `ntut` 資料夾打開終端機，拿老師的新東西（已經拿過就跳過）：

   ```
   git pull
   ```

2. 看一次紅燈。還沒有任何菜單，八項都是紅的，這是正確的起點：

   ```
   python3 tools/check.py runs/a
   ```

   最後一行應該是 `RESULT: RED (0/8)`。Windows 把 `python3` 換成 `py`；找不到 `py` 就用 `python`；不要打 `python3`（Windows 上常會跳出 Microsoft Store）。下面所有指令都照這樣換。

3. 接下來照[第二堂實作頁](https://goodedunote.web.app/prepare/session2-lab.html)的 S0 到收尾做。要貼給 AI 的文件也收在 `goals/` 和 [`prompts.md`](prompts.md) 的最後一節。

## 哪些第一堂的檔案搬進了 `lesson1_backup/`，為什麼

第一堂和第二堂有四個檔案同名，內容卻不能共用：同一個名字只能放一份。第一堂已經上完，所以這四個名字現在是第二堂的；第一堂的原版一個字都沒改，搬進 `lesson1_backup/`，路徑和原來一樣。

| 第一堂的原版在 | 現在原位放的是 | 為什麼不能共用 |
|---|---|---|
| `lesson1_backup/CLAUDE.md` | 第二堂的規則檔 `CLAUDE.md` | 第一堂要 AI 先提計畫、等你說「開始」、最多修三輪；第二堂要它照目標文件做到完、不停下來問。兩套寫在同一份裡，AI 會在兩種做法之間搖擺。 |
| `lesson1_backup/README.md` | 這份說明 | 說明要講現在的資料夾。 |
| `lesson1_backup/spec.md` | 第二堂的規格（一桌菜） | 兩堂的規格不同，關卡讀的都是 `spec.md`。 |
| `lesson1_backup/tools/check.py` | 第二堂的關卡（M1 到 M8） | 兩堂的關卡不同，網頁和文件都叫它 `tools/check.py`。 |

其他第一堂的檔案（`source/`、`data/`、`reference/`、`slides/`、`prompts.md`、`scripts_spec.md`，和 `tools/` 裡的 `render.py`、`plan_check.py`、`gsn.py`、`use_reference.py`）沒有衝突，留在原位。`prompts.md` 只在最後面多了第二堂的一節。

想看第一堂原本的規則：直接打開 `lesson1_backup/CLAUDE.md`。要真的重做第一堂，用下面兩段，把它換回來。

## 想複習第一堂：把 `lesson1_backup/` 帶回來

第一堂的檢查要在原位才跑得動，所以要先換回來。下面兩段是要貼給 AI 的文字（你的 AI 工具開在 `ntut` 資料夾裡），換檔案的是 `tools/switch_lesson.py` 這支程式：只複製、不刪除任何檔案。沒有 AI 工具的人，自己在終端機打框裡「工具」那一行的指令也一樣。

**把第一堂帶回來**（第二堂的四個檔案會先存進 `lesson2_keep/`）

```text
請直接開始，不用先提計畫，做到完、不要停下來問我：我想複習第一堂，請把第一堂的檔案從 lesson1_backup/ 帶回來。
輸入：lesson1_backup/ 裡第一堂的原檔（CLAUDE.md、README.md、spec.md、tools/check.py），和現在資料夾裡同名的第二堂版本。
工具：只執行這一行，指令照抄，前後不要加別的東西（不要在前面加 cd）：python3 tools/switch_lesson.py 1（Windows 把 python3 換成 py，沒有 py 就用 python）。它會先把第二堂的版本存進 lesson2_keep/，再把第一堂的原檔放回原位。
輸出：資料夾回到第一堂的樣子；第二堂的那四個檔案留在 lesson2_keep/。
檢查：那一行跑完，會自己接著跑第一堂的檢查 tools/check.py，印出它的最後一行。第一堂還沒重做的地方是紅的，這是正常的。
邊界：不要刪除、移動或改寫任何檔案，複製檔案交給上面那一行，你自己不要動手；不要執行 git 指令；不要打開 lesson1_backup/ 或 lesson2_keep/ 去改。
停止：看到最後一行是 SWITCH: 開頭就停，用兩句話回報：SWITCH 那一行寫什麼、第一堂檢查的最後一行是什麼。SWITCH: 停 開頭的話，把完整輸出貼給我，不要自己修。
```

換好之後，離開 AI 對話、重新開一個（AI 開始時讀的是當時的 `CLAUDE.md`），再照[第一堂實作頁](https://goodedunote.web.app/prepare/session1-lab.html)做。第一堂的說明在 `README.md`（換回來後就是第一堂的版本），提示詞在 `prompts.md` 的前面幾節。

**複習完，回到第二堂**（第一堂的四個檔案，連你複習時改的地方，存回 `lesson1_backup/`）

```text
請直接開始，不用先提計畫，做到完、不要停下來問我：我複習完第一堂了，請把資料夾換回第二堂。
輸入：lesson2_keep/ 裡第二堂的版本（CLAUDE.md、README.md、spec.md、tools/check.py），和現在資料夾裡同名的第一堂版本。
工具：只執行這一行，指令照抄，前後不要加別的東西（不要在前面加 cd）：python3 tools/switch_lesson.py 2（Windows 把 python3 換成 py，沒有 py 就用 python）。它會先把第一堂的版本（含我複習時改的地方）存回 lesson1_backup/，再把第二堂的版本放回原位。
輸出：資料夾回到第二堂的樣子；第一堂的那四個檔案留在 lesson1_backup/。
檢查：那一行跑完，會自己接著跑第二堂的守衛 tools/guard.py 和起點關卡 tools/check.py runs/a，印出各自的最後一行。守衛要是 GUARD: OK。
邊界：不要刪除、移動或改寫任何檔案，複製檔案交給上面那一行，你自己不要動手；不要執行 git 指令；不要打開 lesson1_backup/ 或 lesson2_keep/ 去改。
停止：看到最後一行是 SWITCH: 開頭就停，用兩句話回報：SWITCH 那一行寫什麼、守衛和關卡的最後一行各是什麼。SWITCH: 停 開頭的話，把完整輸出貼給我，不要自己修。
```

換回來之後，`git status` 只會列出你自己做出來的檔案，第二堂的檔案和老師放上來的一樣。

## 第一堂的實作頁和現在的資料夾，哪裡對不上

第一堂的實作頁是照第一堂的資料夾寫的。拿了第二堂之後，沒換回來就照它做，會遇到：

- 跑 `tools/check.py`，看到的是第二堂的 M1 到 M8，不是第一堂的 G0 到 G8。
- `CLAUDE.md`、`README.md`、`spec.md` 是第二堂的內容。
- 實作頁說「你剛 clone 下來看到的就是這些」：現在多了第二堂的檔案（`goals/`、`cards/`、`inputs/`、`taste.md`、`team.json`、`eval.md`、`expected.json`、`.claude/`、`.codex/`、`.agents/`、`lesson1_backup/`，和 `tools/` 裡的新程式）。

要重做第一堂，先用上面「把第一堂帶回來」那一段。

## 現在資料夾裡有什麼（第二堂的部分）

| 路徑 | 是什麼 | 誰可以改 |
|---|---|---|
| `CLAUDE.md` | 給 AI 看的規則檔（第二堂）。`AGENTS.md`、`GEMINI.md`、`.github/copilot-instructions.md` 只有一行，指向它 | 沒有人 |
| `goals/` | 三份目標文件 `goal_a.md`、`goal_b.md`、`goal_c.md`，收尾要寫的 `my_goal.md`，和老師的範例 | `my_goal.md` 是你的 |
| `spec.md`、`taste.md` | 規格（要交什麼、八條規則），品味五條 | 品味可以在開始跑之前改成你家的版本 |
| `eval.md` | 比較表和你的結論 | 結論只有你寫 |
| `cards/`、`team.json`、`.claude/agents/`、`.codex/agents/`、`.agents/agents/` | 交給幫手的任務卡與角色檔 | 沒有人 |
| `inputs/` | 第三關的材料：一份英文食譜、一張冰箱圖 | 沒有人 |
| `tools/round.py`、`tools/check.py` | AI 自己跑的一輪關卡，和關卡本身（M1 到 M8） | 沒有人 |
| `tools/guard.py`、`tools/compare.py`、`tools/ask.py`、`tools/replay.py`、`tools/goalcheck.py`、`tools/agents.py`、`tools/fixtures/` | 稽核、比較表、叫別家、重播、檢查你的目標文件 | 沒有人 |
| `tools/switch_lesson.py` | 在第一堂和第二堂之間切換（見上面） | 沒有人 |
| `.claude/settings.json` | 讓 Claude Code 跑關卡時不用每次問你（只在這個資料夾有效） | 沒有人 |
| `lesson1_backup/` | 第一堂的四個原檔 | 沒有人（換回來複習時由 `switch_lesson.py` 寫） |
| `expected.json` | 老師檢查起始包用的 | 沒有人 |
| `runs/`、`mytools/` | 跑起來才會有：AI 做的菜單與紀錄、AI 自己寫的小程式 | AI 寫 |

## `git pull` 不成功

把終端機最後幾行和第二堂實作頁 S0 的「常見錯誤」對一下。最常見的是「你改過的檔案會被蓋掉」（`Your local changes ... would be overwritten`）：實作頁教你先把整個 `ntut` 複製一份到旁邊，再讓資料夾和老師的一樣，你第一堂的東西都留在那一份裡。

## 授權

見 [`LICENSE`](LICENSE)。
