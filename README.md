# GSCHPT Reporting Dashboard — Phase 1

A private, locally runnable foundation for manually entering impoundment/recovery records and generating **draft-only** TXT, DOCX, and PPTX reports. The repository contained no original report templates, so the app clearly labels safe fallback outputs and never claims to preserve missing formatting.

## Scope

Implemented: responsive React/TypeScript/Vite dashboard, FastAPI backend, SQLite data layer, Asia/Manila preparation date, batch and vehicle APIs, validation warnings, private server-side draft storage, template upload/version records, and draft generation using `python-docx`, `python-pptx`, and UTF-8 text.

Not implemented by design: Gemini/image analysis, automatic grouping or ID/license matching, bulk photo processing, email/Viber sending, publishing, or public file sharing.

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env  # change GSCHPT_DEV_PASSWORD for any real use
uvicorn backend.app.main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL (usually `http://localhost:5173`). The development dashboard sends `X-Dev-User: admin`; this is only a safe development gate, not production authentication. Before production, replace it with a real identity provider/session system and HTTPS.

## Tests

```bash
PYTHONPATH=backend pytest -q backend/tests
cd frontend && npm run build
```

Tests cover batch creation, Manila preparation date, validation warnings, and opening generated TXT/DOCX/PPTX files. Test data is fictional.

## Templates

Place authoritative files in `templates/` or upload them from the Templates workflow/API. Accepted extensions are `.txt`, `.docx`, and `.pptx`, with a 20 MB limit and server-side filenames. Since no source templates were present in the connected repository, initial generated DOCX/PPTX files use an explicit `fallback-safe-v1` layout and are marked as drafts. Once originals are uploaded, the next generation service extension should copy the selected template before replacing only safe mapped locations.

## API highlights

- `POST /api/batches`, `PUT /api/batches/{batch_id}`
- `POST /api/batches/{batch_id}/vehicles`, `PUT /api/vehicles/{id}`
- `GET /api/batches/{batch_id}/validate`
- `POST /api/batches/{batch_id}/draft/{TXT|DOCX|PPTX}`
- `POST /api/templates`, `GET /api/drafts`, `GET /api/drafts/{id}/download`

All protected endpoints require `X-Dev-User` during development. No generated file is sent anywhere automatically.

## Remaining before later phases

Add real authentication/authorization, audit logging with PII minimization, authoritative templates and field mappings, bulk photo upload, automatic file detection, Gemini analysis, and explicit manual ID/license association review.
