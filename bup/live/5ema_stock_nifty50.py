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
TARGET_POINTS = 10
SL_BUFFER = 2
EMA_GAP = 0.5
QUANTITY = 1

# =========================================================
# NIFTY50
# =========================================================
NIFTY50 = [
"ICICIBANK",
"HDFCBANK",
"SBIN",
"BHARTIARTL",
"RELIANCE",
"DRREDDY",
"TITAN",
"ASIANPAINT",
"LT",
"CIPLA",
"SHRIRAMFIN",
"POWERGRID",
"TATASTEEL",
"AXISBANK",
"M&M",
"ETERNAL",
"ONGC",
"KOTAKBANK",
"TCS",
"ULTRACEMCO",
"INFY",
"BAJFINANCE",
"HINDALCO",
"COALINDIA",
"BEL",
"ADANIENT",
"ADANIPORTS",
"EICHERMOT",
"NTPC",
"INDIGO",
"ITC",
"GRASIM",
"MARUTI",
"BAJAJ-AUTO",
"JIOFIN",
"WIPRO",
"TATACONSUM",
"HINDUNILVR",
"NESTLEIND",
"SUNPHARMA",
"TECHM",
"JSWSTEEL",
"HCLTECH",
"APOLLOHOSP",
"TRENT",
"TMPV",
"SBILIFE",
"HDFCLIFE",
"BAJAJFINSV",
"MAXHEALTH"
]


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
        return open_symbols
    except Exception as e:
        print("get_open_positions", e)
        return set()
# =========================================================
# LOAD OPEN NSE POSITIONS withtotal
# =========================================================
def get_open_positions_withtotal():
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

    except Exception as e:
        print(symbol, e)
# =========================================================
# CHECK SIGNAL
# =========================================================

def check_signal(symbol):
    try:
        cancel_open_orders(symbol)
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
        completed = df.iloc[-2]
        current = df.iloc[-1]
        previous_ema = completed["ema_5"]
        previous_low = completed["low"]
        previous_high = completed["high"]
        current_low = current["low"]
        current_close = current["close"]
        # =================================================
        # SHORT LOGIC
        # =================================================
        if previous_low > previous_ema:
            ema_gap = previous_low - previous_ema
            print(
                symbol,
                " : ",
                previous_low,
                ">",
                previous_ema,
                " ema_gap:",
                round(ema_gap, 2)
            )
            if ema_gap > EMA_GAP:
                if current_low < previous_low:
                    print(f"🔻 SHORT SIGNAL : {symbol}")
                    return {
                        "symbol": symbol,
                        "entry": current_close,
                        "sl": previous_high + SL_BUFFER,
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
        print(f"🚨 SHORTING : {symbol} entry:{entry} sl_price:{sl_price} target_price:{target_price} strategy_name:{strategy_name}")
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
        positions = client.positionbook()
        orders = client.orderbook()
        active_trades = {}
        open_positions = [
            p for p in positions["data"]
            if (
                p.get("exchange") == "NSE"
                and int(p.get("quantity", 0)) < 0
            )
        ]
        order_data = [
            p for p in orders["data"]["orders"]
            if (
                p.get("exchange") == "NSE"
            )
        ]
        for p in open_positions:
            avgprice = float(p.get("average_price", 0))
            symbol= p.get("symbol")
            orderid_buy = p.get("orderid")
            # =============================================
            # FIND SL ORDER
            # =============================================
            sl_order = next(
                (
                    o for o in order_data

                    if (
                        o.get("symbol") == symbol
                        and o.get("pricetype") == "SL-M"
                        and o.get("order_status", "").lower()
                        in ["open", "trigger pending"]
                    )
                ),
                None
            )
            sl_price = (
                    float(sl_order["trigger_price"])
                    if sl_order else None
                )
            if(sl_order==None):
                strategy_name = f"5EMA_SHORT_{symbol}"          
                sl_price = round(avgprice + SL_BUFFER, 1),
                # =================================================
                # SL BUY
                # =================================================
                sl_response = client.placeorder(
                    strategy=f"{strategy_name}_{orderid_buy}_SL",
                    symbol=symbol,
                    action="BUY",
                    exchange="NSE",
                    price_type="SL-M",
                    trigger_price=sl_price,
                    product="MIS",
                    quantity=QUANTITY
                )
                print("SL :", sl_response)
            
            # =============================================
            # FIND TARGET ORDER
            # =============================================
            target_order = next(
                (
                    o for o in order_data

                    if (
                        o.get("symbol") == symbol
                        and o.get("pricetype") == "LIMIT"
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
            if(target_order==None):
                strategy_name = f"5EMA_SHORT_{symbol}"  
                target_price = round(avgprice - TARGET_POINTS, 1)
                # =================================================
                # TARGET BUY
                # =================================================
                target_response = client.placeorder(
                    strategy=f"{strategy_name}_{orderid_buy}_TARGET",
                    symbol=symbol,
                    action="BUY",
                    exchange="NSE",
                    price_type="LIMIT",
                    price=target_price,
                    product="MIS",
                    quantity=QUANTITY
                )
            active_trades[symbol] = {
                "symbol": symbol,
                "qty": int(p["quantity"]),
                "entry": avgprice,
                "sl": sl_price,
                "target": target_price
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
    active_trades = restore_active_trades()
    print(active_trades)
    remove_symbols = []
    for symbol, trade in active_trades.items():
        try:
            ltp = main_obj.safe_ltp(symbol, "NSE")
            if ltp is None:
                continue
            print(f"{symbol} LTP : {ltp}")
            # =============================================
            # TARGET HIT
            # =============================================
            if (
                trade.get("target") is not None
                and
                ltp <= trade["target"]
            ):
                print(f"🎯 TARGET HIT : {symbol}")
                remove_symbols.append(symbol)
            # =============================================
            # SL HIT
            # =============================================
            elif (
                trade.get("sl") is not None
                and
                ltp >= trade["sl"]
            ):
                print(f"🛑 SL HIT : {symbol}")
                remove_symbols.append(symbol)
        except Exception as e:
            print("manage_trades", symbol, e)
    for s in remove_symbols:
        active_trades.pop(s, None)
# =========================================================
# INITIAL RESTORE
# =========================================================
active_trades = restore_active_trades()
# =========================================================
# MAIN LOOP
# =========================================================
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
            print("\n==========================")
            print("🔄 SCANNING NIFTY50")
            print("==========================")
            # =============================================
            # LOAD OPEN NSE POSITIONS
            # =============================================
            open_symbols = get_open_positions()
            print("OPEN POSITIONS :", open_symbols)
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
                else:
                    print("No signals on : ",stock)
                time.sleep(0.2)
            # =============================================
            # MANAGE ACTIVE TRADES
            # =============================================
            print ("manage trade starts")
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