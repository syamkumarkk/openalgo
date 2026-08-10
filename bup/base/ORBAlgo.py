from datetime import datetime
import time
import pandas as pd
class ORBAlgo:
    def __init__(self, client):
        """
        Initialize with OpenAlgo API client
        """
        self.client = client
    def testclass(self):
        print("sssssssss")
        # ==========================================
    # GET OPENING RANGE
    # ==========================================
    def calculate_opening_range(self,instruments=[],INTERVAL="5m", symbol="NIFTY", exchange="NFO", instrumenttype="options"):
        try:
            opening_ranges = {}
            for symbol in instruments:  
                start_date = datetime.now().strftime("%Y-%m-%d")
                end_date = datetime.now().strftime("%Y-%m-%d")
                df = self.client.history(
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
                # print(
                #     f"{symbol:<16} | "
                #     f"{opening_high:>10.2f} | "
                #     f"{opening_low:>10.2f} | "
                #     f"{datetime.now().strftime('%H:%M:%S'):>8}"
                # )
                # print("-" * 70)
                time.sleep(0.1)
            return opening_ranges
        except Exception as e:
            print(symbol, e)
