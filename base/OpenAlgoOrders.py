import time,sys
from datetime import datetime, timedelta
import pandas as pd
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
        print("📋 RAW COMPLETED ORDERS RESPONSE:")           
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
    
    def get_orders_by_stratagy(self,STRATEGY_NAME= ''):
        orders = self.client.orderbook()
        # print("📋 My RAW ORDERS RESPONSE:", orders)
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
                startswithval = (f"{STRATEGY_NAME}_{self.parent.index}")
            else:
                startswithval = startswithval
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
                #print(stratagyOpenName,  '------' , open_nifty)
                if open_nifty == stratagyOpenName:
                    running_orders.append({open_nifty:open_orders['pricetype'],'pricetype':open_orders['pricetype'],'orderid':open_orders['orderid']})
            #print(len(running_orders))
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
    def place_145_order_set(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix):
        try:
            # print(f"📊 Waiting for new order--------")
            running_orders = []
            entered = False

            ltp = self.parent.safe_ltp(symbol)
            if ltp is not None:
                # print("📊 LTP:", ltp)
            # quote = self.client.ltp(symbol=symbol, exchange="NFO")
            # ltp = quote["data"]["ltp"]
                print(f"📊 {symbol} | LTP: {ltp} \n")
                if self.parent.index=='BANKNIFTY':
                    ENTRY_TRIGGER_btw= ENTRY_TRIGGER+10
                else:
                    ENTRY_TRIGGER_btw= ENTRY_TRIGGER+5
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
                    print(order)
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
                        print(orders)
                        my_order = None
                        for o in orders["data"]["orders"]:
                            if o.get("orderid") == placed_order_id:
                                print("order found")
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
        strategy_name=f"145{option_strike}_" 

        # print(complete_buy_orders_status)NIFTY_26012123845718
        # sys.exit
        for k in complete_buy_orders_status:
            symbol = k.get("symbol")               
            if symbol.startswith("BANKNIFTY"):
                strategy_name = strategy_name+"BANKNIFTY_"
            elif symbol.startswith("NIFTY"):
                strategy_name = strategy_name+"NIFTY_"            
            strategy_name= strategy_name+k.get("orderid")+"_"           

            entry_price = k.get("price") 
            sl_price = entry_price - SL_POINTS
            target_price = entry_price + TARGET_POINTS
            print(f"✅ --------Validation for SL placing-------------\n  {symbol} \n  {strategy_name}")
            print(f"✅ BOUGHT @ {entry_price}")
            print(f"🛑 SL: {sl_price} | 🎯 TARGET: {target_price}")
            order_active = [ 
                        j for j in all_sell_orders_status if j.get("strategy", "").startswith(strategy_name)
                    ]
            # print(order_active)
            # print('complete_sell_orders_status')
            # print(complete_sell_orders_status)            
            if len(order_active)==0:
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
                    print("✅ Candle closed, calculating SL and place order")
                    self.bracket_targe_sell(symbol,sl_price,target_price,"MIS",strategy_prefix,placed_order_id)
                    print(f"📌 SL & TARGET PLACED: ",symbol)
                else:
                    print(f"📌 SL & TARGET NOT PLACED: ",symbol)
            else:
                completed_order_status = [ 
                                        j for j in all_sell_orders_status if j.get("order_status") == "complete" and j.get("strategy", "").startswith(strategy_name)
                                    ]
                if(len(completed_order_status)!=0):
                    self.place_145_order_set(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix)   


                # break
    def run_145_option_trade(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike):
        CHECK_INTERVAL =1
        execution_limit=10
        entered = False
        entry_price = sl_price = target_price = 0
        completed_orders =  self.get_orders_by_stratagy(strategy_prefix)
        stratagy_status = sum(
                        1 for o in completed_orders if o.get("order_status") == "complete"  and o.get("action") == "BUY"
                    )
        open_orders_status = sum(
                        1 for o in completed_orders if o.get("order_status") == "open"
                    )   
        if stratagy_status==0:
            runstatus = self.place_145_order_set(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix)            
        if stratagy_status!=0:            
            # self.target_sl_validation(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike)                
            bracket_count =stratagy_status
            print('  -----------  open_orders_status ----------- \n | ',stratagy_status,'/',execution_limit,' \n | Open orders :',open_orders_status)
            print('  ------------------------------------------- \n')
            # cancel if have only once open order
            if open_orders_status==1:
                open_order_to_cancel = next(
                                (
                                    o for o in completed_orders
                                    if o.get("order_status") == "open"
                                    and o.get("action")=="SELL"
                                ),
                                None
                            )
                if open_order_to_cancel!=None:
                                self.client.cancelorder(order_id=open_order_to_cancel["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")
            traile_orders = False
            
            if stratagy_status>=execution_limit and open_orders_status==0:
                print('Todays Limit Exceeded---for',strategy_prefix,":-",stratagy_status,"\n")     
                self.parent.exit_all[option_strike][self.parent.index] = True
                #     return Trueand bracket_count%2==0
            elif stratagy_status<=execution_limit  and open_orders_status!=0:
                print('completed_orders')                 
                # print(completed_orders)         
                open_count = sum(
                        1 for o in completed_orders if o.get("order_status") == "open"
                    )
                # print(open_count)              
                for open_sl in completed_orders:
                    # atm = self.client.quotes(symbol=open_sl.get("symbol"), exchange='NFO')                 
                        if open_sl.get("order_status") == "complete" and open_sl.get("action") == "SELL":
                            if open_sl.get("strategy", "").endswith("_SL"):
                                open_order_to_cancel = next(
                                    (
                                        o for o in completed_orders
                                        if o.get("order_status") == "open"
                                        and o.get("strategy", "").endswith("_TARGET")
                                        and o.get("timestamp")==open_sl.get("timestamp") 
                                        and o.get("symbol") == open_sl.get("symbol")
                                    ),
                                    None
                                )
                                if open_order_to_cancel!=None:
                                    self.client.cancelorder(order_id=open_order_to_cancel["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")

                            if open_sl.get("strategy", "").endswith("_TARGET"):
                                open_order_to_cancel_T = next(
                                    (
                                        o for o in completed_orders
                                        if o.get("order_status") == "open"
                                        and o.get("strategy", "").endswith("_SL")
                                        and o.get("timestamp")==open_sl.get("timestamp") 
                                        and o.get("symbol") == open_sl.get("symbol")
                                    ),
                                    None
                                )
                                if open_order_to_cancel_T!=None:
                                    self.client.cancelorder(order_id=open_order_to_cancel_T["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")

                        elif open_sl.get("order_status") == "open" and open_sl.get("strategy", "").endswith("_SL"):
                            ltp = self.parent.safe_ltp(open_sl.get("symbol"),"NFO")
                            if ltp is None:
                                print(f"\n📈 {open_sl.get('symbol')} LTP open is {ltp}")
                                continue
                            else:
                                # if ltp>0:
                                #     print("📌 ATM STRIKE:", ltp)
                                print(f"\n📈 {open_sl.get('symbol')} LTP open: {ltp}")
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
                                                        o for o in completed_orders
                                                        if o.get("order_status") == "open"
                                                        and o.get("action")=="SELL"
                                                        and o.get("pricetype")=="LIMIT"
                                                    ),
                                                    None
                                                )
                                            print(open_limit_order)
                                            print(open_limit_order["orderid"])
                                            print(open_limit_order["strategy"])
                                            prefix = f"{strategy_prefix}_{self.parent.index}"
                                            parent_order_id = open_limit_order["strategy"].removeprefix(prefix).split("_")[0]

                                            if open_limit_order:
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
                                            self.trail_sl_m_safe(strategy_prefix,open_sl,new_sl,parent_order_id)
                                        # break 


                return True
            else:
                self.target_sl_validation(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix,option_strike)  
                # runstatus = self.place_145_order_set(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix)   
                return True
        else:
            return False    # time.sleep(CHECK_INTERVAL)
        
    def trail_sl_m_safe(self,strategy_prefix,order,trigger_price,parent_order_id=""):
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

        # -----------------------------
        # Generate strike range
        # -----------------------------
        strikes = [
            atm + (i * self.parent.STRIKE_STEP)
            for i in range(-self.parent.STRIKE_RANGE, self.parent.STRIKE_RANGE + 1)
        ]

        for strike in strikes:
            for opt_type in ["CE", "PE"]:

                symbol = f"{self.parent.index}{expiry_date}{strike}{opt_type}"

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
                    opening_df = df.between_time("09:28", "09:30")

                    if opening_df.empty:
                        continue

                    # -----------------------------
                    # Check price range
                    # -----------------------------
                    for _, row in opening_df.iterrows():
                        ltp = row["close"]

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