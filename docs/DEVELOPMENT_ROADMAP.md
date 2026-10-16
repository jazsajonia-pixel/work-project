# Development Roadmap

- **Purpose:** Describe completed, blocked, and future phases.
- **Status:** VERIFIED against repository evidence.
- **Last updated:** 2026-10-16

| Phase | Name | Status | Main blocker or next dependency |
|---|---|---|---|
| 00 | Project Foundation | VERIFIED | Production identity and hosted persistence remain. |
| 01 | Dashboard and Template Engine | IMPLEMENTED — UNVERIFIED | Original templates are missing; fidelity is blocked. |
| 02 | Automatic Upload Detection | DEFERRED | Requires explicit completion workflow and idempotent processing design. |
| 03 | Gemini Image Analysis | DEFERRED | Requires privacy approval, model selection, quotas, and synthetic fixtures. |
| 04 | Vehicle Review and Document Matching | DEFERRED | Manual association exists; richer review history and matching workflow do not. |
| 05 | Automated Report Generation | IMPLEMENTED — UNVERIFIED | Fallback generation works; source-template mapping and approval rules remain. |
| 06 | Validation and Quality Assurance | IN PROGRESS | Current validation exists; regression and fidelity QA need real masters. |
| 07 | Security and Deployment | IN PROGRESS | Local security checks pass; production hosting and identity are absent. |
| 08 | Maintenance and Future Improvements | DEFERRED | Begin after production baseline and template process exist. |

Detailed scope is in each linked [phase document](README.md).

## Acceptance principle

A phase is not VERIFIED merely because code or documentation exists. Its acceptance criteria must be executed and evidenced. Future phase documents are plans, not implementation claims.
