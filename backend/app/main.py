import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .db import conn, execute, get_row, list_rows, now
from .services.report_generator import validate_batch, daily_txt, weekly_docx, weekly_pptx

ROOT = Path(__file__).resolve().parents[2]
STORAGE = Path(os.getenv('GSCHPT_STORAGE_DIR', ROOT / 'generated_drafts'))
TEMPLATE_DIR = ROOT / 'templates'
STORAGE.mkdir(exist_ok=True); TEMPLATE_DIR.mkdir(exist_ok=True)
app = FastAPI(title='GSCHPT Reporting Dashboard API')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'], allow_methods=['*'], allow_headers=['*'])

def auth(x_dev_user: str | None):
    if not x_dev_user:
        raise HTTPException(401, 'Development authentication required. Set X-Dev-User header.')

def batch_or_404(batch_id: str):
    b = get_row('SELECT * FROM batches WHERE batch_id=?', (batch_id,))
    if not b: raise HTTPException(404, 'Batch not found')
    return b

class BatchIn(BaseModel):
    batch_id: str = Field(min_length=2, max_length=80)
    incident_date: str
    incident_time: str
    location: str = Field(min_length=1)
    operational_info: str = ''
    notes: str = ''

class VehicleIn(BaseModel):
    category: str
    make: str = ''; vehicle_type: str = ''; model: str = ''; plate_or_sticker: str = ''
    chassis_number: str = ''; motor_number: str = ''; color: str = ''; recovery_date: str = ''; recovery_place: str = ''
    recovering_unit: str = ''; violation: str = ''; status: str = 'For review'; driver_name: str = ''; driver_address: str = ''
    owner_name: str = ''; owner_address: str = ''; notes: str = ''; review_status: str = 'Needs review'

@app.on_event('startup')
def startup(): conn().close()

@app.get('/api/health')
def health(): return {'ok': True}

@app.get('/api/dashboard')
def dashboard(x_dev_user: str | None = Header(None)):
    auth(x_dev_user)
    return {'total_batches': get_row('SELECT COUNT(*) c FROM batches')['c'], 'draft_reports': get_row('SELECT COUNT(*) c FROM generated_reports')['c'], 'recent_batches': list_rows('SELECT * FROM batches ORDER BY id DESC LIMIT 5'), 'templates': list_rows('SELECT * FROM templates ORDER BY file_type, id DESC')}

@app.post('/api/batches')
def create_batch(data: BatchIn, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); prep = datetime.now(ZoneInfo('Asia/Manila')).date().isoformat()
    try:
        execute('INSERT INTO batches(batch_id,preparation_date,incident_date,incident_time,location,operational_info,notes,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)', (data.batch_id, prep, data.incident_date, data.incident_time, data.location, data.operational_info, data.notes, now(), now()))
    except Exception as e: raise HTTPException(409, 'Batch ID already exists.') from e
    return batch_or_404(data.batch_id)

@app.get('/api/batches/{batch_id}')
def get_batch(batch_id: str, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); return batch_or_404(batch_id)

@app.put('/api/batches/{batch_id}')
def edit_batch(batch_id: str, data: BatchIn, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); batch_or_404(batch_id)
    execute('UPDATE batches SET incident_date=?,incident_time=?,location=?,operational_info=?,notes=?,updated_at=? WHERE batch_id=?', (data.incident_date, data.incident_time, data.location, data.operational_info, data.notes, now(), batch_id))
    return batch_or_404(batch_id)

@app.get('/api/batches/{batch_id}/vehicles')
def get_vehicles(batch_id: str, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); batch_or_404(batch_id); return list_rows('SELECT * FROM vehicles WHERE batch_id=? ORDER BY id', (batch_id,))

