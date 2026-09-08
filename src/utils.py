"""
utils.py — small helpers shared by preprocess/feature_engineering/train/
evaluate/predict so none of those files repeat this logic.
"""
import json
import logging
import sys

import joblib


def get_logger(name: str) -> logging.Logger:
    """Return a configured stdout logger (used instead of bare prints)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        ))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def iqr_bounds(series, k: float = 1.5):
    """Return (lower, upper) Tukey fences for outlier detection."""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def time_bucket(hour: int) -> str:
    """Bucket an hour-of-day (0-23) into a coarse time-of-day label."""
    if hour < 5:
        return "Night"
    if hour < 12:
        return "Morning"
    if hour < 17:
        return "Afternoon"
    if hour < 21:
        return "Evening"
    return "Night"


def save_json(obj: dict, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, default=str)


def load_json(path) -> dict:
    with open(path) as f:
        return json.load(f)


def save_model(obj, path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, path)


def load_model(path):
    return joblib.load(path)
