# Phase 06 — Validation and Quality Assurance

- **Purpose:** Establish repeatable data and document quality gates.
- **Status:** IN PROGRESS
- **Last updated:** 2026-10-16

## Current scope

Validation distinguishes blocking errors from review warnings and covers missing incident data, missing vehicle data, periods, identifiers, photos, ID/license documents, duplicate plates, narrative-count conflicts, and missing templates.

## Remaining scope

Add cross-report consistency, approved-record requirements, uncertain extracted values, generation failure recovery, auditability, real-template regression, formatting comparison, and deployment smoke tests.

## Acceptance and tests

Use synthetic fixtures for valid and invalid records. Compare generated files to each supplied master, verify unchanged masters, exercise retries and failure paths, and record actual results in [Testing Strategy](../TESTING_STRATEGY.md).
