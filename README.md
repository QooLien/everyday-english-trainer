# Everyday English 英文單詞練習器

這是一個跨平台圖形介面的鍵盤拼字練習器，收錄由淺至深的日常常用詞。學習、考試、提示、講解與月曆紀錄都在應用程式視窗中操作，不需要使用終端機。

## Windows 一鍵啟動

1. 安裝 Python 3.10 或更新版本，安裝時勾選 **Add Python to PATH**。
2. 雙擊 `run_windows.bat`，程式會開啟圖形介面且不顯示終端機。

若電腦已裝好 Python，不需要另外安裝任何套件。

## 建立獨立的 Windows EXE

在 Windows 電腦上雙擊 `build_windows_exe.bat`。腳本會安裝 PyInstaller，並以無終端視窗模式產生：

```text
dist\EverydayEnglish.exe
```

這個 EXE 可以複製到其他 Windows 電腦使用，不需要另外安裝 Python。PyInstaller 不支援從 macOS 交叉編譯 Windows EXE，所以建置步驟必須在 Windows 上執行。

## 建立 macOS App

第一次使用時，在「系統設定 → 隱私權與安全性」允許執行 `build_macos_app.command`，或在此資料夾執行一次：

```bash
chmod +x build_macos_app.command
./build_macos_app.command
```

建置後雙擊 `dist/EverydayEnglish.app` 即可開啟圖形介面。建立完成的 App 可移至「應用程式」資料夾。

若 macOS 阻擋第一次開啟，請在 App 上按右鍵並選擇「打開」。

每次會先完整顯示單詞、中文輔助解釋、例句、字根和記憶連結。完成當日學習卡後，程式才會進入鍵盤拼字考試。介面提供：

- 「給我提示」：依序顯示首字母、拼字骨架及字根提示
- 「跳過並講解」：顯示完整分析並將單詞加入錯題回流
- 「確認答案」：也可直接按 Enter 送出答案
- 「學習月曆」：查看每日完成狀態、累積正確率與待加強單詞

答錯的單詞會提高抽題權重，在後續練習中再次出現。程式會自動保存熟練度、答對與答錯次數。在 Windows，進度存放於 `%LOCALAPPDATA%\EverydayEnglish\vocabulary_progress.json`，因此即使 EXE 放在受保護的程式目錄也能正常保存。

## 詞彙安排與辭典來源

使用者不需要選章節或級別。程式會依常用程度、拼字複雜度與個人熟練度，自動從生活基礎詞逐步安排到抽象常用詞；尚未熟練與曾答錯的詞會優先排入後續學習。

詞彙語義架構以 [Open English WordNet](https://en-word.net/) 為基礎，依 CC BY 4.0 授權使用；中文解釋、字根提示及教學記憶法是本專案為學習用途整理的輔助內容。完整標示請見 `ATTRIBUTION.md`。
