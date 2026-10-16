# GSCHPT Reporting Dashboard — Phase 1

Private, locally runnable reporting dashboard for manually reviewed GSCHPT operational records. It supports persistent batches, manual vehicle records, unsorted private photo uploads, manual photo-to-vehicle association, manual possessor ID/license attachment, validation, and draft-only TXT/DOCX/PPTX generation.

## Implemented

- React + TypeScript + Vite responsive dashboard.
- FastAPI backend with SQLite development persistence.
- Development authentication gate and server-side authorization on protected endpoints.
- Batch creation/editing with Asia/Manila preparation date, separate incident date/time, location, title, notes, and weekly reporting period.
- Vehicle record create/edit/delete with MC/MV, recovery, possessor/owner, violation, review, and template-oriented fields.
- Multiple JPG/JPEG/PNG/WebP photo upload in one request, private storage, unassigned upload listing, manual vehicle association, primary-image flag, and protected download.
- Manual possessor ID/license attachment per selected vehicle, attachment type, private storage, and protected download.
- Blocking and review validation warnings for missing fields, invalid periods, missing photos/documents, duplicate plate numbers, missing identifiers, and narrative count conflicts.
- Separate draft generation buttons for daily TXT, weekly DOCX, and weekly PPTX.
- Generated draft metadata, validation status, template version, timestamps, and protected download.
- No Gemini, automatic grouping/extraction, email, Viber, report submission, or public sharing.

## Important template limitation

The connected repository did not contain the authoritative GSCHPT TXT, DOCX, or PPTX files. The `templates/` directory therefore contains only a marker. The application has protected template upload/version infrastructure and will use an active uploaded template when supplied. Until then, DOCX/PPTX use explicitly labeled `fallback-safe-v1` layouts. These fallbacks do **not** claim to preserve unavailable original formatting.

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
- `GET /api/batches/{batch_id}/validate`
- `POST /api/batches/{batch_id}/draft/{TXT|DOCX|PPTX}`
- `GET /api/drafts/{id}/download` and `/api/uploads/{id}/download`

## Deployment and remaining configuration

No hosting or Supabase credentials were available in the repository. Deployment is therefore not claimed. A real deployment needs a private backend host for FastAPI, a managed PostgreSQL database, private object storage, HTTPS, real authentication/session handling, authorization tied to the authenticated user, secure secret injection, backups, and non-public frontend-to-backend configuration. The SQLite/private-folder setup is development-only.

Before the next phase, supply the original templates and validate their structure. Then implement field mappings and fidelity checks against the actual files. The exact next step for Gemini is to add a review-only analysis service behind a feature flag after manual uploads and associations are stable; it must never create official facts or silently associate files.
