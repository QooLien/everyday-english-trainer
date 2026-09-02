#!/bin/bash
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
    osascript -e 'display alert "找不到 Python 3" message "請先從 python.org 安裝 Python 3.10 或更新版本。"'
    exit 1
fi

python3 -m pip install --user --upgrade pyinstaller || exit 1
python3 -m PyInstaller --noconfirm --clean --windowed --name EverydayEnglish vocabulary_gui.py || exit 1

osascript -e 'display notification "已建立 dist/EverydayEnglish.app" with title "Everyday English"'
open dist
