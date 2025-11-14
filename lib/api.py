from __future__ import annotations
import os, time, math, random
from typing import Any, Dict, List
import requests

# Where your FastAPI lives (Railway/Render). No trailing slash.
_API_BASE = os.getenv("HIS_API_BASE", "").rstrip("/")
_TIMEOUT  = (4, 25)

def _base() -> str:
    return _API_BASE

def forecast(arena: str, symbol: str, horizon: int) -> Dict[str, Any]:
    """
    Calls LIPE Core if HIS_API_BASE is set.
    Falls back to synthetic bands so the page always works.
    Expected return:
    {
      "event": {
        "arena": arena, "symbol": symbol, "horizon": horizon,
        "forecast": {"points":[{"ts": "...", "yhat": float, "q10": float, "q90": float}, ...]},
        "metrics": {"entropy": float, "edge": float, "regime": "EXPANSION|COMPRESSION|NEUTRAL"}
      }
    }
    """
    if _base():
        r = requests.post(
            f"{_base()}/v1/forecast",
            json={"arena": arena, "symbol": symbol, "horizon": horizon},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    # --- synthetic fallback (no backend set) ---
    n = 200
    now = int(time.time())
    step = 60*60  # hourly synthetic candles
    xs = [now - (n - i)*step for i in range(n)]
    base = 50000.0
    series = [base + 2000.0*math.sin(i/9.0) + 400.0*math.sin(i/2.7) for i in range(n)]
    last = series[-1]
    pts: List[Dict[str, Any]] = []
    drift = random.uniform(-0.5, 0.5)
    vol   = 0.012
    for h in range(1, horizon+1):
        t  = now + h*step
        yh = last * (1.0 + drift*0.001*h)
        q  = last * vol * math.sqrt(h)
        pts.append({"ts": t, "yhat": yh, "q10": yh - q, "q90": yh + q})
    return {
        "event": {
            "arena": arena, "symbol": symbol, "horizon": horizon,
            "forecast": {"points": pts},
            "metrics": {"entropy": 0.32, "edge": 0.07, "regime": "EXPANSION"},
        }
    }
