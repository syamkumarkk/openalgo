import sys
import os
import time
import itertools
import pandas as pd
from datetime import datetime, timedelta
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from openalgo import ta
from base.MainClass import MainClass

# =========================================================
# INIT
# =========================================================
main_obj = MainClass("NIFTY")
client = main_obj.client
main_obj.debug = False
# =========================================================
# SETTINGS
# =========================================================

INTERVAL = "5m"
TARGET_POINTS = 5
SL_BUFFER = 2
EMA_GAP = 0.3
QUANTITY = 20
TARGET_BUFFER = 4 # value to increase
TARGET_SL_BUFFER = 2 #value for sl near to target
UPPER_LIMIT = 3500
# =========================================================
# NIFTY50 BAJAJ-AUTO MARUTI  "EICHERMOT", "APOLLOHOSP","TRENT","INDIGO","TITAN","LT",
# =========================================================
NIFTY50 = ["ICICIBANK","HDFCBANK","SBIN","BHARTIARTL","RELIANCE","DRREDDY","ASIANPAINT","CIPLA","SHRIRAMFIN",
           "POWERGRID","TATASTEEL","AXISBANK","ETERNAL","ONGC","KOTAKBANK","TCS","INFY","BAJFINANCE","HINDALCO","COALINDIA","BEL","ADANIENT","ADANIPORTS","NTPC","ITC","GRASIM","JIOFIN","WIPRO","TATACONSUM"]

# =========================================================
# ACTIVE TRADES
# =========================================================
active_trades = {}
# =========================================================
# LOAD OPEN NSE POSITIONS
# =========================================================
def get_open_positions():
    try:
        positions = client.positionbook()
        open_symbols = {
            p["symbol"]
            for p in positions["data"]
            if (
                p.get("exchange") == "NSE"
                and int(p.get("quantity", 0)) != 0
            )
        }        
        return {
            "open_symbols":open_symbols,
                "total_pnl_today":positions["total_pnl_today"]
                }
    except Exception as e:
        print("get_open_positions", e)
        return set()
# =========================================================
# Cancel open SIGNAL
# =========================================================

def cancel_open_orders(symbol):
    try:
        orders = client.orderbook()
        order_data = orders.get("orders", [])
        if isinstance(order_data, list):            
            open_orders = [
                o for o in orders["data"]["orders"]
                if (
                    o.get("symbol") == symbol
                    and o.get("exchange") == "NSE"
                    and o.get("order_status", "").lower()
                    in ["open", "trigger pending"]
                )
            ]
            if open_orders:
                for order in open_orders:
                    orderid = order.get("orderid")
                    strategy = order.get("strategy")
                    if not orderid:
                        continue
                    print(f"❌ Cancelling : {symbol} | {orderid}")
                    response = client.cancelorder(order_id=orderid,strategy=strategy)
                    print(response)
                    time.sleep(0.3)
                    return symbol
        return None           
    except Exception as e:
        print(symbol, e)
        return None 
# =========================================================
# CHECK SIGNAL
# =========================================================

