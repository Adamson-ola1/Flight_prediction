"""
tests/test_pipeline.py — sanity checks for the ML pipeline and API.
Run with: pytest -v  (from the project root, after `python main.py` has
produced models/trained_model.pkl and models/feature_maps.json).
"""
import config
from src.predict import predict_price


def test_trained_model_exists():
    assert config.TRAINED_MODEL_PATH.exists(), "Run `python main.py` before testing."


def test_predict_price_is_reasonable():
    price = predict_price(
        year=2013, month=7, day=19, hour=8, minute=30,
        carrier="DL", origin="JFK", dest="LAX", distance=2475,
    )
    assert isinstance(price, float)
    assert 0 < price < 2000


def test_predict_price_short_hop_cheaper_than_long_haul():
    short = predict_price(year=2013, month=3, day=10, hour=10, minute=0,
                           carrier="B6", origin="JFK", dest="BOS", distance=187)
    long = predict_price(year=2013, month=3, day=10, hour=10, minute=0,
                          carrier="B6", origin="JFK", dest="LAX", distance=2475)
    assert short < long


def test_api_health():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_api_predict():
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)
    payload = {
        "year": 2013, "month": 7, "day": 19, "hour": 8, "minute": 30,
        "carrier": "DL", "origin": "JFK", "dest": "LAX", "distance": 2475,
    }
    resp = client.post("/api/predict", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "predicted_price" in body
    assert body["predicted_price"] > 0
