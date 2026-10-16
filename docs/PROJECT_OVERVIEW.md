# Project Overview

- **Purpose:** Describe the GSCHPT reporting problem and intended operating model.
- **Status:** VERIFIED for the current repository scope.
- **Last updated:** 2026-10-16

## Problem and users

The system is intended to help authorized operators prepare GSCHPT operational reports from vehicle photographs and manually entered incident/recovery information. It is designed for a private dashboard used by trained personnel who review and confirm records before a report is generated.

## Scope

The current implementation supports persistent reporting batches, incident details, vehicle records, bulk photo uploads, manual photo-to-vehicle association, manual possessor ID/license attachment, validation, and draft downloads. Outputs are daily TXT, weekly DOCX, and weekly PPTX drafts.

## Current workflow

1. An authorized development user opens the dashboard.
2. The user creates a batch with incident details and, where applicable, a weekly reporting period.
3. The user creates or edits vehicle records.
4. The user uploads unsorted photographs and manually associates them with vehicles.
5. The user attaches possessor ID/license files to a selected vehicle.
6. The system reports blocking errors and review warnings.
7. The user generates one draft format at a time and downloads it for human review.

## Inputs and outputs

Inputs include dates, times, location, operational narrative, notes, vehicle fields, photographs, and manually selected identity-document attachments. Outputs are server-side draft files. The system does not send, publish, email, message, or submit reports.

## Manual responsibilities

Users remain responsible for confirming vehicle grouping, identity-document association, field accuracy, counts, report wording, and final official use. The application must not invent missing facts or silently change official counts.

## Explicit exclusions

Gemini or other AI image analysis, automatic grouping, automatic plate extraction, automatic file detection, automatic batch processing, email, Viber, report submission, and AI-generated official facts are not implemented.

## Current limitations

The repository contains the supplied TXT, DOCX, and PPTX masters under `templates/`. Generation uses the masters by default and preserves their source structure while populating the currently mapped vehicle fields. Picture-placeholder insertion remains a known limitation. Authentication is a development header gate, while production uses Neon and Vercel runtime configuration.

## Long-term vision

Future phases may add idempotent upload detection, AI-assisted suggestions, richer human review, template-aware generation, quality assurance, production security, monitoring, and maintenance. Each addition must preserve human confirmation and draft-only behavior until separately authorized.