def check_signal(symbol):
    try:
        iscancelled = cancel_open_orders(symbol)
        if iscancelled!=symbol:
            start_date = (
                datetime.now() - timedelta(days=1)
            ).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            df = client.history(
                symbol=symbol,
                exchange="NSE",
                interval=INTERVAL,
                start_date=start_date,
                end_date=end_date
            )
            if not isinstance(df, pd.DataFrame):
                return None
            if df.empty:
                return None
            if len(df) < 6:
                return None
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            # =================================================
            # EMA 5
            # =================================================
            df["ema_5"] = ta.ema(df["close"], 5)
            # =================================================
            # VWAP
            # =================================================
            tp = (df["high"] + df["low"] + df["close"]) / 3
            df["vwap"] = ((tp * df["volume"]).cumsum()/ df["volume"].cumsum())
            previous = df.iloc[-3]
            completed = df.iloc[-2]
            current = df.iloc[-1]        
            completed_ema = completed["ema_5"]
            completed_low = completed["low"]
            completed_high = completed["high"]
            current_low = current["low"]
            current_close = current["close"]
            completed_volume = completed["volume"]
            previous_volume = previous["volume"]
            current_vwap = current["vwap"]
            
            # =================================================
            # SHORT LOGIC
            # =================================================
            if(current_low>UPPER_LIMIT):
                global NIFTY50
                if symbol in NIFTY50:
                    NIFTY50.remove(symbol)
                    print(f"{symbol} removed.")
                print(f"Amount on upper limit({UPPER_LIMIT}): ",symbol," : ",current_low)
                return None
            elif completed_low > completed_ema and completed_volume > previous_volume and current_low < completed_low:
                #print(f"🔻 symbol : {symbol}", datetime.now())  and current_close < current_vwap
                ema_gap = completed_low - completed_ema
                if ema_gap > EMA_GAP:
                    if current_low < completed_low:
                        print(
                            f"{'🔻 ':<14} | "
                            f"{'CPTD LOW':>10} | "
                            f"{'CPTD EMA':>10} | "
                            f"{'CUR LOW':>10} | "
                            f"{'CUR CLOSE':>10} | "
                            f"{'EMA GAP':>8} | "
                            f"{'PREV Volume':>10} | "
                            f"{'CPTD Volume':>10} | "
                            f"{'VWAP':>10} | "
                            f"{'TIME':>8}"
                        )
                        print("-" * 92)
                        print(
                            f"{symbol:<15} | "
                            f"{completed_low:>10.2f} | "
                            f"{completed_ema:>10.2f} | "
                            f"{current_low:>10.2f} | "
                            f"{current_close:>10.2f} | "
                            f"{ema_gap:>8.2f} | "
                            f"{previous_volume:>10.2f} | "
                            f"{completed_volume:>10.2f} | "
                            f"{current_vwap:>10.2f} | "
                            f"{datetime.now().strftime('%H:%M:%S'):>8}"
                        )                        
                        #print(f"🔻 SHORT SIGNAL Recived: {symbol}")
                        print("-" * 92)
                        return {
                            "symbol": symbol,
                            "entry": current_close,
                            "sl": completed_high + SL_BUFFER,
                            "target": current_close - TARGET_POINTS
                        }
        return None
    except Exception as e:
        print(symbol, e)
        return None

# =========================================================
# PLACE SHORT TRADE
# =========================================================
def place_trade(signal):
    try:
        symbol = signal["symbol"]
        entry = signal["entry"]
        sl_price = signal["sl"]
        target_price = signal["target"]
        strategy_name = f"5EMA_SHORT_{symbol}"
        print(
                            f"{'SHORTING ':<15} | "
                            f"{'entry':>10} | "
                            f"{'sl_price':>10} | "
                            f"{'target_price':>10} | "
                            f"{'strategy_name':>10} | "
                            f"{'TIME':>8}" ) 
        print("-" * 92)
        # print(
        #                     f"{symbol:<15} | "
        #                     f"{entry:>10.2f} | "
        #                     f"{sl_price:>10.2f} | "
        #                     f"{target_price:>10.2f} | "
        #                     f"{strategy_name:>10.2f} | "
        #                     f"{datetime.now().strftime('%H:%M:%S'):>8}"
        #                 )
        print(f"🚨 SHORTING : {symbol} entry:{entry} sl_price:{sl_price} target_price:{target_price} strategy_name:{strategy_name} Time {datetime.now()}")
        # =================================================
        # SELL STOCK
        # =================================================
        response = client.placeorder(
            strategy=strategy_name,
            symbol=symbol,
            action="SELL",
            exchange="NSE",
            price_type="MARKET",
            product="MIS",
            quantity=QUANTITY
        )
        print(response)
        if response.get("status") != "success":
            return
        orderid = response.get("orderid")
        time.sleep(1)
        # =================================================
        # SL BUY
        # =================================================
        if(sl_price>0):
            sl_response = client.placeorder(
                strategy=f"{strategy_name}_{orderid}_SL",
                symbol=symbol,
                action="BUY",
                exchange="NSE",
                price_type="SL-M",
                trigger_price=round(sl_price, 1),
                product="MIS",
                quantity=QUANTITY
            )
            print("SL :", sl_response)
        else:
            print("SL is empty:", sl_response)
        # =================================================
        # TARGET BUY
        # =================================================
        target_response = client.placeorder(
            strategy=f"{strategy_name}_{orderid}_TARGET",
            symbol=symbol,
            action="BUY",
            exchange="NSE",
            price_type="LIMIT",
            price=round(target_price, 1),
            product="MIS",
            quantity=QUANTITY
        )
        print("TARGET :", target_response)
        active_trades[symbol] = {
            "entry": entry,
            "sl": sl_price,
            "target": target_price,
            "orderid": orderid
        }
    except Exception as e:
        print("place_trade", e)

