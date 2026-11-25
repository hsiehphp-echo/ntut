# 任務佈局 plan.md

| 步 | 輸入 | 誰做 | 輸出 | 怎麼檢查 |
|---|---|---|---|---|
| 1 | runs/c | 我跑關卡 | 起點 RED 0/8 | 看 ROUND 行 |
| 2 | 本文件 | 我（主對話） | plan.md、log.md | 目視 |
| 3a | inputs/fridge.png | Google Gemini(agy) cards/see.md | fridge.md | 每行一個食材 |
| 3b | inputs/recipe_en.txt | Google Gemini(agy) cards/translate.md | recipe_zh.md | 份量（3 蛋、2 番茄、1 湯匙油、1 茶匙糖）與時間（2 分鐘、30 秒）與原文一致 |
| 4 | fridge.md、recipe_zh.md | 我 | shopping.md、menu.json（預算 1000、價錢加總用 mytools/sumcheck.py 算） | mytools/sumcheck.py：加總、對照菜單食材與採購清單、食材不重複 |
| 5 | menu.json | Codex cards/design.md | menu.html | 關卡 M7 + 驗收 |
| 6 | 全部 | 我跑關卡；Google Gemini(agy) cards/review.md 驗收 | review_rN.md、log.md | 關卡綠 + 8 分以上 + 自我檢查三題 |

工具分工：看圖、翻譯、驗收＝Google Gemini；設計 menu.html＝Codex；計畫、shopping、menu.json、紀錄＝我。
