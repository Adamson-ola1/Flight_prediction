# Model Card — Flight Ticket Price Predictor

## Summary

Regression model predicting the ticket price (USD) of a domestic flight
departing a New York City airport (JFK, LGA, EWR), using only information
known **before** departure: route, carrier, distance, date, and time of day.

## ⚠️ Important limitation — synthetic target

The source dataset (`nycflights13`-style, via openintro.org) has **no fare
column**. It records flight times, delays, carrier, route, and distance
only. Because this project's goal is price prediction, `price` was
**formulated synthetically** from a hand-built pricing formula
(`src/preprocess.py::add_synthetic_price`):

```
price = base_fare + distance^0.88 * rate + carrier_premium + season_premium
        + weekend_premium + peak_hour_premium - red_eye_discount
        + origin_premium + gaussian_noise
```

**Treat every model here as a methodology demonstration of an end-to-end
regression pipeline (cleaning → EDA → feature engineering → modeling →
evaluation → deployment) — not as a real airfare forecaster.** Swapping in
a dataset with real historical fares (e.g. from a GDS/OTA feed) is a
drop-in replacement: nothing else in `src/` or `backend/` assumes the
target is synthetic once `data/raw/data.csv` contains a real `price` column.

## Training data

- ~32.7k domestic flights departing NYC airports in 2013
- After cleaning (duplicate/outlier removal): 32,668 rows
- Split: 80% train (26,134 rows) / 20% test (6,534 rows), `random_state=42`

## Features

| Feature | Type | Description |
|---|---|---|
| `month`, `day`, `hour`, `minute` | numeric | Departure date/time components |
| `distance` | numeric | Route distance in miles |
| `weekday`, `is_weekend` | numeric | Derived from the flight date |
| `month_sin/cos`, `hour_sin/cos` | numeric | Cyclical encodings |
| `route_freq`, `dest_freq` | numeric | Frequency encodings (avoids one-hot exploding to 100+ destinations) |
| `carrier`, `origin`, `season`, `time_of_day` | categorical (one-hot) | |

## Models compared

Five regressors were trained on an identical `ColumnTransformer`
(`StandardScaler` on numeric features, `OneHotEncoder` on categoricals):
Linear Regression, Random Forest, XGBoost, LightGBM, and a Stacking
Ensemble (RF + XGBoost + LightGBM base learners, Ridge meta-learner).

## Results (test set, n=6,534)

| Model | RMSE | MAE | R² |
|---|---|---|---|
| **StackingEnsemble (selected)** | **19.66** | **15.60** | **0.803** |
| LightGBM | 19.78 | 15.69 | 0.801 |
| XGBoost | 20.01 | 15.86 | 0.796 |
| RandomForest | 20.60 | 16.31 | 0.784 |
| LinearRegression | 20.79 | 16.60 | 0.780 |

The Stacking Ensemble is selected automatically (`src/evaluate.py`) as the
model with the lowest test RMSE and saved to `models/trained_model.pkl` —
the single file `backend/main.py` loads at serving time.

See `outputs/metrics.json` for the machine-readable leaderboard and
`outputs/plots/` for actual-vs-predicted and residual diagnostics.

## Intended use

- Educational / portfolio demonstration of an end-to-end regression MLOps
  pipeline (data cleaning through a served API and React dashboard).
- **Not** intended for real fare quoting, pricing decisions, or any
  production travel application without retraining on real fare data.

## Caveats & risks

- All prices are synthetic — the model has learned the deterministic
  formula above plus its injected noise, not real market pricing behavior.
- Only 2013 NYC-origin data — a real deployment would need multi-year,
  multi-origin data.
- No feature covers cabin class, booking lead time, or demand — all of
  which dominate real fare variance.
