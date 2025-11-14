from __future__ import annotations
import math, time
from datetime import datetime, timezone, timedelta
from typing import List, Tuple
import os

try:
    import ccxt  # type: ignore
except Exception:
    ccxt = None

def _now():
    return datetime.now(timezone.utc)

def fetch_ohlcv_daily(symbol: str, limit: int = 365) -> List[Tuple[int,float]]:
    """
    Returns list of (ms, close). Tries ccxt (Binance). Falls back to synthetic.
    """
    # Try ccxt
    ex_name = os.getenv("CCXT_EXCHANGE", "binance")
    if ccxt:
        try:
            ex = getattr(ccxt, ex_name)()
            mkt = symbol.replace("USDT","/USDT")
            rows = ex.fetch_ohlcv(mkt, timeframe="1d", limit=limit)
            return [(r[0], float(r[4])) for r in rows]  # (time, close)
        except Exception:
            pass

    # Synthetic fallback
    out = []
    base = 30000.0 if symbol.upper().startswith("BTC") else 2000.0
    for i in range(limit):
        t = _now() - timedelta(days=limit-i)
        close = base * (1 + 0.12*math.sin(i/14.0) + 0.05*math.sin(i/5.5))
        out.append((int(t.timestamp()*1000), float(close)))
    return out
