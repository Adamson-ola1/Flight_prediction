"""
predict.py — reproduces the cleaning/feature-engineering steps for a
*single* new flight record, then feeds it through the saved best model
(models/trained_model.pkl). Used by both backend/main.py and the CLI
entry point below.
"""
import numpy as np
import pandas as pd

import config
from src.utils import get_logger, load_json, load_model, time_bucket

log = get_logger(__name__)

_model = None
_feature_maps = None


def _get_model():
    global _model
    if _model is None:
        if not config.TRAINED_MODEL_PATH.exists():
            raise FileNotFoundError(
                f"No trained model at {config.TRAINED_MODEL_PATH}. Run `python main.py` first."
            )
        _model = load_model(config.TRAINED_MODEL_PATH)
    return _model


def _get_feature_maps():
    global _feature_maps
    if _feature_maps is None:
        from src.feature_engineering import FEATURE_MAPS_PATH
        if not FEATURE_MAPS_PATH.exists():
            raise FileNotFoundError(
                f"No feature maps at {FEATURE_MAPS_PATH}. Run `python main.py` first."
            )
        _feature_maps = load_json(FEATURE_MAPS_PATH)
    return _feature_maps


def prepare_single_flight(year: int, month: int, day: int, hour: int, minute: int,
                           carrier: str, origin: str, dest: str, distance: float) -> pd.DataFrame:
    """Turn one raw flight description into a model-ready feature row."""
    maps = _get_feature_maps()
    route_freq_map = maps["route_freq_map"]
    dest_freq_map = maps["dest_freq_map"]

    date = pd.Timestamp(year=year, month=month, day=day)
    weekday_ = date.weekday()

    row = {
        "month": month, "day": day, "carrier": carrier, "origin": origin,
        "distance": distance, "hour": hour, "minute": minute,
        "weekday": weekday_, "is_weekend": int(weekday_ in (5, 6)),
        "season": config.SEASON_MAP[month],
        "time_of_day": time_bucket(hour),
        "route_freq": route_freq_map.get(f"{origin}_{dest}", 0.0),
        "dest_freq": dest_freq_map.get(dest, 0.0),
        "month_sin": np.sin(2 * np.pi * month / 12),
        "month_cos": np.cos(2 * np.pi * month / 12),
        "hour_sin": np.sin(2 * np.pi * hour / 24),
        "hour_cos": np.cos(2 * np.pi * hour / 24),
    }
    return pd.DataFrame([row])


def predict_price(year, month, day, hour, minute, carrier, origin, dest, distance) -> float:
    model = _get_model()
    row = prepare_single_flight(year, month, day, hour, minute, carrier, origin, dest, distance)
    price = float(model.predict(row)[0])
    return round(price, 2)


if __name__ == "__main__":
    sample = dict(year=2013, month=7, day=19, hour=8, minute=30,
                   carrier="DL", origin="JFK", dest="LAX", distance=2475)
    price = predict_price(**sample)
    log.info(f"Sample flight {sample['origin']} -> {sample['dest']} predicted price: ${price:.2f}")
