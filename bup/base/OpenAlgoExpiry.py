class OpenAlgoExpiry:
    """
    Utility class to handle expiry related operations using OpenAlgo
    """

    def __init__(self, client):
        """
        Initialize with OpenAlgo API client
        """
        self.client = client

    def fetch_expiry(self, symbol="NIFTY", exchange="NFO", instrumenttype="options"):
        """
        Fetch all available expiry dates for a symbol

        Returns:
            list: Expiry dates like ['26SEP25', '03OCT25', ...]
        """
        response = self.client.expiry(
            symbol=symbol,
            exchange=exchange,
            instrumenttype=instrumenttype
        )

        if response.get("status") != "success":
            raise ValueError(f"Failed to fetch expiry dates: {response}")

        return response.get("data", [])

    def nearest_expiry(self, symbol="NIFTY", exchange="NFO", instrumenttype="options"):
        """
        Get nearest (current weekly) expiry
        """
        # print("Get nearest #(current weekly) expiry")
        expiries = self.fetch_expiry(symbol, exchange, instrumenttype)
        #print(expiries)
        return expiries[0] if expiries else None

    def all_expiries(self, symbol="NIFTY", exchange="NFO", instrumenttype="options"):
        """
        Get all expiries (alias method)
        """
        return self.fetch_expiry(symbol, exchange, instrumenttype)
