# Workflow Studio

Self-hosted editor and runner for visual, node-based workflows: connect nodes on
a canvas, wire outputs to inputs, run the graph.

```
Angular (frontend)  ──REST──►  FastAPI (backend)  ──►  PostgreSQL
```

## Database

```
cd deploy/compose
cp .env.example .env
docker compose up -d
```

## Backend

```
cd backend
python -m venv .venv
.venv/Scripts/pip install -e . --group dev
cp .env.example .env
.venv/Scripts/alembic upgrade head
.venv/Scripts/pytest
.venv/Scripts/uvicorn app.main:app --reload
```

## Frontend

```
cd frontend
npm install
npm start
```
