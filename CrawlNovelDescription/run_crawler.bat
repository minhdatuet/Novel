@echo off
chcp 65001 >nul
title SangTacViet Novel Crawler

echo.
echo ================================================
echo     🕸️ SANGTACVIET NOVEL CRAWLER 🕸️
echo ================================================
echo.
echo Chọn chức năng:
echo 1. 🖥️  Chạy GUI (Giao diện đồ họa)
echo 2. 💻  Chạy CLI (Dòng lệnh)
echo 3. 🔄  Cập nhật số chương cho truyện cũ
echo 4. 📊  Xem thống kê database
echo 0. ❌  Thoát
echo.

set /p choice="Nhập lựa chọn (0-4): "

if "%choice%"=="0" goto exit
if "%choice%"=="1" goto gui
if "%choice%"=="2" goto cli
if "%choice%"=="3" goto update
if "%choice%"=="4" goto stats
goto invalid

:gui
echo.
echo 🖥️ Khởi động GUI Version...
python sangtacviet_gui.py
pause
goto menu

:cli
echo.
echo 💻 Khởi động CLI Version...
python sangtacviet_final_crawler.py
pause
goto menu

:update
echo.
echo 🔄 Cập nhật số chương cho truyện đã có...
python update_chapters.py
pause
goto menu

:stats
echo.
echo 📊 Hiển thị thống kê database...
python show_stats.py
pause
goto menu

:invalid
echo.
echo ❌ Lựa chọn không hợp lệ!
timeout /t 2 >nul
goto menu

:menu
cls
goto :eof

:exit
echo.
echo 👋 Tạm biệt!
timeout /t 1 >nul
exit
