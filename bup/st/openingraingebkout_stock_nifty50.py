import sys,os,time
import pandas as pd
from datetime import datetime, timedelta
ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
from base.MainClass import MainClass
# ==========================================
# INIT
# ==========================================
main_obj = MainClass("NIFTY")
client = main_obj.client
main_obj.debug = False
# ==========================================
# SETTINGS
# ==========================================
INTERVAL = "5m"
OPENING_RANGE_MINUTES = 15
TARGET_POINTS = 10
SL_BUFFER = 2
QUANTITY = 15
UPPER_LIMIT = 3000
# ==========================================
# STOCKS "MARUTI","APOLLOHOSP","INDIGO","EICHERMOT","TITAN","LT","ADANIENT","GRASIM",
# ==========================================
NIFTY50 = ["ICICIBANK","HDFCBANK","SBIN","BHARTIARTL","RELIANCE","DRREDDY","ASIANPAINT","CIPLA","SHRIRAMFIN",
           "POWERGRID","TATASTEEL","AXISBANK","ETERNAL","ONGC","KOTAKBANK","TCS","INFY","BAJFINANCE","HINDALCO","COALINDIA","BEL","ADANIPORTS","NTPC","ITC","JIOFIN","WIPRO","TATACONSUM", "TRENT","HINDUNILVR","NESTLEIND","SUNPHARMA","TECHM","JSWSTEEL","HCLTECH","TMPV","SBILIFE","BAJAJFINSV","HDFCLIFE"]
# NIFTY50 = ["TRENT"]
print(NIFTY50)
active_trades = {}
traded_today = set()
last_processed_candle = {}
opening_ranges = {}

