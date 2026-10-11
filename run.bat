@echo off
title ADB Tools GUI
echo Starting ADB Tools GUI...
python main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
