import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from openalgo import api, ta
from base.MainClass import MainClass
from base.OptionChainDB import OptionChainDB
import pandas as pd
import time,os,sys
from datetime import datetime, timedelta
main_obj = MainClass('NIFTY')
client = main_obj.client
expiry_dateVal = main_obj.expiry_date
order_utilObj = main_obj.order_util
# ✅ RUN STRATEGY
#main_obj.run()
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
posflag = 0
stoploss = 0
entry = 0
flag = 0
exit = 0
target = 0
deltaValue = 0.50
expiry_date = expiry_dateVal.replace("-", "")
expiry_date = main_obj.expiry_date.replace("-", "")
atm = main_obj.get_atm()
now = datetime.now().strftime("%Y-%m-%d")
while True:
    completed_positions =  main_obj.order_util.get_positions()
    if len(completed_positions)>0:
        open_negative_priced_positions_status = [ o for o in completed_positions if o.get("pnl") <=0 and o.get("quantity") >0   ]
        print("opened un profitted list")
        print(open_negative_priced_positions_status)
        
        if len(open_negative_priced_positions_status)>0:
            open_positions_for_cancel = [ o for o in open_negative_priced_positions_status if o.get("pnl", 0) < -1000   ]
            for clearorder in open_positions_for_cancel:
                print("opened un profitted values")
                print(clearorder)        
                main_obj.order_util.place_safety_order(clearorder['symbol'],clearorder['ltp'],clearorder['ltp'],"MIS",clearorder['quantity'])
            #print(open_positions_for_cancel)
    
    time.sleep(30)