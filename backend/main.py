"""
backend/main.py — FastAPI service for the Flight Price Prediction model.

Run locally:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

API endpoints:
    GET  /
    GET  /health
    GET  /model/info
    POST /predict
    POST /predict/batch
    GET  /docs
"""

import sys
import time
from pathlib import Path

# ─────────────────────────────────────────────
# PROJECT ROOT
# ─────────────────────────────────────────────

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ─────────────────────────────────────────────
# FASTAPI
# ─────────────────────────────────────────────

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# ─────────────────────────────────────────────
# PROJECT MODULES
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# LOGGER
# ─────────────────────────────────────────────

log = get_logger("backend")


# ─────────────────────────────────────────────
# STARTUP MODEL CHECK
# ─────────────────────────────────────────────

startup_start = time.perf_counter()

MODEL_AVAILABLE = config.TRAINED_MODEL_PATH.exists()
FEATURE_MAPS_AVAILABLE = (
    config.MODELS_DIR / "feature_maps.json"
).exists()

if MODEL_AVAILABLE and FEATURE_MAPS_AVAILABLE:
    log.info("Flight prediction model and feature maps are available.")
else:
    if not MODEL_AVAILABLE:
        log.warning(
            f"Trained model not found: {config.TRAINED_MODEL_PATH}"
        )

    if not FEATURE_MAPS_AVAILABLE:
        log.warning(
            f"Feature maps not found: "
            f"{config.MODELS_DIR / 'feature_maps.json'}"
        )

startup_time = time.perf_counter() - startup_start

log.info(f"Backend startup checks completed in {startup_time:.3f}s")


# ─────────────────────────────────────────────
# FASTAPI APPLICATION
# ─────────────────────────────────────────────

app = FastAPI(
    title="Flight Price Prediction API",
    description=(
        "Machine learning API for predicting flight ticket prices "
        "from NYC departure airports."
    ),
    version="1.0.0",
)


# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────────

@app.get("/", tags=["System"])
def root():
    return {
        "message": "Flight Price Prediction API is running",
        "docs": "/docs",
        "health": "/health",
        "model_info": "/model/info",
        "predict": "/predict",
        "batch_predict": "/predict/batch",
    }

# ─────────────────────────────────────────────
# HEALTH
# ─────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health():
    model_loaded = (
        config.TRAINED_MODEL_PATH.exists()
        and (config.MODELS_DIR / "feature_maps.json").exists()
    )

    return HealthResponse(
        status="ok",
        model_loaded=model_loaded,
    )


# ─────────────────────────────────────────────
# MODEL INFO
# ─────────────────────────────────────────────

@app.get(
    "/model/info",
    response_model=MetricsResponse,
    tags=["Model"],
)
def model_info():

    if not config.METRICS_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "metrics.json not found. "
                "Run the training/evaluation pipeline first."
            ),
        )

    try:
        metrics = load_json(config.METRICS_PATH)

        return MetricsResponse(
            best_model=metrics["best_model"],
            leaderboard=metrics["leaderboard"],
            n_test_rows=metrics["n_test_rows"],
        )

    except KeyError as exc:
        log.error(f"Invalid metrics.json structure: missing {exc}")

        raise HTTPException(
            status_code=500,
            detail=f"Invalid metrics.json structure: missing {exc}",
        )

@app.post(
    "/api/predict",
    response_model=FlightPredictionResponse,
    tags=["Prediction"],
)
def api_predict(flight: FlightRequest):
    return predict(flight)

@app.get(
    "/api/metrics",
    response_model=MetricsResponse,
    tags=["Model"],
)
def api_metrics():
    return model_info()

# ─────────────────────────────────────────────
# SINGLE PREDICTION
# ─────────────────────────────────────────────

@app.post(
    "/predict",
    response_model=FlightPredictionResponse,
    tags=["Prediction"],
)
def predict(flight: FlightRequest):

    if not config.TRAINED_MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Trained model not found. "
                "Run the training/evaluation pipeline first."
            ),
        )

    feature_maps_path = config.MODELS_DIR / "feature_maps.json"

    if not feature_maps_path.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Feature maps not found. "
                "Run the feature-engineering/training pipeline first."
            ),
        )

    try:
        price = predict_price(**flight.model_dump())

        metrics = load_json(config.METRICS_PATH)

        return FlightPredictionResponse(
            predicted_price=price,
            currency="USD",
            model_used=metrics.get(
                "best_model",
                "unknown",
            ),
        )

    except Exception as exc:
        log.exception(
            f"Prediction failed for "
            f"{flight.origin} -> {flight.dest}"
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


# ─────────────────────────────────────────────
# BATCH PREDICTION
# ─────────────────────────────────────────────

@app.post(
    "/predict/batch",
    response_model=BatchFlightPredictionResponse,
    tags=["Prediction"],
)
def predict_batch(payload: BatchFlightRequest):

    if not config.TRAINED_MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Trained model not found. "
                "Run the training/evaluation pipeline first."
            ),
        )

    feature_maps_path = config.MODELS_DIR / "feature_maps.json"

    if not feature_maps_path.exists():
        raise HTTPException(
            status_code=503,
            detail=(
                "Feature maps not found. "
                "Run the feature-engineering/training pipeline first."
            ),
        )

    try:
        metrics = load_json(config.METRICS_PATH)

        best_model = metrics.get(
            "best_model",
            "unknown",
        )

        predictions = []

        for flight in payload.flights:

            price = predict_price(
                **flight.model_dump()
            )

            predictions.append(
                FlightPredictionResponse(
                    predicted_price=price,
                    currency="USD",
                    model_used=best_model,
                )
            )

        return BatchFlightPredictionResponse(
            predictions=predictions
        )

    except Exception as exc:
        log.exception("Batch prediction failed")

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

@app.post(
    "/api/predict/batch",
    response_model=BatchFlightPredictionResponse,
    tags=["Prediction"],
)
def api_predict_batch(payload: BatchFlightRequest):
    return predict_batch(payload)

# ─────────────────────────────────────────────
# LOCAL DEVELOPMENT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
    )