# Database Schema

- **Purpose:** Describe the actual SQLite schema and distinguish proposed future entities.
- **Status:** VERIFIED against `backend/app/db.py`.
- **Last updated:** 2026-10-16

## Current tables

### `batches`

`id INTEGER PRIMARY KEY AUTOINCREMENT`; `batch_id TEXT UNIQUE NOT NULL`; `title TEXT`; `preparation_date TEXT NOT NULL`; `incident_date TEXT NOT NULL`; `incident_time TEXT NOT NULL`; `location TEXT NOT NULL`; `period_start TEXT`; `period_end TEXT`; `operational_info TEXT`; `notes TEXT`; `status TEXT`; `created_at TEXT NOT NULL`; `updated_at TEXT NOT NULL`.

### `vehicles`

`id INTEGER PRIMARY KEY AUTOINCREMENT`; `batch_id TEXT NOT NULL` references `batches(batch_id)` with cascade delete; `category TEXT NOT NULL`; vehicle identity fields (`make`, `vehicle_type`, `model`, `plate_or_sticker`, `chassis_number`, `motor_number`, `color`); recovery fields (`recovery_date`, `recovery_place`, `recovering_unit`, `mode_of_recovery`); `violation`; `status`; possessor fields (`driver_name`, `driver_address`); owner fields (`owner_name`, `owner_address`); `notes`; `review_status`.

### `templates`

`id INTEGER PRIMARY KEY AUTOINCREMENT`; `file_type`; `filename`; `version`; `path`; `active`; `created_at`. The current code deactivates earlier templates of the same type before inserting a new active record.

### `generated_reports`

`id INTEGER PRIMARY KEY AUTOINCREMENT`; `batch_id`; `file_type`; `filename`; `path`; `template_version`; `validation_status`; `generated_at`. It links output metadata to a batch but does not currently declare a database foreign key.

### `uploads`

`id INTEGER PRIMARY KEY AUTOINCREMENT`; `batch_id` references `batches(batch_id)` with cascade delete; `vehicle_id` references `vehicles(id)` with set-null on delete; `kind` (`PHOTO` or `DOCUMENT`); `filename`; `content_type`; `path`; `primary_image`; `document_type`; `created_at`.

## Constraints and indexes

Primary keys and the unique `batches.batch_id` constraint are implemented. Foreign-key enforcement is enabled per SQLite connection. No explicit secondary indexes, row-level security, or database-level user ownership policies exist.

## Storage references

Database rows store server-side paths for templates, generated drafts, and private uploads. These paths must not be exposed directly to browsers; protected download endpoints resolve them after authorization.

## Migration procedure

The current application runs `CREATE TABLE IF NOT EXISTS` and a small additive-column migration in `db.conn()` at startup. This is sufficient for local development only. A hosted deployment needs versioned migrations and PostgreSQL schema management.

## Proposed schema — not implemented

Future entities may include:

- `audit_events` for actor, action, target, timestamp, and outcome.
- `report_generation_runs` for retries, failure details, and run status.
- User/role ownership tables for multi-user authorization.
- Object-storage metadata and retention records.
- Explicit review/approval history.

These are proposals, not current tables.
