from __future__ import annotations
import os, time, math, random
from typing import Any, Dict, List
import requests

_API_BASE = (os.getenv("HIS_API_BASE") or "").rstrip("/")
_TIMEOUT = (4, 25)

def forecast(arena: str, symbol: str, horizon: int) -> Dict[str, Any]:
    if _API_BASE:
        r = requests.post(
            f"{_API_BASE}/v1/forecast",
            json={"arena": arena, "symbol": symbol, "horizon": horizon},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    # synthetic fallback
    n = 200
    now = int(time.time())
    step = 60*60
    last = 50000.0
    pts: List[Dict[str, Any]] = []
    vol = 0.012
    for h in range(1, horizon+1):
        t = now + h*step
        yh = last * (1 + 0.0004*h)
        q  = last * vol * (h ** 0.5)
        pts.append({"ts": t, "yhat": yh, "q10": yh - q, "q90": yh + q})
    return {
        "event": {"arena": arena, "symbol": symbol, "horizon": horizon,
                  "forecast": {"points": pts},
                  "metrics": {"entropy": 0.31, "edge": 0.06, "regime": "EXPANSION"}}
    }
