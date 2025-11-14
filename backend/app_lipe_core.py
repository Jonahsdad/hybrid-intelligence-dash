from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HIS – LIPE Core", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

# --- include routers AFTER app is created, and avoid heavy work at import time ---
try:
    from backend.routes.forecast import router as forecast_router
    app.include_router(forecast_router, prefix="/v1")
except Exception as e:
    # Don’t crash boot if optional routes fail; check logs instead
    @app.get("/v1/forecast/disabled")
    def disabled():
        return {"error": "forecast router not loaded", "detail": str(e)}
