
from base.OpenAlgoOrders import OpenAlgoOrders
from base.TrailingTargetStopPercent import TrailingTargetStopPercent
from base.OpenAlgoExpiry import OpenAlgoExpiry
import os,pytz,time
from openalgo import api
import pandas as pd
from datetime import datetime, timedelta, time as dtime
from dotenv import load_dotenv
class MainClass:
    def __init__(self,index='NIFTY'):        
        load_dotenv()
        self.strategy_name = "MyStrategy"
        self.index = index
        self.debug = True
        if self.index == "NIFTY" or self.index == "BANKNIFTY" or self.index == "FINNIFTY" or self.index == "MIDCPNIFTY" or self.index == "SENSEX"  :
            self.exchange="NSE_INDEX"
            self.underlying_exchange ="NSE_INDEX"
            self.exchangeExpiory="NFO"
            self.exchangeSymbol="NFO"
        if self.index == "NIFTY":
            self.quantity = 65
            self.STRIKE_STEP = 50
            self.STRIKE_RANGE =10
        if self.index == "BANKNIFTY":
            self.quantity = 30
            self.STRIKE_STEP = 100
            self.STRIKE_RANGE =5
        self._LAST_LTP_CALL = {}
        self.exit_all = {"PE":{"NIFTY":False,"BANKNIFTY":False},"CE":{"NIFTY":False,"BANKNIFTY":False}}
        # Get API key
        api_key = os.getenv('OPENALGO_APIKEY')
        if not api_key:
            raise EnvironmentError("❌ OPENALGO_APIKEY environment variable not set")

        # Initialize OpenAlgo client
        self.client = api(
            api_key=api_key,
            host='http://127.0.0.1:5000'
        )

        # Expiry utility
        self.expiry_util = OpenAlgoExpiry(self.client)
        self.order_util = OpenAlgoOrders(self)
        self.trailing_target = TrailingTargetStopPercent(entry_price=100,    sl_pct=20, target_pct=40,    trail_step_pct=10)
        self.expiry_date = self.expiry_util.nearest_expiry(self.index,self.exchangeExpiory)        

        print("📅 Using Expiry:", self.expiry_date)
        

    def place_atm_call(self):
        """
        Place ATM CE order 
        """
        expiry_date = self.get_expiry()

        response = self.client.optionsorder(
            strategy=self.strategy_name,
            underlying=self.index,
            exchange=self.exchange,
            expiry_date=expiry_date,
            offset="ATM",
            option_type="CE",
            action="BUY",
            quantity=self.qantity,        
            pricetype="MARKET",
            product="NRML",
            splitsize=0
        )

        print("Order Response:", response)
        return response

    def place_atm_put(self):
        """
        Place ATM PE order for
        """
        expiry_date = self.get_expiry()

        response = self.client.optionsorder(
            strategy=self.strategy_name,
            underlying=self.index,
            exchange=self.exchange,
            expiry_date=expiry_date,
            offset="ATM",
            option_type="PE",
            action="BUY",
            quantity=self.qantity,
            pricetype="MARKET",
            product="NRML",
            splitsize=0
        )

        print("Order Response:", response)
        return response
    
    def get_atm(self):
        now = time.time()
        last = self._LAST_LTP_CALL.get(2, 0)

        if now - last < 2:
            return None  # skip API call

        self._LAST_LTP_CALL[self.index] = now
        

        # Fetch NIFTY LTP
        quote = self.client.quotes(symbol=self.index, exchange=self.exchange)
        if quote['status'] !='error':
            # print(quote)  # print quotes immediately as your rule
            df_quote = pd.DataFrame([quote["data"]])            
            #print(df_quote)
            ltp = quote["data"]["ltp"]
            high = quote["data"]["high"]
            low = quote["data"]["low"]
            open = quote["data"]["open"]
            prev_close = quote["data"]["prev_close"]
            print(f"\n📌 {self.index}")
            print(f"📌 LTP: {ltp} ")
            print(f"📌 high: {high}")
            print(f"📌 low: {low} ")
            print(f"📌 open: {open}")
            print(f"📌 prev_close: {prev_close}")
            # print(f"\n📌 {self.index} low: {quote["data"]["low"]} ")
            # print(f"\n📌 {self.index} open: {quote["data"]["open"]} ")
            # print(f"\n📌 {self.index} prev_close: {quote["data"]["prev_close"]} ")
            # NIFTY strike interval = 100
            strike_interval = 100
            # Compute ATM strike
            atm = round(ltp / strike_interval) * strike_interval
            return atm
        else:
            return quote
            
    def run(self):
        """
        Strategy execution point
        """
        print("🚀 Running MyStrategy")
        constants = {"expiry_date":self.expiry_date}
        # Example logic (modify as needed)
        #self.place_atm_call()
        return self.client
    
    def get_last_min_candle(self,lMinit=5,candlePosition=-1,startingDate =datetime.now().strftime("%Y-%m-%d") ,endDate = datetime.now().strftime("%Y-%m-%d")):
        interval=f"{lMinit}m"
        df = self.client.history(
            symbol=self.index,
            exchange="NSE_INDEX",
            interval=interval,
            start_date=startingDate,
            end_date=endDate
        )
        try:
            # ------------------------------------------
            # SAFETY CHECK (MANDATORY)
            # ------------------------------------------
            if isinstance(df, dict):
                print("❌ History error:", df['message'])
                return None

            if df.empty:
                print("❌ History returned empty DataFrame")
                return None
            # Ensure datetime index
            if not isinstance(df.index, pd.DatetimeIndex):
                df.index = pd.to_datetime(df.index)
            
            last_candle = df.iloc[candlePosition]   # most recent 5m candle
            candle_time = df.index[candlePosition] 
            #print(f"\n📌 Last {lMinit}-minute {candlePosition}candle:")
            #print(last_candle)
            #print(f"\n⏰ Candle Time: {candle_time.strftime('%Y-%m-%d %H:%M:%S')}")
            return df
        except Exception as e:
            print("Error:", e)
            return e
        
    def is_after_IST(self,timeVal=9,minVal=45):
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist).time()
        return now_ist >= dtime(timeVal, minVal)
    
    

    def safe_ltp(self,symbol, exchange="NFO", cooldown=2):
        """
        Fetch LTP safely using OpenAlgo quotes()
        cooldown = minimum seconds between calls per symbol
        """
        now = time.time()
        last = self._LAST_LTP_CALL.get(symbol, 0)

        if now - last < cooldown:
            return None  # skip API call

        self._LAST_LTP_CALL[symbol] = now

        resp = self.client.quotes(symbol=symbol, exchange=exchange)

        if resp.get("status") != "success":
            print("⚠️ Quote error:", resp)
            return None

        return resp["data"].get("ltp")
    
    # ==============================
    # UTILS
    # ==============================
    def next_5min_close(self,dt):
        """Return next 5-min candle close time"""
        minute = (dt.minute // 5 + 1) * 5
        if minute == 60:
            return dt.replace(hour=dt.hour + 1, minute=0, second=0, microsecond=0)
        return dt.replace(minute=minute, second=0, microsecond=0)


    def get_last_completed_5min_candle(self):
        INTERVAL_MIN = 5
        """Fetch last completed 5-min candle safely"""
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        df = self.get_last_min_candle(
            INTERVAL_MIN,
            -1,
            start_date,
            end_date
        )

        if not isinstance(df, pd.DataFrame) or df.empty or len(df) < 2:
            return None

        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)

        return df.iloc[-2]   # ✅ last COMPLETED candle