# =========================================================
# RESTORE ACTIVE TRADES
# =========================================================

def restore_active_trades():
    try:
        nifty50_set = set(NIFTY50)
        positions = client.positionbook()        
        active_trades = {}
        # open_positions = [
        #     p for p in positions["data"]
        #     if (
        #         p.get("exchange") == "NSE"
        #         and int(p.get("quantity", 0)) < 0
        #         and p.get("symbol") in nifty50_set
        #     )
        # ]
        position_dict = {
            p["symbol"]: p
            for p in positions["data"]
            if (
                p.get("exchange") == "NSE"
                and int(p.get("quantity", 0)) < 0
            )
        }
        orders = client.orderbook()
        open_positions = [
            p for p in orders["data"]["orders"]
            if (
                p.get("exchange") == "NSE"
                and p.get("action") == "SELL"
                and p.get("quantity") == QUANTITY
                and p.get("product") == "MIS"                
                and p.get("strategy").startswith("5EMA_SHORT")
                and p.get("order_status", "").lower()
                in ["complete"]
                and p.get("symbol") in position_dict    # <-- Only symbols with open positions
            )
        ]
        # and p.get("symbol") in nifty50_set
        order_data = [
                order_val for order_val in orders["data"]["orders"]
                if (
                    order_val.get("exchange") == "NSE"
                )
            ]    
        for p in open_positions:      
                    
            avgprice = float(p.get("average_price", 0))
            symbol= p.get("symbol")
            #orderid_buy = p.get("orderid")
            # =============================================
            # FIND SL ORDER
            # =============================================
            sl_order = next(
                (
                    o for o in order_data

                    if (
                        o.get("symbol") == symbol
                        and o.get("pricetype") == "SL-M"
                        and o.get("strategy").startswith("5EMA_SHORT")
                        and o.get("order_status", "").lower()
                        in ["open", "trigger pending"]
                    )
                ),
                None
            )           
            if(sl_order==None):                
                strategy_name = f"5EMA_SHORT_{symbol}"          
                sl_price = round(avgprice + SL_BUFFER, 1)
                # =================================================
                # SL BUY
                # =================================================
                if(sl_price>0):
                    sl_response = client.placeorder(
                        strategy=f"{strategy_name}_SL",
                        symbol=symbol,
                        action="BUY",
                        exchange="NSE",
                        price_type="SL-M",
                        trigger_price=sl_price,
                        product="MIS",
                        quantity=QUANTITY
                    )
                    print("SL :", sl_response)
                else:
                    print("SL is empty :", sl_price)
                sl_response_id = (sl_response['orderid'] if sl_response['orderid'] else None)
            else:
                sl_price = (
                    float(sl_order["trigger_price"])
                    if sl_order else None
                )                
                sl_response_id = (sl_order['orderid'] if sl_order['orderid'] else None)
            
            # =============================================
            # FIND TARGET ORDER
            # =============================================
            target_order = next(
                (
                    o for o in order_data

                    if (
                        o.get("symbol") == symbol
                        and o.get("pricetype") == "LIMIT"
                        and o.get("strategy").startswith("5EMA_SHORT")
                        and o.get("order_status", "").lower()
                        == "open"
                    )
                ),
                None
            )
            target_price = (
                    float(target_order["price"])
                    if target_order else None
                )
            
            strategy_name = f"5EMA_SHORT_{symbol}"  
            if(target_order==None):
                target_price = round(avgprice - TARGET_POINTS, 1)
                # =================================================
                # TARGET BUY
                # =================================================
                target_response = client.placeorder(
                    strategy=f"{strategy_name}_TARGET",
                    symbol=symbol,
                    action="BUY",
                    exchange="NSE",
                    price_type="LIMIT",
                    price=target_price,
                    product="MIS",
                    quantity=QUANTITY
                )
                target_response_id = (target_response['orderid'] if target_response['orderid'] else None)
            else:
                 target_response_id = (target_order['orderid'] if target_order['orderid'] else None)
            
            target_stratagy_name = f"{strategy_name}_TARGET"
            sl_stratagy_name = f"{strategy_name}_SL"
            active_trades[symbol] = {
                "symbol": symbol,
                "qty": int(p["quantity"]),
                "entry": avgprice,
                "sl_id": sl_response_id,
                "sl": sl_price,
                "sl_stratagy_name": sl_stratagy_name,
                "target_id": target_response_id,
                "target": target_price,
                "target_stratagy_name": target_stratagy_name,
            }
            
        #print("✅ RESTORED")
        #print(active_trades)
        return active_trades
    except Exception as e:
        print("restore_active_trades", e)
        #return NULL