# ==========================================
# CHECK SIGNAL
# ==========================================
def check_signal(symbol):
    try:
        if symbol not in opening_ranges:
            return None
        if(opening_ranges[symbol]["low"]>UPPER_LIMIT):
            global NIFTY50
            if symbol in NIFTY50:
                NIFTY50.remove(symbol)
                print(f"{symbol} removed.")
            print(f"Amount on upper limit({UPPER_LIMIT}): ",symbol," : ",opening_ranges[symbol]["low"])
            return None
        start_date = datetime.now().strftime("%Y-%m-%d")
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
        if len(df) < 2:
            return None
        current_candle_time = df.index[-1]
        # Skip if this candle was already processed
        if last_processed_candle.get(symbol) == current_candle_time:
            return None        
        # Mark this candle as processed
        last_processed_candle[symbol] = current_candle_time
        # ==========================================
        # VWAP
        # ==========================================
        df["tp"] = (df["high"] + df["low"] + df["close"]) / 3
        df["vwap"] = (df["tp"] * df["volume"]).cumsum() / df["volume"].cumsum()
        current_vwap = df.iloc[-1]["vwap"]
        # ==========================================
        # AVERAGE VOLUME
        # ==========================================
        # avg_volume = df["volume"].iloc[-11:-1].mean()
        # previous 5 candles average volume
        timeVal = datetime.now().strftime('%H:%M:%S')        
        if timeVal <= "09:40":
            print(f"timeVal : ",timeVal)
            avg_volume = df["volume"].iloc[:-2].mean()
        else:
            avg_volume = df["volume"].iloc[-7:-2].mean()
        # avg_volume = df["volume"].iloc[-6:-1].mean()        
        # previous candle volume
        previous_volume = df["volume"].iloc[-2]        
        rvol = previous_volume / avg_volume
        # ==========================================
        # ATR (14)
        # ==========================================        
        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift()).abs()
        low_close = (df["low"] - df["close"].shift()).abs()        
        true_range = pd.concat(
            [high_low, high_close, low_close],
            axis=1
        ).max(axis=1)        
        df["atr"] = true_range.rolling(window=14).mean()
        atr = df.iloc[-1]["atr"]
        
        current = df.iloc[-1]
        current_volume = current["volume"]
        current_close = current["close"]
        current_high = current["high"]
        current_low = current["low"]
        opening_high = opening_ranges[symbol]["high"]
        opening_low = opening_ranges[symbol]["low"]
        # print("-" * 92)
        # print(
        #     f"symbol :"
        #     f"{'current_close':>10} | "
        #     f"{'current_vwap':>10} | "
        #     f"{'current_volume':>10} | "
        #     f"{'TIME':>8}"
        # )
        # print("-" * 92)
        print(
            f"{symbol} | "
            f"Close={current_close:.2f} | "
            f"VWAP={current_vwap:.2f} | "
            f"Vol={current_volume:.0f} | "
            f"P Vol={previous_volume:.0f} | "            
            f"AvgVol={avg_volume:.0f} | "
            f"rvol={rvol:.0f} | "            
            f"{datetime.now().strftime('%H:%M:%S')}"
        )
        print("-" * 92)
        # ==========================================
        # BUY BREAKOUT
        # ==========================================
        if current_close > opening_high and current_close > current_vwap and rvol > 1.5:
            print(
                f"🚀 ORB BUY : {symbol}"            )
            entry_price = current_close
            max_sl_val = max(opening_low, current_low)  
            stop_loss = max_sl_val
            # - SL_BUFFER            
            risk = abs(entry_price - stop_loss)            
            atr_target = atr * 1.5
            rr_target = risk * 2            
            #target_points = min(atr_target, rr_target)            
            #target = entry_price + target_points              
            if risk > atr:
                print(f"{symbol} skipped - Risk {risk:.2f} > ATR {atr:.2f}")
                return None            
            target = entry_price + rr_target            
            # Balance trade value minimum target and SL
            if rr_target<1:
                print("placed static target")
                target = entry_price + 2
            if max_sl_val<1:
                print("placed static sl")
                stop_loss = entry_price - 1
            
            print(
                f"{symbol} | "
                f"Opening_high ={opening_ranges[symbol]["high"]:.2f} | "
                f"Opening_low ={opening_ranges[symbol]["low"]:.2f} | "
                f"Entry={entry_price:.2f} | "
                f"SL={stop_loss:.2f} | "
                f"Risk abs(entry_price - opening_low) ={risk:.2f} | "
                f"ATR ATR (14)={atr:.2f} | "
                f"ATR Target atr * 1.5={atr_target:.2f} | "
                f"RR Target risk * 2 ={rr_target:.2f} | "
                f"Final Target={target:.2f}"
            )
            return {
                "symbol": symbol,
                "side": "BUY",
                "entry": entry_price,
                "sl": stop_loss,
                "target": round(target, 2)
            }
            # return {
            #     "symbol": symbol,
            #     "side": "BUY",
            #     "entry": current_close,
            #     "sl": opening_low - SL_BUFFER,
            #     "target": current_close + TARGET_POINTS            }

        # ==========================================
        # SELL BREAKDOWN
        # ==========================================
        if current_close < opening_low and current_close < current_vwap and rvol > 1.5:
            print(
                f"🔻 ORB SELL : {symbol}"            )
            entry_price = current_close
            max_sl_val = max(opening_low, current_low)  
            stop_loss = max_sl_val
            # + SL_BUFFER            
            risk = abs(stop_loss - entry_price)            
            atr_target = atr * 1.5
            rr_target = risk * 2            
            # target_points = max(atr_target, rr_target)            
            # target = entry_price - target_points        
            if risk > atr:
                print(f"{symbol} skipped - Risk {risk:.2f} > ATR {atr:.2f}")
                return None            
            target = entry_price - rr_target
            # Balance trade value minimum target and SL
            if rr_target<1:
                print("placed static target")
                target = entry_price - 2
            if max_sl_val<1:
                print("placed static sl")
                stop_loss = entry_price + 1
            
            print(
                f"{symbol} | "
                f"Entry={entry_price:.2f} | "
                f"SL={stop_loss:.2f} | "
                f"Risk abs(stop_loss - entry_price)    ={risk:.2f} | "
                f"ATR ATR (14)={atr:.2f} | "
                f"ATR Target atr * 1.5={atr_target:.2f} | "
                f"RR Target risk * 2 ={rr_target:.2f} | "
                f"Final Target={target:.2f}"
            )
            return {
                "symbol": symbol,
                "side": "SELL",
                "entry": entry_price,
                "sl": stop_loss,
                "target": round(target, 2)
            }
        return None

    except Exception as e:

        print(symbol, e)

        return None

