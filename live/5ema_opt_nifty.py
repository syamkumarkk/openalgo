import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from openalgo import api, ta
from base.MainClass import MainClass
import pandas as pd
import time
from datetime import datetime, timedelta
# ✅ INSTANTIATE THE CLASS
main_obj = MainClass('NIFTY')
# ✅ ACCESS INSTANCE VARIABLES
client = main_obj.client
expiry_dateVal = main_obj.expiry_date
order_utilObj = main_obj.order_util
main_obj.debug = False # True to show array prints
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
# sys.exit

def check_signal(marketOnTheDay=0):

    # -----------------------------
    # Date setup (OpenAlgo standard)
    # -----------------------------
    if main_obj.is_after_IST(9,30):
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
   
    end_date   = (datetime.now() - timedelta(days=0)).strftime("%Y-%m-%d")
    interval   = "5m"
    print(f"start_date : {start_date}")
    print(f"end_date : {end_date}")
    print(f"\n🔄 Checking NIFTY ({datetime.now()})")

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
    ltp = main_obj.safe_ltp("NIFTY","NSE_INDEX")
    if ltp is not None:
        atm = round(ltp / 100) * 100
        print(f"\n📈 NIFTY LTP: {ltp} | ATM: {atm}")
    else:
        print("❌ LTP fetch failed:", ltp)
        return  {'posflag':0,'msg':"Quote fetch failed"}

    return identifyTheTrigger(atm,ltp,previous_ema,previous_low,previous_high,current_ema,current_low)
def identifyTheTrigger(atm,ltp,previous_ema,previous_low,previous_high,current_ema,current_low):
    try:
        # -----------------------------
        # SIGNAL LOGIC
        # -----------------------------
        print(f"previous_low > previous_ema")
        print(f"{previous_low} > {previous_ema}")
        if previous_low > previous_ema:
            print(f"current_low < previous_low")
            print(f"{current_low} < {previous_low}")
            if current_low < previous_low:
                print("✅") 
                growPersentatge = ((previous_high - current_low) / current_low) * 100
                #growVal = (previous_high - current_low)
                #toreachVal = previous_low-growVal
                index_sl_position = (previous_high - current_low)
                reachVal = current_low - index_sl_position
                #stoploss = toreachVal
                print(f"\n📢 SIGNAL → BUY PE (Price ABOVE EMA 5) {growPersentatge}% - {current_low} ")
                #print(f"\n📢 toreachVal  {toreachVal} ")
                triggerVal = triggerBuySeLLPE('ATM','BUY')
                return {'toreachVal':reachVal,'growPersentatge':growPersentatge,'index_sl_position':index_sl_position, 'BUY':triggerVal}
        else:
            print("\n❌ NO SIGNAL")
            return {'posflag':0,'msg':"NO SIGNAL"}

    except Exception as e:
        print("Error:", e)
def triggerBuySeLLPE(offset='ATM',BuySeLL='BUY'):
    try:
        # ------------------------------------------
        # Fetch NIFTY Spot (must print immediately)
        # ------------------------------------------
        # quote = client.quotes(symbol="NIFTY", exchange="NSE_INDEX")
        # print("NIFTY QUOTE:", quote)

        # ------------------------------------------
        # Place BANKNIFTY ATM Option Order - 09DEC25
        # ------------------------------------------
        response = client.optionsorder(
            strategy="5EMA_NIFTY_STRIKE",
            underlying="NIFTY",          # Underlying Index
            exchange="NFO",        # Index exchange
            expiry_date=expiry_date,       # Correct expiry
            offset=offset,                # Auto-select ATM strike
            option_type="PE",            # CE or PE
            action=BuySeLL,                # BUY or SELL
            quantity=65,                 # 1 Lot = 75
            pricetype="MARKET",          # MARKET or LIMIT
            product="MIS",              # NRML or MIS
            splitsize=0                  # 0 = no split
        )

        print("ORDER RESPONSE:", response)
        posflag = 1
        return {'posflag':1,'response':response,'msg':"success"}
    except Exception as e:
        print("Error:", e)
        return {'posflag':0,'msg':e}