# =========================================================
# MANAGE TRADES
# =========================================================
def manage_trades():
    #print ("\n")
    print ("Manage fnc()")
    active_trades = restore_active_trades()
    remove_symbols = []
    if active_trades == "None":
        print("active_trades is empty")
    else:
        for symbol, trade in active_trades.items():
            try:
                ltp = main_obj.safe_ltp(symbol, "NSE")
                if ltp is None:
                    continue
                #print(f"{symbol} LTP : {ltp} target: {trade["target"]} sl: {trade["sl"]}")
                # =============================================
                # TARGET HIT
                # =============================================
                if (
                    trade.get("target") is not None
                    and
                    ltp <= trade["target"]
                ):
                    print(f"🎯 Mange TARGET HIT : {symbol} LTP : {ltp} target: {trade["target"]} sl: {trade["sl"]} ", datetime.now())
                    # ==========================================
                    # CANCEL OLD
                    # ==========================================            
                    client.cancelorder(order_id=trade["sl_id"])
                    time.sleep(0.5)   
                    client.cancelorder(order_id=trade["target_id"])
                    time.sleep(0.5)            
                    # ==========================================
                    # PLACE NEW Market
                    # ==========================================      
                    client.placeorder(            
                        strategy="EMERGENCY_EXIT_5EMA_SHORT",            
                        symbol=symbol,            
                        action="BUY",            
                        exchange="NSE",            
                        price_type="MARKET",            
                        product="MIS",            
                        quantity=QUANTITY
                    )
                # =============================================
                # SL HIT
                # =============================================
                elif (
                    trade.get("sl") is not None
                    and
                    ltp >= trade["sl"]
                ):
                    print(f"🛑 SL HIT : {symbol} LTP : {ltp} target: {trade["target"]} sl: {trade["sl"]} ", datetime.now())
                    #print(f"LTP : {ltp} > SL : {trigger_price}")            
                    # ==========================================
                    # CANCEL OLD
                    # ==========================================            
                    client.cancelorder(order_id=trade["sl_id"])
                    time.sleep(0.5)   
                    client.cancelorder(order_id=trade["target_id"])
                    time.sleep(0.5)            
                    # ==========================================
                    # PLACE NEW Market
                    # ==========================================      
                    client.placeorder(            
                        strategy="EMERGENCY_EXIT_5EMA_SHORT",            
                        symbol=symbol,            
                        action="BUY",            
                        exchange="NSE",            
                        price_type="MARKET",            
                        product="MIS",            
                        quantity=QUANTITY
                    )
            except Exception as e:
                print("manage_trades", symbol, e)

