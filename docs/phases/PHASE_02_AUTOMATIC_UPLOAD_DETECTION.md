# Phase 02 — Automatic Upload Detection

- **Purpose:** Plan safe detection and ingestion of new uploads.
- **Status:** DEFERRED
- **Last updated:** 2026-10-16

## Objective

Detect new files only after an explicit user-selected batch context and preserve idempotency, failure visibility, and manual control.

## Proposed scope

Track upload identity and checksum, associate files with a batch, detect duplicates, record completion, expose failed uploads, retry safely, and require an explicit **Complete Batch** action before processing. Detection must never generate or send reports.

## Dependencies

Requires production object storage, ownership-aware authentication, an upload-status model, background-job infrastructure, and a recovery policy.

## Acceptance and tests

Test duplicate files, incomplete batches, failed uploads, retries, idempotency, unauthorized access, and explicit completion. No implementation exists in the current repository.
