# Flight Price Prediction

End-to-end ML project: predicts the ticket price of a domestic flight
departing NYC (JFK, LGA, EWR) from the nycflights13 dataset, served through
a FastAPI backend and a React dashboard.

> ⚠️ The source dataset has no fare column — `price` is a **synthetic
> target** formulated from a realistic pricing formula (see
> `docs/model_card.md`). Treat this as a methodology demo, not real fares.

## Project structure

```
flight-prediction/
├── backend/          FastAPI app (main.py, schema.py)
├── charts/           EDA chart PNGs
├── docker/           docker-compose.yml, credentials template
├── .github/workflows/ci.yml
├── data/
│   ├── raw/           original dataset, never modified
│   ├── processed/      cleaned + feature-engineered dataset
│   └── external/
├── docs/              deployment guide, model card, technical report
├── notebooks/         exploratory notebook (narrative counterpart to src/)
├── models/            trained_model.pkl, scaler.pkl, per-model artifacts
├── outputs/           predictions.csv, metrics.json, plots/
├── src/               preprocess, feature_engineering, train, evaluate, predict, utils
├── tests/             pytest suite
├── dockerfile / .dockerignore
├── config.py          paths, hyperparameters, constants
├── requirements.txt
├── main.py            run the complete pipeline
└── frontend/          React (Vite) dashboard
```

## Quickstart

```bash
# 1. Backend — train the pipeline and serve the API
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py                      # trains 5 models, saves the best one
uvicorn backend.main:app --reload   # http://localhost:8000/docs

# 2. Frontend — in a second terminal
cd frontend
npm install
npm run dev                         # http://localhost:5173
```

Or with Docker Compose (backend + frontend together):

```bash
cp docker/.env.example docker/.env
docker compose -f docker/docker-compose.yml up --build
```

See `docs/deployment_guide.md` for full deployment options and CI/CD.

## Results

| Model | RMSE | MAE | R² |
|---|---|---|---|
| **StackingEnsemble (selected)** | **19.66** | **15.60** | **0.803** |
| LightGBM | 19.78 | 15.69 | 0.801 |
| XGBoost | 20.01 | 15.86 | 0.796 |
| RandomForest | 20.60 | 16.31 | 0.784 |
| LinearRegression | 20.79 | 16.60 | 0.780 |

Full write-up: `docs/model_card.md` and `docs/technical_report.md`.

## Testing

```bash
pytest -v
```

## License

Portfolio / educational project. Dataset via [openintro.org](https://www.openintro.org/data/index.php?data=nycflights).