# =========================================================
# TRAIL TRADES
# =========================================================
def trail_trades():
    #print ("\n")
    print ("Trail fnc()")
    active_trades = restore_active_trades()
    #print(active_trades)
    remove_symbols = []
    for symbol, trade in active_trades.items():
        try:
            ltp = main_obj.safe_ltp(symbol, "NSE")
            if ltp is None:
                continue
            #print(f"{symbol} LTP : {ltp} target: {trade["target"]} sl: {trade["sl"]}")
            # =============================================
            # TARGET REACHING
            # =============================================
            if (trade.get("target") is not None):
                new_sl_val = trade["target"]+TARGET_SL_BUFFER
                if (ltp<new_sl_val):
                    new_safety_sl_val = new_sl_val+1
                    new_target_val = trade["target"]-TARGET_BUFFER
                    print(f"🎯 Trail TARGET HIT : {symbol} LTP : {ltp} target: {trade["target"]} sl: {trade["sl"]} ", datetime.now())
                    # ==========================================
                    # CANCEL OLD
                    # ==========================================            
                    client.cancelorder(order_id=trade["sl_id"])
                    time.sleep(0.5)   
                    client.modifyorder(
                        order_id=trade["target_id"],
                        action="SELL",
                        product="MIS",
                        pricetype="LIMIT",
                        price=new_target_val,
                        quantity=QUANTITY,
                        symbol=symbol,
                        exchange="NSE",
                        )
                    time.sleep(0.3)                    
                    # ==========================================
                    # PLACE NEW Market
                    # ==========================================      
                    sl_response = client.placeorder(            
                        strategy=trade["sl_stratagy_name"],          
                        symbol=symbol,            
                        action="BUY",                        
                        exchange="NSE",            
                        price_type="SL-M",
                        trigger_price=new_safety_sl_val,
                        product="MIS",            
                        quantity=QUANTITY
                    )
                    print(f"trailed SL ",sl_response)
                   
                    time.sleep(0.5)  
        except Exception as e:
            print("manage_trades", symbol, e)
            
# =========================================================
# INITIAL RESTORE
# =========================================================
active_trades = restore_active_trades()
# =========================================================
# MAIN LOOP
# =========================================================
print("LIST POSITIONS :", NIFTY50)
while True:
   
    try:
        # =================================================
        # MARKET CLOSE
        # =================================================
        if main_obj.is_after_IST(15, 15):
            print("🛑 MARKET CLOSED")
            break
        # =================================================
        # MARKET START
        # =================================================
        if main_obj.is_after_IST(9, 20):
            # =============================================
            # LOAD OPEN NSE POSITIONS
            # =============================================
            open_symbol_array = get_open_positions()
            total_pnl_today = open_symbol_array['total_pnl_today']
            if abs(total_pnl_today)>1100 and total_pnl_today<0:
                print("Your lose become ",total_pnl_today," stopped exicutions! ");
                print("🛑 CLOSED exicutions")
                break
            else:
                open_symbols_fromlist = open_symbol_array['open_symbols']
                open_symbols = set(NIFTY50) & open_symbols_fromlist 
                
                print("="*100)
                print("🔄 SCANNING NIFTY50 :", datetime.now())                
                if open_symbols:
                    print("OPEN POSITIONS :", open_symbols)
                print("="*100)
                # =============================================
                # SCAN STOCKS
                # ============================================
                for stock in NIFTY50:
                    # -----------------------------------------
                    # SKIP IF ALREADY ACTIVE
                    # ----------------------------------------
                    if stock in open_symbols:
                        #print(f"⏭ ACTIVE : {stock}")
                        continue
                    # ----------------------------------------
                    # FIND SIGNAL
                    # -----------------------------------------
                    #print(f"Signal processing : {stock}")
                    signal = check_signal(stock)
                    if signal:
                        place_trade(signal)
                    #else:
                    #    print("No signals on : ",stock)
                    time.sleep(0.2)
                # =============================================
                # MANAGE ACTIVE TRADES
                # =============================================                
                trail_trades()
                time.sleep(0.2)
                manage_trades()
        else:
            sys.stdout.write(                f"\r⏳ Waiting Market Open {next(spinner)}"            )
            sys.stdout.flush()
        # =================================================
        # WAIT
        # =================================================
        time.sleep(30)
    except Exception as e:
        print("MAIN LOOP ERROR :", e)
        time.sleep(5)