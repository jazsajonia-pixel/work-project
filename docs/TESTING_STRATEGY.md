# Testing Strategy

- **Purpose:** Describe current automated tests, audit evidence, and remaining verification work.
- **Status:** VERIFIED for the listed local tests; production and template-fidelity testing remain blocked.
- **Last updated:** 2026-10-16

## Current commands and observed results

From the repository root:

```bash
PYTHONPATH=backend pytest -q backend/tests
```

Observed during the 2026-10-16 audit: **3 passed**, with three non-blocking deprecation warnings from Starlette/FastAPI.

```bash
cd frontend && npm run build
```

Observed: production build completed successfully. Vite emitted non-blocking `lucide-react` module-directive warnings.

## Existing automated coverage

`backend/tests/test_reports.py` uses synthetic data and covers authentication, batch creation/editing, vehicle CRUD, multiple image upload, batch/photo association, vehicle/document association, protected downloads, validation, Manila preparation date, and TXT/DOCX/PPTX generation/opening signatures.

## Manual fictional end-to-end audit

The audit created `AUDIT-001`, edited it, added and edited a vehicle, uploaded two photos, associated a photo, attached a fake license PDF, ran count-conflict validation, generated all three drafts, inspected TXT content, opened DOCX with `python-docx`, opened PPTX with `python-pptx`, and tested authorized/unauthorized downloads. All checks passed.

## Test areas

| Area | Current state |
|---|---|
| Unit/integration backend | Exists and passed. |
| Frontend compilation | Passed; no browser interaction test suite exists. |
| Authentication/access | Development exact-user tests passed; production auth not tested because absent. |
| Upload validation | Extension, size, persistence, and association tested. |
| TXT generation | Content marker and file generation tested. |
| DOCX/PPTX generation | Files opened successfully; fidelity blocked by missing masters. |
| Date/time | Asia/Manila preparation date tested; broader timezone matrix remains. |
| Security | Basic access and private-path tests passed; threat/malware/production tests remain. |
| Regression | Current suite passed after audit fixes. |

## Required future tests

Add browser-level tests, real template regression fixtures, fixed-wording comparisons, page/slide/layout comparisons, retry/failure tests, ownership isolation tests, malware scanning tests, backup/recovery tests, accessibility checks, and production deployment smoke tests. Use synthetic or redacted data only.
