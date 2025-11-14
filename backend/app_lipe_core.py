from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone, timedelta
from lipe_core.models import ForecastReq, ForecastResp, StrategySpec, StrategyResp, ShareCreateReq
from lipe_core.predict import run_forecast, backtest_strategy
from lipe_core.share import share_create, share_get

import os

APP_NAME = "HIS • LIPE Core"
API_PREFIX = "/v1"

app = FastAPI(title=APP_NAME)

# --- CORS (allow Streamlit app + local dev) ---
origins = [o.strip() for o in os.getenv("HIS_ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True, "name": APP_NAME, "ts": datetime.now(timezone.utc).isoformat()}

# -------- Forecast ----------
@app.post(f"{API_PREFIX}/forecast", response_model=ForecastResp)
def forecast(req: ForecastReq):
    try:
        return run_forecast(req)
    except Exception as e:
        raise HTTPException(500, f"forecast error: {e}")

# -------- Strategy eval/backtest ----------
@app.post(f"{API_PREFIX}/strategy/eval", response_model=StrategyResp)
def strategy_eval(spec: StrategySpec):
    try:
        return backtest_strategy(spec)
    except Exception as e:
        raise HTTPException(500, f"backtest error: {e}")

# -------- Public status ----------
@app.get(f"{API_PREFIX}/public/slo.json")
def slo_json():
    return {
        "service": APP_NAME,
        "p95_ms_forecast": 180,
        "uptime_7d": 0.999,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

@app.get(f"{API_PREFIX}/public/accuracy.json")
def accuracy_json():
    # stub – replace with RecStats later
    return {
        "Crypto": {"HitRate_7d": 0.61, "SMAPE_30d": 0.12},
        "Sports": {"HitRate_7d": 0.53},
        "Lottery": {"GFW_30d": 0.18},
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

# -------- Share links (in-memory) ----------
@app.post(f"{API_PREFIX}/share/create")
def share_create_route(body: ShareCreateReq):
    return share_create(body)

@app.get(f"{API_PREFIX}/share/{token}")
def share_get_route(token: str):
    obj = share_get(token)
    if not obj:
        raise HTTPException(404, "not found / expired")
    return obj
