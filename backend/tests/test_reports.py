import os
from pathlib import Path
os.environ['GSCHPT_DB_PATH'] = '/tmp/gschpt_test.db'
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
H = {'X-Dev-User':'test'}

def setup_function():
    Path('/tmp/gschpt_test.db').unlink(missing_ok=True)
    from app.db import conn
    conn().close()

def test_batch_and_validation():
    r=client.post('/api/batches',headers=H,json={'batch_id':'T-001','incident_date':'2026-10-16','incident_time':'10:30','location':'Test location','operational_info':'','notes':''})
    assert r.status_code==200 and r.json()['preparation_date']
    assert client.get('/api/batches/T-001/validate',headers=H).json()['warnings']

def test_drafts_open():
    client.post('/api/batches',headers=H,json={'batch_id':'T-002','incident_date':'2026-10-16','incident_time':'10:30','location':'Test location','operational_info':'1 motorcycles','notes':'fictional test'})
    client.post('/api/batches/T-002/vehicles',headers=H,json={'category':'MC','recovery_date':'2026-10-16','recovery_place':'Test location','make':'Test','plate_or_sticker':'ABC-123'})
    for kind, magic in [('TXT',b'RHPU12'),('DOCX',b'PK'),('PPTX',b'PK')]:
        r=client.post(f'/api/batches/T-002/draft/{kind}',headers=H); assert r.status_code==200
        reports=client.get('/api/drafts',headers=H).json(); path=Path('/home/ubuntu/work-project/generated_drafts')/r.json()['filename']; assert path.exists() and path.read_bytes().startswith(magic)
