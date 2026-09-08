"""
backend/main.py — FastAPI service exposing the trained flight-price model.

Run locally:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

The React frontend (frontend/) talks to this API's /api/* routes.
"""
import sys
from pathlib import Path

# Allow `python backend/main.py` as well as `uvicorn backend.main:app`
# to both resolve the project-root imports (config, src.*).
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import config
from backend.schema import (
    BatchFlightPredictionResponse,
    BatchFlightRequest,
    FlightPredictionResponse,
    FlightRequest,
    HealthResponse,
    MetricsResponse,
)
from src.predict import predict_price
from src.utils import get_logger, load_json

log = get_logger("backend")

app = FastAPI(
    title="Flight Price Prediction API",
    description="Predicts NYC-departure domestic flight ticket price from a trained regression ensemble.",
    version="1.0.0",
)

# Allow the Vite dev server (and any deployed frontend origin) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _model_available() -> bool:
    return config.TRAINED_MODEL_PATH.exists()


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health():
    return HealthResponse(status="ok", model_loaded=_model_available())


@app.get("/api/metrics", response_model=MetricsResponse, tags=["Model"])
def get_metrics():
    if not config.METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="metrics.json not found — run `python main.py` first.")
    return load_json(config.METRICS_PATH)


@app.post("/api/predict", response_model=FlightPredictionResponse, tags=["Prediction"])
def predict(flight: FlightRequest):
    if not _model_available():
        raise HTTPException(status_code=503, detail="Model not trained yet — run `python main.py` first.")
    try:
        price = predict_price(**flight.model_dump())
    except Exception as exc:  # bad carrier code, unseen category, etc.
        log.error(f"Prediction failed: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))

    metrics = load_json(config.METRICS_PATH) if config.METRICS_PATH.exists() else {}
    return FlightPredictionResponse(
        predicted_price=price,
        model_used=metrics.get("best_model", "unknown"),
    )


@app.post("/api/predict/batch", response_model=BatchFlightPredictionResponse, tags=["Prediction"])
def predict_batch(payload: BatchFlightRequest):
    if not _model_available():
        raise HTTPException(status_code=503, detail="Model not trained yet — run `python main.py` first.")
    metrics = load_json(config.METRICS_PATH) if config.METRICS_PATH.exists() else {}
    best_model = metrics.get("best_model", "unknown")

    results = []
    for flight in payload.flights:
        try:
            price = predict_price(**flight.model_dump())
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid flight {flight}: {exc}")
        results.append(FlightPredictionResponse(predicted_price=price, model_used=best_model))
    return BatchFlightPredictionResponse(predictions=results)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
