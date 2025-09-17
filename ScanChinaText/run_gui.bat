@echo off
title Chinese Text Translator GUI
echo.
echo ========================================
echo   Chinese Text Translator - GUI
echo ========================================
echo.
echo Starting GUI application...
echo.

cd /d "%~dp0"
python chinese_translator_gui.py

if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to start GUI application.
    echo Please make sure Python is installed and accessible.
    echo.
    pause
)
