# Changelog

- **Purpose:** Record repository-supported project changes.
- **Status:** VERIFIED
- **Last updated:** 2026-10-16

## 2026-10-16 — Documentation audit baseline

Added the complete documentation system required by the documentation task. The documentation records the actual local stack, the fictional end-to-end audit, the absence of authoritative templates, and production blockers.

## 2026-10-16 — `06877a7`

Improved hosted diagnostics: `/api/health` now verifies a database query and reports connected database/storage mode, Neon connections use a five-second timeout, CORS origins are configurable, and the regression suite covers the health contract. The verified Vercel deployment uses this commit.

## 2026-10-16 — Gemini integration

Connected Gemini through an encrypted server-side deployment variable and added an explicit review-only photo analysis endpoint. The endpoint returns structured suggestions, preserves uncertainty, never auto-associates a vehicle, and requires human review.

## 2026-10-16 — Make.com draft intake

Created the active `GSCHPT Draft Generated Intake` Make scenario (ID `6656649`) with custom webhook ID `2942297`. A synthetic `gschpt.draft.generated` event returned HTTP `200` and a Make execution ID, confirming end-to-end receipt. The application callback is non-blocking and sends metadata only.

## 2026-10-16 — `5b41e2c`

Hardened audit configuration and development access. The backend now uses the configured upload-size limit and exact configured development username. The frontend API base URL and development user are configurable through Vite variables. README and environment examples were updated.

## 2026-10-16 — `9591981`

Added private bulk photo uploads, manual photo association, primary-image selection, manual possessor ID/license attachments, richer validation, batch periods, and the related tests and interface workflows.

## 2026-10-16 — `1b375a3`

Created the Phase 1 dashboard foundation with React/Vite, FastAPI, SQLite, batch and vehicle records, validation, draft generation, template upload infrastructure, tests, and local setup documentation.

## Initial repository

The repository initially contained only a minimal README. No authoritative report templates or production deployment configuration were present.
