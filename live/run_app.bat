@echo off
title Live Strategy Launcher

REM =========================
REM CONFIGURATION
REM =========================
set PROJECT_PATH=D:\python\openalgo
set VENV_NAME=venv
set STRATEGY_PATH=strategies\live

REM =========================
REM START NIFTY STRATEGY
REM =========================
start "NIFTY LIVE" cmd /k ^
"cd /d %PROJECT_PATH% && ^
call %VENV_NAME%\Scripts\activate && ^
cd %STRATEGY_PATH% && ^
echo === NIFTY STRATEGY STARTED === && ^
:loop_nifty && ^
python 145_nifty.py && ^
echo === NIFTY CRASHED - RESTARTING IN 5 SECONDS === && ^
timeout /t 5 && ^
goto loop_nifty"

REM =========================
REM START BANKNIFTY STRATEGY
REM =========================
start "BANKNIFTY LIVE" cmd /k ^
"cd /d %PROJECT_PATH% && ^
call %VENV_NAME%\Scripts\activate && ^
cd %STRATEGY_PATH% && ^
echo === BANKNIFTY STRATEGY STARTED === && ^
:loop_bank && ^
python 145_bank.py && ^
echo === BANKNIFTY CRASHED - RESTARTING IN 5 SECONDS === && ^
timeout /t 5 && ^
goto loop_bank"

exit
