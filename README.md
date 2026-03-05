# Strategies

Intraday options strategies built on the shared `base/` framework, connecting to a locally running [OpenAlgo](https://github.com/marketcalls/openalgo) server.

---

## Directory Structure

```
strategies/
├── base/                             # Shared framework
│   ├── MainClass.py                  # Core class: client, expiry, ATM, candle utilities
│   ├── OpenAlgoOrders.py             # Order placement, bracket SL/target, trailing stop
│   ├── OpenAlgoExpiry.py             # Nearest expiry resolver
│   ├── OptionChainDB.py              # SQLite cache for daily strike selections
│   ├── TrailingTargetStopPercent.py  # Percent-based trailing SL/target tracker
│   └── __init__.py
│
├── live/                             # Ready-to-run strategies
│   ├── 5ema_opt_nifty.py             # 5-EMA pullback — NIFTY options
│   ├── 5ema_opt_bank.py              # 5-EMA pullback — BANKNIFTY options
│   ├── 145_nifty.py                  # ₹145 entry trigger — NIFTY options
│   ├── 145_bank.py                   # ₹145 entry trigger — BANKNIFTY options
│   ├── 145_strikefinder.py           # Strike scanner for the ₹145 strategy
│   ├── run_5ema_nifty.bat            # Windows launcher (auto-restarts on crash)
│   ├── run_5ema_bank.bat
│   ├── run_145_nifty.bat
│   ├── run_145_bank.bat
│   └── run_app.bat                   # Runs all strategies together
│
├── examples/                         # Starter templates
│   ├── simple_ema_strategy.py
│   └── macd_strategy.py
│
└── README.md
```

---

## Prerequisites

- OpenAlgo server running at `http://127.0.0.1:5000` with an active broker session.
- A valid API key added to the root `.env`:
  ```env
  OPENALGO_APIKEY=your_api_key_here
  ```
- Python packages: `openalgo`, `python-dotenv`, `pandas`, `colorama`, `pytz`

---

## Base Framework

### `MainClass`

The entry point for every strategy.

```python
from base.MainClass import MainClass
main = MainClass('NIFTY')  # or 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX'
```

| Attribute / Method | Description |
|---|---|
| `main.client` | Authenticated OpenAlgo API client |
| `main.expiry_date` | Nearest expiry (auto-resolved on init) |
| `main.order_util` | `OpenAlgoOrders` instance |
| `main.quantity` | Default lot quantity for the index |
| `main.STRIKE_STEP` | Strike price interval |
| `get_atm()` | Current ATM strike (throttled) |
| `safe_ltp(symbol)` | LTP with per-symbol cooldown |
| `get_last_min_candle(n, pos, start, end)` | n-minute OHLCV DataFrame |
| `is_after_IST(hour, minute)` | Time-of-day guard (IST) |
| `next_5min_close(dt)` | Next 5-min candle close timestamp |

### `OpenAlgoOrders` (`main.order_util`)

Handles all order operations.

| Method | Description |
|---|---|
| `get_running_orders()` | Fetch open/pending orders |
| `get_orders_by_stratagy(name)` | Filter orders by strategy prefix |
| `bracket_targe_sell(symbol, sl, target, ...)` | Place SL-M + LIMIT sell bracket |
| `run_145_option_trade(...)` | Full ₹145 trade loop per strike |
| `identify_5ema_trigger(...)` | Detect 5-EMA pullback entry signal |
| `trigger_5ema_bracketOrder(...)` | Place bracket after 5-EMA entry |
| `trail_sl_m_safe(...)` | Trail a SL-M order safely |
| `get_option_greeks(symbol, underlying)` | Fetch delta / gamma / theta |

### Other Base Classes

| Class | Purpose |
|---|---|
| `OpenAlgoExpiry` | Resolves nearest expiry date for an index + exchange |
| `OptionChainDB` | SQLite cache — persists CE/PE strike selections across restarts |
| `TrailingTargetStopPercent` | Tracks trailing SL/target by configurable percentage steps |

---

## Live Strategies

### 5-EMA Pullback (`5ema_opt_nifty.py` / `5ema_opt_bank.py`)

Enters when the 5-minute EMA(5) shows a pullback signal (prior candle low vs EMA relationship). After entry, calculates a delta-adjusted SL and places a bracket order. Trails the SL-M as profit grows. Exits at **15:15 IST**.

```python
# Key constant
deltaValue = 0.50   # fallback delta when greeks are unavailable
```

### ₹145 Entry Trigger (`145_nifty.py` / `145_bank.py`)

Monitors pre-selected CE+PE strikes (LTP ₹150–₹170 at open) and enters when LTP crosses ₹185 (configurable). Waits for the 5-min candle to close, then places a bracket. Trails SL through fixed LTP levels. Exits at **15:00 IST** or after the daily trade limit per side.

```python
# Key constants
ENTRY_TRIGGER = 185   # entry LTP
SL_POINTS     = 30
TARGET_POINTS = 45
```

---

## Running a Strategy

**Direct Python:**
```bash
python strategies/live/5ema_opt_nifty.py
```

**Windows `.bat` launcher** (auto-restarts on crash — recommended for live trading):
```
run_5ema_nifty.bat
run_5ema_bank.bat
run_145_nifty.bat
run_145_bank.bat
run_app.bat            # all at once
```

---

## Writing a New Strategy

```python
import sys, os
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from base.MainClass import MainClass
import time

main = MainClass('NIFTY')

while True:
    if main.is_after_IST(15, 30):
        break
    if main.is_after_IST(9, 15):
        atm = main.get_atm()
        # Your signal + order logic here using main.order_util
    time.sleep(5)
```

> Use `main.order_util` for all orders to stay consistent with strategy naming conventions.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'base'` | Add the `sys.path` bootstrap shown above, or run via a `.bat` launcher |
| `OPENALGO_APIKEY not set` | Add `OPENALGO_APIKEY=...` to the root `.env` file |
| Quote / history API errors | Ensure the OpenAlgo server is running with an active broker session |
| Strategy stops after one trade | Check `days_limit` / `exit_all` flags — the strategy exits when the daily limit is reached |
