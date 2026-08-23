# NIRMAANDRISHTI API

FastAPI service layer for Project Sentinel.

```bash
pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed_data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

See the root README for model integration.
