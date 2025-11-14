# hybrid-intelligence-dash
# HIS — Dash Flagship

## 1) Set backend URL
Your FastAPI (LIPE Core) must expose:
- POST /v1/forecast
- POST /v1/explain/forecast
- POST /v1/share/create
- POST /v1/auth/login
- GET  /v1/public/{slo.json,accuracy.json,plans.json}
- POST /v1/billing/checkout (optional)

## 2) Run locally
export API_BASE_URL=http://localhost:8000
python -m pip install -r requirements.txt
python -m dash_app.app

## 3) Deploy on Render
- Push this repo
- Create Web Service → it reads render.yaml
- Set API_BASE_URL env var to your backend
- Open the URL → Home → Crypto → Run Forecast
# HIS – LIPE Core (Railway)

Minimal FastAPI backend powering the Streamlit Crypto Flagship.

Endpoints:
- GET /healthz
- POST /v1/forecast  {arena:"crypto", symbol:"BTCUSDT", horizon:5}
- POST /v1/strategy/eval
- GET /v1/public/slo.json
- GET /v1/public/accuracy.json
- POST /v1/share/create
- GET /v1/share/{token}

Env:
- HIS_ALLOWED_ORIGINS="*"
- CCXT_EXCHANGE="binance"

Start locally:
  pip install -r requirements.txt
  uvicorn app_lipe_core:app --reload

Deploy on Railway: connect repo → set env vars → deploy.
