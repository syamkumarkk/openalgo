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
expiry_date = main_obj.expiry_date.replace("-", "")
atm = main_obj.get_atm()
now = datetime.now().strftime("%Y-%m-%d")
while True:
    print(datetime.now())
    main_obj.order_util.cancel_an_order()
    time.sleep(30)