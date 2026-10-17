@echo off
chcp 65001 > nul
title the goldshire republick — Бордель The World (WoW Forever 1.0)
cd /d "%~dp0"

echo ==========================================================
echo    THE GOLDSHIRE REPUBLICK — БОРДЕЛЬ THE WORLD
echo               WoW Forever 1.0 (Рейты х1)
echo          Открытие: 4 ноября в 15:00 по МСК
echo ==========================================================
echo.

set PYTHON_CMD=python
if exist ".\venv\bin\python.exe" (
    set PYTHON_CMD=.\venv\bin\python.exe
) else if exist ".\venv\Scripts\python.exe" (
    set PYTHON_CMD=.\venv\Scripts\python.exe
)

echo [1/2] Проверка базы данных и параметров...
%PYTHON_CMD% -c "import database; database.init_db()"

echo [2/2] Запуск сервера на http://localhost:5000 ...
echo.
echo Для доступа друзей в локальной сети или через Radmin/Hamachi/ngrok:
echo используйте ваш IP-адрес с портом :5000 (например: http://192.168.1.X:5000)
echo.
echo Логин администратора: admin
echo Пароль: admin123
echo.
echo Нажмите Ctrl+C в этом окне, чтобы остановить сервер.
echo ==========================================================
echo.

start http://localhost:5000
%PYTHON_CMD% app.py

pause
