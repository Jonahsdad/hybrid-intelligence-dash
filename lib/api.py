from __future__ import annotations
import os, time, math
from typing import Any, Dict, List
import requests

_API = (os.getenv("HIS_API_BASE") or "").rstrip("/")
_TIMEOUT = (4, 25)

def forecast(arena: str, symbol: str, horizon: int) -> Dict[str, Any]:
    if _API:
        r = requests.post(f"{_API}/v1/forecast",
                          json={"arena": arena, "symbol": symbol, "horizon": horizon},
                          timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()

    # synthetic fallback (same shape)
    now = int(time.time()); step = 3600; last = 50000.0; vol = 0.012
    pts: List[Dict[str, Any]] = []
    for h in range(1, horizon+1):
        t  = now + h*step
        yh = last * (1 + 0.0004*h)
        q  = last * vol * (h ** 0.5)
        pts.append({"ts": t, "yhat": yh, "q10": yh - q, "q90": yh + q})
    return {"event":{"arena":arena,"symbol":symbol,"horizon":horizon,
                     "forecast":{"points":pts},
                     "metrics":{"entropy":0.31,"edge":0.06,"regime":"EXPANSION"}}}
