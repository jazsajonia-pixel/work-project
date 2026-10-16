# Phase 07 — Security and Deployment

- **Purpose:** Move from local development controls to production security and hosting.
- **Status:** IN PROGRESS
- **Last updated:** 2026-10-16

## Objective

Provide real authentication and authorization, private storage, HTTPS, protected secrets, database restrictions, backups, recovery, retention, and production acceptance testing.

## Current foundation

The repository has an exact development-user gate, private local upload paths, configurable limits, protected download endpoints, and no committed secrets. These controls are not sufficient for production.

## Required deliverables

Configure identity and roles, PostgreSQL migrations, private object storage, signed/authorized file access, HTTPS, secret injection, audit logging, malware scanning, retention, backup/recovery, access reviews, monitoring, and incident response.

## Acceptance

Test tenant/user isolation, unauthorized downloads, secret absence, TLS, backup restoration, retention, file validation, and production smoke tests. No production deployment is currently claimed.
