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

from base.MainClass import MainClass

# ==========================================
# COLORS
# ==========================================

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

spinner = itertools.cycle(["|", "/", "-", "\\"])

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

TARGET_POINTS = 15

SL_BUFFER = 2

QUANTITY = 1

# ==========================================
# STOCKS
# ==========================================

NIFTY50 = [

    "RELIANCE",
    "HDFCBANK",
    "ICICIBANK",
    "INFY",
    "TCS",
    "SBIN",
    "LT",
    "AXISBANK",
    "KOTAKBANK",
    "BHARTIARTL",
    "ITC",
    "HCLTECH",
    "MARUTI",
    "SUNPHARMA",
    "BAJFINANCE",
    "ULTRACEMCO"

]

# ==========================================
# ACTIVE TRADES
# ==========================================

active_trades = {}

# ==========================================
# OPENING RANGE CACHE
# ==========================================

opening_ranges = {}

# ==========================================
# GET OPENING RANGE
# ==========================================

def calculate_opening_range(symbol):

    try:

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

        if len(df) < 3:
            return None

        if not isinstance(df.index, pd.DatetimeIndex):

            df.index = pd.to_datetime(df.index)

        # ==========================================
        # FIRST 15 MINUTES
        # ==========================================

        opening_df = df.iloc[:3]

        opening_high = opening_df["high"].max()

        opening_low = opening_df["low"].min()

        opening_ranges[symbol] = {

            "high": opening_high,

            "low": opening_low
        }

        print(
            f"📊 OPENING RANGE : {symbol}"
            f" HIGH={opening_high}"
            f" LOW={opening_low}"
        )

    except Exception as e:

        print(symbol, e)

# ==========================================
# CHECK SIGNAL
# ==========================================

def check_signal(symbol):

    try:

        if symbol not in opening_ranges:
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

        current = df.iloc[-1]

        current_close = current["close"]

        current_high = current["high"]

        current_low = current["low"]

        opening_high = opening_ranges[symbol]["high"]

        opening_low = opening_ranges[symbol]["low"]

        # ==========================================
        # BUY BREAKOUT
        # ==========================================

        if current_high > opening_high:

            print(
                f"🚀 ORB BUY : {symbol}"
            )

            return {

                "symbol": symbol,

                "side": "BUY",

                "entry": current_close,

                "sl": opening_low - SL_BUFFER,

                "target": current_close + TARGET_POINTS
            }

        # ==========================================
        # SELL BREAKDOWN
        # ==========================================

        if current_low < opening_low:

            print(
                f"🔻 ORB SELL : {symbol}"
            )

            return {

                "symbol": symbol,

                "side": "SELL",

                "entry": current_close,

                "sl": opening_high + SL_BUFFER,

                "target": current_close - TARGET_POINTS
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
            f"🚀 NEW ORB TRADE\n"
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

        print(response)

        if response.get("status") != "success":
            return

        # ==========================================
        # SL ORDER
        # ==========================================

        sl_action = "SELL" if side == "BUY" else "BUY"

        client.placeorder(

            strategy=f"{strategy}_SL",

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

            strategy=f"{strategy}_TARGET",

            symbol=symbol,

            action=sl_action,

            exchange="NSE",

            price_type="LIMIT",

            price=round(target, 1),

            product="MIS",

            quantity=QUANTITY
        )

        active_trades[symbol] = signal

    except Exception as e:

        print("place_trade", e)

# ==========================================
# RESTORE TRADES
# ==========================================

def restore_active_trades():

    try:

        positions = client.positionbook()

        if not isinstance(positions, dict):
            return

        position_data = positions.get("data", [])

        for p in position_data:

            qty = int(p.get("quantity", 0))

            if qty == 0:
                continue

            symbol = p.get("symbol")

            active_trades[symbol] = {

                "symbol": symbol
            }

        print(
            f"✅ ACTIVE RESTORED"
        )

    except Exception as e:

        print("restore", e)

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

            print(
                f"\n"
                f"📊 CALCULATING OPENING RANGE"
                f""
            )

            for stock in NIFTY50:

                calculate_opening_range(stock)

                time.sleep(0.2)

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
            f"🔍 SCANNING ORB STOCKS\n"
            f"{'=' * 70}"
        )

        for stock in NIFTY50:

            if stock in active_trades:

                print(
                    f"⚠ ACTIVE : {stock}"
                )

                continue

            signal = check_signal(stock)

            if signal:

                place_trade(signal)

            time.sleep(0.5)

        time.sleep(20)

    except Exception as e:

        print("MAIN LOOP", e)

        time.sleep(5)