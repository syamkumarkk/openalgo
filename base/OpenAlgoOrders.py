import time,sys
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
        print("📋 My RAW ORDERS RESPONSE:", orders)
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
        completed = 0
        for o in order_list_orders:
            if not isinstance(o, dict):
                print("⚠️ Skipping non-dict order entry:", o)
                continue
            strategy = str(o.get("strategy", "")).strip()
            transformed_text = strategy.split('_')
            stratagy_Name = ('_'.join(transformed_text[:2])) # Result: '5EMA_NIFTY')

            status = str(o.get("order_status", "")).lower().strip()
            symbol = str(o.get("symbol", ""))
            if symbol.startswith(self.parent.index):
                # print("➡️ ORDER STATUS CHECK:", status)
                completed = completed+1

            if status in {"open", "pending", "trigger_pending","complete","cancelled"}:
                if STRATEGY_NAME!='':
                    if stratagy_Name == (f"{STRATEGY_NAME}_{self.parent.index}"):
                        running_orders.append(o)
                else:
                    running_orders.append(o)
        if completed>0:            
            print("➡️ MY COMPLETED ORDERS:", completed)
        # ------------------------------------------
        # Print Running Orders Immediately
        # ------------------------------------------
        if not running_orders:
            print(f"✅ My running {self.parent.index} orders (all completed)")
        else:
            print(f"\n🚀 MY ORDERS IN {self.parent.index}:\n")
            for o in running_orders:                
                order_id = o.get("orderid")
                symbol   = o.get("symbol")
                status   = o.get("order_status")
                qty      = o.get("quantity")
                action   = o.get("action")
                stratagyName   = o.get("strategy")
                stratagyTime   = o.get("timestamp")
                if symbol.startswith(self.parent.index):
                    print(
                        f"OrderID: {order_id} | "
                        f"Symbol: {symbol} | "
                        f"Action: {action} | "
                        f"Qty: {qty} | "
                        f"Statuses: {status} | "
                        f"stratagyName: {stratagyName} | "
                        f"stratagy Time: {stratagyTime}"
                        
                    )

        return running_orders

    def get_post_flag(self,runstatus,running_orders,stratagyNameStartsWith="5EMA"):
        posflag=0
        if len(runstatus)>0:
            for open_orders in runstatus:
                #print(f"{open_orders}!")
                transformed_text = open_orders['strategy'].split('_')
                open_nifty = ('_'.join(transformed_text[:2])) # Result: '5EMA_NIFTY')
                stratagyOpenName = (f"{stratagyNameStartsWith}_{self.parent.index}")
                print(stratagyOpenName,  '------' , open_nifty)
                if open_nifty == stratagyOpenName:
                    running_orders.append({open_nifty:open_orders['pricetype'],'pricetype':open_orders['pricetype'],'orderid':open_orders['orderid']})
            print(len(running_orders))
            if len(running_orders)==0:
                posflag=0
            elif len(running_orders)==1:
                stratagyName = (f"{stratagyNameStartsWith}_{self.parent.index}_CANCEL")
                self.client.cancelorder(order_id=running_orders[0]['orderid'], strategy=stratagyName)
                posflag=0
            else:
                posflag=1
        return posflag
    
    def bracket_targe_sell(self,option_value,sl_price,target_price,order_type="MIS",strategy_prefix="5EMA"):
        try:
            # PLACE SL
            self.client.placeorder(
                strategy=f"{strategy_prefix}_{self.parent.index}_SL",
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
                strategy=f"{strategy_prefix}_{self.parent.index}_TARGET",
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
        
        # print(STRIKE_STEP)
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
        for strike in strikes:
            # print(strike)
            # selections_val.clear()
            for opt_type in ["CE", "PE"]:
                symbol = f"{self.parent.index}{expiry_date}{strike}{opt_type}"
                # print(symbol)
                try:
                    quote = self.client.quotes(symbol=symbol, exchange="NFO")
                    if self.parent.debug==True:
                        print(quote)
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
            print(f"📊 Waiting for new order--------")
            runstatus = self.get_running_orders(strategy_prefix)
            running_orders = []
            entered = False
            # posflag = self.get_post_flag(
            #     runstatus,
            #     running_orders,
            #     strategy_prefix
            # )

            # if posflag != 0:
            #     print(f"🚀 RUNNING POSITION FOR {symbol}")
            #     time.sleep(CHECK_INTERVAL)
                # continue

            quote = self.client.quotes(symbol=symbol, exchange="NFO")
            ltp = quote["data"]["ltp"]

            print(f"📊 {symbol} | LTP: {ltp}")
            if self.parent.index=='BANKNIFTY':
                ENTRY_TRIGGER_btw= ENTRY_TRIGGER+100
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
                    self.bracket_targe_sell(symbol,sl_price,target_price,"MIS",strategy_prefix)
                    print("📌 SL & TARGET PLACED")
                    # break
                else:
                    print(order)
            return True
        except Exception as e:
            print("Error in order sell order:", e)
            return False
    def run_145_option_trade(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix):
        CHECK_INTERVAL =1
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
            bracket_count =stratagy_status*2
            print('open_orders_status ------------------------',stratagy_status,bracket_count,open_orders_status)
            
            # print(stratagy_status,bracket_count,open_orders_status)    
            # return False
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
            if stratagy_status>4 :
                print('Todays Limit Exceeded---',stratagy_status)                 
                print(completed_orders)   
            elif stratagy_status<=4 and bracket_count%2==0 and open_orders_status!=0:
                print('completed_orders')                 
                print(completed_orders)         
                open_count = sum(
                        1 for o in completed_orders if o.get("order_status") == "open"
                    )
                # print(open_count)              
                for open_sl in completed_orders:
                    atm = self.client.quotes(symbol=open_sl.get("symbol"), exchange='NFO')
                    data = atm.get("data", {})
                    if not data:
                        print("⚠️ Empty quote data:", atm)
                        continue
                    else:
                        if len(atm['data'])>0:
                            print("📌 ATM STRIKE:", atm['data'])
                            print(atm['data']['ltp'])
                            print("**********************************")                    
                        if open_sl.get("order_status") == "complete" and open_sl.get("action") == "SELL":
                            # print(open_sl["strategy"])
                            # print(open_sl.get("strategy"))
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
                            SL_LEVELS = [
                                (195, 193),
                                (201, 195),
                                (205, 200),
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
                                
                                if(atm['data']['ltp']>=ltp_level and open_sl["trigger_price"]<ltp_level and open_sl["trigger_price"]!=new_sl and open_sl["trigger_price"]<new_sl):
                                    print(atm['data']['ltp'],">=",ltp_level," and ",open_sl["trigger_price"],"<",ltp_level,"and",open_sl["trigger_price"],"<=",new_sl)
                                    self.trail_sl_m_safe(strategy_prefix,open_sl,new_sl)
                                    break 


                return True
            else:
                runstatus = self.place_145_order_set(ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix)   
                return True
        else:
            return False    # time.sleep(CHECK_INTERVAL)
        
    def trail_sl_m_safe(self,strategy_prefix,order,trigger_price):
        self.client.cancelorder(order_id=order['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
        # PLACE SL
        self.client.placeorder(
            strategy=f"{strategy_prefix}_{self.parent.index}_SL",
            symbol=order['symbol'],
            exchange="NFO",
            action="SELL",
            trigger_price=trigger_price,
            price_type="SL-M",
            product="MIS",
            quantity=self.parent.quantity
        )
        return True
    



#     if len(completed_orders)!=0 and len(completed_orders)==3 and open_count>0:
#     open_SL = next(
#         (
#             o for o in completed_orders
#             if o.get("order_status") == "open"
#             and o.get("strategy", "").endswith("_SL")
#         ),
#         None
#     )
#     if open_SL:
#         print("🎯 OPEN TARGET ORDER:", open_SL["orderid"])
#         print(open_SL)
#         # atm = self.parent.get_atm(open_SL["symbol"])
#         atm = self.client.quotes(symbol=open_SL["symbol"], exchange='NFO')
#         if len(atm['data'])>0:
#             print("📌 ATM STRIKE:", atm['data'])
#             print(atm['data']['ltp'])
#             print("**********************************")
#             if(atm['data']['ltp']>=195 and open_SL["trigger_price"]<195):
#                     self.client.cancelorder(order_id=atm['data']['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=atm['data']['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=193,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
#             if(atm['data']['ltp']>=201 and open_SL["trigger_price"]<201):
#                     self.client.cancelorder(order_id=atm['data']['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=atm['data']['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=195,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
#             if(atm['data']['ltp']>=205 and open_SL["trigger_price"]<205):
#                     self.client.cancelorder(order_id=atm['data']['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=atm['data']['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=200,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
#             if(atm['data']['ltp']>=215 and open_SL["trigger_price"]<215):
#                     self.client.cancelorder(order_id=atm['data']['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=atm['data']['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=210,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
        
#     completed_count = sum(
#         1 for o in completed_orders if o.get("order_status") == "complete"
#     )

#     completed_count = sum(
#         1 for o in completed_orders if o.get("order_status") == "complete"
#     )
#     print("✅ Completed orders:", completed_count) 
#     if(completed_count==2):
#         open_orders = [
#                 o for o in completed_orders
#                 if o.get("order_status") == "open"
#             ]
#         orderid = open_orders[0]['orderid']
#         self.client.cancelorder(order_id=orderid, strategy=f"{strategy_prefix}_{self.parent.index}")

# elif len(completed_orders)!=0 and len(completed_orders)==16 and open_count>0:
    
                
#     open_SL = next(
#         (
#             o for o in completed_orders
#             if o.get("order_status") == "open"
#             and o.get("strategy", "").endswith("_SL")
#         ),
#         None
#     )
#     print(open_SL)
#     sys.exit
#     self.client.placeorder(
#                     strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                     symbol=open_SL['symbol'],
#                     exchange="NFO",
#                     action="SELL",
#                     trigger_price=193,
#                     price_type="SL-M",
#                     product="MIS",
#                     quantity=self.parent.quantity
#                 )
#     if open_SL:
#         print("🎯 OPEN TARGET ORDER:", open_SL["orderid"])
#         print(open_SL)
#         # atm = self.parent.get_atm(open_SL["symbol"])
#         atm = self.client.quotes(symbol=open_SL["symbol"], exchange='NFO')
#         if len(atm['data'])>0:
#             print("📌 ATM STRIKE:", atm['data'])
#             print(atm['data'])
#             print("**********************************")
#             if(atm['data']['ltp']>=195 and open_SL["trigger_price"]<195):
                    
#                     self.client.cancelorder(order_id=open_SL["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=open_SL['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=193,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
#             if(atm['data']['ltp']>=201 and open_SL["trigger_price"]<201):
#                     self.client.cancelorder(order_id=open_SL["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=open_SL['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=195,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
#             if(atm['data']['ltp']>=205 and open_SL["trigger_price"]<205):
#                     self.client.cancelorder(order_id=open_SL["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=open_SL['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=205,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
#             if(atm['data']['ltp']>=215 and open_SL["trigger_price"]<215):
#                     self.client.cancelorder(order_id=open_SL["orderid"], strategy=f"{strategy_prefix}_{self.parent.index}")
#                             # PLACE SL
#                     self.client.placeorder(
#                         strategy=f"{strategy_prefix}_{self.parent.index}_SL",
#                         symbol=open_SL['symbol'],
#                         exchange="NFO",
#                         action="SELL",
#                         trigger_price=215,
#                         price_type="SL-M",
#                         product="MIS",
#                         quantity=self.parent.quantity
#                     )
#     completed_count = sum(
#         1 for o in completed_orders if o.get("order_status") == "complete"
#     )
#     print("✅ Completed orders:", completed_count) 
#     if(completed_count==2):
#         open_orders = [
#                 o for o in completed_orders
#                 if o.get("order_status") == "open"
#             ]
#         orderid = open_orders[0]['orderid']
#         self.client.cancelorder(order_id=orderid, strategy=f"{strategy_prefix}_{self.parent.index}")
# # # print(completed_orders)
# # if(len(completed_orders)%3!=0):
# #     runstatus =  self.get_orders_by_stratagy(strategy_prefix)
# #     print(runstatus)
# #     running_orders=[]
# #     if len(runstatus)>0:
# #         for open_orders in runstatus:
# #             print(f"{open_orders}!")
# #             transformed_text = open_orders['strategy'].split('_')
# #             open_nifty = ('_'.join(transformed_text[:2]))
# #             if open_nifty == f"{strategy_prefix}_{self.parent.index}":
# #                 running_orders.append({open_nifty:open_orders['pricetype'],'pricetype':open_orders['pricetype'],'orderid':open_orders['orderid']})
# #     print(len(running_orders))
# #     if len(running_orders)==1:
# #         self.cancelorder(order_id=running_orders[0]['orderid'], strategy=f"{strategy_prefix}_{self.parent.index}")
# #         runstatus =  self.get_running_orders(strategy_prefix)
# #         print(len(runstatus))


# # break
# # if len(completed_orders) > 0:
# #     print(completed_orders)
# #     break
# else:
#     runstatus = self.place_145_order_set(self,ENTRY_TRIGGER,SL_POINTS,TARGET_POINTS,symbol,strategy_prefix)
# return True