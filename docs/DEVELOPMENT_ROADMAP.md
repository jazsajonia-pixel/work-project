# Development Roadmap

- **Purpose:** Describe completed, blocked, and future phases.
- **Status:** VERIFIED against repository evidence.
- **Last updated:** 2026-10-16

| Phase | Name | Status | Main blocker or next dependency |
|---|---|---|---|
| 00 | Project Foundation | VERIFIED | Production identity and durable file storage remain. |
| 01 | Dashboard and Template Engine | IMPLEMENTED — UNVERIFIED | Original templates are missing; fidelity is blocked. |
| 02 | Automatic Upload Detection | DEFERRED | Requires explicit completion workflow and idempotent processing design. |
| 03 | Gemini Image Analysis | IN PROGRESS | Server-side review-only suggestions are connected; privacy approval, quotas, retention, and human-review UI remain. |
| 04 | Vehicle Review and Document Matching | DEFERRED | Manual association exists; richer review history and matching workflow do not. |
| 05 | Automated Report Generation | IMPLEMENTED — UNVERIFIED | Fallback generation works; source-template mapping and approval rules remain. |
| 06 | Validation and Quality Assurance | IN PROGRESS | Current validation exists; regression and fidelity QA need real masters. |
| 07 | Security and Deployment | IN PROGRESS | Vercel/Neon smoke deployment passes; real identity and durable private storage remain. |
| 08 | Maintenance and Future Improvements | IN PROGRESS | Make draft-event intake is connected; downstream archival/notification actions and production hardening remain. |

Detailed scope is in each linked [phase document](README.md).

## Acceptance principle

A phase is not VERIFIED merely because code or documentation exists. Its acceptance criteria must be executed and evidenced. Future phase documents are plans, not implementation claims.
