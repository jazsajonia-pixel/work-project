# Phase 04 — Vehicle Review and Document Matching

- **Purpose:** Plan richer human review for groups, fields, and identity documents.
- **Status:** DEFERRED
- **Last updated:** 2026-10-16

## Current boundary

The current Phase 1 implementation already allows manual image association and manual ID/license attachment. It does not provide full review history, merge/split suggestions, confirmation states, or audit events.

## Planned scope

Support suggested-group review, merge/split, reassignment, field correction, document replacement/removal, confirmation status, missing-document warnings, audit history, and review completion rules. The user remains responsible for matching the correct identity document to the correct vehicle.

## Acceptance and tests

Test reassignment, merge/split, removal, wrong-batch protection, confirmation gates, missing-document warnings, audit records, and refusal to infer identity. Depends on Phase 03 suggestions or can be implemented independently for manual review.
