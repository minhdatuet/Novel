@echo off
echo ========================================
echo    HE THONG DICH TRUYEN AI
echo ========================================
echo.

cd /d "D:\Novel\Translate\scripts"

echo Chon che do:
echo 1. GUI (Giao dien do hoa)
echo 2. Command Line
echo 3. Cai dat thu vien
echo.

set /p choice="Nhap lua chon (1-3): "

if "%choice%"=="1" (
    echo Khoi chay GUI...
    python manager.py --gui
) else if "%choice%"=="2" (
    echo Che do Command Line
    python manager.py
) else if "%choice%"=="3" (
    echo Cai dat cac thu vien can thiet...
    pip install openai pathlib dataclasses
    echo Hoan thanh cai dat!
) else (
    echo Lua chon khong hop le!
)

pause