@app.post('/api/batches/{batch_id}/vehicles')
def add_vehicle(batch_id: str, data: VehicleIn, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); batch_or_404(batch_id); values = data.model_dump()
    execute('INSERT INTO vehicles(batch_id,category,make,vehicle_type,model,plate_or_sticker,chassis_number,motor_number,color,recovery_date,recovery_place,recovering_unit,violation,status,driver_name,driver_address,owner_name,owner_address,notes,review_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (batch_id, *[values[k] for k in values]))
    return list_rows('SELECT * FROM vehicles WHERE batch_id=? ORDER BY id', (batch_id,))[-1]

@app.put('/api/vehicles/{vehicle_id}')
def edit_vehicle(vehicle_id: int, data: VehicleIn, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); values = data.model_dump()
    execute('UPDATE vehicles SET category=?,make=?,vehicle_type=?,model=?,plate_or_sticker=?,chassis_number=?,motor_number=?,color=?,recovery_date=?,recovery_place=?,recovering_unit=?,violation=?,status=?,driver_name=?,driver_address=?,owner_name=?,owner_address=?,notes=?,review_status=? WHERE id=?', (*[values[k] for k in values], vehicle_id))
    item = get_row('SELECT * FROM vehicles WHERE id=?', (vehicle_id,))
    if not item: raise HTTPException(404, 'Vehicle not found')
    return item

@app.get('/api/batches/{batch_id}/validate')
def validate(batch_id: str, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); batch_or_404(batch_id); vehicles = list_rows('SELECT * FROM vehicles WHERE batch_id=?', (batch_id,)); active = {x['file_type'] for x in list_rows('SELECT * FROM templates WHERE active=1')}
    return {'warnings': validate_batch(batch_or_404(batch_id), vehicles, active)}

@app.post('/api/batches/{batch_id}/draft/{kind}')
def draft(batch_id: str, kind: str, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); batch = batch_or_404(batch_id); vehicles = list_rows('SELECT * FROM vehicles WHERE batch_id=?', (batch_id,)); warnings = validate_batch(batch, vehicles)
    if warnings: raise HTTPException(422, detail={'message': 'Validation warnings must be resolved before generation.', 'warnings': warnings})
    kind = kind.upper(); ext = {'TXT': '.txt', 'DOCX': '.docx', 'PPTX': '.pptx'}.get(kind)
    if not ext: raise HTTPException(400, 'Supported draft types: TXT, DOCX, PPTX')
    filename = f"DRAFT_{batch_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"; path = STORAGE / filename
    if kind == 'TXT': path.write_text(daily_txt(batch, vehicles), encoding='utf-8')
    elif kind == 'DOCX': weekly_docx(path, batch, vehicles)
    else: weekly_pptx(path, batch, vehicles)
    execute('INSERT INTO generated_reports(batch_id,file_type,filename,path,template_version,validation_status,generated_at) VALUES(?,?,?,?,?,?,?)', (batch_id, kind, filename, str(path), 'fallback-safe-v1', 'Passed — draft only', now()))
    return {'filename': filename, 'validation_status': 'Passed — draft only', 'warnings': []}

@app.get('/api/drafts')
def drafts(x_dev_user: str | None = Header(None)):
    auth(x_dev_user); return list_rows('SELECT * FROM generated_reports ORDER BY id DESC')

@app.get('/api/drafts/{report_id}/download')
def download(report_id: int, x_dev_user: str | None = Header(None)):
    auth(x_dev_user); report = get_row('SELECT * FROM generated_reports WHERE id=?', (report_id,))
    if not report or not Path(report['path']).is_file(): raise HTTPException(404, 'Draft not found')
    return FileResponse(report['path'], filename=report['filename'])

@app.post('/api/templates')
def upload_template(file: UploadFile = File(...), x_dev_user: str | None = Header(None)):
    auth(x_dev_user); allowed = {'.txt': 'TXT', '.docx': 'DOCX', '.pptx': 'PPTX'}; ext = Path(file.filename or '').suffix.lower()
    if ext not in allowed: raise HTTPException(400, 'Only TXT, DOCX, and PPTX templates are accepted.')
    if (awaitable := file) is None: raise HTTPException(400, 'Invalid file')
    data = awaitable.file.read()
    if len(data) > 20 * 1024 * 1024: raise HTTPException(413, 'Template exceeds 20 MB limit.')
    safe_name = Path(file.filename or 'template' + ext).name; target = TEMPLATE_DIR / safe_name; target.write_bytes(data); kind = allowed[ext]; version = datetime.now().strftime('v%Y%m%d%H%M%S')
    execute('UPDATE templates SET active=0 WHERE file_type=?', (kind,)); execute('INSERT INTO templates(file_type,filename,version,path,active,created_at) VALUES(?,?,?,?,1,?)', (kind, safe_name, version, str(target), now()))
    return {'filename': safe_name, 'file_type': kind, 'version': version, 'active': True}
