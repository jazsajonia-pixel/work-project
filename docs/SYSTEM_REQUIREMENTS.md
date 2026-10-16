# System Requirements

- **Purpose:** Trace requirements to current behavior, tests, and future work.
- **Status:** VERIFIED for implemented items; planned items are labeled.
- **Last updated:** 2026-10-16

## Functional requirements

| ID | Requirement | Status | Evidence or note |
|---|---|---|---|
| FR-001 | Private dashboard access | VERIFIED | Exact configured development user required by `backend/app/main.py`; production auth remains required. |
| FR-002 | Create and edit batches | VERIFIED | API and tests cover create/edit. |
| FR-003 | Store incident/recovery date and time separately | VERIFIED | Separate batch fields and fictional audit. |
| FR-004 | Store weekly reporting period | VERIFIED | `period_start` and `period_end`; invalid order is blocking. |
| FR-005 | Bulk image uploads | VERIFIED | Multiple JPG/JPEG/PNG/WebP files accepted in one request. |
| FR-006 | Manual image-to-vehicle association | VERIFIED | `/api/uploads/{id}/associate`; no automatic grouping. |
| FR-007 | Vehicle record CRUD | VERIFIED | Create, edit, and delete endpoints tested. |
| FR-008 | Manual possessor ID/license attachment | VERIFIED | Attachment requires a selected vehicle. |
| FR-009 | Generate daily TXT draft | VERIFIED | UTF-8 output tested and checked for RHPU12. |
| FR-010 | Generate weekly DOCX draft | IMPLEMENTED — UNVERIFIED | Fallback opens; original-template fidelity blocked because source is missing. |
| FR-011 | Generate weekly PPTX draft | IMPLEMENTED — UNVERIFIED | Fallback opens; original-template fidelity blocked because source is missing. |
| FR-012 | Protected draft downloads | VERIFIED | Authorized and unauthorized download tests passed. |
| FR-013 | Validation warnings | VERIFIED | Missing data, duplicate plates, missing files, periods, and count conflicts are covered. |
| FR-014 | Future automatic file detection | DEFERRED | See Phase 02. |
| FR-015 | Future Gemini-assisted grouping/extraction | DEFERRED | See Phase 03. |

## Non-functional requirements

| ID | Requirement | Status | Note |
|---|---|---|---|
| NFR-001 | Privacy and private file paths | VERIFIED — DEVELOPMENT | Files are outside frontend assets; production object storage is still required. |
| NFR-002 | Server-side validation and size limits | VERIFIED | Extension checks and configurable size limit. |
| NFR-003 | Reliability and retry behavior | IMPLEMENTED — UNVERIFIED | Generation errors surface as HTTP errors; robust job retry is future work. |
| NFR-004 | Data integrity | VERIFIED — DEVELOPMENT | SQLite foreign keys and persistent records; no production migration system. |
| NFR-005 | Maintainability | VERIFIED | Separate database, validation, and generation modules. |
| NFR-006 | Responsive interface | VERIFIED | Responsive CSS and production build passed; broad accessibility review remains. |
| NFR-007 | Accessibility | IMPLEMENTED — UNVERIFIED | Semantic controls exist, but no dedicated accessibility audit has run. |
| NFR-008 | Template fidelity | BLOCKED | Original templates are absent. |
| NFR-009 | Auditability | DEFERRED | No audit-events table or download-history table exists. |
| NFR-010 | No automatic sending | VERIFIED | No email, Viber, or submission route exists. |
