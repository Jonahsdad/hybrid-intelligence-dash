from __future__ import annotations
import statistics, math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from lipe_core.models import ForecastReq, ForecastResp, FcPoint, StrategySpec, StrategyResp, EqPoint
from lipe_core.data import fetch_ohlcv_daily

def _ts_iso(ms:int)->str:
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc).isoformat()

def _entropy(returns: List[float]) -> float:
    if not returns: return 1.0
    vol = statistics.pstdev(returns) or 1e-9
    # squash to 0..1-ish
    return max(0.0, min(1.0, vol / 0.05))

def _edge(returns: List[float]) -> float:
    if not returns: return 0.0
    mu = statistics.mean(returns)
    vol = statistics.pstdev(returns) or 1e-9
    return float(mu / vol)  # Sharpe-ish

def run_forecast(req: ForecastReq) -> ForecastResp:
    rows = fetch_ohlcv_daily(req.symbol, limit=300)
    closes = [c for _,c in rows]
    rets = [ (closes[i]/closes[i-1]-1.0) for i in range(1,len(closes)) ]
    ent = _entropy(rets[-90:])
    edg = _edge(rets[-90:])
    regime = "Compression→Expansion" if ent < 0.35 else "Chop"

    last_ms, last_close = rows[-1]
    horizon = req.horizon
    # simple Gaussian walk using mu/vol
    mu = statistics.mean(rets[-60:]) if len(rets)>60 else statistics.mean(rets[-20:])
    vol = statistics.pstdev(rets[-60:]) if len(rets)>60 else statistics.pstdev(rets[-20:]) or 0.02
    pts: List[FcPoint] = []
    price = last_close
    for d in range(1, horizon+1):
        price *= (1 + mu)
        # 80% band approx
        band = 1.28 * vol * math.sqrt(d)
        q10 = price * (1 - band)
        q90 = price * (1 + band)
        ts = _ts_iso(last_ms + d*24*3600*1000)
        pts.append(FcPoint(ts=ts, yhat=float(price), q10=float(q10), q90=float(q90)))

    meta = {
        "arena": req.arena,
        "symbol": req.symbol,
        "model": "lipe.naive_ewma.v1",
        "data_source": "ccxt/binance_or_synthetic",
        "generated_at": _ts_iso(last_ms),
        "regime": regime,
    }
    metrics = {"entropy": float(ent), "edge": float(edg)}
    series_tail = [{"ts": _ts_iso(t), "close": c} for t,c in rows[-60:]]
    return ForecastResp(meta=meta, metrics=metrics, forecast={"points": pts}, series_tail=series_tail)

def _rule_hit(val: float, op: str, thresh: float)->bool:
    return (op == ">=" and val >= thresh) or (op == "<=" and val <= thresh)

def backtest_strategy(spec: StrategySpec) -> StrategyResp:
    rows = fetch_ohlcv_daily(spec.symbol, limit=spec.lookback_days+30)
    closes = [c for _,c in rows]
    rets = [ (closes[i]/closes[i-1]-1.0) for i in range(1,len(closes)) ]
    ent = _entropy(rets[-90:])
    edg = _edge(rets[-90:])

    # naive backtest: daily step with same signals (for demo)
    equity = 1.0
    peak = 1.0
    in_pos = False
    curve: List[EqPoint] = []
    wins = 0; trades = 0
    for i in range(1, len(closes)):
        # evaluate signals using current ent/edge (demo)
        enter_ok = all(_rule_hit(edg if r.field=="edge" else ent, r.op, r.value) for r in spec.enter)
        exit_ok  = any(_rule_hit(edg if r.field=="edge" else ent, r.op, r.value) for r in spec.exit) if spec.exit else False
        if not in_pos and enter_ok:
            in_pos = True; trades += 1
            entry = closes[i]
        elif in_pos and exit_ok:
            in_pos = False
            if closes[i] > entry: wins += 1

        if in_pos:
            equity *= (closes[i]/closes[i-1])
        peak = max(peak, equity)
        curve.append(EqPoint(ts=_ts_iso(rows[i][0]), equity=float(equity)))

    hit = (wins/trades) if trades else 0.0
    maxdd = float(1.0 - min(p.equity for p in curve)/max(peak,1e-9)) if curve else 0.0
    roi = float(curve[-1].equity-1.0) if curve else 0.0
    return StrategyResp(metrics={"HitRate": hit, "ROI": roi, "MaxDD": maxdd, "Trades": trades}, equity_curve=curve)
