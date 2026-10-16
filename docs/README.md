# GSCHPT Reporting System Documentation

- **Purpose:** Documentation index and maintainer entry point.
- **Status:** VERIFIED
- **Last updated:** 2026-10-16

## Project

- [Project Overview](PROJECT_OVERVIEW.md)
- [System Requirements](SYSTEM_REQUIREMENTS.md)
- [System Architecture](SYSTEM_ARCHITECTURE.md)
- [Database Schema](DATABASE_SCHEMA.md)
- [Security and Privacy](SECURITY_AND_PRIVACY.md)
- [Report Templates](REPORT_TEMPLATES.md)
- [Validation Rules](VALIDATION_RULES.md)
- [Testing Strategy](TESTING_STRATEGY.md)
- [Deployment and Setup](DEPLOYMENT_AND_SETUP.md)
- [Development Roadmap](DEVELOPMENT_ROADMAP.md)
- [Changelog](CHANGELOG.md)
- [AI Agent Guide](AI_AGENT_GUIDE.md)

## Phase documents

- [Phase 00 — Project Foundation](phases/PHASE_00_PROJECT_FOUNDATION.md)
- [Phase 01 — Dashboard and Template Engine](phases/PHASE_01_DASHBOARD_AND_TEMPLATE_ENGINE.md)
- [Phase 02 — Automatic Upload Detection](phases/PHASE_02_AUTOMATIC_UPLOAD_DETECTION.md)
- [Phase 03 — Gemini Image Analysis](phases/PHASE_03_GEMINI_IMAGE_ANALYSIS.md)
- [Phase 04 — Vehicle Review and Document Matching](phases/PHASE_04_VEHICLE_REVIEW_AND_DOCUMENT_MATCHING.md)
- [Phase 05 — Automated Report Generation](phases/PHASE_05_AUTOMATED_REPORT_GENERATION.md)
- [Phase 06 — Validation and Quality Assurance](phases/PHASE_06_VALIDATION_AND_QUALITY_ASSURANCE.md)
- [Phase 07 — Security and Deployment](phases/PHASE_07_SECURITY_AND_DEPLOYMENT.md)
- [Phase 08 — Maintenance and Future Improvements](phases/PHASE_08_MAINTENANCE_AND_FUTURE_IMPROVEMENTS.md)

## Recommended reading order

1. Root [README](../README.md)
2. This index
3. [Project Overview](PROJECT_OVERVIEW.md) and [System Architecture](SYSTEM_ARCHITECTURE.md)
4. [System Requirements](SYSTEM_REQUIREMENTS.md), [Database Schema](DATABASE_SCHEMA.md), and [Validation Rules](VALIDATION_RULES.md)
5. The phase document relevant to the task
6. [Testing Strategy](TESTING_STRATEGY.md) and [Deployment and Setup](DEPLOYMENT_AND_SETUP.md)

## Status vocabulary

`NOT STARTED`, `IN PROGRESS`, `IMPLEMENTED — UNVERIFIED`, `VERIFIED`, `BLOCKED`, and `DEFERRED` are used consistently. Phase documents are specifications and plans; they are not evidence that future work is implemented.

## For developers and AI agents

Inspect the current repository and tests before changing behavior. Keep master templates immutable, use synthetic test data, preserve official wording, run relevant tests, and update the appropriate documentation when behavior or schema changes. Read [AI Agent Guide](AI_AGENT_GUIDE.md) before making code changes.
