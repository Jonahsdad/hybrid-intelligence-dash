from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

class ForecastReq(BaseModel):
    arena: Literal["crypto"]
    symbol: str = Field(..., description="BTCUSDT / ETHUSDT etc.")
    horizon: int = Field(ge=1, le=30, default=5)

class FcPoint(BaseModel):
    ts: str
    yhat: float
    q10: float
    q90: float

class ForecastResp(BaseModel):
    meta: Dict[str, Any]
    metrics: Dict[str, float]
    forecast: Dict[str, List[FcPoint]]
    series_tail: List[Dict[str, Any]]

class Rule(BaseModel):
    field: Literal["edge","entropy","drawdown"]
    op: Literal[">=", "<="]
    value: float

class StrategySpec(BaseModel):
    arena: Literal["crypto"]
    symbol: str
    horizon: int = 5
    lookback_days: int = 180
    enter: List[Rule] = []
    exit: List[Rule] = []

class EqPoint(BaseModel):
    ts: str
    equity: float

class StrategyResp(BaseModel):
    metrics: Dict[str, float]
    equity_curve: List[EqPoint]

class ShareCreateReq(BaseModel):
    arena: str
    symbol: str
    horizon: int
    ttl_hours: int = 24
