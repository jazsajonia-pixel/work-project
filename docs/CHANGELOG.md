# Changelog

- **Purpose:** Record repository-supported project changes.
- **Status:** VERIFIED
- **Last updated:** 2026-10-16

## 2026-10-16 — Documentation audit baseline

Added the complete documentation system required by the documentation task. The documentation records the actual local stack, the fictional end-to-end audit, the absence of authoritative templates, and production blockers.

## 2026-10-16 — `06877a7`

Improved hosted diagnostics: `/api/health` now verifies a database query and reports connected database/storage mode, Neon connections use a five-second timeout, CORS origins are configurable, and the regression suite covers the health contract. The verified Vercel deployment uses this commit.

## 2026-10-16 — `5b41e2c`

Hardened audit configuration and development access. The backend now uses the configured upload-size limit and exact configured development username. The frontend API base URL and development user are configurable through Vite variables. README and environment examples were updated.

## 2026-10-16 — `9591981`

Added private bulk photo uploads, manual photo association, primary-image selection, manual possessor ID/license attachments, richer validation, batch periods, and the related tests and interface workflows.

## 2026-10-16 — `1b375a3`

Created the Phase 1 dashboard foundation with React/Vite, FastAPI, SQLite, batch and vehicle records, validation, draft generation, template upload infrastructure, tests, and local setup documentation.

## Initial repository

The repository initially contained only a minimal README. No authoritative report templates or production deployment configuration were present.
