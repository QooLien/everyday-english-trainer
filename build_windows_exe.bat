@echo off
setlocal
chcp 65001 >nul
title Build Everyday English EXE
cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 goto no_python
    set "PYTHON_CMD=python"
)

echo Installing the Windows packager...
%PYTHON_CMD% -m pip install --user --upgrade pyinstaller
if not %errorlevel%==0 goto failed

echo.
echo Building EverydayEnglish.exe...
%PYTHON_CMD% -m PyInstaller --noconfirm --clean --onefile --windowed --name EverydayEnglish vocabulary_gui.py
if not %errorlevel%==0 goto failed

echo.
echo Build complete: dist\EverydayEnglish.exe
echo You may copy this EXE to another Windows computer.
goto finished

:no_python
echo [Error] Python 3 was not found.
echo Install it from https://www.python.org/downloads/windows/
goto finished

:failed
echo [Error] The build failed. Review the messages above.

:finished
echo.
pause
endlocal
