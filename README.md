# bnc-backend

BNC ecommerce demo API (FastAPI + MySQL).

## Setup

```bash
# from testdemo/
docker compose up -d

cd bnc-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Demo accounts

- Customer: `customer@demo.com` / `demo1234`
- Admin: `admin@demo.com` / `admin1234`

## Tests

```bash
pytest -v
```
