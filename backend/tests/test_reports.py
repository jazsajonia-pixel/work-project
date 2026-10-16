import os
from pathlib import Path
os.environ['GSCHPT_DB_PATH']='/tmp/gschpt_test.db'; os.environ['GSCHPT_PRIVATE_STORAGE_DIR']='/tmp/gschpt_private'; os.environ['GSCHPT_DEV_USERNAME']='test'
from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app); H={'X-Dev-User':'test'}
def setup_function():
    Path('/tmp/gschpt_test.db').unlink(missing_ok=True); import shutil; shutil.rmtree('/tmp/gschpt_private',ignore_errors=True)
def make_batch(batch='T-001'):
    return client.post('/api/batches',headers=H,json={'batch_id':batch,'title':'Synthetic test','incident_date':'2026-10-16','incident_time':'10:30','location':'Test location','period_start':'2026-10-12','period_end':'2026-10-18','operational_info':'1 motorcycles','notes':'fictional'})
def test_health_reports_database_connection():
    r=client.get('/api/health'); assert r.status_code==200 and r.json()['ok'] is True and r.json()['database']=='connected' and r.json()['storage']=='local'
def test_gemini_analysis_is_explicit_and_requires_configuration():
    make_batch(); p=client.post('/api/batches/T-001/photos',headers=H,files=[('files',('car.jpg',b'fake-jpg','image/jpeg'))]).json()[0]
    r=client.post(f"/api/uploads/{p['id']}/analyze",headers=H); assert r.status_code==503 and 'Gemini' in r.json()['detail']
def test_auth_and_batch_edit():
    assert client.get('/api/dashboard').status_code==401
    r=make_batch(); assert r.status_code==200 and r.json()['preparation_date']
    r=client.put('/api/batches/T-001',headers=H,json={**r.json(),'batch_id':'T-001','title':'Edited','incident_date':'2026-10-17','incident_time':'11:00','location':'New location','period_start':'2026-10-12','period_end':'2026-10-18','status':'Draft'}); assert r.status_code==200 and r.json()['title']=='Edited'
def test_vehicle_crud_photo_and_document_association():
    make_batch(); v=client.post('/api/batches/T-001/vehicles',headers=H,json={'category':'MC','recovery_date':'2026-10-16','recovery_place':'Test location','plate_or_sticker':'ABC-123'}).json(); assert v['id']
    p=client.post('/api/batches/T-001/photos',headers=H,files=[('files',('car.jpg',b'fake-jpg','image/jpeg')),('files',('car2.png',b'fake-png','image/png'))]); assert p.status_code==200 and len(p.json())==2
    u=p.json()[0]; a=client.patch(f"/api/uploads/{u['id']}/associate?vehicle_id={v['id']}&primary_image=true",headers=H); assert a.status_code==200 and a.json()['vehicle_id']==v['id']
    d=client.post(f"/api/vehicles/{v['id']}/attachments",headers=H,files={'file':('license.pdf',b'fake-pdf','application/pdf')}); assert d.status_code==200 and d.json()['kind']=='DOCUMENT'
    assert len(client.get('/api/batches/T-001/uploads',headers=H).json())==3
    assert client.delete(f"/api/vehicles/{v['id']}",headers=H).status_code==200
def test_validation_and_all_drafts():
    make_batch('T-002'); client.post('/api/batches/T-002/vehicles',headers=H,json={'category':'MC','recovery_date':'2026-10-16','recovery_place':'Test location','plate_or_sticker':'ABC-123'})
    result=client.get('/api/batches/T-002/validate',headers=H).json(); assert result['blocking']==[] and result['review']
    for kind,magic in [('TXT',b'RHPU12'),('DOCX',b'PK'),('PPTX',b'PK')]:
        r=client.post(f'/api/batches/T-002/draft/{kind}',headers=H); assert r.status_code==200
        report=client.get('/api/drafts',headers=H).json()[0]; assert Path(report['path']).read_bytes().startswith(magic)
        assert client.get(f"/api/drafts/{report['id']}/download",headers=H).status_code==200
