
import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from openalgo import api, ta
import pandas as pd
import time
import itertools
spinner = itertools.cycle(["|", "/", "-", "\\"])
from datetime import datetime, timedelta
from base.MainClass import MainClass
main_obj = MainClass('BANKNIFTY')
# ✅ ACCESS INSTANCE VARIABLES
client = main_obj.client
expiry_dateVal = main_obj.expiry_date

order_utilObj = main_obj.order_util
main_obj.debug = False # True to show array prints
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
deltaValue = 0.45
expiry_date = expiry_dateVal.replace("-", "")

def check_signal(marketOnTheDay=0):
    
    # -----------------------------
    # Date setup (OpenAlgo standard)
    # -----------------------------
    if main_obj.is_after_IST(9,45):
        #print("✅ Current time is greater than 9:30 AM IST")
        start_date = (datetime.now() - timedelta(days=marketOnTheDay)).strftime("%Y-%m-%d")
    else:
        #print("⏳ Waiting for 9:30 AM IST")
        d = datetime.now()
        if d.weekday()==0:
            start_date   = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        elif d.weekday()==6:
            start_date   = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            start_date   = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # start_date   = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date   = (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d")
    interval   = "5m"

    print(f"\n🔄 Checking BANKNIFTY ({datetime.now()})")

    df = main_obj.get_last_min_candle(5,-1,start_date,end_date)

    # Safety check
    if not isinstance(df, pd.DataFrame) or df.empty:
        print("❌ No candle data available")
        return
    
    # Ensure datetime index
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)

    if len(df) < 3:
        print(f"❌ Not enough candles for EMA(5). Candles available: {len(df)}")
        return None
    
    # -----------------------------
    # Calculate EMA(5)
    # -----------------------------
    df["ema_5"] = ta.ema(df["close"], 5)
    # -----------------------------
    # Print LAST 5 EMA VALUES
    # -----------------------------
    #print("📊 Last 1 EMA(5) values (Completed Candles):")

    # for idx, row in df.iloc[-2:-1].iterrows():   # exclude running candle
    #     print(
    #         f"Time: {idx.strftime('%H:%M')} | "
    #         f"Low: {row['low']} | "
    #         f"EMA(5): {row['ema_5']}"
    #     )
    previous_ema = df.iloc[-2]
    # -----------------------------
    # Current (running) candle
    # -----------------------------
    current_candle = df.iloc[-1]
    print("⏳ Current RUNNING Candle:")
    print(
        f"Time: {df.index[-1].strftime('%H:%M')} | "
        f"Open: {current_candle['open']} | "
        f"High: {current_candle['high']} | "
        f"Low: {current_candle['low']} | "
        f"Close: {current_candle['close']} | "
        f"EMA(5): {current_candle['ema_5']}"
    )

    # -----------------------------
    # Last completed candle (SAFE)
    # -----------------------------
    completed = df.iloc[-2]
    current = df.iloc[-1]

    previous_ema = completed["ema_5"]
    previous_low  = completed["low"]
    previous_high  = completed["high"]
    current_ema = current["ema_5"]
    current_low  = current["low"]

    print("\n✅ Last COMPLETED Candle Used for Signal:")
    print(
        f"Time: {df.index[-2].strftime('%H:%M')} | "
        f"Low: {previous_low} | EMA(5): {previous_ema}"
    )
    print(
        f"Time: {df.index[-1].strftime('%H:%M')} | "
        f"Low: {current_low} | EMA(5): {current_ema}"
    )

    # -----------------------------
    # Fetch LTP (single call only)
    # -----------------------------
    # ltp = main_obj.safe_ltp("BANKNIFTY","NSE_INDEX")
    # if ltp is not None:
    #     atm = round(ltp / 100) * 100
    #     print(f"\n📈 BANKNIFTY LTP: {ltp} | ATM: {atm}")
    # else:
    #     print("❌ LTP fetch failed:", ltp)
    #     return  {'posflag':0,'msg':"Quote fetch failed"}
    
    # quote = client.quotes(symbol="BANKNIFTY", exchange="NSE_INDEX")
    # if quote.get("status") == "success":
    #     ltp = quote["data"]["ltp"]
    #     atm = round(ltp / 100) * 100
    #     print(f"\n📈 BANKNIFTY LTP: {ltp} | ATM: {atm}")
    # else:
    #     print("❌ Quote fetch failed:", quote)
    #     return  {'posflag':0,'msg':"Quote fetch failed"}
    return main_obj.order_util.identify_5ema_trigger(previous_ema,previous_low,previous_high,current_low)


