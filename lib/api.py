# lib/api.py
from __future__ import annotations
import os, math, time, datetime as dt
from typing import Any, Dict, Optional, List
import requests

_API_BASE = os.getenv("HIS_API_BASE", "").rstrip("/")
_TENANT_ID = os.getenv("HIS_TENANT_ID", "demo-tenant")
_USER_EMAIL = os.getenv("HIS_USER_EMAIL", "demo@user.dev")
TIMEOUT = (3, 25)

def set_api_base(base: str) -> None:
    global _API_BASE
    _API_BASE = (base or "").rstrip("/")

def _hdr(token: Optional[str] = None) -> Dict[str, str]:
    h = {"Accept": "application/json", "x-tenant-id": _TENANT_ID, "x-user-email": _USER_EMAIL}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def ping() -> bool:
    if not _API_BASE:
        return False
    try:
        r = requests.get(f"{_API_BASE}/healthz", timeout=(2, 5))
        return r.status_code == 200
    except Exception:
        return False

def api_lipe_forecast(token: Optional[str], arena: str, symbol: str, horizon: int) -> Dict[str, Any]:
    """Calls backend if configured; otherwise returns a synthetic forecast so UI works now."""
    if _API_BASE:
        r = requests.post(
            f"{_API_BASE}/v1/forecast",
            headers=_hdr(token),
            json={"arena": arena, "symbol": symbol, "horizon": horizon},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return r.json()

    # ---- Fallback: synthetic forecast (so the page is usable without backend) ----
    now = dt.datetime.utcnow()
    points: List[Dict[str, Any]] = []
    for i in range(horizon + 30):
        t = now + dt.timedelta(days=i)
        base = 100 + 5 * math.sin(i / 3.2)
        band = 2.5 + 0.2 * i
        points.append({"ts": t.isoformat() + "Z", "yhat": base, "q10": base - band, "q90": base + band})

    return {
        "event": {
            "arena": arena,
            "symbol": symbol,
            "horizon": horizon,
            "forecast": {"points": points},
            "metrics": {"entropy": 0.33, "edge": 0.12, "regime": "Compression→Expansion"},
        }
    }

def api_lipe_strategy_eval(token: Optional[str], arena: str, symbol: str, spec: Dict[str, Any], lookback_days: int = 180) -> Dict[str, Any]:
    if not _API_BASE:
        # minimal synthetic response
        eq = [{"t": i, "equity": 100 + 0.3 * i} for i in range(lookback_days // 3)]
        return {"metrics": {"roi": 0.07, "hitrate": 0.58, "maxdd": 0.10}, "equity_curve": eq}
    r = requests.post(
        f"{_API_BASE}/v1/strategy/eval",
        headers=_hdr(token),
        json={"arena": arena, "symbol": symbol, "spec": spec, "lookback_days": lookback_days},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()

def api_checkout(token: Optional[str], arena: str, plan_id: str) -> Dict[str, Any]:
    if not _API_BASE:
        return {"url": "https://example.com/checkout"}
    r = requests.post(
        f"{_API_BASE}/v1/billing/checkout",
        headers=_hdr(token),
        json={"arena": arena, "plan_id": plan_id},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()

# Backwards-compatible aliases some pages use:
forecast = api_lipe_forecast
strategy_backtest = api_lipe_strategy_eval
checkout = api_checkout
