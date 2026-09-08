"""
feature_engineering.py — turns the cleaned frame from src/preprocess.py
into the model-ready feature table (notebooks/exploration.ipynb section 3).

`route_freq_map` / `dest_freq_map` are fit on the full processed dataset
and saved alongside the model so src/predict.py can reproduce identical
frequency encodings for a single new flight at inference time.
"""
import numpy as np
import pandas as pd

import config
from src.utils import get_logger, save_json, time_bucket

log = get_logger(__name__)

FEATURE_MAPS_PATH = config.MODELS_DIR / "feature_maps.json"


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    weekday = df.pop("_weekday") if "_weekday" in df.columns else pd.to_datetime(
        dict(year=2013, month=df.month, day=df.day)).dt.weekday
    df["weekday"] = weekday.values
    df["is_weekend"] = df["weekday"].isin([5, 6]).astype(int)

    df["season"] = df["month"].map(config.SEASON_MAP)
    df["time_of_day"] = df["hour"].apply(time_bucket)

    df["route"] = df["origin"] + "_" + df["dest"]
    route_freq_map = df["route"].value_counts(normalize=True)
    df["route_freq"] = df["route"].map(route_freq_map)

    dest_freq_map = df["dest"].value_counts(normalize=True)
    df["dest_freq"] = df["dest"].map(dest_freq_map)

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    # Persist the frequency maps so a single new flight can be encoded
    # identically at prediction time (unseen routes/destinations -> 0.0).
    save_json({
        "route_freq_map": route_freq_map.to_dict(),
        "dest_freq_map": dest_freq_map.to_dict(),
    }, FEATURE_MAPS_PATH)

    log.info(f"Feature engineering complete — shape {df.shape}")
    return df


def get_model_matrix(df: pd.DataFrame):
    """Split into X (features used by the model) and y (target)."""
    X = df.drop(columns=[config.TARGET_COL, "dest", "route"])
    y = df[config.TARGET_COL]
    return X, y


def run(df: pd.DataFrame):
    df_feat = engineer(df)
    config.PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_feat.to_csv(config.PROCESSED_DATA_PATH, index=False)
    log.info(f"Saved processed data -> {config.PROCESSED_DATA_PATH}")
    return df_feat


if __name__ == "__main__":
    from src.preprocess import run as preprocess_run
    df_feat = run(preprocess_run())
    print(df_feat.head())
