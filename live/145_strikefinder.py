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
# ✅ INSTANTIATE THE CLASS
main_obj = MainClass('NIFTY')
db = OptionChainDB("145_NIFTY.db")
# ✅ ACCESS INSTANCE VARIABLES
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
print(now)
opening_strikes = main_obj.order_util.get_opening_range_strikes(
    expiry_date=expiry_date,
    atm=atm,
    PRICE_LOW=150,
    PRICE_HIGH=170
)
db.save_options_today(opening_strikes)
print("📊 OPENING RANGE STRIKES:", opening_strikes)


# %%
# ✅ INSTANTIATE THE CLASS
main_obj = MainClass('BANKNIFTY')
db = OptionChainDB("145_BANKNIFTY.db")
# ✅ ACCESS INSTANCE VARIABLES
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
print(now)
opening_strikes = main_obj.order_util.get_opening_range_strikes(
    expiry_date=expiry_date,
    atm=atm,
    PRICE_LOW=350,
    PRICE_HIGH=400
)
db.save_options_today(opening_strikes)
print("📊 OPENING RANGE STRIKES:", opening_strikes)


