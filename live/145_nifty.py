import sys, os
from datetime import datetime
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from base.MainClass import MainClass
from openalgo import api
from base.OptionChainDB import OptionChainDB
import pandas as pd
import time
import itertools
spinner = itertools.cycle(["|", "/", "-", "\\"])
# Enable ANSI escape characters in the terminal (workaround)
os.system("")

# Define color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m' # Reset color to default
print("SYS.PATH =", sys.path)
# ============================
# GLOBAL CONFIG
# ============================
ENTRY_TRIGGER = 185
ENTRY_TRIGGER_BTW = (ENTRY_TRIGGER+5)
SL_POINTS = 30
TARGET_POINTS = 45
# ============================
# INIT
# ============================
main_obj = MainClass("NIFTY")
db = OptionChainDB("145_NIFTY.db")
main_obj.debug = False # True to show array prints
client = main_obj.client
expiry_date = main_obj.expiry_date.replace("-", "")
# ============================
# SAFE ATM FETCH (ONCE)
# ============================
atm = main_obj.get_atm()
if type(atm) != int and atm['status']=='error':
    print(atm['message'])
    sys.exit()
if not isinstance(atm, int):
    print("❌ ATM FETCH FAILED:", atm)
    raise SystemExit
print("📌 ATM STRIKE:", atm,"\n")
# selections = main_obj.order_util.get_strikes(expiry_date,atm)
# db.save_options_today(selections)
# selections = []
# selections = [{'symbol': 'NIFTY13JAN2626200PE', 'type': 'PE', 'strike': 26200},{'symbol': 'NIFTY13JAN2625950CE', 'type': 'CE', 'strike': 25950}]
while True:
    time_exit=False
    if main_obj.is_after_IST(9, 35):        
        selections = db.get_today_options_as_dict()  
        if len(selections)==0:
            # expiry_date = main_obj.expiry_date.replace("-", "")
            atm = main_obj.get_atm()
            now = datetime.now().strftime("%Y-%m-%d")
            opening_strikes = main_obj.order_util.get_opening_range_strikes(
                expiry_date=expiry_date,
                atm=atm,
                PRICE_LOW=150,
                PRICE_HIGH=170
            )
            print(opening_strikes)
            db.save_options_today(opening_strikes)
            time.sleep(1)
        selections = db.get_today_options_as_dict()
        if len(selections):
            # ============================
            # MAIN LOOP
            # ============================
            while True:
                # if len(selections)==0:
                # --- Scan window (9:28 – 9:31)
                # if main_obj.is_after_IST(9, 28) and not main_obj.is_after_IST(9, 31):        
                #     print("🔍 SCANNING OPTIONS...")
                #     selections = main_obj.order_util.get_strikes(expiry_date,atm)
                #     db.save_options_today(selections)
                #     time.sleep(5)
                # --- Trade window (after 9:31 before 14:00)

                if main_obj.is_after_IST(15, 0):
                    print("⛔ TIME EXIT – AFTER 15:00 PM")
                    time_exit=True
                    break
                    sys.exit
                print(Colors.BLUE + f"\n-----------------🚀 EXECUTING TRADES--{len(selections)}   :___:    "
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}-------------"+ Colors.ENDC)
                selected_side = ''
                # print(len(selections))
                for selected in selections:   
                    if selected_side!=selected['type']:
                        print(f"--------------{selected['type']} Run  ---------------")                    
                    main_obj.order_util.run_145_option_trade(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,
                        symbol=selected["symbol"],
                        strategy_prefix=(f"145{selected['type']}"),
                        option_strike=selected['type']
                    )
                    selected_side = selected['type']

                if main_obj.exit_all["PE"]["NIFTY"]  == True and main_obj.exit_all["CE"]["NIFTY"]  == True :
                    break 
                sys.stdout.write(f"\r⏳ Waiting for candle time {next(spinner)}")
                sys.stdout.flush()
                time.sleep(1)
        else:
            print("\n-----------------🚀 END TRADES      ---------------")
    if time_exit==True:
        break    
print("✅ STRATEGY FINISHED")