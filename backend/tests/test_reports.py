import os
import io
import zipfile
from pathlib import Path
from PIL import Image
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
def test_period_weekly_reports_aggregate_matching_batches():
    make_batch('W-001'); client.post('/api/batches/W-001/vehicles',headers=H,json={'category':'MC','recovery_date':'2026-10-12','recovery_place':'Manila','plate_or_sticker':'AAA-111'})
    r=client.post('/api/batches',headers=H,json={'batch_id':'W-002','title':'Second operation','incident_date':'2026-10-14','incident_time':'14:00','location':'Pasig','period_start':'2026-10-12','period_end':'2026-10-18','operational_info':'1 motorcycles','notes':'fictional'}); assert r.status_code==200
    client.post('/api/batches/W-002/vehicles',headers=H,json={'category':'MV','recovery_date':'2026-10-14','recovery_place':'Pasig','plate_or_sticker':'BBB-222'})
    r=client.post('/api/batches',headers=H,json={'batch_id':'W-OUT','title':'Outside','incident_date':'2026-10-20','incident_time':'09:00','location':'Cebu','period_start':'2026-10-20','period_end':'2026-10-20','operational_info':'1 motorcycles','notes':'fictional'}); assert r.status_code==200
    client.post('/api/batches/W-OUT/vehicles',headers=H,json={'category':'MC','recovery_date':'2026-10-20','recovery_place':'Cebu','plate_or_sticker':'CCC-333'})
    for kind,magic in [('DOCX',b'W-001'),('PPTX',b'W-001')]:
        response=client.post('/api/reports/weekly',headers=H,json={'period_start':'2026-10-12','period_end':'2026-10-18','file_type':kind}); assert response.status_code==200, response.text
        body=response.json(); assert set(body['batch_ids'])=={'W-001','W-002'} and body['vehicle_count']==2
        report=client.get(f"/api/drafts/{body['report_id']}",headers=H); assert report.status_code==404
        data=Path(client.get('/api/drafts',headers=H).json()[0]['path']).read_bytes(); assert data.startswith(b'PK')
    bad=client.post('/api/reports/weekly',headers=H,json={'period_start':'2026-10-19','period_end':'2026-10-18','file_type':'DOCX'}); assert bad.status_code==422

def test_vehicle_photo_is_mapped_into_docx_and_pptx_placeholders():
    make_batch('IMG-001')
    vehicle=client.post('/api/batches/IMG-001/vehicles',headers=H,json={'category':'MC','make':'HONDA','model':'PHOTO','plate_or_sticker':'IMG-123','recovery_date':'2026-10-16','recovery_place':'Test location'}).json()
    image=Image.new('RGB',(24,12),(220,30,30)); stream=io.BytesIO(); image.save(stream,format='PNG'); payload=stream.getvalue()
    uploaded=client.post('/api/batches/IMG-001/photos',headers=H,files=[('files',('vehicle.png',payload,'image/png'))]).json()[0]
    assert client.patch(f"/api/uploads/{uploaded['id']}/associate?vehicle_id={vehicle['id']}&primary_image=true",headers=H).status_code==200
    generated={kind:client.post(f'/api/batches/IMG-001/draft/{kind}',headers=H).json() for kind in ('DOCX','PPTX')}
    reports={x['id']:x for x in client.get('/api/drafts',headers=H).json()}
    for kind,result in generated.items():
        report=reports[result['report_id']]
        with zipfile.ZipFile(report['path']) as archive:
            media=[archive.read(name) for name in archive.namelist() if name.startswith('word/media/' if kind=='DOCX' else 'ppt/media/')]
        assert any(payload in item for item in media), f'uploaded photo missing from {kind}'
