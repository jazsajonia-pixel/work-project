from datetime import datetime
from pathlib import Path
import os, sqlite3

DB_PATH = Path(os.getenv('GSCHPT_DB_PATH', './storage/gschpt.db'))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT UNIQUE NOT NULL, title TEXT NOT NULL DEFAULT '', preparation_date TEXT NOT NULL, incident_date TEXT NOT NULL, incident_time TEXT NOT NULL, location TEXT NOT NULL, period_start TEXT NOT NULL DEFAULT '', period_end TEXT NOT NULL DEFAULT '', operational_info TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'Draft', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS vehicles (id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT NOT NULL REFERENCES batches(batch_id) ON DELETE CASCADE, category TEXT NOT NULL, make TEXT NOT NULL DEFAULT '', vehicle_type TEXT NOT NULL DEFAULT '', model TEXT NOT NULL DEFAULT '', plate_or_sticker TEXT NOT NULL DEFAULT '', chassis_number TEXT NOT NULL DEFAULT '', motor_number TEXT NOT NULL DEFAULT '', color TEXT NOT NULL DEFAULT '', recovery_date TEXT NOT NULL DEFAULT '', recovery_place TEXT NOT NULL DEFAULT '', recovering_unit TEXT NOT NULL DEFAULT '', mode_of_recovery TEXT NOT NULL DEFAULT '', violation TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'For review', driver_name TEXT NOT NULL DEFAULT '', driver_address TEXT NOT NULL DEFAULT '', owner_name TEXT NOT NULL DEFAULT '', owner_address TEXT NOT NULL DEFAULT '', notes TEXT NOT NULL DEFAULT '', review_status TEXT NOT NULL DEFAULT 'Needs review');
CREATE TABLE IF NOT EXISTS templates (id INTEGER PRIMARY KEY AUTOINCREMENT, file_type TEXT NOT NULL, filename TEXT NOT NULL, version TEXT NOT NULL, path TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS generated_reports (id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT NOT NULL, file_type TEXT NOT NULL, filename TEXT NOT NULL, path TEXT NOT NULL, template_version TEXT NOT NULL, validation_status TEXT NOT NULL, generated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS uploads (id INTEGER PRIMARY KEY AUTOINCREMENT, batch_id TEXT NOT NULL REFERENCES batches(batch_id) ON DELETE CASCADE, vehicle_id INTEGER REFERENCES vehicles(id) ON DELETE SET NULL, kind TEXT NOT NULL, filename TEXT NOT NULL, content_type TEXT NOT NULL, path TEXT NOT NULL, primary_image INTEGER NOT NULL DEFAULT 0, document_type TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL);
"""
def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); c.executescript(SCHEMA)
    migrations={'batches': [('title',"TEXT NOT NULL DEFAULT ''"),('period_start',"TEXT NOT NULL DEFAULT ''"),('period_end',"TEXT NOT NULL DEFAULT ''")], 'vehicles':[('mode_of_recovery',"TEXT NOT NULL DEFAULT ''")]}
    for table, cols in migrations.items():
        existing={r[1] for r in c.execute(f'PRAGMA table_info({table})')}
        for name, typ in cols:
            if name not in existing: c.execute(f'ALTER TABLE {table} ADD COLUMN {name} {typ}')
    c.commit(); return c
def now(): return datetime.now().astimezone().isoformat(timespec='seconds')
def rowdict(row): return dict(row) if row else None
def list_rows(query,args=()):
    with conn() as c: return [dict(x) for x in c.execute(query,args).fetchall()]
def get_row(query,args=()):
    with conn() as c: return rowdict(c.execute(query,args).fetchone())
def execute(query,args=()):
    with conn() as c: cur=c.execute(query,args); c.commit(); return cur.lastrowid
