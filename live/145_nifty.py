import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from base.MainClass import MainClass
from openalgo import api
from base.OptionChainDB import OptionChainDB
import pandas as pd
import time
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
if not isinstance(atm, int):
    print("❌ ATM FETCH FAILED:", atm)
    raise SystemExit
print("📌 ATM STRIKE:", atm)
# selections = main_obj.order_util.get_strikes(expiry_date,atm)
# db.save_options_today(selections)
# selections = []
# selections = [{'symbol': 'NIFTY13JAN2626200PE', 'type': 'PE', 'strike': 26200},{'symbol': 'NIFTY13JAN2625950CE', 'type': 'CE', 'strike': 25950}]
# ============================
# MAIN LOOP
# ============================
while True:
    # if len(selections)==0:
    # --- Scan window (9:28 – 9:31)
    if main_obj.is_after_IST(9, 28) and not main_obj.is_after_IST(9, 31):        
        print("🔍 SCANNING OPTIONS...")
        selections = main_obj.order_util.get_strikes(expiry_date,atm)
        db.save_options_today(selections)
        time.sleep(5)
    # --- Trade window (after 9:31 before 14:00)
    if main_obj.is_after_IST(9, 31):
        if main_obj.is_after_IST(14, 0):
            print("⛔ TIME EXIT – AFTER 2:00 PM")
            break
        print("\n-----------------🚀 EXECUTING TRADES---------------")
        selections = db.get_today_options_as_dict()
        if len(selections):
              for selected in selections:              
                print(f"--------------{selected['type']} Run {selected['symbol']} ---------------")                    
                main_obj.order_util.run_145_option_trade(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,
                    symbol=selected["symbol"],
                    strategy_prefix=(f"145{selected['type']}")
                )           
    time.sleep(1)
print("✅ STRATEGY FINISHED")