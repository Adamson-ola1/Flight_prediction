"""
config.py
Central place for paths, constants and hyperparameters used across the
project (src/, backend/, main.py). Keeping this in one file means every
script agrees on where data/models/outputs live.
"""
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "data.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "processed_data.csv"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

CHARTS_DIR = PROJECT_ROOT / "charts"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
PLOTS_DIR = OUTPUTS_DIR / "plots"
PREDICTIONS_PATH = OUTPUTS_DIR / "predictions.csv"
METRICS_PATH = OUTPUTS_DIR / "metrics.json"

TRAINED_MODEL_PATH = MODELS_DIR / "trained_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"  # fitted ColumnTransformer (scaler + encoder)

for d in (DATA_DIR / "raw", DATA_DIR / "processed", EXTERNAL_DATA_DIR,
          CHARTS_DIR, MODELS_DIR, OUTPUTS_DIR, PLOTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Modeling constants
# ---------------------------------------------------------------------------
TARGET_COL = "price"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Columns dropped because they leak post-flight info, are redundant, or are
# high-cardinality identifiers that don't generalize.
LEAKAGE_COLS = ["dep_delay", "arr_delay", "arr_time", "air_time"]
REDUNDANT_COLS = ["year", "dep_time"]
IDENTIFIER_COLS = ["flight", "tailnum"]
DROP_COLS = LEAKAGE_COLS + REDUNDANT_COLS + IDENTIFIER_COLS

CATEGORICAL_COLS = ["carrier", "origin", "season", "time_of_day"]

# Synthetic price-formula constants (see docs/model_card.md for rationale)
CARRIER_PREMIUM = {
    "UA": 18, "AA": 22, "DL": 20, "US": 12, "B6": 8, "VX": 25,
    "9E": 5, "EV": 0, "F9": -10, "FL": -8, "HA": 30, "MQ": 2,
    "OO": 3, "WN": -15, "YV": 0, "AS": 15,
}
ORIGIN_PREMIUM = {"JFK": 10, "EWR": 4, "LGA": 0}
BASE_FARE = 45
MIN_PRICE = 39.0

SEASON_MAP = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring", 5: "Spring",
    6: "Summer", 7: "Summer", 8: "Summer",
    9: "Fall", 10: "Fall", 11: "Fall",
}

# Hyperparameters for each candidate model (kept identical to the exploration
# notebook so results are reproducible between notebooks/ and src/train.py)
MODEL_PARAMS = {
    "RandomForest": dict(n_estimators=200, max_depth=12, random_state=RANDOM_STATE, n_jobs=-1),
    "XGBoost": dict(n_estimators=300, max_depth=6, learning_rate=0.08, random_state=RANDOM_STATE, n_jobs=-1),
    "LightGBM": dict(n_estimators=300, max_depth=6, learning_rate=0.08, random_state=RANDOM_STATE, verbosity=-1),
}
STACKING_PARAMS = {
    "rf": dict(n_estimators=150, max_depth=10, random_state=RANDOM_STATE, n_jobs=-1),
    "xgb": dict(n_estimators=200, max_depth=5, learning_rate=0.08, random_state=RANDOM_STATE, n_jobs=-1),
    "lgbm": dict(n_estimators=200, max_depth=5, learning_rate=0.08, random_state=RANDOM_STATE, verbosity=-1),
}

API_HOST = "0.0.0.0"
API_PORT = 8000