# ==========================================
# PLACE TRADE
# ==========================================
def place_trade(signal):
    try:
        symbol = signal["symbol"]
        side = signal["side"]
        entry = signal["entry"]
        sl = signal["sl"]
        target = signal["target"]
        strategy = f"ORB_{side}_{symbol}"
        print(
            f"\n"
            f"{'=' * 70}\n"
            f"🚀 NEW ORB TRADE {datetime.now().strftime('%H:%M:%S')}\n"
            f"{'-' * 70}\n"
            f"📌 SYMBOL : {symbol}\n"
            f"📌 SIDE   : {side}\n"
            f"📌 ENTRY  : {entry}\n"
            f"📌 SL     : {sl}\n"
            f"📌 TARGET : {target}\n"
            f"{'=' * 70}\n"
        )
        # ==========================================
        # MAIN ORDER
        # ==========================================
        response = client.placeorder(
            strategy=strategy,
            symbol=symbol,
            action=side,
            exchange="NSE",
            price_type="MARKET",
            product="MIS",
            quantity=QUANTITY
        )        
        if response.get("status") != "success":
            return
        global traded_today
        #global active_trades
        traded_today.add(symbol)
        # print(response)
        # ==========================================
        # SL ORDER
        # ==========================================
        sl_action = "SELL" if side == "BUY" else "BUY"
        client.placeorder(
            strategy=f"{strategy}_{response.get("orderid")}_SL",
            symbol=symbol,
            action=sl_action,
            exchange="NSE",
            price_type="SL-M",
            trigger_price=round(sl, 1),
            product="MIS",
            quantity=QUANTITY
        )
        # ==========================================
        # TARGET ORDER
        # ==========================================
        client.placeorder(
            strategy=f"{strategy}_{response.get("orderid")}_TARGET",
            symbol=symbol,
            action=sl_action,
            exchange="NSE",
            price_type="LIMIT",
            price=round(target, 1),
            product="MIS",
            quantity=QUANTITY
        )
        #active_trades[symbol] = signal
    except Exception as e:
        print("place_trade", e)

# ==========================================
# RESTORE TRADES
# ==========================================
def restore_active_trades():
    try:
        nifty50_set = set(NIFTY50)
        positions = client.positionbook()
        if not isinstance(positions, dict):
            return
        position_dict = {
            p["symbol"]: p
            for p in positions["data"]
            if (
                p.get("exchange") == "NSE"
                and int(p.get("quantity", 0)) != 0
                and p.get("symbol") in nifty50_set
            )
        }
        print(f"IN open positions : ",position_dict)
        orders = client.orderbook()
        order_data = [
            p for p in orders["data"]["orders"]
            if (
                p.get("exchange") == "NSE"
                and int(p.get("quantity", 0)) != 0
                and p.get("strategy", "").startswith("ORB")
                and p.get("order_status", "").lower() in ["complete"]
                and p.get("symbol") in position_dict    # <-- Only symbols with open positions
            )
        ]
        complete_order_data = [
            p for p in orders["data"]["orders"]
            if (
                p.get("exchange") == "NSE"
                and int(p.get("quantity", 0)) != 0
                and p.get("strategy", "").startswith("ORB")                
                and p.get("pricetype", "") in ["MARKET"]
                and p.get("order_status", "").lower() in ["complete"]
            )
        ]
        for co in complete_order_data:
            symbol = co.get("symbol")
            global traded_today
            if symbol not in traded_today:
                traded_today.add(symbol)   
        # print(order_data)
        for p in order_data:
            symbol = p.get("symbol")
            global active_trades            
            # Latest order already processed for this symbol
            if symbol in active_trades:
                continue
            qty = int(p.get("quantity", 0))
            
            active_trades[symbol] = {
                "symbol": symbol,
                "quantity": QUANTITY,
                "order_val":p
            }
            
        print(f"✅ ACTIVE RESTORED traded_today : ",traded_today)
    except Exception as e:
        print("restore", e)

