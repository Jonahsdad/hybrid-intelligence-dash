# lib/api.py
from __future__ import annotations
import os, time
from typing import Any, Dict, Optional
import requests

# Base URL for your backend (Railway/Render/etc.)
_API_BASE = os.getenv("HIS_API_BASE", "").rstrip("/")
_TENANT_ID = os.getenv("HIS_TENANT_ID", "demo-tenant")
_USER_EMAIL = os.getenv("HIS_USER_EMAIL", "demo@user.dev")

TIMEOUT = (3, 25)

def set_api_base(base: str) -> None:
    """Allow pages to override at runtime (e.g., from st.secrets)."""
    global _API_BASE
    _API_BASE = (base or "").rstrip("/")

def _hdr(token: Optional[str] = None) -> Dict[str, str]:
    h = {
        "Accept": "application/json",
        "x-tenant-id": _TENANT_ID,
        "x-user-email": _USER_EMAIL,
    }
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

def login(email: str, team: str) -> Dict[str, Any]:
    # optional; only if your backend exposes /v1/auth/login
    r = requests.post(
        f"{_API_BASE}/v1/auth/login",
        json={"email": email, "team": team},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()

def api_lipe_forecast(
    token: Optional[str],
    arena: str,
    symbol: str,
    horizon: int
) -> Dict[str, Any]:
    r = requests.post(
        f"{_API_BASE}/v1/forecast",
        headers=_hdr(token),
        json={"arena": arena, "symbol": symbol, "horizon": horizon},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()

def api_lipe_strategy_eval(
    token: Optional[str],
    arena: str,
    symbol: str,
    spec: Dict[str, Any],
    lookback_days: int = 180
) -> Dict[str, Any]:
    r = requests.post(
        f"{_API_BASE}/v1/strategy/eval",
        headers=_hdr(token),
        json={"arena": arena, "symbol": symbol, "spec": spec, "lookback_days": lookback_days},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()

def api_checkout(
    token: Optional[str],
    arena: str,
    plan_id: str
) -> Dict[str, Any]:
    r = requests.post(
        f"{_API_BASE}/v1/billing/checkout",
        headers=_hdr(token),
        json={"arena": arena, "plan_id": plan_id},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()

# ---- Aliases to avoid changing older page code ----
forecast = api_lipe_forecast
strategy_backtest = api_lipe_strategy_eval
checkout = api_checkout
