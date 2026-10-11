@echo off
title Build ADB Tools GUI Single File EXE
echo ===================================================
echo   Building ADB Tools GUI as SINGLE STANDALONE EXE
echo ===================================================
echo Closing background ADB daemons to release file locks...
taskkill /f /im adb.exe >nul 2>&1
taskkill /f /im ADB_Tools_GUI.exe >nul 2>&1
taskkill /f /im ADB_Tools_GUI_Single.exe >nul 2>&1

python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name "ADB_Tools_GUI_Single" ^
  --add-data "ui;ui" ^
  --add-data "core;core" ^
  --add-data "data;data" ^
  --add-data "bin;bin" ^
  main.py

echo.
echo ===================================================
echo   Build complete! Output: dist\ADB_Tools_GUI_Single.exe
echo   (Hanya 1 file .exe ini saja yang disalin ke PC lain)
echo ===================================================
pause
