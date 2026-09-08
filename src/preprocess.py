"""
preprocess.py — data cleaning and synthetic `price` target construction.

Mirrors notebooks/exploration.ipynb sections 1 ("Data Cleaning") and
"Target Variable Construction", but as reusable, importable functions
instead of notebook cells.
"""
import numpy as np
import pandas as pd

import config
from src.utils import get_logger, iqr_bounds

log = get_logger(__name__)


def load_raw(path=config.RAW_DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    log.info(f"Loaded raw data: {df.shape[0]} rows, {df.shape[1]} cols")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Missing values, duplicates, the hour==24 quirk, and distance outliers."""
    df = df.copy()

    n_missing = df.isna().sum().sum()
    log.info(f"Missing values across all columns: {n_missing}")

    before = len(df)
    df = df.drop_duplicates()
    log.info(f"Duplicate rows removed: {before - len(df)}")

    # Source data encodes midnight departures as hour=24 / dep_time=2400.
    # Normalize to hour=0 so downstream hour-based features stay in 0-23.
    midnight_mask = df["hour"] == 24
    log.info(f"Rows with hour==24 (midnight quirk) fixed: {midnight_mask.sum()}")
    df.loc[midnight_mask, "hour"] = 0
    df.loc[midnight_mask, "dep_time"] = df.loc[midnight_mask, "dep_time"] - 2400

    # dep_delay/arr_delay/air_time are dropped later (leakage) so their
    # outliers don't need treatment here. distance IS a modeling feature,
    # so long-haul outliers are trimmed to keep the price formula sane.
    lo, hi = iqr_bounds(df["distance"])
    before = len(df)
    df = df[(df["distance"] >= lo) & (df["distance"] <= hi)].reset_index(drop=True)
    log.info(f"Distance outliers dropped: {before - len(df)} (bounds {lo:.1f}-{hi:.1f})")

    return df


def add_synthetic_price(df: pd.DataFrame, rng: np.random.Generator | None = None) -> pd.DataFrame:
    """
    The source data has no fare column. `price` is formulated from a
    realistic airfare pricing model built only from pre-departure-known
    fields, so there is no leakage from flight outcomes:

        price = base_fare + distance^0.88 rate + carrier premium
                + season premium + weekend premium + peak-hour premium
                - red-eye discount + origin premium + noise
    """
    df = df.copy()
    rng = rng or np.random.default_rng(config.RANDOM_STATE)

    date = pd.to_datetime(dict(year=df.year, month=df.month, day=df.day))
    weekday = date.dt.weekday  # Monday=0 ... Sunday=6

    carrier_prem = df["carrier"].map(config.CARRIER_PREMIUM).fillna(0)
    distance_component = 0.11 * df["distance"] ** 0.88
    season_prem = df["month"].isin([6, 7, 8, 12]).astype(int) * 25
    weekend_prem = weekday.isin([4, 6]).astype(int) * 15
    peak_prem = (df["hour"].between(6, 9).astype(int) * 12
                 + df["hour"].between(16, 19).astype(int) * 12)
    redeye_disc = (df["hour"] < 5).astype(int) * -20
    origin_prem = df["origin"].map(config.ORIGIN_PREMIUM).fillna(0)

    noise = rng.normal(0, 18, size=len(df))
    mult_noise = rng.normal(1, 0.05, size=len(df))

    raw_price = (config.BASE_FARE + distance_component + carrier_prem + season_prem
                 + weekend_prem + peak_prem + redeye_disc + origin_prem + noise) * mult_noise
    df["price"] = raw_price.clip(lower=config.MIN_PRICE).round(2)

    df["_weekday"] = weekday.values  # handed to feature_engineering, avoids recomputation
    log.info(f"Synthetic price added — mean=${df['price'].mean():.2f}, "
              f"median=${df['price'].median():.2f}")
    return df


def drop_unused_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=[c for c in config.DROP_COLS if c in df.columns])
    log.info(f"Columns kept after drop: {list(df.columns)}")
    return df


def run(raw_path=config.RAW_DATA_PATH) -> pd.DataFrame:
    """Full preprocessing pipeline: load -> clean -> synthetic price -> drop cols."""
    df = load_raw(raw_path)
    df = clean(df)
    df = add_synthetic_price(df)
    df = drop_unused_columns(df)
    return df


if __name__ == "__main__":
    out = run()
    print(out.head())
