import time,sys
from datetime import datetime, timedelta
import pandas as pd
from colorama import Fore, Back, Style, init
class OpenAlgoOrders:
    """
    Utility class to handle expiry related operations using OpenAlgo
    """

    def __init__(self, parent):
        """
        Initialize with OpenAlgo API client
        """
        self.client = parent.client
        self.parent = parent

    def get_running_orders(self,STRATEGY_NAME= ''):
        orders = self.client.orderbook()
        if self.parent.debug==True:
            print("📋 RAW ORDERS RESPONSE:", orders)
        if orders.get("status") != "success":
            print("❌ Failed to fetch orders")
            return []
        order_list = orders.get("data", [])

        if not order_list:
            print("ℹ️ No orders found")
            return []
        #print(order_list)
        # ------------------------------------------
        # Filter running orders
        # ------------------------------------------
        running_orders = []
        order_list_orders = order_list["orders"]
        for o in order_list_orders:
            if not isinstance(o, dict):
                print("⚠️ Skipping non-dict order entry:", o)
                continue
            strategy = str(o.get("strategy", "")).strip()
            status = str(o.get("order_status", "")).lower().strip()
            symbol = str(o.get("symbol", ""))

            if status in {"open", "pending", "trigger_pending"}:
                if STRATEGY_NAME!='':
                    if strategy == (f"{STRATEGY_NAME}_{self.parent.index}_BUY"):
                        running_orders.append(o)
                else:
                    running_orders.append(o)
        completed = sum(
                    1 for o in order_list_orders if o.get("symbol").startswith(self.parent.index)
                )   
        if completed>0:            
            print("➡️ TOTAL ORDERS:", completed)
            completed_buy = sum(
                    1 for o in order_list_orders if o.get("symbol").startswith(self.parent.index)  and o.get("action") == "BUY"
                )  
            print("➡️ TOTAL BUY:", completed_buy)
            completed_sell = sum(
                    1 for o in order_list_orders if o.get("symbol").startswith(self.parent.index)  and o.get("action") == "SELL"
                )  
            print("➡️ TOTAL SEL:", completed_sell)

        # ------------------------------------------
        # Print Running Orders Immediately
        # ------------------------------------------
        if not running_orders:
            print(f"✅ No running {self.parent.index} orders (all completed)")
        else:
            print(f"\n🚀 RUNNING ORDERS IN {self.parent.index}:\n")
            for o in running_orders:                
                order_id = o.get("orderid")
                symbol   = o.get("symbol")
                status   = o.get("order_status")
                qty      = o.get("quantity")
                action   = o.get("action")
                stratagyName   = o.get("strategy")
                if symbol.startswith(self.parent.index):
                    print(
                        f"OrderID: {order_id} | "
                        f"Symbol: {symbol} | "
                        f"Action: {action} | "
                        f"Qty: {qty} | "
                        f"Statuses: {status} | "
                        f"stratagyName: {stratagyName}"
                    )

        return running_orders
    
    def get_completed_orders(self,STRATEGY_NAME= ''):        
        orders = self.client.orderbook()
        print("📋 RAW COMPLETED ORDERS RESPONSE:", orders)
        if orders.get("status") != "success":
            print("❌ Failed to fetch orders")
            return []
        order_list = orders.get("data", [])

        if not order_list:
            print("ℹ️ No orders found")
            return []
        #print(order_list)
        # ------------------------------------------
        # Filter running orders
        # ------------------------------------------
        completed_orders = []
        order_list_orders = order_list["orders"]
        completed = 0
        for o in order_list_orders:
            if not isinstance(o, dict):
                print("⚠️ Skipping non-dict order entry:", o)
                continue

            strategy = str(o.get("strategy", "")).strip()
            status = str(o.get("order_status", "")).lower().strip()
            symbol = str(o.get("symbol", ""))
            if symbol.startswith(self.parent.index):
                # print("➡️ ORDER STATUS CHECK:", status)
                completed = completed+1

            if status in {"complete"}:
                if STRATEGY_NAME:
                    if strategy == (f"{STRATEGY_NAME}_{self.parent.index}_BUY"):
                        completed_orders.append(o)
        if completed>0:            
            print("➡️ COMPLETED ORDERS:", completed)
        # ------------------------------------------
        # Print Running Orders Immediately
        # ------------------------------------------
        if not completed_orders:
            print(f"✅ No completed {self.parent.index} orders (all empty)")
        else:
            print(f"🚀 COMPLETED BUY ORDERS IN {STRATEGY_NAME} stratagy in {self.parent.index}:\n")
            for o in completed_orders:                
                order_id = o.get("orderid")
                symbol   = o.get("symbol")
                status   = o.get("order_status")
                qty      = o.get("quantity")
                action   = o.get("action")
                stratagyName   = o.get("strategy")
                if symbol.startswith(self.parent.index):
                    print(
                        f"OrderID: {order_id} | "
                        f"Symbol: {symbol} | "
                        f"Action: {action} | "
                        f"Qty: {qty} | "
                        f"Statuses: {status} | "
                        f"stratagyName: {stratagyName}"
                    )

        return completed_orders
    
    def get_positions(self,STRATEGY_NAME= ''):        
        positions = self.client.positionbook()
        print("📋 RAW COMPLETED ORDERS RESPONSE:", positions)
        if positions.get("status") != "success":
            print("❌ Failed to fetch orders")
            return []
        positions_list = positions.get("data", [])

        if not positions_list:
            print("ℹ️ No positions found")
            return []
        # ------------------------------------------
        # Filter running orders
        # ------------------------------------------
        positions_list_orders = positions_list
        for o in positions_list_orders:
            if not isinstance(o, dict):
                print("⚠️ Skipping non-dict order entry:", o)
                continue
        return positions_list_orders


    def get_option_greeks(self,
        symbol,
        underlying_symbol
    ):
        """
        Fetch option greeks using OpenAlgo

        Parameters:
            client               : OpenAlgo client instance
            symbol               : Option symbol (e.g. NIFTY25NOV2526000CE)
            underlying_symbol    : Index name (e.g. NIFTY)
            interest_rate        : Risk-free interest rate (default 0.00)
            exchange             : Derivatives exchange (NFO/BFO)
            underlying_exchange  : Spot exchange (NSE_INDEX/BSE_INDEX)

        Returns:
            dict: Greeks response
        """
        print(symbol,self.parent.exchangeSymbol,'0.00',underlying_symbol,self.parent.underlying_exchange)
        response = self.client.optiongreeks(
            symbol=symbol,
            exchange=self.parent.exchangeSymbol,                    # MUST be NFO
            interest_rate=0.00,
            underlying_symbol=underlying_symbol,
            underlying_exchange=self.parent.underlying_exchange
        )

        print("📊 Option Greeks Response:", response)
        return response
    
    def get_orders_by_stratagy(self,STRATEGY_NAME= '',print_count=True):
        orders = self.client.orderbook()
        # print("📋 My RAW ORDERS RESPONSE:", orders)
        if orders.get("status") != "success":
            print("❌ Failed to fetch orders")
            return []
        
        order_list = orders.get("data", [])
        if not order_list:
            print("ℹ️ No orders found")
            return []
        # print(order_list)
        # ------------------------------------------
        # Filter running orders
        # ------------------------------------------
        running_orders = []
        order_list_orders = order_list["orders"]
        completed=open_orders=cancelled_orders=exicuted_orders=target_sl_orders = 0
        for o in order_list_orders:
            if not isinstance(o, dict):
                print("⚠️ Skipping non-dict order entry:", o)
                continue
            strategy = str(o.get("strategy", "")).strip()
            transformed_text = strategy.split('_')
            stratagy_Name = ('_'.join(transformed_text[:2])) # Result: '5EMA_NIFTY')

            status = str(o.get("order_status", "")).lower().strip()
            symbol = str(o.get("symbol", ""))
            if STRATEGY_NAME:
                # if STRIKE:
                #     expiry_date = self.parent.expiry_date.replace("-", "")
                #     # print(expiry_date)
                #     # print(self.parent.index)
                #     indexremoved = STRIKE.replace(self.parent.index, "")
                #     strikeVal= indexremoved.replace(expiry_date,"")
                #     startswithval = (f"{STRATEGY_NAME}_{self.parent.index}_{strikeVal}")
                # else:
                startswithval = (f"{STRATEGY_NAME}_{self.parent.index}")
            else:
                startswithval = startswithval
            # print(startswithval)    
            if o.get("strategy").startswith(startswithval):
                # print("➡️ ORDER STATUS CHECK:", status)
                completed = completed+1
                if status.startswith("open"):
                    # print("➡️ ORDER STATUS CHECK:", status)
                    open_orders = open_orders+1
                if status.startswith("cancelled") and o.get("strategy").startswith(startswithval):
                    # print("➡️ ORDER STATUS CHECK:", status)
                    cancelled_orders = cancelled_orders+1
                if status.startswith("complete") and o.get("action").startswith("BUY"):
                    # print("➡️ ORDER STATUS CHECK:", status)
                    exicuted_orders = exicuted_orders+1
                if status.startswith("complete") and o.get("action").startswith("SELL"):
                    # print("➡️ ORDER STATUS CHECK:", status)
                    target_sl_orders = target_sl_orders+1
            
            if status in {"open", "pending", "trigger_pending","complete","cancelled"}:
                if STRATEGY_NAME!='':
                    if stratagy_Name == (f"{STRATEGY_NAME}_{self.parent.index}"):
                        running_orders.append(o)
                else:
                    running_orders.append(o)
        if completed>0:
            if print_count==True:
                print(f"✅MY running {STRATEGY_NAME}  {self.parent.index} orders ")
                print("➡️ MY TOTAL ORDERS     :",exicuted_orders,'/',completed)
                print("➡️ MY OPEN ORDERS      :", open_orders)
                print("➡️ MY SL/TARGET ORDERS :", target_sl_orders)
                print("➡️ MY CANCELLED ORDERS :", cancelled_orders)
        return running_orders

    def get_post_flag(self,runstatus,running_orders,stratagyNameStartsWith="5EMA"):
        posflag=0
        if len(runstatus)>0:
            for open_orders in runstatus:
                #print(f"{open_orders}!")
                transformed_text = open_orders['strategy'].split('_')
                open_nifty = ('_'.join(transformed_text[:2])) # Result: '5EMA_NIFTY')
                stratagyOpenName = (f"{stratagyNameStartsWith}_{self.parent.index}")
                # print(stratagyOpenName,  '------' , open_nifty)
                if open_nifty == stratagyOpenName:
                    running_orders.append({open_nifty:open_orders['pricetype'],'pricetype':open_orders['pricetype'],'orderid':open_orders['orderid']})
            # print(len(running_orders))
            if len(running_orders)==0:
                posflag=0
            elif len(running_orders)==1:
                stratagyName = (f"{stratagyNameStartsWith}_{self.parent.index}_CANCEL")
                self.client.cancelorder(order_id=running_orders[0]['orderid'], strategy=stratagyName)
                posflag=0
            else:
                posflag=1
        return posflag

    def bracket_targe_sell(self,option_value,sl_price,target_price,order_type="MIS",strategy_prefix="5EMA",order_id=""):
        try:
            #finding open orders in same order then dont place order 
            completed_orders =  self.get_orders_by_stratagy(strategy_prefix)
            placed_order_str_id = f"{strategy_prefix}_{self.parent.index}_{order_id}_"
            stratagy_status=0
            open_sl_orders = [  j for j in completed_orders if j.get("symbol")==option_value and placed_order_str_id in j.get("strategy") and j.get("action") == "SELL"]
            stratagy_status = len(open_sl_orders)
            if stratagy_status==0:
                # PLACE SL
                self.client.placeorder(
                    strategy=f"{strategy_prefix}_{self.parent.index}_{order_id}_SL",
                    symbol=option_value,
                    exchange="NFO",
                    action="SELL",
                    trigger_price=sl_price,
                    price_type="SL-M",
                    product=order_type,
                    quantity=self.parent.quantity
                )
                # PLACE TARGET
                self.client.placeorder(
                    strategy=f"{strategy_prefix}_{self.parent.index}_{order_id}_TARGET",
                    symbol=option_value,
                    exchange="NFO",
                    action="SELL",
                    price_type="LIMIT",
                    price=target_price,
                    product=order_type,
                    quantity=self.parent.quantity
                )
            return True
        except Exception as e:
            print("Error in bracket sell order:", e)
            return False
    def get_strikes(self,expiry_date,atm,PRICE_LOW = 150,PRICE_HIGH = 170):
        
        #print('STRIKE_STEP')
        # ============================
        # STRIKE RANGE
        # ============================
        strikes = [
            atm + (i * self.parent.STRIKE_STEP)
            for i in range(-self.parent.STRIKE_RANGE, self.parent.STRIKE_RANGE + 1)
        ]
        selections_val = []
        selections =[]
        i=0
        print('get_strikes')
        for strike in strikes:
            # print(strike)
            # selections_val.clear()
            for opt_type in ["CE", "PE"]:
                symbol = f"{self.parent.index}{expiry_date}{strike}{opt_type}"
                # print(symbol)
                try:
                    now = time.time()
                    last = self.parent._LAST_LTP_CALL.get(symbol, 0)
                    if now - last < 2:
                        return None  # skip API call
                    self.parent._LAST_LTP_CALL[symbol] = now
                    quote = self.client.quotes(symbol=symbol, exchange="NFO")
                    if self.parent.debug==True:
                        print(symbol,quote)
                    ltp = quote["data"]["ltp"]
                    # print(PRICE_LOW," <= ",ltp," <= ",PRICE_HIGH)
                    if PRICE_LOW <= ltp <= PRICE_HIGH:
                        print(f"✅ MATCH → {symbol} | LTP: {ltp} | type: {opt_type}")
                        selections_val.append({
                                "symbol": symbol,
                                "type": opt_type,
                                "strike": strike,
                                "ltp": ltp
                            })

                except Exception as e:
                    print(f"⚠️ ERROR {symbol}: {e}")
            if len(selections_val)>0:
                selections = selections_val
        return selections
    # =====================================================
    # FUNCTION: RUN CE / PE 145 OPTION TRADE
    # =====================================================
    def place_145_order_set(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike,placed_order_id=''):
        try:
            completed_orders =  self.get_orders_by_stratagy(strategy_prefix,print_count=False)
            if placed_order_id!='':
                sltarget_order_status = [
                                            o for o in completed_orders if placed_order_id in o.get("strategy")  and o.get("action") == "SELL"
                                        ]
                if len(sltarget_order_status)==0:
                    self.target_sl_validation(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike)  
                    print("--- Waiting to add SL/TARGET ---")
                    return True
                
            # opened_buy_orders_status = [
            #                                     o for o in completed_orders if o.get("order_status") == "complete" and o.get("strategy", "").startswith(strategy_prefix) and o.get("action") == "BUY"
            #                                 ]
            # opened_sell_orders_status = 1 # true means all orders having a target and sell order
            

            # for opened_buy in opened_buy_orders_status:
            #     print(opened_buy['orderid'])
            #     opened_sell_orders_status = sum(
            #                         1 for o in completed_orders if  opened_buy['orderid'] in o.get("strategy")  and o.get("action") == "SELL"
            #                     )
            #     if opened_sell_orders_status!= 0:
            #                 break
            # if opened_sell_orders_status==0:
            #     self.target_sl_validation(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike)  
            #     print("--- Waiting to add SL/TARGET ---")
            #     return True
            # else:
            if True:
                print(f"🚀 RUN order placing @ {datetime.now()}")
                ltp = self.parent.safe_ltp(symbol)
                if ltp is not None:
                    # print("📊 LTP:", ltp)
                # quote = self.client.ltp(symbol=symbol, exchange="NFO")
                # ltp = quote["data"]["ltp"]
                # print(Fore.RED + 'This is red text!')
                # print(Fore.GREEN + 'This is red text!')                    
                    if self.parent.index=='BANKNIFTY':
                        ENTRY_TRIGGER_btw= ENTRY_TRIGGER+10
                    else:
                        ENTRY_TRIGGER_btw= ENTRY_TRIGGER+5
                    if ltp >= (ENTRY_TRIGGER_btw):
                        # print(f"📊 {symbol} || "+Fore.GREEN +f"LTP: {ltp} \n"+ Style.RESET_ALL)
                        print(f"📊 {symbol} || {ltp} \n")
                    elif ltp < (ENTRY_TRIGGER_btw):
                        # print(f"📊 {symbol} || "+Fore.BLUE +f"LTP: {ltp} \n"+ Style.RESET_ALL)
                        print(f"📊 {symbol} || {ltp} \n")
                    # ENTRY
                    if ltp >= ENTRY_TRIGGER and ltp <= (ENTRY_TRIGGER_btw):
                        print(f"🚀 ENTRY TRIGGER HIT @ {ltp}")

                        order = self.client.placeorder(
                            strategy=f"{strategy_prefix}_{self.parent.index}_BUY",
                            symbol=symbol,
                            exchange="NFO",
                            action="BUY",
                            pricetype="MARKET",
                            product="MIS",
                            quantity=self.parent.quantity 
                        )
                        # print(order)
                        if order.get("status") == "success":
                            entry_price = ltp
                            sl_price = entry_price - SL_POINTS
                            target_price = entry_price + TARGET_POINTS
                            print(f"✅ BOUGHT @ {entry_price}")
                            print(f"🛑 SL: {sl_price} | 🎯 TARGET: {target_price}")
                            
                            placed_order_id = order.get("orderid")
                            print(placed_order_id)
                            time.sleep(1)  # allow exchange to update orderbook
                            orders = self.client.orderbook()
                            # print(orders)
                            my_order = None
                            for o in orders["data"]["orders"]:
                                if o.get("orderid") == placed_order_id:
                                    # print("order found")
                                    my_order= o
                                    break
                            print(my_order)
                            order_id = my_order.get("orderid")
                            print(order_id)
                            print(my_order.get("timestamp"))
                            time.sleep(1)  # allow exchange to update orderbook
                            # placed_time = None                        
                            placed_time = datetime.strptime(my_order.get("timestamp"), "%Y-%m-%d %H:%M:%S")
                            if not placed_time:
                                raise Exception("❌ Unable to find order placed time")
                            print("📅 ORDER PLACED TIME:", placed_time)
                            # ==============================
                            # STEP 1: WAIT FOR 5-MIN CANDLE CLOSE
                            # ==============================
                            sl_place_time = self.parent.next_5min_close(placed_time)
                            print("⏳ Waiting till candle close:", sl_place_time)
                            print("⏳ datetime.now():", datetime.now())
                            # while datetime.now() < sl_place_time:
                            #     time.sleep(1)
                            #print(datetime.now(),sl_place_time)
                            if datetime.now() > sl_place_time:
                                print("✅ Candle closed, calculating SL and place order")
                                self.bracket_targe_sell(symbol,sl_price,target_price,"MIS",strategy_prefix,placed_order_id)
                                print("📌 SL & TARGET PLACED")
                            else:
                                print("📌 SL & TARGET NOT PLACED")
                            # break
                        else:
                            print(order)
                else:
                    print(f"🚀 FAIL TO FIND LTP @ {ltp}")
            return True
        except Exception as e:
            print("Error in order sell order:", e)
            return False
    
    def target_sl_validation(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike):
        orders = self.client.orderbook()
        order_list = orders.get("data", [])
        if not order_list:
            print("ℹ️ No orders found")
            return []
        # print(order_list)
        # ------------------------------------------
        # Filter running orders
        # ------------------------------------------
        order_list_orders = order_list["orders"]
        complete_buy_orders_status = [ 
                                    o for o in order_list_orders if o.get("order_status") == "complete" and o.get("strategy", "").startswith(f"145{option_strike}_{self.parent.index}") and o.get("action") == "BUY" 
                                ]
        all_sell_orders_status = [ 
                                    o for o in order_list_orders if o.get("strategy", "").startswith(f"145{option_strike}_{self.parent.index}") and o.get("action") == "SELL"
                                ]        
        # print(complete_buy_orders_status)NIFTY_26012123845718
        # sys.exit
        for k in complete_buy_orders_status:
            strategy_name=f"145{option_strike}_{self.parent.index}_" 
            symbol = k.get("symbol")               
            # if symbol.startswith("BANKNIFTY"):
            #     strategy_name = strategy_name+"BANKNIFTY_"
            # elif symbol.startswith("NIFTY"):
            #     strategy_name = strategy_name+"NIFTY_"            
            strategy_name= strategy_name+k.get("orderid")+"_"           

            entry_price = k.get("price") 
            sl_price = entry_price - SL_POINTS
            target_price = entry_price + TARGET_POINTS
            order_active = [ 
                        j for j in all_sell_orders_status if j.get("strategy", "").startswith(strategy_name)
                    ]
            print(f"✅ --------Validation for SL placing-------------  {symbol} ")
            #Check any sl/tareget present on the buy order, if not then check the time and place the sl/target
            # print(order_active)
            # print('complete_sell_orders_status')
            # print(complete_sell_orders_status)            
            if len(order_active)==0:
                print(f"Ther is not a sl/target orders now, need to check and place after the candle\n  {strategy_name} ")
                print(f"✅ BOUGHT @ {entry_price}")
                print(f"🛑 SL: {sl_price} | 🎯 TARGET: {target_price}")
                # complete_open_orders_status = [ 
                #                         j for j in all_sell_orders_status if j.get("order_status") == "open" and j.get("strategy", "").startswith(strategy_name)
                #                     ]
                # print(complete_open_orders_status)
                # if(len(complete_open_orders_status)==0):
                placed_order_id=k.get("orderid")
                time.sleep(1)  # allow exchange to update orderbook
                # placed_time = None                        
                placed_time = datetime.strptime(k.get("timestamp"), "%Y-%m-%d %H:%M:%S")
                if not placed_time:
                    raise Exception("❌ Unable to find order placed time")
                print("📅 ORDER PLACED TIME:", placed_time)
                # ==============================
                # STEP 1: WAIT FOR 5-MIN CANDLE CLOSE
                # ==============================
                sl_place_time = self.parent.next_5min_close(placed_time)
                print("⏳ Waiting till candle close:", sl_place_time)
                print("⏳ datetime.now():", datetime.now())
                # while datetime.now() < sl_place_time:
                #     time.sleep(1)
                if datetime.now() > sl_place_time:
                    print("✅ Candle closed, calculating SL and place order, in target_sl_validation on zero_order")
                    self.bracket_targe_sell(symbol,sl_price,target_price,"MIS",strategy_prefix,placed_order_id)
                    print(f"📌 SL & TARGET PLACED: ",symbol)
                else:
                    print(f"📌 SL & TARGET NOT PLACED: ",symbol)
            elif len(order_active)>0:
                strategy_name=f"145{option_strike}_{self.parent.index}_" 
                symbol = k.get("symbol")               
                # if symbol.startswith("BANKNIFTY"):
                #     strategy_name = strategy_name+"BANKNIFTY_"
                # elif symbol.startswith("NIFTY"):
                #     strategy_name = strategy_name+"NIFTY_"            
                strategy_name= strategy_name+k.get("orderid")+"_"        
                print(f" Orders present need to check is any open orders present,\n  {strategy_name} ")
                placed_order_id=k.get("orderid")
                time.sleep(1)  # allow exchange to update orderbook
                # placed_time = None                        
                placed_time = datetime.strptime(k.get("timestamp"), "%Y-%m-%d %H:%M:%S")
                if not placed_time:
                    raise Exception("❌ Unable to find order placed time")
                print("📅 ORDERS PLACED TIME:", placed_time)
                # ==============================
                # STEP 1: WAIT FOR 5-MIN CANDLE CLOSE
                # ==============================
                sl_place_time = self.parent.next_5min_close(placed_time)
                print("⏳ placing Wait till candle close:", sl_place_time)
                print("⏳ datetime.now():", datetime.now())
                # while datetime.now() < sl_place_time:
                #     time.sleep(1)
                if datetime.now() > sl_place_time:
                    print("✅ Candle closed, calculating SL and place order, in target_sl_validation on order present")
                    
                    found_open_from_sltarget_waitingArr = [ 
                                        o for o in order_active if o.get("order_status") == "open" 
                    ]                    
                    found_open_from_sltarget_waiting = len(found_open_from_sltarget_waitingArr)
                    print(found_open_from_sltarget_waiting)
                    if found_open_from_sltarget_waiting==1:
                        print("open order is present, need to cancel it")
                        timestamp_open = found_open_from_sltarget_waitingArr[0]["timestamp"]
                        placed_time = datetime.strptime(timestamp_open, "%Y-%m-%d %H:%M:%S")
                        currenttime = datetime.now()                        
                        if (currenttime - placed_time) > timedelta(minutes=5.2):
                            print("Order older than 5.2 minutes. Cancel order.")
                            self.client.cancelorder(order_id=found_open_from_sltarget_waitingArr[0]["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")
                        self.place_145_order_set(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike,placed_order_id)   
                    if found_open_from_sltarget_waiting==2:
                        print("open and target/sl order is present. No action")
                        

    def run_145_option_trade(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike):
        # print(Fore.RED + 'This is red text!')
        # print(Fore.GREEN + 'This is red text!')
        # print(Back.GREEN + 'This has a green background!')
        # print(Style.BRIGHT + 'This text is bright!' + Style.RESET_ALL) # Manually reset if autoreset is False

        CHECK_INTERVAL =1
        execution_limit=self.parent.days_limit
        entered = False
        entry_price = sl_price = target_price = 0        
        completed_orders_full =  self.get_orders_by_stratagy(strategy_prefix)
        completed_orders =  completed_orders_full
        stratagy_status=0
        completed_orders = [  j for j in completed_orders if j.get("order_status") == "complete" and j.get("symbol")==symbol and  j.get("action") == "BUY"]
        stratagy_status = len(completed_orders)

        # print(completed_orders)        
        if stratagy_status==0:
            # it run only in the beggining of the application that have not placed any order on thestrike
            runstatus = self.place_145_order_set(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike)            
        if stratagy_status!=0:
            completed_sell_orders = [  j for j in completed_orders_full if  j.get("symbol")==symbol and  j.get("action") == "SELL"]
            #print(completed_sell_orders)
            open_orders_status = sum(
                        1 for o in completed_sell_orders if o.get("order_status") == "open"
                    )   
            # bracket_count =stratagy_status
            print('  -----------  open_orders_status ----------- \n | ',stratagy_status,'/',execution_limit,' \n | Open orders :',open_orders_status)
            print('  ------------------------------------------- \n')
            # cancel if have only once open order
            if open_orders_status==1:
                open_order_to_cancel = next(
                                (
                                    o for o in completed_orders_full
                                    if o.get("order_status") == "open"
                                    and o.get("action")=="SELL"
                                ),
                                None
                            )
                if open_order_to_cancel!=None:
                                self.client.cancelorder(order_id=open_order_to_cancel["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")
            traile_orders = False
            
            if stratagy_status>=execution_limit and open_orders_status==0:
                #print("stratagy_status",stratagy_status,">= execution_limit",execution_limit,"and  open_orders_status =",open_orders_status)
                #This is the case where more exicutions happend and neeed to stopp all the open orders
                for orders_active in completed_orders:
                    open_complete_orders_status = sum(
                        1 for o in completed_orders if o.get("strategy", "").startswith(f"{strategy_prefix}_{self.parent.index}_{orders_active.get('orderid')}")
                    )
                    #condetion for place sl/target
                    if open_complete_orders_status==0:
                        entry_price = orders_active.get('average_price')
                        sl_price = entry_price - SL_POINTS
                        target_price = entry_price + TARGET_POINTS
                        self.bracket_targe_sell(orders_active.get('symbol'),sl_price,target_price,"MIS",strategy_prefix,orders_active.get('orderid'))
                # sys.exit()
                print('Todays Limit Exceeded---for',strategy_prefix,":-",stratagy_status,"\n")     
                self.parent.exit_all[option_strike][self.parent.index] = True
                #     return Trueand bracket_count%2==0
            elif stratagy_status<=execution_limit  and open_orders_status!=0:
                #print("stratagy_status",stratagy_status,"<= execution_limit",execution_limit,"and  open_orders_status !=0")
                complete_145_orders = [  j for j in completed_orders_full if j.get("symbol")==symbol]
                for open_sl in complete_145_orders:
                    #only 2 open orders need if more then it will cleared
                    if open_orders_status>2:
                        print('open_orders_id',open_sl.get("orderid"))
                        
                        complete_open_orders_status = [ 
                                                    j for j in complete_145_orders if j.get("order_status") == "open" and j.get("strategy", "").startswith(f"{strategy_prefix}_{self.parent.index}_") and j.get("action") == "SELL"
                        ]
                        print("only 2 open orders need if more then it will cleared",len(complete_open_orders_status))
                        if(len(complete_open_orders_status))>2:
                                complete_open_orders_status_LIMIT = [ 
                                                    j for j in complete_145_orders if j.get("order_status") == "open" and j.get("strategy", "").startswith(f"{strategy_prefix}_{self.parent.index}_") and j.get("action") == "SELL" and j.get("pricetype") == "LIMIT"
                                ] 
                                if(len(complete_open_orders_status_LIMIT))>1:
                                    # -----------------------------
                                    # Sort by timestamp DESC (latest first)
                                    # -----------------------------
                                    open_orders_sorted_LIMIT = sorted(
                                        complete_open_orders_status_LIMIT,
                                        key=lambda o: datetime.strptime(
                                            o["timestamp"], "%Y-%m-%d %H:%M:%S"
                                        ),
                                        reverse=True
                                    )
                                    # Keep newest, cancel rest
                                    latest_order_LIMIT = open_orders_sorted_LIMIT[0]
                                    old_orders_LIMIT = open_orders_sorted_LIMIT[1:]

                                    print("✅ Keeping latest order:", latest_order_LIMIT["orderid"])

                                    # -----------------------------
                                    # Cancel older orders
                                    # -----------------------------
                                    for o in old_orders_LIMIT:
                                        try:
                                            print("❌ Cancelling old order:", o["orderid"])
                                            self.client.cancelorder(
                                                order_id=o["orderid"],
                                                strategy=o.get("strategy", "")
                                            )
                                        except Exception as e:
                                            print("⚠️ Cancel failed:", o["orderid"], e)
                                
                                
                                complete_open_orders_status_SL_M = [ 
                                                    j for j in complete_145_orders if j.get("order_status") == "open" and j.get("strategy", "").startswith(f"{strategy_prefix}_{self.parent.index}_{open_sl.get('orderid')}") and j.get("action") == "SELL" and j.get("pricetype") == "SL-M"
                                ] 
                                if(len(complete_open_orders_status_SL_M))>1:
                                    # -----------------------------
                                    # Sort by timestamp DESC (latest first)
                                    # -----------------------------
                                    open_orders_sorted_SL_M= sorted(
                                        complete_open_orders_status_SL_M,
                                        key=lambda o: datetime.strptime(
                                            o["timestamp"], "%Y-%m-%d %H:%M:%S"
                                        ),
                                        reverse=True
                                    )
                                    # Keep newest, cancel rest
                                    latest_order_SL_M = open_orders_sorted_SL_M[0]
                                    old_orders_SL_M= open_orders_sorted_SL_M[1:]

                                    print("✅ Keeping latest order:", latest_order_SL_M["orderid"])
                                    # -----------------------------
                                    # Cancel older orders
                                    # -----------------------------
                                    for o in old_orders_SL_M:
                                        try:
                                            print("❌ Cancelling old order:", o["orderid"])
                                            self.client.cancelorder(
                                                order_id=o["orderid"],
                                                strategy=o.get("strategy", "")
                                            )
                                        except Exception as e:
                                            print("⚠️ Cancel failed:", o["orderid"], e)


                            # print(complete_open_orders_status)
                    #ENDS only 2 open orders need if more then it will cleared

                    # atm = self.client.quotes(symbol=open_sl.get("symbol"),    exchange='NFO')                 
                    print(open_sl.get("order_status"),open_sl.get("strategy", ""))
                    if open_sl.get("order_status") == "complete" and open_sl.get("action") == "SELL":
                        # clear the sibling orders
                        if open_sl.get("strategy", "").endswith("_SL"):
                            order_val = f"{strategy_prefix}_{self.parent.index}_{open_sl.get('orderid')}_TARGET"
                            open_order_to_cancel = next(
                                (
                                    o for o in complete_145_orders
                                    if o.get("order_status") == "open"
                                    and o.get("strategy", "").startswith(order_val)
                                    and o.get("symbol") == open_sl.get("symbol")
                                ),
                                None
                            )
                            if open_order_to_cancel!=None:
                                print("open_order_to_cancel")
                                print(open_order_to_cancel)
                                self.client.cancelorder(order_id=open_order_to_cancel["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")

                        if open_sl.get("strategy", "").endswith("_TARGET"):
                            order_val = f"{strategy_prefix}_{self.parent.index}_{open_sl.get('orderid')}_SL"
                            open_order_to_cancel_T = next(
                                (
                                    o for o in complete_145_orders
                                    if o.get("order_status") == "open"
                                    and o.get("strategy", "").startswith(order_val)
                                    and o.get("symbol") == open_sl.get("symbol")
                                ),
                                None
                            )
                            if open_order_to_cancel_T!=None:
                                print("open_order_to_cancel_T")
                                print(open_order_to_cancel_T)
                                self.client.cancelorder(order_id=open_order_to_cancel_T["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")

                return True
            else:
 
                self.target_sl_validation(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike)  
                return True
        else:
            return False    # time.sleep(CHECK_INTERVAL)
        
    def trail_sl_m_safe(self,strategy_prefix,order,trigger_price,parent_order_id=""):
        time.sleep(1)
        print(f"Canceling order {order['orderid']}")
        self.client.cancelorder(order_id=order['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
        # PLACE SL
        self.client.placeorder(
            strategy=f"{strategy_prefix}_{self.parent.index}_{parent_order_id}_SL",
            symbol=order['symbol'],
            exchange="NFO",
            action="SELL",
            trigger_price=trigger_price,
            price_type="SL-M",
            product="MIS",
            quantity=self.parent.quantity
        )
        return True
    
    def manage_trades_untracked(self,strategy_prefix,order,target_order_id,parent_order_id="",ltp=""):
        time.sleep(1)
        #print(f"{strategy_prefix} LTP : {ltp} target: {target_order_id} sl: {order}")
        if (strategy_prefix=="15EMA"):
            if (ltp <= order["sl"]):
                print(f"🛑 SL HIT : {order['symbol']}")
                print(f"⚠ SL FAILED : {order['symbol']}")                
                # ==========================================
                # CANCEL OLD
                # ==========================================            
                self.client.cancelorder(order_id=order['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
                time.sleep(0.5)   
                self.client.cancelorder(order_id=target_order_id)
                time.sleep(0.5)            
                # ==========================================
                # PLACE NEW Market
                # ==========================================      
                self.client.placeorder(            
                    strategy=f"EMERGENCY_EXIT_{strategy_prefix}_{self.parent.index}_{parent_order_id}",            
                    symbol=order['symbol'],            
                    action="SELL",            
                    exchange="NFO",            
                    price_type="MARKET",            
                    product="MIS",            
                    quantity=self.parent.quantity
                )
        elif (ltp <= order["sl"]):
            print(f"🛑 SL HIT : {order['symbol']}")
            print(f"⚠ SL FAILED : {order['symbol']}")                
            # ==========================================
            # CANCEL OLD
            # ==========================================            
            self.client.cancelorder(order_id=order['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
            time.sleep(0.5)   
            self.client.cancelorder(order_id=target_order_id)
            time.sleep(0.5)            
            # ==========================================
            # PLACE NEW Market
            # ==========================================      
            self.client.placeorder(            
                strategy=f"EMERGENCY_EXIT_{strategy_prefix}_{self.parent.index}_{parent_order_id}",            
                symbol=order['symbol'],            
                action="SELL",            
                exchange="NFO",            
                price_type="MARKET",            
                product="MIS",            
                quantity=self.parent.quantity
            )

        return True
    def trail_145_option_trade(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike):
        print("trail_145_option_trade",strategy_prefix)
        execution_limit=self.parent.days_limit    
        completed_orders_full =  self.get_orders_by_stratagy(strategy_prefix)
        completed_orders =  completed_orders_full
        stratagy_status=0
        completed_orders = [  j for j in completed_orders if j.get("order_status") == "complete" and j.get("symbol")==symbol and  j.get("action") == "BUY"]
        stratagy_status = len(completed_orders)         
        if stratagy_status!=0:
            completed_sell_orders = [  j for j in completed_orders_full if  j.get("symbol")==symbol and  j.get("action") == "SELL"]
            open_orders_status = sum(
                        1 for o in completed_sell_orders if o.get("order_status") == "open"
                    )   
            print('  -----------  open_orders_status ----------- \n | ',stratagy_status,'/',execution_limit,' \n | Open orders :',open_orders_status)
            print('  ------------------------------------------- \n')
            
            if stratagy_status<=execution_limit  and open_orders_status!=0:
                #print("stratagy_status",stratagy_status,"<= execution_limit",execution_limit,"and  open_orders_status !=0")
                complete_145_orders = [  j for j in completed_orders_full if j.get("symbol")==symbol]
                for open_sl in complete_145_orders:                                          
                    if open_sl.get("order_status") == "open" and open_sl.get("strategy", "").endswith("_SL"):
                        print("Trailing SL  started")
                        ltp = self.parent.safe_ltp(open_sl.get("symbol"),"NFO")
                        if ltp is None:
                            print(f"\n📈 {open_sl.get('symbol')} LTP open is {ltp}")
                            continue
                        else:
                            # if ltp>0:
                            #     print("📌 ATM STRIKE:", ltp)
                            if ltp >= (ENTRY_TRIGGER):
                                print(f"📊 {open_sl.get('symbol')} | "+Fore.GREEN +f"LTP open: {ltp} \n"+ Style.RESET_ALL)
                            elif ltp < (ENTRY_TRIGGER):
                                print(f"📊 {open_sl.get('symbol')} | "+Fore.RED +f"LTP: {ltp} \n"+ Style.RESET_ALL)

                            # print(f"\n📈 {open_sl.get('symbol')} LTP open: {ltp}")
                            print("**********************************")   
                            if self.parent.index=='BANKNIFTY':
                                SL_LEVELS = [
                                    (433, 430),
                                    (445, 440),
                                    (455, 450),
                                    (465, 460),
                                    (475, 470),
                                    (485, 480),
                                    (495, 490),
                                    (555, 500),
                                ]
                            else:
                                SL_LEVELS = [
                                    (198, 195),
                                    (200, 198),
                                    (205, 200),
                                    (210, 205),
                                    (215, 210),
                                    (220, 215),
                                    (225, 220),
                                    (230, 225),
                                    (235, 230),
                                    (240, 235),
                                    (245, 240),
                                    (255, 250),
                                    (265, 260),
                                    (275, 270),
                                    (280, 275),
                                    (285, 280),
                                ]
                            for ltp_level, new_sl in SL_LEVELS:
                                print(
                                    f"LTP {ltp_level} | "
                                    f"SL {new_sl}"
                                )
                                
                                if(ltp>=ltp_level and open_sl["trigger_price"]<ltp_level and open_sl["trigger_price"]!=new_sl and open_sl["trigger_price"]<new_sl):
                                    print(ltp,">=",ltp_level," and ",open_sl["trigger_price"],"<",ltp_level,"and",open_sl["trigger_price"],"<=",new_sl)
                                    if open_orders_status==2:
                                        open_limit_order = next(
                                                (
                                                    o for o in complete_145_orders
                                                    if o.get("order_status") == "open"
                                                    and o.get("action")=="SELL"
                                                    and o.get("pricetype")=="LIMIT"
                                                ),
                                                None
                                            )
                                        print(open_limit_order)
                                        parent_order_id = 0
                                        if open_limit_order:
                                            print(open_limit_order["orderid"])
                                            print(open_limit_order["strategy"])
                                            prefix = f"{strategy_prefix}_{self.parent.index}"
                                            parent_order_id = open_limit_order["strategy"].removeprefix(prefix).split("_")[1]

                                            response = self.client.modifyorder(
                                            order_id=open_limit_order["orderid"],
                                            action="SELL",
                                            product="MIS",
                                            pricetype="LIMIT",
                                            price=new_sl+50,
                                            quantity=self.parent.quantity,
                                            symbol=open_limit_order['symbol'],
                                            exchange="NFO",
                                            )
                                        if parent_order_id:
                                            self.trail_sl_m_safe(strategy_prefix,open_sl,new_sl,parent_order_id)
                                    # break 
                return True
        else:
            return False    # time.sleep(CHECK_INTERVAL)
    
    def get_opening_range_strikes(self,expiry_date,atm,PRICE_LOW=150,PRICE_HIGH=170):
        """
        Find option strikes whose price was between PRICE_LOW–PRICE_HIGH
        between 09:28 and 09:30 IST using historical data.
        """

        results = []

        # -----------------------------
        # Date setup (TODAY)
        # -----------------------------
        today = datetime.now().strftime("%Y-%m-%d")

        start_date = today
        end_date   = today
        interval   = "1m"
        # print(atm)
        # -----------------------------
        # Generate strike range
        # -----------------------------
        strikes = [
            atm + (i * self.parent.STRIKE_STEP)
            for i in range(-self.parent.STRIKE_RANGE, self.parent.STRIKE_RANGE + 1)
        ]
        #print(strikes)
        for strike in strikes:
            #print(self.parent.index)
            #print(expiry_date)
            #print(strike)
            for opt_type in ["CE", "PE"]:
                #print(opt_type)
                symbol = f"{self.parent.index}{expiry_date}{strike}{opt_type}"
                # print(symbol)
                try:
                    df = self.client.history(
                        symbol=symbol,
                        exchange="NFO",
                        interval=interval,
                        start_date=start_date,
                        end_date=end_date
                    )

                    # -----------------------------
                    # Safety checks
                    # -----------------------------
                    if not isinstance(df, pd.DataFrame) or df.empty:
                        continue

                    if not isinstance(df.index, pd.DatetimeIndex):
                        df.index = pd.to_datetime(df.index)

                    # -----------------------------
                    # Filter 09:28 – 09:30 candles
                    # -----------------------------
                    opening_df = df.between_time("09:28", "09:31")
                    # opening_df = df.between_time("10:10", "10:11")

                    if opening_df.empty:
                        continue
                    # print(PRICE_LOW)
                    # print(PRICE_HIGH)
                    # print(symbol)
                    # -----------------------------
                    # Check price range
                    # -----------------------------
                    for _, row in opening_df.iterrows():
                        ltp = row["close"]
                        #print(row.name.strftime("%H:%M")," - ",symbol,ltp)
                        if PRICE_LOW <= ltp <= PRICE_HIGH:
                            print(
                                f"✅ OPENING MATCH → {symbol} | "
                                f"Time: {row.name.strftime('%H:%M')} | "
                                f"LTP: {ltp}"
                            )

                            results.append({
                                "symbol": symbol,
                                "strike": strike,
                                "type": opt_type,
                                "ltp": ltp,
                                "time": row.name.strftime("%H:%M")
                            })

                            break  # one match is enough per symbol

                except Exception as e:
                    print(f"⚠️ HISTORY ERROR {symbol}: {e}")

        return results
    
    def trigger_5ema_bracketOrder(self,symbol,price,slprice,orderid):
        try:
            trigger_price = price + slprice
            print("🔁 Square-off at Target Price (LIMIT)")
            target_response = self.client.placeorder(
                strategy=f"5EMA_{self.parent.index}_{orderid}_TARGET",
                symbol=symbol,
                exchange="NFO",
                action="SELL",
                price_type="LIMIT",
                price=trigger_price,
                product="MIS",
                quantity=self.parent.quantity
            )
            print("TARGET RESPONSE: ", target_response)
            sl_price = price - slprice
            if sl_price<=0:
                sl_price= 0.5
            print("🔁 Square-off with Stop Loss (SL-L)")
            sl_response = self.client.placeorder(
                    strategy=f"5EMA_{self.parent.index}_{orderid}_SL",
                    symbol=symbol,
                    exchange="NFO",
                    action="SELL",
                    price_type="SL-M",
                    trigger_price=sl_price,
                    product="MIS",
                    quantity=self.parent.quantity
                )
            print("SL RESPONSE:", sl_response)
            return sl_response
        except Exception as e:
            print("Error:", e)
            return e
    def trigger_5ema_placeorder(self,offset='ATM',BuySeLL='BUY'):
        try:
            expiry_dateVal = self.parent.expiry_date
            expiry_date = expiry_dateVal.replace("-", "")
            # ------------------------------------------
            # Place ATM Option Order
            # ------------------------------------------
            response = self.client.optionsorder(
                strategy=f"5EMA_{self.parent.index}_STRIKE",
                underlying=self.parent.index,          # Underlying Index
                exchange="NFO",        # Index exchange
                expiry_date=expiry_date,       # Correct expiry
                offset=offset,                # Auto-select ATM strike
                option_type="PE",            # CE or PE
                action=BuySeLL,                # BUY or SELL
                quantity=self.parent.quantity,                 # 1 Lot = 75
                pricetype="MARKET",          # MARKET or LIMIT
                product="MIS",              # NRML or MIS
                splitsize=0                  # 0 = no split
            )
            print("ORDER RESPONSE:", response)
            return {'posflag':1,'response':response,'msg':"success"}
        except Exception as e:
            print("Error:", e)

    def identify_5ema_trigger(self,previous_ema,previous_low,previous_high,current_low):
        try:
            # -----------------------------
            # SIGNAL LOGIC
            # -----------------------------
            print(f"previous_low : {previous_low} > previous_ema : {previous_ema}")
            # print(f"{previous_low} > {previous_ema}")
            if previous_low > previous_ema:
                ema_candle_gap = previous_low - previous_ema
                if ema_candle_gap>self.parent.EMA_GAP:
                    print(f"current_low : {current_low} < previous_low : {previous_low}")
                    # print(f"{current_low} < {previous_low}")
                    if current_low < previous_low:
                        # print("✅") 
                        growPersentatge = ((previous_high - current_low) / current_low) * 100
                        # index_sl_position = (previous_high - current_low)
                        index_sl_position = (previous_high - previous_low)
                        # reachVal = current_low - index_sl_position
                        reachVal = previous_low - index_sl_position
                        print(f"\n📢 SIGNAL → BUY PE (Price ABOVE EMA 5) {growPersentatge}% - {current_low} ")
                        triggerVal = self.trigger_5ema_placeorder('ATM','BUY')
                        return {'growPersentatge':growPersentatge,'index_sl_position':index_sl_position, 'BUY':triggerVal}
                else:
                    print("\n❌ NO SIGNAL - EMA very close to candle.")
                    return {'posflag':0,'msg':"NO SIGNAL"}
            else:
                print("\n❌ NO SIGNAL")
                return {'posflag':0,'msg':"NO SIGNAL"}

        except Exception as e:
            print("Error:", e)

    def trigger_15ema_placeorder(self,offset='ATM',BuySeLL='BUY'):
        try:
            expiry_dateVal = self.parent.expiry_date
            expiry_date = expiry_dateVal.replace("-", "")
            # ------------------------------------------
            # Place ATM Option Order
            # ------------------------------------------
            response = self.client.optionsorder(
                strategy=f"15EMA_{self.parent.index}_STRIKE",
                underlying=self.parent.index,          # Underlying Index
                exchange="NFO",        # Index exchange
                expiry_date=expiry_date,       # Correct expiry
                offset=offset,                # Auto-select ATM strike
                option_type="CE",            # CE or PE
                action=BuySeLL,                # BUY or SELL
                quantity=self.parent.quantity,                 # 1 Lot = 75
                pricetype="MARKET",          # MARKET or LIMIT
                product="MIS",              # NRML or MIS
                splitsize=0                  # 0 = no split
            )
            print("ORDER RESPONSE:", response)
            return {'posflag':1,'response':response,'msg':"success"}
        except Exception as e:
            print("Error:", e)

    def trigger_15ema_bracketOrder(self,symbol,price,slprice,orderid):
        try:
            trigger_price = price + slprice
            print("🔁 Square-off at Target Price (LIMIT)")
            target_response = self.client.placeorder(
                strategy=f"15EMA_{self.parent.index}_{orderid}_TARGET",
                symbol=symbol,
                exchange="NFO",
                action="SELL",
                price_type="LIMIT",
                price=trigger_price,
                product="MIS",
                quantity=self.parent.quantity
            )
            print("TARGET RESPONSE: ", target_response)
            sl_price = price - slprice
            if sl_price<=0:
                sl_price= 0.5
            print("🔁 Square-off with Stop Loss (SL-L)")
            sl_response = self.client.placeorder(
                    strategy=f"15EMA_{self.parent.index}_{orderid}_SL",
                    symbol=symbol,
                    exchange="NFO",
                    action="SELL",
                    price_type="SL-M",
                    trigger_price=sl_price,
                    product="MIS",
                    quantity=self.parent.quantity
                )
            print("SL RESPONSE:", sl_response)
            return sl_response
        except Exception as e:
            print("Error:", e)
            return e
    def identify_15ema_trigger(self,previous_ema,previous_low,previous_high,current_low,current_high):
        try:
            # -----------------------------
            # SIGNAL LOGIC
            # -----------------------------
            print(f"previous_high : {previous_high} < previous_ema : {previous_ema}")
            # print(f"{previous_low} > {previous_ema}")
            if previous_high < previous_ema:
                ema_candle_gap = previous_ema - previous_high
                if ema_candle_gap>self.parent.EMA_GAP:
                    print(f"current_high : {current_high} > previous_high : {previous_high}")
                    if current_high > previous_high:
                        # print("✅") 
                        growPersentatge = ((previous_high - current_low) / current_low) * 100
                        # index_sl_position = (previous_high - current_low)
                        index_sl_position = (previous_high - previous_low)
                        # reachVal = current_low - index_sl_position
                        reachVal = previous_high + index_sl_position
                        print(f"\n📢 SIGNAL → BUY CE (Price ABOVE EMA 15) {growPersentatge}% - {current_low} ")
                        triggerVal = self.trigger_15ema_placeorder('ATM','BUY')
                        return {'growPersentatge':growPersentatge,'index_sl_position':index_sl_position, 'BUY':triggerVal}
                else:
                    print("\n❌ NO SIGNAL - EMA very close to candle.")
                    return {'posflag':0,'msg':"NO SIGNAL"}
            else:
                print("\n❌ NO SIGNAL")
                return {'posflag':0,'msg':"NO SIGNAL"}

        except Exception as e:
            print("Error:", e)
    
    def place_safety_order(self,option_value,sl_price,target_price,order_type="MIS",quantity=0):
                    self.client.placeorder(
                    strategy=f"SAFETY_{self.parent.index}_SL",
                    symbol=option_value,
                    exchange="NFO",
                    action="SELL",
                    trigger_price=sl_price,
                    price_type="SL-M",
                    product=order_type,
                    quantity=quantity
                )
    def cancel_order_fromorder(self,orderid):
        orders = self.client.orderbook()
        open_sl_orders = [  j for j in orders if  orderid in j.get("strategy") and j.get("action") == "SELL"]
        for k in open_sl_orders:
            symbol = k.get("symbol")   
            stratagyName=1
            self.client.cancelorder(order_id=k.get("orderid"), strategy=stratagyName)
            posflag=0

    def cancel_an_order(self):
        # Get positions (list of dicts)
        positions = self.client.positionbook()

        # Get all orders (list of dicts inside 'data')
        orders_response = self.client.orderbook()
        if len(orders_response['data'])>0:
            orders_list = orders_response['data']['orders']
            positions_list = positions['data']
            #print(orders_list)
            #print(positions_list)
            # Identify SELL orders for negative quantity positions that are pending
            order_ids_to_cancel = [
                o["orderid"]
                for pos in positions_list
                for o in orders_list
                if pos.get("quantity", 0) < 0
                and o.get("symbol") == pos.get("symbol")
                and o.get("action") == "SELL"
                and o.get("pricetype") == "SL-M"           
                and o.get("order_status") in ["open", "trigger pending"]
                and o.get("exchange") == "NFO" 
                
            ]
            print("Orders to cancel:", order_ids_to_cancel)
            # Close oder with market price
            if len(order_ids_to_cancel)<=0:
                for pos in positions['data']:
                    #print(pos)
                    if pos['exchange']!='NSE':
                        if pos['quantity'] < 0:  # active position
                            qty_to_close = abs(pos['quantity'])
                            action = 'BUY'   
                            print(pos['product'])                     
                            self.client.placeorder(
                                strategy=f"negative_balance",
                                symbol=pos['symbol'],
                                exchange="NFO",
                                action="BUY",
                                product="MIS",
                                quantity=qty_to_close,
                                pricetype='MARKET'
                            )
                    # elif pos['exchange']=='NSE':
                    #     if pos['pnl'] < -100:  # active position
                    #         qty_to_close = abs(pos['quantity'])
                    #         action = 'BUY'   
                    #         print(pos['product'])                     
                    #         self.client.placeorder(
                    #             strategy=f"negative_balance",
                    #             symbol=pos['symbol'],
                    #             exchange="NSE",
                    #             action="BUY",
                    #             product="MIS",
                    #             quantity=qty_to_close,
                    #             pricetype='MARKET'
                    #         )


    # =========================================================
    # MANAGE TRADES
    # =========================================================
    def manage_trades(self,symbol,strategy_prefix):
        print(
            f"\n"
            f"{'=' * 70}\n"
            f"✅ MANAGE SQUARE-OFF ON SKIPPED TARGETS - START\n"
            f"{'-' * 70}\n"
            f"📌 SYMBOL   : {symbol}\n"
            f"📌 STRATEGY : {strategy_prefix}\n"
            f"{'=' * 70}\n"
        )
        execution_limit=self.parent.days_limit    
        completed_orders_full =  self.get_orders_by_stratagy(strategy_prefix)
        completed_orders =  completed_orders_full
        stratagy_status=0
        completed_orders = [  j for j in completed_orders if j.get("order_status") == "complete" and j.get("symbol")==symbol and  j.get("action") == "BUY"]
        stratagy_status = len(completed_orders)        
        if stratagy_status!=0:
            completed_sell_orders = [  j for j in completed_orders_full if  j.get("symbol")==symbol and  j.get("action") == "SELL"]           
            open_orders_status = sum(
                        1 for o in completed_sell_orders if o.get("order_status") == "open"
                    )   
            #print('  -----------  open_orders_status ----------- \n | ',stratagy_status,'/',execution_limit,' \n | Open orders :',open_orders_status)
            #print('  ------------------------------------------- \n')            
            for open_sl in completed_sell_orders:
                print("Start un identified SL/TG")
                             
                if open_sl.get("order_status") == "open" and open_sl.get("strategy", "").endswith("_SL"):              
                        ltp = self.parent.safe_ltp(open_sl.get("symbol"),"NFO")                        
                        if ltp is None:
                            print(f"\n📈 {open_sl.get('symbol')} LTP open is {ltp}")
                            continue
                        else:
                            try:
                                open_target_to_cancel = next(
                                                (
                                                    o for o in completed_sell_orders
                                                    if o.get("strategy", "").endswith("_TARGET")
                                                    and o.get("order_status") == "open"
                                                ),
                                                None
                                            )                                
                                print(open_sl)
                                print(open_target_to_cancel)        
                                if open_target_to_cancel!=None:
                                    open_target_to_cancel_id=open_target_to_cancel["orderid"]
                                # =============================================
                                # SL HIT
                                # =============================================
                                if (
                                    open_sl.get("trigger_price") is not None
                                    and
                                    ltp < open_sl["trigger_price"]
                                ):
                                    print(f"🛑 SL HIT : {symbol}")
                                    print(f"⚠ SL FAILED : {symbol}")                     
                                    # ==========================================
                                    # CANCEL OLD
                                    # ==========================================            
                                    self.client.cancelorder(order_id=open_sl["orderid"])
                                    time.sleep(0.5)   
                                    self.client.cancelorder(order_id=open_target_to_cancel_id)
                                    time.sleep(0.5)            
                                    # ==========================================
                                    # PLACE NEW Market SELL
                                    # ==========================================      
                                    self.client.placeorder(            
                                        strategy="EMERGENCY_EXIT",            
                                        symbol=symbol,            
                                        action="SELL",            
                                        exchange="NFO",            
                                        price_type="MARKET",            
                                        product="MIS",            
                                        quantity=self.parent.quantity
                                    )
                                            
                            except Exception as e:
                                print("manage_trades", symbol, e)
        print(
            f"\n"
            f"{'=' * 70}\n"
            f"✅ MANAGE SQUARE-OFF ON SKIPPED TARGETS - END\n"
            f"{'-' * 70}\n"
            f"📌 SYMBOL   : {symbol}\n"
            f"📌 STRATEGY : {strategy_prefix}\n"
            f"{'=' * 70}\n"
        )
    
    def clear_running_unknown_stock_orders(self,STRATEGY_NAME= ''):
        orders = self.client.orderbook()
        if self.parent.debug==True:
            print("📋 RAW ORDERS RESPONSE:", orders)
        if orders.get("status") != "success":
            print("❌ Failed to fetch orders")
            return []
        order_list = orders.get("data", [])

        if not order_list:
            print("ℹ️ No orders found")
            return []
        #print(order_list)
        # ------------------------------------------
        # Filter running orders
        # ------------------------------------------
        running_orders = []
        order_list_orders = order_list["orders"]
        for o in order_list_orders:
            if not isinstance(o, dict):
                print("⚠️ Skipping non-dict order entry:", o)
                continue
            strategy = str(o.get("strategy", "")).strip()
            status = str(o.get("order_status", "")).lower().strip()
            symbol = str(o.get("symbol", ""))

            if o.get("strategy").startswith(STRATEGY_NAME):
                running_orders.append(o)
        # print(running_orders)
        completed = sum(
                    1 for o in running_orders if o.get("strategy").startswith(STRATEGY_NAME)
                )   
        if completed>0:            
            print("➡️ TOTAL ORDERS:", completed)
            completed_buy = sum(
                    1 for o in running_orders if o.get("strategy").startswith(STRATEGY_NAME)  and o.get("action") == "BUY"
                )  
            print("➡️ TOTAL BUY:", completed_buy)
            completed_sell = sum(
                    1 for o in running_orders if o.get("strategy").startswith(STRATEGY_NAME)  and o.get("action") == "SELL"
                )  
            print("➡️ TOTAL SEL:", completed_sell)

        # ------------------------------------------
        # Print Running Orders Immediately
        # ------------------------------------------
        if not running_orders:
            print(f"✅ No running {self.parent.index} orders (all completed)")
        else:
            print(f"\n🚀 RUNNING ORDERS IN {self.parent.index}:\n")
            for o in running_orders:                
                order_id = o.get("orderid")
                symbol   = o.get("symbol")
                status   = o.get("order_status")
                qty      = o.get("quantity")
                action   = o.get("action")
                stratagyName   = o.get("strategy")
                if symbol.startswith(self.parent.index):
                    print(
                        f"OrderID: {order_id} | "
                        f"Symbol: {symbol} | "
                        f"Action: {action} | "
                        f"Qty: {qty} | "
                        f"Statuses: {status} | "
                        f"stratagyName: {stratagyName}"
                    )

        return running_orders