# NIRMAANDRISHTI AI — Project Sentinel

AI-powered infrastructure project intelligence and early warning system.

Three engines sit behind a FastAPI service layer. The React command centre never talks to a model file — it only consumes stable JSON contracts.

```
PROJECT DATA → processing → Cost / Time / Trend engines → Intelligence layer → Dashboard
```

---

## 1. Prerequisites

- Python 3.11+ (3.13 is fine)
- Node.js 20+
- Optional: PostgreSQL 14+ (SQLite is the default)

---

## 2. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

### Database

SQLite is created automatically:

```
DATABASE_URL=sqlite:///./nirmaandrishti.db
```

To use PostgreSQL, start Postgres, create a database, then set:

```
DATABASE_URL=postgresql+psycopg2://nirmaan:nirmaan@localhost:5432/nirmaandrishti
```

Tables are created on API startup (`init_db()`).

### Seed realistic projects

```bash
cd backend
python -m scripts.seed_data
```

This loads 34 Indian infrastructure projects with monthly histories.

### Run the API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)  
Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

Vite proxies `/api` → `http://127.0.0.1:8000`. Components never hardcode a backend host.

Production build:

```bash
cd frontend
npm run build
```

---

## 4. What you can do

1. Open the landing page.
2. Enter the intelligence dashboard.
3. Browse / search / filter projects.
4. Open a project dossier and health score.
5. Inspect cost, time and trend intelligence.
6. Run the cost and time prediction forms.
7. Analyse a project’s real historical trend.
8. Use Risk Monitor and Analytics.

---

## 5. How to integrate the real Cost Model

The mock engine is isolated. The frontend does not need to change.

### Step 1 — Place artifacts

Copy your trained files into:

```
backend/app/ml/cost/artifacts/model.pkl
backend/app/ml/cost/artifacts/preprocessor.pkl
backend/app/ml/cost/artifacts/feature_config.json
```

`feature_config.json` example:

```json
{
  "features": [
    "original_cost_cr",
    "revised_cost_cr",
    "physical_progress_pct",
    "previous_progress",
    "previous_expenditure",
    "project_age_days",
    "days_to_original_completion",
    "days_overdue"
  ],
  "categorical": ["agency", "state"]
}
```

### Step 2 — How a request is transformed

`POST /api/predict/cost` accepts the Pydantic payload `CostPredictRequest`.

`CostPredictor._to_feature_frame()` builds a one-row frame in the order above (or the order in `feature_config.json`). If `preprocessor.pkl` exists it is applied before `model.predict()`.

### Step 3 — Which file to edit (only if needed)

| File | When to touch it |
|---|---|
| `backend/app/ml/cost/predictor.py` | Model output is not a single float (predicted expenditure in Cr) |
| `backend/app/ml/cost/model_loader.py` | Artifact filenames / extra files |
| `backend/app/services/cost_prediction_service.py` | Never required for a standard sklearn / XGBoost / LightGBM regressor |

`CostPredictionService.predict()` already:

1. Tries the real model.
2. Falls back to the deterministic mock if artifacts are missing or inference throws.
3. Converts the predicted expenditure into overrun, risk level, confidence and explanations.

### Step 4 — Test

```bash
curl -s http://127.0.0.1:8000/api/predict/cost \
  -H 'Content-Type: application/json' \
  -d '{
    "original_cost_cr": 10000,
    "revised_cost_cr": 12000,
    "current_expenditure_cr": 6400,
    "physical_progress_pct": 48,
    "previous_progress": 44,
    "previous_expenditure": 5600,
    "project_age_days": 900,
    "days_to_original_completion": -30,
    "days_overdue": 30,
    "agency": "NHAI",
    "state": "Maharashtra"
  }'
```

If the model loaded, `used_real_model` is `true` and `model_name` is the estimator class.

The same pattern applies to the time model under `backend/app/ml/time/artifacts/`.

---

## 6. API map

| Method | Path |
|---|---|
| GET | `/api/health` |
| GET | `/api/dashboard` |
| GET | `/api/projects` |
| GET | `/api/projects/filters` |
| GET | `/api/projects/{id}` |
| GET | `/api/projects/{id}/history` |
| GET | `/api/intelligence/{id}` |
| POST | `/api/predict/cost` |
| POST | `/api/predict/time` |
| GET | `/api/analyze/trend/{id}` |
| GET | `/api/risks` |
| GET | `/api/analytics/overview` |

Query params on `/api/projects`: `page`, `limit`, `state`, `agency`, `risk_level`, `search`, `sort`.

---

## 7. Folder structure

```
backend/
  app/
    main.py
    api/routes/          dashboard, projects, predictions, intelligence, analytics, risks
    core/                config, database
    models/              Project, ProjectUpdate, Prediction
    schemas/
    services/            engines + intelligence + analytics
    ml/cost|time/        loaders + predictors + artifacts/
  scripts/seed_data.py
  requirements.txt
frontend/
  src/pages              landing + 9 application screens
  src/components         layout, ui, charts
  src/lib                api client, types, formatters
```
