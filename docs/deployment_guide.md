# Deployment Guide

## 1. Local development (no Docker)

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py                     # trains models, writes models/ and outputs/
uvicorn backend.main:app --reload  # http://localhost:8000/docs

# Frontend (separate terminal)
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

The frontend reads `VITE_API_BASE_URL` from `frontend/.env` (defaults to
`http://localhost:8000`) — see `frontend/.env` for the value to change when
the backend runs somewhere else.

## 2. Docker (backend only)

```bash
docker build -t flight-prediction-api -f dockerfile .
docker run -p 8000:8000 flight-prediction-api
```

The image trains the pipeline at build time (`RUN python main.py` in the
`dockerfile`), so `models/trained_model.pkl` is already baked in — no
volume mount required for a demo deployment. For production, prefer
mounting `models/` and `outputs/` as volumes (see `docker/docker-compose.yml`)
so re-training doesn't require a rebuild.

## 3. Docker Compose (backend + frontend together)

```bash
cp docker/.env.example docker/.env   # fill in real values if pushing images
docker compose -f docker/docker-compose.yml up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## 4. CI/CD (GitHub Actions)

`.github/workflows/ci.yml` runs on every push/PR to `main`:

1. **backend-tests** — installs `requirements.txt`, lints with flake8, runs
   `python main.py` (full retrain), then `pytest`.
2. **docker-build** — builds the backend image and pushes it to Docker Hub
   (`push` events only). Requires two repository secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_PASSWORD` (a Docker Hub access token, not your account password)
3. **frontend-build** — installs Node deps and runs `npm run build` to catch
   frontend build breakage.

Set the secrets under **Settings → Secrets and variables → Actions** in
GitHub; `docker/.env.example` documents the same two values for local pushes.

## 5. Environment variables

| Variable | Where | Purpose |
|---|---|---|
| `DOCKERHUB_USERNAME` / `DOCKERHUB_PASSWORD` | GitHub Actions secrets, `docker/.env` | Push the backend image to Docker Hub |
| `VITE_API_BASE_URL` | `frontend/.env` | Base URL the React app calls for `/api/*` |

## 6. Retraining

Any time `data/raw/data.csv` changes, re-run `python main.py` (or rebuild the
Docker image) to regenerate `models/trained_model.pkl`, `outputs/metrics.json`,
and the comparison plots in `outputs/plots/`.
