@echo off
cd /d D:\python\openalgo
call venv\Scripts\activate
cd strategies\live

echo === NIFTY STRATEGY STARTED ===
:loop
python 5ema_opt_nifty.py
echo === NIFTY CRASHED - RESTARTING IN 5 SECONDS ===
timeout /t 5
goto loop
