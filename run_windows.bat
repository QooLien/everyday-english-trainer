@echo off
setlocal
chcp 65001 >nul
title Everyday English - Vocabulary Trainer
cd /d "%~dp0"

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 vocabulary_gui.py
    goto finished
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw vocabulary_gui.py
    goto finished
)

echo.
echo [Error] Python 3 was not found.
echo Please install Python from https://www.python.org/downloads/windows/
echo During installation, select "Add Python to PATH".

:finished
endlocal