# =========================================================
# MANAGE TRADES
# =========================================================
def manage_trades(stock,ltp=None):   
    print(f"Managing starts: {stock}  {datetime.now().strftime('%H:%M:%S')}")
    global active_trades
    if active_trades == "None":
        print("active_trades is empty")
    else:
        symbol = stock
        trade = active_trades.get(symbol)
        if trade is None:
            print(f"{symbol} is not an active trade")
        else:
            # return
            # for symbol, trade in active_trades.items():
            try:
                # print(trade)
                # ltp = main_obj.safe_ltp(symbol, "NSE")
                if ltp is None:
                   print(f"{symbol} LTP is empty {datetime.now().strftime('%H:%M:%S')}")
                    # print(trade)
                    # if stock==symbol:
                else:    
                    print(f"{symbol} LTP : {ltp} {datetime.now().strftime('%H:%M:%S')}")
                    position = trade.get("order_val")
                    orders = client.orderbook()
                    order_data = [
                        p for p in orders["data"]["orders"]
                        if (
                            p.get("exchange") == "NSE"
                            and p.get("symbol")==symbol
                            and p.get("order_status", "").lower() in ["open", "trigger pending"]
                            and  position["orderid"] in p.get("strategy", "")                            
                        )
                    ]                    
                    print(f"Length: {len(order_data)}  {datetime.now().strftime('%H:%M:%S')}")
                    print(trade.get("order_val"))
                    limit_order = None
                    sl_order = None
                    for order in order_data:
                        if order['pricetype'] =='LIMIT':
                            limit_order =order
                        if order['pricetype'] =='SL-M':
                            sl_order=order
                    print(f" limit_order : ",limit_order)     
                    print(f" sl_order : ",sl_order)    
                    
                    # if len(order_data)==0:
                    #     # print("Active trave with zero order data")
                    #     # print(active_trades)
                    #     # ==========================================
                    #     # SL ORDER
                    #     # ==========================================
                    #     if position["action"] == "BUY":
                    #         sl_action = "SELL" 
                    #         new_target_val = ltp+2
                    #         new_safety_sl_val = ltp-1
                    #     else:
                    #         sl_action = "BUY" 
                    #         new_target_val = ltp-2
                    #         new_safety_sl_val = ltp+1
                    #     client.placeorder(
                    #         strategy=f"{position["strategy"]}_{position["orderid"]}_SL",
                    #         symbol=symbol,
                    #         action=sl_action,
                    #         exchange="NSE",
                    #         price_type="SL-M",
                    #         trigger_price=round(new_safety_sl_val, 1),
                    #         product="MIS",
                    #         quantity=QUANTITY
                    #     )
                    #     # ==========================================
                    #     # TARGET ORDER
                    #     # ==========================================
                    #     client.placeorder(
                    #         strategy=f"{position["strategy"]}_{position["orderid"]}_TARGET",
                    #         symbol=symbol,
                    #         action=sl_action,
                    #         exchange="NSE",
                    #         price_type="LIMIT",
                    #         price=round(new_target_val, 1),
                    #         product="MIS",
                    #         quantity=QUANTITY
                    #     )
                    if len(order_data)==1:
                        # ==========================================
                        # SL ORDER
                        # ==========================================
                        if position["action"] == "BUY":
                            action = "SELL" 
                        else:
                            action = "BUY" 
                        for order in order_data:
                                print(
                                    f" only 1 order to runCancelling {order['strategy']} | "
                                    f"Order ID: {order['orderid']}"
                                )
                            
                                client.cancelorder(order_id=order["orderid"])
                                time.sleep(0.5)    
                        client.placeorder(            
                                    strategy="EMERGENCY_EXIT",            
                                    symbol=symbol,            
                                    action=action,            
                                    exchange="NSE",            
                                    price_type="MARKET",            
                                    product="MIS",            
                                    quantity=QUANTITY
                                )
                    
                    if len(order_data)>=2:
                        print(order_data)
                        if position["action"] == "SELL":
                            action= "BUY"
                            print(sl_order['trigger_price'])
                            # =============================================
                            # TARGET HIT
                            # =============================================
                            if (ltp <= limit_order['price']):
                                print(f"🎯 TARGET HIT : {symbol} LTP: {ltp} >= limit_order: {limit_order['price']}   {datetime.now().strftime('%H:%M:%S')}")
                                # ==========================================
                                # CANCEL OLD
                                # ==========================================            
                                for order in order_data:
                                        print(
                                            f"Cancelling {order['strategy']} | "
                                            f"Order ID: {order['orderid']}"
                                        )
                                    
                                        client.cancelorder(order_id=order["orderid"])
                                        time.sleep(0.5)             
                                # ==========================================
                                # PLACE NEW Market
                                # ==========================================
     
                                client.placeorder(            
                                    strategy="EMERGENCY_EXIT",            
                                    symbol=symbol,            
                                    action=action,            
                                    exchange="NSE",            
                                    price_type="MARKET",            
                                    product="MIS",            
                                    quantity=QUANTITY
                                )
                            # =============================================
                            # SL HIT
                            # =============================================
                            elif (ltp >= sl_order['trigger_price']):
                                print(f"🛑 SL HIT : {symbol} LTP: {ltp} >= sl_order: {sl_order['price']}    {datetime.now().strftime('%H:%M:%S')}")
                                #print(f"LTP : {ltp} > SL : {trigger_price}")            
                                # ==========================================
                                # CANCEL OLD
                                # ==========================================      
                                for order in order_data:
                                    print(
                                        f"Cancelling {order['strategy']} | "
                                        f"Order ID: {order['orderid']}"
                                    )
                                
                                    client.cancelorder(order_id=order["orderid"])
                                    time.sleep(0.5)         
                                # ==========================================
                                # PLACE NEW Market
                                # ==========================================
                                client.placeorder(            
                                    strategy="EMERGENCY_EXIT",            
                                    symbol=symbol,            
                                    action=action,            
                                    exchange="NSE",            
                                    price_type="MARKET",            
                                    product="MIS",            
                                    quantity=QUANTITY
                                )
                        if position["action"] == "BUY":
                            action= "SELL"
                            # =============================================
                            # TARGET HIT
                            # =============================================
                            if (ltp >= limit_order['price']):
                                print(f"🎯 TARGET HIT : {symbol} LTP: {ltp} >= limit_order: {limit_order['price']}   {datetime.now().strftime('%H:%M:%S')}")
                                # ==========================================
                                # CANCEL OLD
                                # ==========================================            
                                for order in order_data:
                                        print(
                                            f"Cancelling {order['strategy']} | "
                                            f"Order ID: {order['orderid']}"
                                        )
                                    
                                        client.cancelorder(order_id=order["orderid"])
                                        time.sleep(0.5)             
                                # ==========================================
                                # PLACE NEW Market
                                # ==========================================
     
                                client.placeorder(            
                                    strategy="EMERGENCY_EXIT",            
                                    symbol=symbol,            
                                    action=action,            
                                    exchange="NSE",            
                                    price_type="MARKET",            
                                    product="MIS",            
                                    quantity=QUANTITY
                                )
                            # =============================================
                            # SL HIT
                            # =============================================
                            elif (ltp <= sl_order['trigger_price']):
                                print(f"🛑 SL HIT : {symbol} LTP: {ltp} >= sl_order: {sl_order['price']}    {datetime.now().strftime('%H:%M:%S')}")
                                #print(f"LTP : {ltp} > SL : {trigger_price}")            
                                # ==========================================
                                # CANCEL OLD
                                # ==========================================      
                                for order in order_data:
                                    print(
                                        f"Cancelling {order['strategy']} | "
                                        f"Order ID: {order['orderid']}"
                                    )
                                
                                    client.cancelorder(order_id=order["orderid"])
                                    time.sleep(0.5)         
                                # ==========================================
                                # PLACE NEW Market
                                # ==========================================
                                client.placeorder(            
                                    strategy="EMERGENCY_EXIT",            
                                    symbol=symbol,            
                                    action=action,            
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
def trail_trades(symbol="",ltp=None):
    print(f"Trailing starts: {symbol}  {datetime.now().strftime('%H:%M:%S')}")
    global active_trades
    trade = active_trades.get(symbol)
    remove_symbols = []
    update = 0
    if symbol == "":
        print("symbol is empty")
        return update
    else:
            try:                
                # ltp = main_obj.safe_ltp(symbol, "NSE")
                if ltp is None:
                    print(f"{symbol} LTP is empty {datetime.now().strftime('%H:%M:%S')}")
                    return update
                else:
                    print("trade : ")
                    print(trade)
                    position = trade.get("order_val")
                    orders = client.orderbook()
                    order_data = [
                        p for p in orders["data"]["orders"]
                        if (
                            p.get("exchange") == "NSE"
                            and p.get("symbol")==symbol
                            and p.get("order_status", "").lower() in ["open", "trigger pending"]
                            and  position["orderid"] in p.get("strategy", "")                            
                        )
                    ]                    
                    print(f"Length: {len(order_data)}  {datetime.now().strftime('%H:%M:%S')}")                
                    
                    if len(order_data)>=2:
                        # print(order_data)
                        #return true
                        # print(position)
                        for order in order_data:
                            if order['pricetype'] =='LIMIT':
                                limit_order =order
                            if order['pricetype'] =='SL-M':
                                sl_order=order                        
                        print(limit_order)
                        print(sl_order)
                        cancel_order_id = sl_order['orderid']
                        modifyorder_id = limit_order['orderid']
                        placeorder_name=sl_order["strategy"]
                        if position["action"] == "BUY":
                            print("  Increase trailing")
                            action="BUY"                            
                            if ltp > limit_order['price']-1:
                                update =1
                                new_target_val = ltp+2
                                new_safety_sl_val = ltp-1
                        else:
                            print(" V Decrease trailing")                            
                            action="SELL"
                            if ltp < limit_order['price']+1:
                                update =1
                                new_target_val =ltp-2
                                new_safety_sl_val = ltp+1
                    # =============================================
                    # TARGET REACHING
                    # =============================================
                    if (update==1):
                            print(f"🎯 TARGET REACHING : {symbol} {datetime.now().strftime('%H:%M:%S')}")
                            # ==========================================
                            # CANCEL OLD
                            # ==========================================            
                            client.cancelorder(order_id=cancel_order_id)
                            time.sleep(0.5)   
                            client.modifyorder(
                                order_id=modifyorder_id,
                                action=action,
                                product="MIS",
                                pricetype="LIMIT",
                                price=new_target_val,
                                quantity=QUANTITY,
                                symbol=symbol,
                                exchange="NSE",
                                )
                            time.sleep(0.5)                    
                            # ==========================================
                            # PLACE NEW Market
                            # ==========================================      
                            client.placeorder(            
                                strategy=placeorder_name,          
                                symbol=symbol,            
                                action=action,
                                exchange="NSE",            
                                price_type="SL-M",
                                trigger_price=new_safety_sl_val,
                                product="MIS",            
                                quantity=QUANTITY
                            )
                            time.sleep(0.5)  
                return update   
            except Exception as e:
                print("trail_trades", symbol, e)
# ==========================================
# MAIN LOOP
# ==========================================

while True:
    try:
        # ==========================================
        # MARKET CLOSE
        # ==========================================
        if main_obj.is_after_IST(15, 15):
            print(
                f"🛑 MARKET CLOSED"
            )            
            break
        # ==========================================
        # WAIT MARKET OPEN
        # ==========================================
        if not main_obj.is_after_IST(9, 30):
            sys.stdout.write(
                f"\r"
                f"⏳ Waiting Market Open "
                f"{next(spinner)}"
            )
            sys.stdout.flush()
            time.sleep(1)
            continue

        # ==========================================
        # CALCULATE OPENING RANGE
        # ==========================================
        if not opening_ranges:
            # print("-" * 70)
            # print(
            #     f"📊 OPENING RANGE :"
            #     f"{'HIGH LOW':>10} | "
            #     f"{'LOW EMA':>10} | "
            #     f"{'TIME':>8}"
            # )
            # print("-" * 70)
            opening_ranges = main_obj.orb_util.calculate_opening_range(NIFTY50,INTERVAL)         
        # ==========================================
        # RESTORE
        # ==========================================
        restore_active_trades()
        # ==========================================
        # SCAN
        # ==========================================
        print(
            f"\n"
            f"{'=' * 70}\n"
            f"🔍 SCANNING ORB STOCKS {datetime.now().strftime('%H:%M:%S')}\n"
            f"{'=' * 70}"
        )
        print(active_trades)
        for stock in NIFTY50:
            #print(traded_today)
            if len(active_trades)>0:
                if stock in active_trades:
                    print(
                        f"🔍 ACTIVE STOCKS {stock} {datetime.now().strftime('%H:%M:%S')}\n"
                        f"{'=' * 70}"
                    )
                    ltp = main_obj.safe_ltp(stock, "NSE")
                    if ltp is None:
                        print(f"{symbol} LTP is empty {datetime.now().strftime('%H:%M:%S')}")
                    else:
                        trail_status = trail_trades(stock,ltp)
                        time.sleep(0.5)
                        print(f"{'=' * 70}")
                        if trail_status==0:
                            manage_trades(stock,ltp)
                            print(f"{'=' * 70}")
                    continue
            if stock in traded_today:                
                print(f"{stock} already traded today.")
                continue
            signal = check_signal(stock)
            if signal:
                place_trade(signal)
                restore_active_trades()
            time.sleep(0.5)
        time.sleep(20)
    except Exception as e:
        print("MAIN LOOP", e)
        time.sleep(5)