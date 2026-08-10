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
# ==========================================
# FORCE CLOSE ALL @ 3:10 PM
# ==========================================

def close_all_positions_and_orders():

    try:

        print("\n🚨 CLOSING ALL POSITIONS & ORDERS 🚨\n")

        # ==========================================
        # CANCEL OPEN ORDERS
        # ==========================================

        orders = client.orderbook()

        if isinstance(orders, dict):

            order_data = orders.get("data", [])

            for order in order_data:

                try:

                    status = (
                        order.get("order_status", "")
                        .lower()
                    )

                    if status not in [
                        "open",
                        "trigger pending"
                    ]:
                        continue

                    orderid = order.get("orderid")

                    strategy = order.get("strategy")

                    symbol = order.get("symbol")

                    print(
                        f"❌ CANCEL ORDER : "
                        f"{symbol} | "
                        f"{orderid}"
                    )

                    response = client.cancelorder(

                        orderid=orderid,

                        strategy=strategy
                    )

                    print(response)

                    time.sleep(0.3)

                except Exception as e:

                    print(
                        "cancel order error",
                        e
                    )

        # ==========================================
        # CLOSE POSITIONS
        # ==========================================

        positions = client.positionbook()

        if isinstance(positions, dict):

            position_data = positions.get("data", [])

            for pos in position_data:

                try:

                    qty = int(pos.get("quantity", 0))

                    if qty == 0:
                        continue

                    symbol = pos.get("symbol")

                    exchange = pos.get("exchange")

                    product = pos.get("product", "MIS")

                    # ==========================================
                    # SHORT POSITION
                    # ==========================================

                    if qty < 0:

                        action = "BUY"

                    # ==========================================
                    # LONG POSITION
                    # ==========================================

                    else:

                        action = "SELL"

                    print(
                        f"🚨 EXIT POSITION : "
                        f"{symbol} | "
                        f"QTY={abs(qty)} | "
                        f"{action}"
                    )

                    response = client.placeorder(

                        strategy="AUTO_CLOSE_1510",

                        symbol=symbol,

                        action=action,

                        exchange=exchange,

                        price_type="MARKET",

                        product=product,

                        quantity=abs(qty)
                    )

                    print(response)

                    time.sleep(0.5)

                except Exception as e:

                    print(
                        "close position error",
                        e
                    )

        print("\n✅ ALL CLOSED\n")

    except Exception as e:

        print(
            "close_all_positions_and_orders",
            e
        )
while True:
    # ==========================================
    # AUTO CLOSE @ 3:10 PM
    # ==========================================
    
    if main_obj.is_after_IST(15, 10):
    
        close_all_positions_and_orders()
    
        break