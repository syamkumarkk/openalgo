@echo off
cd /d D:\python\openalgo
call venv\Scripts\activate
cd strategies\live

echo === BANKNIFTY STRATEGY STARTED ===
:loop
python 5ema_opt_bank.py
echo === BANKNIFTY CRASHED - RESTARTING IN 5 SECONDS ===
timeout /t 5
goto loop
