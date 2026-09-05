# Workflow Studio

Selbst gehosteter Editor und Runner für visuelle, knotenbasierte Workflows: Nodes
auf einer Fläche verbinden, Ausgänge mit Eingängen verdrahten, den Graphen ausführen.

```
Angular (Frontend)  ──REST──►  FastAPI (Backend)  ──►  PostgreSQL
```

## Datenbank

PostgreSQL 16, lokal installiert oder über Docker Compose:

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

## Stand

Grundarchitektur, Datenmodell und Ausführungs-Engine stehen: Workflows lassen sich
im Editor bauen, als Version speichern und laden und über die API ausführen –
validiert gegen die registrierten Node-Typen, inklusive Zyklen- und
Port-Typprüfung. Zwei Node-Typen (Texteingabe, Ausgabe) sind vollständig, weitere
folgen mit Datei-Upload, Context Vault, Prompt-Versionierung und einem manuellen
LLM-Provider. Noch offen: echte Nebenläufigkeit über Celery und Redis,
Containerisierung sowie ein Run-Verlauf im Frontend.
