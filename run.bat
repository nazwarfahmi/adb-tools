@echo off
title ADB Studio
echo Starting ADB Studio...
python main.py
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
