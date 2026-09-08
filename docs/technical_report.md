# Technical Report — Flight Price Prediction Pipeline

## 1. Objective

Build and deploy an end-to-end regression pipeline that predicts a flight's
ticket price from pre-departure information, exposed via a REST API and a
React dashboard.

## 2. Data pipeline (`src/preprocess.py`)

1. **Load** `data/raw/data.csv` (32,735 rows, 16 columns) — never modified in place.
2. **Clean**: drop duplicates (0 found), fix the `hour==24` midnight
   encoding quirk (3 rows), remove `distance` outliers via the IQR method
   (67 rows, bounds ≈ [-832, 2725] miles).
3. **Synthetic target**: since the source has no fare column, `price` is
   constructed from a deterministic formula over pre-departure-known fields
   plus Gaussian noise (see `docs/model_card.md` for the full formula and
   rationale — this keeps the target leakage-free by construction).
4. **Drop columns**: leakage (`dep_delay`, `arr_delay`, `arr_time`,
   `air_time`), redundant (`year`, `dep_time`), and high-cardinality
   identifiers (`flight`, `tailnum`).

Output: 32,668 cleaned rows, 10 columns.

## 3. Feature engineering (`src/feature_engineering.py`)

- `weekday` / `is_weekend` from the flight date
- `season` (Winter/Spring/Summer/Fall) grouped from `month`
- `time_of_day` (Night/Morning/Afternoon/Evening) grouped from `hour`
- `route_freq` / `dest_freq` — frequency encodings instead of one-hot,
  since `dest` has 100+ distinct values
- `month_sin/cos`, `hour_sin/cos` — cyclical encodings so December/January
  and 23:00/00:00 are seen as close rather than maximally distant

Frequency maps are persisted to `models/feature_maps.json` so a single new
flight can be encoded identically at inference time (`src/predict.py`).

Output written to `data/processed/processed_data.csv` (20 columns, 32,668 rows).

## 4. Modeling (`src/train.py`)

A shared `ColumnTransformer` (StandardScaler on numeric features,
OneHotEncoder on `carrier`/`origin`/`season`/`time_of_day`) feeds five
regressors, each wrapped in its own `sklearn.Pipeline` so preprocessing is
never fit on the test split:

- Linear Regression (baseline)
- Random Forest (`n_estimators=200, max_depth=12`)
- XGBoost (`n_estimators=300, max_depth=6, lr=0.08`)
- LightGBM (`n_estimators=300, max_depth=6, lr=0.08`)
- Stacking Ensemble — RF + XGBoost + LightGBM base learners (lighter
  hyperparameters), Ridge meta-learner

80/20 train/test split, `random_state=42` throughout for reproducibility.

## 5. Evaluation (`src/evaluate.py`)

Metrics: RMSE, MAE, R² (continuous target). The lowest-RMSE model is copied
to `models/trained_model.pkl` — the one file the API loads — and the full
leaderboard is written to `outputs/metrics.json` / `outputs/model_report.csv`.
Diagnostic plots (actual-vs-predicted, residuals, model comparison bars) are
saved to `outputs/plots/`. See `docs/model_card.md` for the current numbers.

## 6. Serving (`backend/main.py`)

FastAPI app with `/api/predict`, `/api/predict/batch`, `/api/metrics`, and
`/api/health`. `src/predict.py` reproduces the exact feature-engineering
steps for a single incoming flight (using the persisted frequency maps) so
online and offline features never drift apart.

## 7. Frontend (`frontend/`)

A Vite + React dashboard (`pages/Dashboard.jsx`, `pages/ModelInfo.jsx`) that
posts to `/api/predict` for a single fare estimate and renders
`/api/metrics` as a model leaderboard.

## 8. Reproducibility

`python main.py` from the project root re-runs the entire pipeline
(preprocess → feature engineering → train → evaluate) deterministically —
the same command that both the Docker image build and CI use.
