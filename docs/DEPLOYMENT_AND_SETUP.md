# Deployment and Setup

- **Purpose:** Provide reproducible local setup and state the production blockers.
- **Status:** VERIFIED for local development and Vercel/Neon smoke deployment; production hardening remains BLOCKED.
- **Last updated:** 2026-10-16

## Prerequisites

Python 3.11+, Node.js 22+, npm, and Git. The repository uses FastAPI, Uvicorn, SQLite for local fallback, PostgreSQL/Neon when `DATABASE_URL` is set, `python-docx`, `python-pptx`, React, TypeScript, and Vite.

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

Backend variables: `DATABASE_URL`, `GEMINI_API_KEY`, `GEMINI_MODEL`, `MAKE_DRAFT_WEBHOOK_URL`, `GSCHPT_DB_PATH`, `GSCHPT_STORAGE_DIR`, `GSCHPT_PRIVATE_STORAGE_DIR`, `GSCHPT_TEMPLATE_DIR`, `GSCHPT_MAX_UPLOAD_MB`, `GSCHPT_ALLOWED_ORIGINS`, `GSCHPT_DEV_USERNAME`, and `GSCHPT_DEV_PASSWORD` placeholder configuration. Frontend build variables: `VITE_API_BASE_URL` and `VITE_DEV_USER`. The current frontend header gate must match the configured backend development user. Keep `GEMINI_API_KEY` and `MAKE_DRAFT_WEBHOOK_URL` server-side; never put them in the frontend bundle, source control, or logs.

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

Open `http://localhost:5173`. The API health endpoint is `http://localhost:8000/api/health`; it verifies a database query and reports whether storage is local or ephemeral.

## Database and storage

SQLite and local folders are created automatically for development. Generated drafts go to `GSCHPT_STORAGE_DIR`; private uploads go to `GSCHPT_PRIVATE_STORAGE_DIR`; templates go to `templates/`. The current startup migration is additive and is not a production migration system.

## Templates

Supply authoritative `.txt`, `.docx`, and `.pptx` files through the protected template upload route. Do not use fallback files as official-format replacements. See [Report Templates](REPORT_TEMPLATES.md).

## Tests

```bash
PYTHONPATH=backend pytest -q backend/tests
cd frontend && npm run build
```

## Vercel and Neon deployment

The application is deployed at [gschpt-reporting.vercel.app](https://gschpt-reporting.vercel.app) from the `feature/gschpt-phase1` branch. Vercel serves the Vite build and Python API function; Neon provides PostgreSQL persistence. The deployment was smoke-tested with frontend `200`, `/api/health` `200` returning `{"ok":true,"database":"connected","storage":"ephemeral"}`, unauthorized dashboard `401`, authorized dashboard `200`, and same-origin CORS preflight `200`.

Gemini is connected through an encrypted Vercel environment variable. Image analysis is explicit and review-only through `POST /api/uploads/{id}/analyze`; it does not auto-associate images or create official facts. The test suite covers the unconfigured-key failure path without sending synthetic fixtures to the external model.

Make.com receives a `gschpt.draft.generated` JSON event after a draft is created. The active scenario is `GSCHPT Draft Generated Intake` (scenario ID `6656649`) with webhook ID `2942297`; a synthetic event returned HTTP `200` and a Make execution ID. The callback is non-blocking and metadata-only; Make outages do not fail draft generation.

Weekly aggregation uses `POST /api/reports/weekly` with `period_start`, `period_end`, and `file_type` (`DOCX` or `PPTX`). A batch is included when its reporting interval overlaps the requested period; batches without an interval use their incident date. Each request rebuilds a period snapshot and stores it as a generated report.

This is not yet an operational production baseline: authentication is still the development header gate, and Vercel `/tmp` storage is ephemeral. Move photos, documents, templates, and generated drafts to durable private object storage; then add real identity/roles, signed or authorized downloads, malware scanning, backups, monitoring, retention, and recovery procedures.

## Troubleshooting

- `401`: ensure `X-Dev-User` or `VITE_DEV_USER` matches `GSCHPT_DEV_USERNAME` in development.
- CORS errors: ensure the frontend origin is allowed by the backend and `VITE_API_BASE_URL` points to the API.
- Missing templates: expected until authoritative files are supplied; fallback outputs are not fidelity verified.
- Upload rejection: check extension and `GSCHPT_MAX_UPLOAD_MB`.
- Database reset for local tests: stop the API and remove the configured SQLite file only when synthetic data may be discarded.
