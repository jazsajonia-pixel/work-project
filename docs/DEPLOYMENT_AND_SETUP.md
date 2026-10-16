# Deployment and Setup

- **Purpose:** Provide reproducible local setup and state the production blockers.
- **Status:** VERIFIED for local development; production deployment is BLOCKED.
- **Last updated:** 2026-10-16

## Prerequisites

Python 3.11+, Node.js 22+, npm, and Git. The repository currently uses FastAPI, Uvicorn, SQLite, `python-docx`, `python-pptx`, React, TypeScript, and Vite.

## Local installation

```bash
git clone <repository-url>
cd work-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
cd frontend
npm install
```

Do not commit `.env`, operational records, uploaded photos, ID documents, generated reports, or credentials.

## Environment variables

Backend variables: `GSCHPT_DB_PATH`, `GSCHPT_STORAGE_DIR`, `GSCHPT_PRIVATE_STORAGE_DIR`, `GSCHPT_MAX_UPLOAD_MB`, `GSCHPT_DEV_USERNAME`, and `GSCHPT_DEV_PASSWORD` placeholder configuration. Frontend build variables: `VITE_API_BASE_URL` and `VITE_DEV_USER`. The current frontend header gate must match the configured backend development user.

## Start services

Terminal 1:

```bash
source .venv/bin/activate
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Terminal 2:

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Open `http://localhost:5173`. The API health endpoint is `http://localhost:8000/api/health`.

## Database and storage

SQLite and local folders are created automatically for development. Generated drafts go to `GSCHPT_STORAGE_DIR`; private uploads go to `GSCHPT_PRIVATE_STORAGE_DIR`; templates go to `templates/`. The current startup migration is additive and is not a production migration system.

## Templates

Supply authoritative `.txt`, `.docx`, and `.pptx` files through the protected template upload route. Do not use fallback files as official-format replacements. See [Report Templates](REPORT_TEMPLATES.md).

## Tests

```bash
PYTHONPATH=backend pytest -q backend/tests
cd frontend && npm run build
```

## Production deployment

No production host, Supabase project, credentials, or deployment configuration is present. Before deployment, configure a private FastAPI host, PostgreSQL, private object storage, HTTPS, real identity and roles, secret injection, backups, monitoring, retention, and recovery procedures. A static frontend alone is insufficient.

## Troubleshooting

- `401`: ensure `X-Dev-User` or `VITE_DEV_USER` matches `GSCHPT_DEV_USERNAME` in development.
- CORS errors: ensure the frontend origin is allowed by the backend and `VITE_API_BASE_URL` points to the API.
- Missing templates: expected until authoritative files are supplied; fallback outputs are not fidelity verified.
- Upload rejection: check extension and `GSCHPT_MAX_UPLOAD_MB`.
- Database reset for local tests: stop the API and remove the configured SQLite file only when synthetic data may be discarded.
