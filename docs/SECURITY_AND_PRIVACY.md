# Security and Privacy

- **Purpose:** Define current controls and required safeguards for sensitive operational and identity records.
- **Status:** IN PROGRESS for production; VERIFIED for the tested development controls.
- **Last updated:** 2026-10-16

## Current controls

- Protected API routes require an exact configured development username.
- Upload extensions are allowlisted and file size is configurable through `GSCHPT_MAX_UPLOAD_MB`.
- Uploaded files are stored server-side with generated UUID filenames.
- Uploads and generated drafts are not placed in frontend public assets.
- Download endpoints require the development authorization header.
- Tests use synthetic records and fake file bytes.
- No API keys or credentials are committed.

## Important limitations

The header gate is not production authentication. The SQLite database has no user ownership or row-level security. Local folders are not a substitute for encrypted private object storage. HTTPS, production identity, role-based authorization, audit logging, retention, backups, and incident response are not configured.

## Handling identity documents

Possessor ID/license documents must be attached only after a user selects and confirms the vehicle. The application does not read identity information automatically. Do not store real documents in Git, test fixtures, frontend assets, or chat messages.

## AI and third-party processing

Real operational images and personal documents must not be submitted to Gemini or another AI service until the service, legal basis, access controls, retention behavior, and data-handling terms have been approved for that information. Future AI output must remain a suggestion for human review.

## Required production controls

1. Real authentication and server-side authorization with user/role ownership.
2. HTTPS and secure cookies or tokens.
3. PostgreSQL with migrations and restricted credentials.
4. Private object storage with signed, authorized access.
5. Secret injection through the deployment platform.
6. Minimal logging with no unnecessary PII.
7. Retention and deletion policy for photos, IDs, drafts, and logs.
8. Encrypted backups and tested recovery.
9. Incident response, access reviews, and audit events.
10. File malware scanning and content validation before production use.

## Threat considerations

Validate filenames, MIME types, size, path ownership, and download authorization. Avoid returning absolute storage paths. Treat uploaded office files and identity documents as sensitive. Do not add automatic sending or public links.
