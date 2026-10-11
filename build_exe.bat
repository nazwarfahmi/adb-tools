@echo off
title Build ADB Studio Executable
echo ===================================================
echo   Building ADB Studio Standalone Windows EXE
echo ===================================================
echo Closing background ADB daemons to release file locks...
taskkill /f /im adb.exe >nul 2>&1
taskkill /f /im ADB_Studio.exe >nul 2>&1

python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onedir --windowed --name "ADB_Studio" ^
  --add-data "ui;ui" ^
  --add-data "core;core" ^
  --add-data "data;data" ^
  --add-data "bin;bin" ^
  main.py

echo.
echo ===================================================
echo   Build complete! Output is in: dist\ADB_Studio\
echo ===================================================
pause
