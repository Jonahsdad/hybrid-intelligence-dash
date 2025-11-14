from __future__ import annotations
import os, requests
from typing import Optional, Dict, Any

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
TIMEOUT  = (3, 25)

def _h(tok: Optional[str] = None) -> Dict[str, str]:
    h = {"Accept": "application/json"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

# ---------- Auth ----------
def login(email: str, team: str) -> Dict[str, Any]:
    r = requests.post(f"{API_BASE}/v1/auth/login",
                      json={"email": email, "team": team},
                      timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

# ---------- Core ----------
def forecast(tok: Optional[str], arena: str, symbol: str, horizon: int) -> Dict[str, Any]:
    r = requests.post(f"{API_BASE}/v1/forecast",
                      headers=_h(tok),
                      json={"arena": arena, "symbol": symbol, "horizon": horizon},
                      timeout=TIMEOUT)
    if r.status_code in (401, 402):
        return {"_error": r.status_code, "_json": r.json()}
    r.raise_for_status()
    return r.json()

def explain(tok: Optional[str], arena: str, symbol: str, horizon: int) -> Dict[str, Any]:
    r = requests.post(f"{API_BASE}/v1/explain/forecast",
                      headers=_h(tok),
                      json={"arena": arena, "symbol": symbol, "horizon": horizon},
                      timeout=TIMEOUT)
    return r.json() if r.ok else {}

def share_create(tok: Optional[str], arena: str, symbol: str, horizon: int, ttl_hours: int = 24) -> Dict[str, Any]:
    r = requests.post(f"{API_BASE}/v1/share/create",
                      headers=_h(tok),
                      json={"arena": arena, "symbol": symbol, "horizon": horizon, "ttl_hours": ttl_hours},
                      timeout=TIMEOUT)
    return r.json() if r.ok else {}

# ---------- Public ----------
def public_slo() -> Dict[str, Any]:
    r = requests.get(f"{API_BASE}/v1/public/slo.json", timeout=TIMEOUT)
    return r.json() if r.ok else {}

def public_accuracy() -> Dict[str, Any]:
    r = requests.get(f"{API_BASE}/v1/public/accuracy.json", timeout=TIMEOUT)
    return r.json() if r.ok else {}

def public_plans() -> Dict[str, Any]:
    r = requests.get(f"{API_BASE}/v1/public/plans.json", timeout=TIMEOUT)
    return r.json() if r.ok else {}

def billing_checkout(tok: Optional[str], arena: str) -> Dict[str, Any]:
    r = requests.post(f"{API_BASE}/v1/billing/checkout",
                      headers=_h(tok),
                      json={"arena": arena},
                      timeout=TIMEOUT)
    return r.json() if r.ok else {}
