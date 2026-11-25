# lesson1_backup：第一堂的四個原檔

這個資料夾放的是第一堂（2026-11-23）的 `CLAUDE.md`、`README.md`、`spec.md`、`tools/check.py`，路徑和它們原來在 `ntut` 裡的位置一樣，內容一個字都沒改。

第一堂已經上完。第二堂（2026-11-30）有四個同名的檔案，同一個名字只能放一份，所以原位現在放第二堂的版本，第一堂的搬到這裡。第一堂的其他檔案（`source/`、`data/`、`reference/`、`slides/`、`prompts.md`、`scripts_spec.md`、`tools/` 裡的 `render.py` 等）沒有衝突，還在原位；你第一堂做出來的檔案也都還在原位。

- **只想看第一堂的規則**：直接打開這裡的 `CLAUDE.md`。
- **想重做第一堂**：第一堂的檢查要在原位才跑得動（它是照 `ntut` 最上層的位置找檔案的），不要在這個資料夾裡跑。在 `ntut` 資料夾執行下面這一行（Windows 把 `python3` 換成 `py`），或把 `prompts.md` 最後一節「把第一堂帶回來」那一段貼給你的 AI：

  ```
  python3 tools/switch_lesson.py 1
  ```

  它先把第二堂的版本存進 `lesson2_keep/`，再把這裡的四個檔案放回原位，然後跑一次第一堂的檢查。只複製，不刪除任何檔案。之後照第一堂實作頁做：<https://goodedunote.web.app/prepare/session1-lab.html>
- **複習完，回到第二堂**：`python3 tools/switch_lesson.py 2`，或貼「回到第二堂」那一段。