#sys.exit("Critical failure")
runstatus =  main_obj.order_util.get_running_orders()
running_orders=[]
posflag =  main_obj.order_util.get_post_flag(runstatus,running_orders,"5EMA")
# ------------------------------------
# 4. Run Script in Loop
# ------------------------------------
while True:
    if main_obj.is_after_IST(15,15):
        print("✅ Current time is greater than 15:15 AM IST")
        break
        sys.exit()
    if main_obj.is_after_IST(9, 30):
        try:
            #runstatus =  get_running_orders()
            #break
            #get_running_orders()
            if posflag==0:
                    runstatus = check_signal()                       
                    if ( runstatus==None or runstatus.get("posflag") != ""):
                        print(f"❌ -----Waiting for the candles in {main_obj.index}----- ❌")
                        #break
                    if (runstatus!=None):
                        print(runstatus) 
                        if runstatus.get("BUY"):
                            posflag = runstatus['BUY']['posflag']
                            responseVal = runstatus['BUY']['response']
                            growPersentatge = runstatus['growPersentatge']
                            index_sl_position = runstatus['index_sl_position']
                            time.sleep(2)
                            if posflag==1:
                                symbol = responseVal['symbol']
                                
                                orderid = responseVal['orderid']
                                order_response = client.orderstatus(
                                            order_id=orderid,
                                            strategy="BN_Option_Intraday"
                                        )
                                print(order_response)
                                price = order_response['data']['price']
                                # trigger_price = price + (price * (growPersentatge+1) / 100)
                                print(price)
                                start_date = (datetime.now() - timedelta()).strftime("%Y-%m-%d")
                                print(start_date)
                                df = client.history(
                                symbol=symbol,
                                exchange="NFO",
                                interval="5m",
                                start_date=start_date,
                                end_date=start_date
                                )
                                last_candle = df.iloc[-2]
                                high_price = last_candle["high"]
                                low_price = last_candle["low"]
                                
                                print(f'index_sl_position : {index_sl_position}')
                                print(f'symbol : {symbol}')
                                #last_candle_percentage = ((high_price - low_price) / high_price) * 100                        
                                print(f'optin_high_price : {high_price}')
                                greeks = order_utilObj.get_option_greeks(symbol,main_obj.index)
                                if greeks['greeks']['delta']:
                                    deltaValue = greeks['greeks']['delta']
                                #slprice = high_price-low_price
                                slprice = (index_sl_position * abs(deltaValue))
                                #print("Last Candle %:", round(last_candle_percentage, 2))
                                print(f'option slprice : {slprice}')
                                trigger_price = price + slprice
                                print(f'trigger_price : {trigger_price}')
                                # Target order
                                order_utilObj.trigger_5ema_bracketOrder(symbol,price,slprice,orderid)
            else:
                    # runstatus =  main_obj.order_util.get_running_orders()
                    runstatus =  main_obj.order_util.get_orders_by_stratagy(f"5EMA")
                    running_orders=[]
                    if len(runstatus)>0:
                        open_orders_status = [
                                    o for o in runstatus if o.get("order_status") == "open" and o.get("strategy", "").startswith("5EMA_BANKNIFTY")
                                ]
                        print(len(open_orders_status))
                        if len(open_orders_status)==2:
                            opensymbol = open_orders_status[0]["symbol"]
                            atm_ltp = main_obj.safe_ltp(opensymbol)
                            # atm = client.quotes(symbol=opensymbol, exchange='NFO')
                            
                            if atm_ltp is None:
                                print("⚠️ Empty data in ATM LTP:", atm_ltp)
                                continue

                            # data = atm.get("data", {})
                            # if not data:
                            #     print("⚠️ Empty quote data:", atm)
                            #     continue
                            else:
                                if atm_ltp>0:
                                    print("📌 ATM STRIKE:", atm_ltp)
                                    print("***************bank*******************")   
                                    target_order = next(
                                                (
                                                    o for o in open_orders_status
                                                    if o.get("order_status") == "open"
                                                    and o.get("pricetype") == "LIMIT"
                                                    and o.get("symbol") == opensymbol
                                                ),
                                                None
                                            )
                                    sl_order = next(
                                                (
                                                    o for o in open_orders_status
                                                    if o.get("order_status") == "open"
                                                    and o.get("pricetype") == "SL-M"
                                                    and o.get("symbol") == opensymbol
                                                ),
                                                None
                                            )
                                    pricedifference_t_l = round(target_order["price"])-round(sl_order['trigger_price'])
                                    pricedifference = round(pricedifference_t_l/2)
                                    print('---------------pricedifference----------------')
                                    print(pricedifference)
                                    new_target_price = target_order["price"]+5
                                    new_sl_price = target_order["price"]-2
                                    new_target_price_escalation = target_order["price"]-1
                                    if(atm_ltp>=new_target_price_escalation ):
                                        print("ientered")

                                    if(sl_order["trigger_price"]<new_target_price_escalation and sl_order["trigger_price"]!=new_sl_price and sl_order["trigger_price"]<new_sl_price):
                                        if(atm_ltp>=new_target_price_escalation):
                                            print(atm_ltp,">=",new_target_price_escalation," and ",sl_order["trigger_price"],"<",new_target_price_escalation,"and",sl_order["trigger_price"],"<=",new_sl_price)
                                            response = client.modifyorder(
                                            order_id=target_order["orderid"],
                                            action="SELL",
                                            product="MIS",
                                            pricetype="LIMIT",
                                            price=new_target_price,
                                            quantity=target_order["quantity"],
                                            exchange="NFO",
                                            symbol=target_order['symbol'],
                                            strategy= f"5EMA_{main_obj.index}_{target_order['orderid']}"
                                            )
                                            print(target_order["strategy"])
                                            prefix = f"5EMA_{main_obj.index}"
                                            parent_order_id = target_order["strategy"].removeprefix(prefix).split("_")[1]                               
                                            main_obj.order_util.trail_sl_m_safe("5EMA",sl_order,new_sl_price,parent_order_id)
                                        else:
                                            parent_order_id = target_order["strategy"].removeprefix(prefix).split("_")[1]  
                                            strategy_buyed = [
                                    o for o in runstatus if o.get("order_status") == "open" and o.get("strategy", "").startswith(f"{strategy_prefix}_{self.parent.index}_{parent_order_id}_BUY")
                                ]
                                            buy_price = open_orders_status[0]["price"]
                                            print(atm_ltp,">=",buy_price)
                                            if atm_ltp>=buy_price:
                                                price_movement = atm_ltp-buy_price
                                                print (atm_ltp-buy_price)
                                                if(price_movement>=10):
                                                    print("do increase")
                                                    new_sl_price = atm_ltp-5
                                                    print(target_order["strategy"])
                                                    prefix = f"5EMA_{main_obj.index}"                                              

                                                    main_obj.order_util.trail_sl_m_safe("5EMA",sl_order,new_sl_price,parent_order_id)


    
                        elif len(open_orders_status)==1:
                            client.cancelorder(order_id=open_orders_status[0]['orderid'], strategy="5EMA_BANKNIFTY")
                        elif len(open_orders_status)>2:
                            print("need code for remove unwanted valid orders")
                    todays_orders_status = [
                                    o for o in runstatus if o.get("action") == "BUY" and o.get("strategy", "").startswith(f"5EMA_{main_obj.index}")
                                ]
                    # print(runstatus)
                    print(len(todays_orders_status))
                    if len(todays_orders_status)>=3:
                        if len(open_orders_status)==0:
                            print('Todays Limit Exceeded---',todays_orders_status)    
                            break
                    
                    runstatus =  main_obj.order_util.get_orders_by_stratagy("5EMA") # this for get open after place sl/Trigger 
                    # print(runstatus)
                    open_orders_status = [ 
                                    o for o in runstatus if o.get("order_status") == "open" and o.get("strategy", "").startswith(f"5EMA_{main_obj.index}")
                                ]
                    # print(open_orders_status)
                    # sys.exit()
                    if len(open_orders_status)==0:
                        print("-----------------No active orders present-----------Loop continue------------")
                        posflag=0
                    else:
                        posflag=1
                    # if len(runstatus)==0:
                    #      posflag=0
                        
        except Exception as e:
            print("Error in while:", e)    
    else:
        sys.stdout.write(f"\r ❌ -----Waiting to start ----- ❌ ⏳  {next(spinner)}")
        sys.stdout.flush()
    time.sleep(5)   # check every 5 seconds
    #break