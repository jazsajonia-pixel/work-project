# Validation Rules

- **Purpose:** Define blocking errors and review warnings before draft generation.
- **Status:** VERIFIED for current implemented rules; expanded future rules are planned.
- **Last updated:** 2026-10-16

## Blocking errors

Current generation is blocked when:

- The incident date is missing.
- The incident time is missing.
- The location is missing.
- No vehicle records exist.
- A vehicle lacks a valid `MC` or `MV` category.
- A vehicle lacks recovery date or recovery place.
- The reporting period start is after the end.

## Review warnings

Generation may proceed while warning the user when:

- The weekly reporting period is incomplete.
- A vehicle has neither plate/sticker nor chassis number.
- A vehicle has no photograph.
- A vehicle has no possessor ID/license document.
- Duplicate plate/sticker values occur within a batch.
- Narrative counts disagree with listed vehicles, such as five motorcycles stated versus one listed.
- An active authoritative template is unavailable.

## Rules and principles

The system must not invent values, silently correct counts, or infer identity. Users must correct records and regenerate drafts. The current API returns `blocking`, `review`, and `can_generate` fields from validation.

## Planned validation

Future work should add uncertain extracted values, cross-report reconciliation, approved-record requirements, template field-map validation, generation retry state, review completion rules, and audit history. These are not current implementation claims.
