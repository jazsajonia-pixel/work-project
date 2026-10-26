# GSCHPT Reporting Dashboard — Phase 1

Private, locally runnable reporting dashboard for manually reviewed GSCHPT operational records. It supports persistent batches, manual vehicle records, unsorted private photo uploads, manual photo-to-vehicle association, manual possessor ID/license attachment, validation, and draft-only TXT/DOCX/PPTX generation.

## Project documentation

The maintained documentation system is indexed at [`docs/README.md`](docs/README.md). Start with the [Project Overview](docs/PROJECT_OVERVIEW.md), [System Architecture](docs/SYSTEM_ARCHITECTURE.md), and [AI Agent Guide](docs/AI_AGENT_GUIDE.md). The documentation records actual implementation status, test evidence, template limitations, security requirements, deployment blockers, and detailed phase plans.

## Implemented

- React + TypeScript + Vite responsive dashboard.
- FastAPI backend with SQLite development persistence.
- Development authentication gate and server-side authorization on protected endpoints.
- Database-backed `/api/health` check with configurable CORS origins for local and hosted environments.
- Batch creation/editing with Asia/Manila preparation date, separate incident date/time, location, title, notes, and weekly reporting period.
- Vehicle record create/edit/delete with MC/MV, recovery, possessor/owner, violation, review, and template-oriented fields.
- Multiple JPG/JPEG/PNG/WebP photo upload in one request, private storage, unassigned upload listing, manual vehicle association, primary-image flag, and protected download.
- Manual possessor ID/license attachment per selected vehicle, attachment type, private storage, and protected download.
- Blocking and review validation warnings for missing fields, invalid periods, missing photos/documents, duplicate plate numbers, missing identifiers, and narrative count conflicts.
- Separate draft generation buttons for daily TXT, weekly DOCX, and weekly PPTX.
- Explicit, review-only Gemini photo suggestion endpoint; it never auto-associates photos or creates official facts.
- Non-blocking Make.com event after draft generation, sending report metadata only.
- Generated draft metadata, validation status, template version, timestamps, and protected download.
- No Gemini, automatic grouping/extraction, email, Viber, report submission, or public sharing.

## Important template limitation

The supplied GSCHPT examples are bundled as `templates/daily_master.txt`, `templates/weekly_master.docx`, and `templates/weekly_master.pptx`. The application uses an active uploaded template when available, otherwise it uses these bundled masters. DOCX/PPTX generation preserves the source master, populates mapped vehicle summary content, and inserts each vehicle’s primary (or first valid) attached photo into the matching recovery placeholder.

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://localhost:5173`. The development dashboard sends `X-Dev-User: admin`. This is a development gate, not production-grade identity management.

## Environment variables

- `GSCHPT_DB_PATH` — SQLite path, default `./storage/gschpt.db`.
- `GSCHPT_STORAGE_DIR` — generated draft directory.
- `GSCHPT_PRIVATE_STORAGE_DIR` — private photo/document storage directory.
- `GSCHPT_MAX_UPLOAD_MB` — documented upload limit; current safe default is 20 MB per file.
- `GSCHPT_DEV_USERNAME` / `GSCHPT_DEV_PASSWORD` — reserved development configuration; replace the header gate with real authentication before deployment.
- `VITE_API_BASE_URL` — frontend build-time API base URL, defaulting to `http://localhost:8000/api`; set it in `frontend/.env.local` when frontend and backend are hosted separately.
- `VITE_DEV_USER` — frontend development header value; keep it equal to `GSCHPT_DEV_USERNAME` for local use. This header gate must be replaced by real authentication before production.
- `BLOB_READ_WRITE_TOKEN` / `BLOB_STORE_ID` — optional Vercel Blob credentials. When configured, private uploads, templates, and generated drafts are stored in Blob instead of Vercel's ephemeral filesystem. A Blob store connected to the Vercel project can also provide these through Vercel's environment integration.

## Tests

```bash
PYTHONPATH=backend pytest -q backend/tests
cd frontend && npm run build
```

Tests use synthetic records and cover authentication, batch creation/editing, vehicle CRUD, multiple photo upload, batch-to-photo association, vehicle-to-document association, private download, validation, Manila date handling, and TXT/DOCX/PPTX generation.

## Template installation

Upload authoritative `.txt`, `.docx`, and `.pptx` templates to the protected `POST /api/templates` endpoint using the `X-Dev-User` header during development. Templates are stored server-side, versioned, and kept unchanged; generation reads from the selected master. Inspect the actual source files before adding field mappings. Do not commit operational reports, photos, ID documents, or secrets.

## Useful API routes

- `POST/PUT /api/batches` and `/api/batches/{batch_id}`
- `POST/PUT/DELETE /api/batches/{batch_id}/vehicles` and `/api/vehicles/{id}`
- `POST /api/batches/{batch_id}/photos`
- `PATCH /api/uploads/{id}/associate`
- `POST /api/vehicles/{id}/attachments`
- `POST /api/uploads/{id}/analyze`
- `MAKE_DRAFT_WEBHOOK_URL` receives `gschpt.draft.generated` metadata when configured.
- `GET /api/batches/{batch_id}/validate`
- `POST /api/batches/{batch_id}/draft/{TXT|DOCX|PPTX}`
- `POST /api/reports/weekly` with `{period_start, period_end, file_type: DOCX|PPTX}` aggregates all overlapping batches.
- `GET /api/drafts/{id}/download` and `/api/uploads/{id}/download`

## Current Vercel/Neon deployment

The current production deployment is **https://gschpt-reporting.vercel.app** from `main`, commit `1429a73`. Vercel project: `gschpt-reporting`. Neon project: `gschpt-reporting` in `aws-ap-southeast-1`, with the application schema initialized in PostgreSQL.

The deployment is a verified smoke deployment, not a production-security claim. It currently uses the development `X-Dev-User` header gate. Without Vercel Blob credentials, Vercel's writable filesystem is ephemeral; with Blob configured, the health endpoint reports `storage: persistent` and private uploads, templates, and generated drafts use the Blob adapter. Real identity/session handling, authorization tied to users, malware scanning, backups, retention, monitoring, and recovery are still required.

Before the next phase, supply the original templates and validate their structure. Then implement field mappings and fidelity checks against the actual files. The exact next step for Gemini is to add a review-only analysis service behind a feature flag after manual uploads and associations are stable; it must never create official facts or silently associate files.
