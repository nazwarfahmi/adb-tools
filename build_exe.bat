@echo off
title Build ADB Tools GUI Executable
echo ===================================================
echo   Building ADB Tools GUI Standalone Windows EXE
echo ===================================================
echo Closing background ADB daemons to release file locks...
taskkill /f /im adb.exe >nul 2>&1
taskkill /f /im ADB_Tools_GUI.exe >nul 2>&1

python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --name "ADB_Tools_GUI" ^
  --add-data "ui;ui" ^
  --add-data "core;core" ^
  --add-data "data;data" ^
  --add-data "bin;bin" ^
  main.py

echo.
echo ===================================================
echo   Build complete! Output is in: dist\ADB_Tools_GUI\
echo ===================================================
pause
