class TrailingTargetStopPercent:
    def __init__(
        self,
        entry_price: float,
        sl_pct: float,
        target_pct: float,
        trail_step_pct: float
    ):
        """
        entry_price   : Entry price
        sl_pct        : Stop loss percentage (e.g. 20 for 20%)
        target_pct    : Initial target percentage (e.g. 40)
        trail_step_pct: Trailing step percentage (e.g. 10)
        """

        self.entry = entry_price
        self.sl_pct = sl_pct
        self.target_pct = target_pct
        self.trail_step_pct = trail_step_pct

        self.max_price = entry_price

        # Initial SL & Target
        self.stop_loss = entry_price * (1 - sl_pct / 100)
        self.target = entry_price * (1 + target_pct / 100)

    def update(self, ltp: float):
        """
        Update trailing SL and Target based on LTP
        """
        if ltp > self.max_price:
            self.max_price = ltp

            # How many trail steps price has moved
            move_pct = ((self.max_price - self.entry) / self.entry) * 100
            steps = int(move_pct // self.trail_step_pct)

            # Trail target
            self.target = self.entry * (
                1 + (self.target_pct + steps * self.trail_step_pct) / 100
            )

            # Trail stop loss (always behind target)
            self.stop_loss = self.max_price * (1 - self.sl_pct / 100)

        return round(self.stop_loss, 2), round(self.target, 2)

    def should_exit(self, ltp: float):
        """
        Exit conditions
        """
        if ltp <= self.stop_loss:
            return "SL HIT"

        if ltp >= self.target:
            return "TARGET HIT"

        return None
