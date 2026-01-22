@echo off
title Live Strategy Launcher

start "NIFTY 5EMA" cmd /k run_5ema_nifty.bat
start "BANKNIFTY 5EMA" cmd /k run_5ema_bank.bat
start "NIFTY 145" cmd /k run_145_nifty.bat
start "BANKNIFTY 145" cmd /k run_145_bank.bat

exit
