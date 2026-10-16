# Phase 00 — Project Foundation

- **Purpose:** Establish the repository, local stack, storage, testing, and development conventions.
- **Status:** VERIFIED locally; production foundation is IN PROGRESS.
- **Last updated:** 2026-10-16

## Scope and dependencies

This phase depends only on the repository and local Python/Node runtimes. It establishes React/Vite, FastAPI, SQLite, local private folders, environment examples, and pytest.

## Delivered

The repository has `frontend/`, `backend/`, `templates/`, `generated_drafts/`, `storage/`, `.env.example`, and test instructions. Startup and build commands are documented. Development authorization and configurable paths are present.

## Acceptance and evidence

The backend test suite passed with 3 tests. The frontend production build passed. Health, CORS, and exact development-user checks passed during the audit.

## Remaining work

Production identity, PostgreSQL migrations, private object storage, HTTPS, backups, retention, and audit events remain necessary before deployment.