def triggerPEBracketOrder(symbol,price,slprice,quantity=65):
    try:
        trigger_price = price + slprice
        print("🔁 Square-off at Target Price (LIMIT)")
        target_response = client.placeorder(
            strategy="5EMA_NIFTY_TARGET",
            symbol=symbol,
            exchange="NFO",
            action="SELL",
            price_type="LIMIT",
            price=trigger_price,
            product="MIS",
            quantity=quantity
        )
        print("TARGET RESPONSE: ", target_response)
        sl_price = price - slprice
        print("🔁 Square-off with Stop Loss (SL-M)")
        sl_response = client.placeorder(
                strategy="5EMA_NIFTY_SL",
                symbol=symbol,
                exchange="NFO",
                action="SELL",
                price_type="SL-M",
                trigger_price=sl_price,
                product="MIS",
                quantity=quantity
            )
        print("SL RESPONSE:", sl_response)
        return sl_response
    except Exception as e:
        print("Error:", e)
        return e

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
    if main_obj.is_after_IST(9, 15):
        try:
            
            if posflag==0:
                    runstatus = check_signal()                       
                    if ( runstatus==None or runstatus.get("posflag") != ""):
                        print("❌ -----Waiting for the candles----- ❌")
                        #break
                    if (runstatus!=None):
                        print(runstatus) 
                        if runstatus.get("BUY"):
                            posflag = runstatus['BUY']['posflag']
                            responseVal = runstatus['BUY']['response']
                            growPersentatge = runstatus['growPersentatge']
                            index_sl_position = runstatus['index_sl_position']
                            time.sleep(2)
                            # if and oreder has been placed then the postFlag is true
                            if posflag==1:
                                symbol = responseVal['symbol']
                                
                                orderid = responseVal['orderid']
                                order_response = client.orderstatus(
                                            order_id=orderid,
                                            strategy="NIFTY_Option_Intraday"
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
                                greeks = order_utilObj.get_option_greeks(symbol,"NIFTY")
                                if greeks['greeks']['delta']:
                                    deltaValue = greeks['greeks']['delta']
                                #slprice = high_price-low_price
                                slprice = (index_sl_position * abs(deltaValue))
                                #print("Last Candle %:", round(last_candle_percentage, 2))
                                print(f'option slprice : {slprice}')
                                trigger_price = price + slprice
                                print(f'trigger_price : {trigger_price}')
                                # Target order
                                triggerPEBracketOrder(symbol,price,slprice)                    
            else:   
                            
                    runstatus =  main_obj.order_util.get_orders_by_stratagy("5EMA")
                    running_orders=[]
                    if len(runstatus)>0:
                        open_orders_status = [
                                    o for o in runstatus if o.get("order_status") == "open" and o.get("strategy", "").startswith(f"5EMA_{main_obj.index}")
                                ]
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
                                    print("**********************************")   
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
                                    new_target_price = target_order["price"]+5
                                    new_sl_price = target_order["price"]-2
                                    new_target_price_escalation = target_order["price"]-1
                                    print(target_order)
                                    if(atm_ltp>=new_target_price_escalation and sl_order["trigger_price"]<new_target_price_escalation and sl_order["trigger_price"]!=new_sl_price and sl_order["trigger_price"]<new_sl_price):
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
                                        )                                    
                                        main_obj.order_util.trail_sl_m_safe("5EMA",sl_order,new_sl_price)

    
                        elif len(open_orders_status)==1:
                            client.cancelorder(order_id=open_orders_status[0]['orderid'], strategy=f"5EMA_{main_obj.index}")
                    
                    open_orders_status = [
                                    o for o in runstatus if o.get("order_status") == "open" and o.get("strategy", "").startswith(f"5EMA_{main_obj.index}")
                                ]
                    todays_orders_status = [
                                    o for o in runstatus if o.get("order_status") == "BUY" and o.get("strategy", "").startswith(f"5EMA_{main_obj.index}")
                                ]
                    if len(todays_orders_status)>=3:
                        if len(open_orders_status)==0:
                            print('Todays Limit Exceeded---',todays_orders_status)    
                            break
                    if len(open_orders_status)==0:
                        posflag=0
                    else:
                        posflag=1
                    # posflag =  main_obj.order_util.get_post_flag(runstatus,running_orders,"5EMA")

        except Exception as e:
            print("Error in while:", e)    
    else:
        print("❌ -----Waiting to start at 9:15----- ❌")
    time.sleep(5)   # check every 5 seconds
    #break