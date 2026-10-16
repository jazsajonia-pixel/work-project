# AI Agent Guide

- **Purpose:** Give future coding agents a safe, evidence-based continuation procedure.
- **Status:** VERIFIED
- **Last updated:** 2026-10-16

## Required reading and inspection

Read the root [README](../README.md), this [documentation index](README.md), [Project Overview](PROJECT_OVERVIEW.md), [System Architecture](SYSTEM_ARCHITECTURE.md), and the phase document relevant to the task. Inspect current code, schema, tests, Git status, and available templates before editing.

## Working rules

Preserve existing conventions and working behavior. Do not change official report wording without explicit authorization. Keep master templates unchanged and generate from working copies. Use synthetic or redacted data. Never commit secrets, real IDs, operational documents, or generated private files. Do not implement automatic report sending.

Phase documents are specifications and plans, not proof of implementation. Use the status vocabulary in [the documentation index](README.md). Never claim a feature is complete without running the relevant test or documenting the blocker.

## Change procedure

First write a concise implementation plan. Make the smallest focused change. Update tests and the relevant documentation when behavior, schema, architecture, requirements, or limitations change. Run `PYTHONPATH=backend pytest -q backend/tests` and `cd frontend && npm run build` when applicable. Inspect generated documents with the appropriate libraries and compare them to supplied masters before claiming fidelity.

## Future AI work

Gemini integration must remain server-side, feature-gated, privacy-approved, and suggestion-only. It must not invent unseen identifiers or incident details and must not silently associate documents with vehicles. Automatic file detection must never trigger sending or submission.
