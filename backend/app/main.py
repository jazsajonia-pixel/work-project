import os, re, uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .db import conn, execute, get_row, list_rows, now
from .services.report_generator import validate_batch, daily_txt, weekly_docx, weekly_pptx
ROOT=Path(__file__).resolve().parents[2]; RUNTIME_ROOT=Path('/tmp') if os.getenv('VERCEL') else ROOT; STORAGE=Path(os.getenv('GSCHPT_STORAGE_DIR',RUNTIME_ROOT/'generated_drafts')); PRIVATE=Path(os.getenv('GSCHPT_PRIVATE_STORAGE_DIR',RUNTIME_ROOT/'storage'/'private')); TEMPLATE_DIR=Path(os.getenv('GSCHPT_TEMPLATE_DIR',ROOT/'templates')); STORAGE.mkdir(parents=True,exist_ok=True); PRIVATE.mkdir(parents=True,exist_ok=True); TEMPLATE_DIR.mkdir(parents=True,exist_ok=True)
ALLOWED_ORIGINS=[x.strip() for x in os.getenv('GSCHPT_ALLOWED_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',') if x.strip()]
app=FastAPI(title='GSCHPT Reporting Dashboard API'); app.add_middleware(CORSMiddleware,allow_origins=ALLOWED_ORIGINS,allow_methods=['*'],allow_headers=['*'])
IMAGE_TYPES={'.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp'}; DOC_TYPES={'.pdf':'application/pdf','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.webp':'image/webp'}; MAX_UPLOAD=int(os.getenv('GSCHPT_MAX_UPLOAD_MB','20'))*1024*1024
def auth(user):
    expected=os.getenv('GSCHPT_DEV_USERNAME','admin')
    if not user or user!=expected: raise HTTPException(401,'Development authentication failed. Use the configured development user.')
def batch_or_404(batch_id):
    b=get_row('SELECT * FROM batches WHERE batch_id=?',(batch_id,));
    if not b: raise HTTPException(404,'Batch not found')
    return b
def vehicle_or_404(vehicle_id):
    v=get_row('SELECT * FROM vehicles WHERE id=?',(vehicle_id,));
    if not v: raise HTTPException(404,'Vehicle not found')
    return v
class BatchIn(BaseModel):
    batch_id:str=Field(min_length=2,max_length=80); title:str=''; incident_date:str; incident_time:str; location:str=Field(min_length=1); period_start:str=''; period_end:str=''; operational_info:str=''; notes:str=''; status:str='Draft'
class VehicleIn(BaseModel):
    category:str; make:str=''; vehicle_type:str=''; model:str=''; plate_or_sticker:str=''; chassis_number:str=''; motor_number:str=''; color:str=''; recovery_date:str=''; recovery_place:str=''; recovering_unit:str=''; mode_of_recovery:str=''; violation:str=''; status:str='For review'; driver_name:str=''; driver_address:str=''; owner_name:str=''; owner_address:str=''; notes:str=''; review_status:str='Needs review'
@app.on_event('startup')
def startup(): conn().close()
@app.get('/api/health')
def health():
    try:
        row=get_row('SELECT 1 AS database_check')
        return {'ok':True,'database':'connected' if row and row['database_check']==1 else 'unknown','storage':'ephemeral' if os.getenv('VERCEL') else 'local'}
    except Exception as exc:
        raise HTTPException(503,'Database unavailable') from exc
@app.get('/api/dashboard')
def dashboard(x_dev_user:str|None=Header(None)):
    auth(x_dev_user); return {'total_batches':get_row('SELECT COUNT(*) c FROM batches')['c'],'draft_reports':get_row('SELECT COUNT(*) c FROM generated_reports')['c'],'pending_vehicles':get_row("SELECT COUNT(*) c FROM vehicles WHERE review_status!='Reviewed'")['c'],'records_review':get_row("SELECT COUNT(*) c FROM vehicles WHERE review_status!='Reviewed'")['c'],'recent_batches':list_rows('SELECT * FROM batches ORDER BY id DESC LIMIT 5'),'templates':list_rows('SELECT * FROM templates ORDER BY file_type,id DESC')}
@app.post('/api/batches')
def create_batch(data:BatchIn,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); prep=datetime.now(ZoneInfo('Asia/Manila')).date().isoformat()
    try: execute('INSERT INTO batches(batch_id,title,preparation_date,incident_date,incident_time,location,period_start,period_end,operational_info,notes,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(data.batch_id,data.title,prep,data.incident_date,data.incident_time,data.location,data.period_start,data.period_end,data.operational_info,data.notes,data.status,now(),now()))
    except Exception as e: raise HTTPException(409,'Batch ID already exists.') from e
    return batch_or_404(data.batch_id)
@app.get('/api/batches/{batch_id}')
def get_batch(batch_id:str,x_dev_user:str|None=Header(None)): auth(x_dev_user); return batch_or_404(batch_id)
@app.put('/api/batches/{batch_id}')
def edit_batch(batch_id:str,data:BatchIn,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); batch_or_404(batch_id); execute('UPDATE batches SET title=?,incident_date=?,incident_time=?,location=?,period_start=?,period_end=?,operational_info=?,notes=?,status=?,updated_at=? WHERE batch_id=?',(data.title,data.incident_date,data.incident_time,data.location,data.period_start,data.period_end,data.operational_info,data.notes,data.status,now(),batch_id)); return batch_or_404(batch_id)
@app.get('/api/batches/{batch_id}/vehicles')
def get_vehicles(batch_id:str,x_dev_user:str|None=Header(None)): auth(x_dev_user); batch_or_404(batch_id); return list_rows('SELECT * FROM vehicles WHERE batch_id=? ORDER BY id',(batch_id,))
@app.post('/api/batches/{batch_id}/vehicles')
def add_vehicle(batch_id:str,data:VehicleIn,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); batch_or_404(batch_id); vals=data.model_dump(); execute('INSERT INTO vehicles(batch_id,category,make,vehicle_type,model,plate_or_sticker,chassis_number,motor_number,color,recovery_date,recovery_place,recovering_unit,mode_of_recovery,violation,status,driver_name,driver_address,owner_name,owner_address,notes,review_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(batch_id,*[vals[k] for k in vals])); return list_rows('SELECT * FROM vehicles WHERE batch_id=? ORDER BY id',(batch_id,))[-1]
@app.put('/api/vehicles/{vehicle_id}')
def edit_vehicle(vehicle_id:int,data:VehicleIn,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); vehicle_or_404(vehicle_id); vals=data.model_dump(); execute('UPDATE vehicles SET category=?,make=?,vehicle_type=?,model=?,plate_or_sticker=?,chassis_number=?,motor_number=?,color=?,recovery_date=?,recovery_place=?,recovering_unit=?,mode_of_recovery=?,violation=?,status=?,driver_name=?,driver_address=?,owner_name=?,owner_address=?,notes=?,review_status=? WHERE id=?',(*[vals[k] for k in vals],vehicle_id)); return vehicle_or_404(vehicle_id)
@app.delete('/api/vehicles/{vehicle_id}')
def delete_vehicle(vehicle_id:int,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); vehicle_or_404(vehicle_id); execute('DELETE FROM vehicles WHERE id=?',(vehicle_id,)); return {'deleted':True}
@app.get('/api/batches/{batch_id}/uploads')
def uploads(batch_id:str,x_dev_user:str|None=Header(None)): auth(x_dev_user); batch_or_404(batch_id); return list_rows('SELECT id,batch_id,vehicle_id,kind,filename,content_type,primary_image,document_type,created_at FROM uploads WHERE batch_id=? ORDER BY id',(batch_id,))
def save_upload(batch_id,file,kind,vehicle_id=None,document_type=''):
    PRIVATE.mkdir(parents=True,exist_ok=True); ext=Path(file.filename or '').suffix.lower(); allowed=IMAGE_TYPES if kind=='PHOTO' else DOC_TYPES
    if ext not in allowed: raise HTTPException(400,f'Unsupported {kind.lower()} file type.')
    data=file.file.read()
    if len(data)>MAX_UPLOAD: raise HTTPException(413,'File exceeds 20 MB limit.')
    safe=f'{uuid.uuid4().hex}{ext}'; path=PRIVATE/safe; path.write_bytes(data); uid=execute('INSERT INTO uploads(batch_id,vehicle_id,kind,filename,content_type,path,document_type,created_at) VALUES(?,?,?,?,?,?,?,?)',(batch_id,vehicle_id,kind,Path(file.filename or safe).name,allowed[ext],str(path),document_type,now())); return get_row('SELECT id,batch_id,vehicle_id,kind,filename,content_type,primary_image,document_type,created_at FROM uploads WHERE id=?',(uid,))
@app.post('/api/batches/{batch_id}/photos')
def upload_photos(batch_id:str,files:list[UploadFile]=File(...),x_dev_user:str|None=Header(None)):
    auth(x_dev_user); batch_or_404(batch_id); return [save_upload(batch_id,f,'PHOTO') for f in files]
@app.post('/api/vehicles/{vehicle_id}/attachments')
def attach_document(vehicle_id:int,file:UploadFile=File(...),document_type:str=Form('Possessor ID/license'),x_dev_user:str|None=Header(None)):
    auth(x_dev_user); v=vehicle_or_404(vehicle_id); return save_upload(v['batch_id'],file,'DOCUMENT',vehicle_id,document_type)
@app.patch('/api/uploads/{upload_id}/associate')
def associate_upload(upload_id:int,vehicle_id:int|None=None,primary_image:bool=False,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); u=get_row('SELECT * FROM uploads WHERE id=?',(upload_id,));
    if not u: raise HTTPException(404,'Upload not found')
    if vehicle_id is not None:
        v=vehicle_or_404(vehicle_id)
        if v['batch_id']!=u['batch_id']: raise HTTPException(400,'Vehicle and upload must belong to the same batch.')
    if primary_image: execute("UPDATE uploads SET primary_image=0 WHERE batch_id=? AND vehicle_id=? AND kind='PHOTO'",(u['batch_id'],vehicle_id))
    execute('UPDATE uploads SET vehicle_id=?,primary_image=? WHERE id=?',(vehicle_id,int(primary_image),upload_id)); return get_row('SELECT id,batch_id,vehicle_id,kind,filename,content_type,primary_image,document_type,created_at FROM uploads WHERE id=?',(upload_id,))
@app.delete('/api/uploads/{upload_id}')
def delete_upload(upload_id:int,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); u=get_row('SELECT * FROM uploads WHERE id=?',(upload_id,));
    if not u: raise HTTPException(404,'Upload not found')
    Path(u['path']).unlink(missing_ok=True); execute('DELETE FROM uploads WHERE id=?',(upload_id,)); return {'deleted':True}
@app.get('/api/uploads/{upload_id}/download')
def download_upload(upload_id:int,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); u=get_row('SELECT * FROM uploads WHERE id=?',(upload_id,));
    if not u or not Path(u['path']).is_file(): raise HTTPException(404,'Upload not found')
    return FileResponse(u['path'],filename=u['filename'],media_type=u['content_type'])
def validation(batch_id):
    b=batch_or_404(batch_id); vs=list_rows('SELECT * FROM vehicles WHERE batch_id=?',(batch_id,)); us=list_rows('SELECT * FROM uploads WHERE batch_id=?',(batch_id,)); active={x['file_type'] for x in list_rows('SELECT * FROM templates WHERE active=1')}; return validate_batch(b,vs,us,active)
@app.get('/api/batches/{batch_id}/validate')
def validate(batch_id:str,x_dev_user:str|None=Header(None)): auth(x_dev_user); return validation(batch_id)
@app.post('/api/batches/{batch_id}/draft/{kind}')
def draft(batch_id:str,kind:str,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); b=batch_or_404(batch_id); vs=list_rows('SELECT * FROM vehicles WHERE batch_id=?',(batch_id,)); result=validation(batch_id)
    if result['blocking']: raise HTTPException(422,detail={'message':'Blocking validation errors must be resolved.','blocking':result['blocking'],'review':result['review']})
    kind=kind.upper(); ext={'TXT':'.txt','DOCX':'.docx','PPTX':'.pptx'}.get(kind)
    if not ext: raise HTTPException(400,'Supported draft types: TXT, DOCX, PPTX')
    active=get_row('SELECT * FROM templates WHERE file_type=? AND active=1 ORDER BY id DESC',(kind,)); template=Path(active['path']) if active and Path(active['path']).is_file() else None; filename=f"DRAFT_{batch_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"; path=STORAGE/filename
    if kind=='TXT': path.write_text(daily_txt(b,vs),encoding='utf-8')
    elif kind=='DOCX': weekly_docx(path,b,vs,template)
    else: weekly_pptx(path,b,vs,template)
    status='Passed — draft only' if not result['review'] else 'Generated — review warnings'; execute('INSERT INTO generated_reports(batch_id,file_type,filename,path,template_version,validation_status,generated_at) VALUES(?,?,?,?,?,?,?)',(batch_id,kind,filename,str(path),active['version'] if active else 'fallback-safe-v1',status,now())); return {'filename':filename,'validation_status':status,'blocking':[],'review':result['review']}
@app.get('/api/drafts')
def drafts(x_dev_user:str|None=Header(None)): auth(x_dev_user); return list_rows('SELECT * FROM generated_reports ORDER BY id DESC')
@app.get('/api/drafts/{report_id}/download')
def download(report_id:int,x_dev_user:str|None=Header(None)):
    auth(x_dev_user); r=get_row('SELECT * FROM generated_reports WHERE id=?',(report_id,));
    if not r or not Path(r['path']).is_file(): raise HTTPException(404,'Draft not found')
    return FileResponse(r['path'],filename=r['filename'])
@app.post('/api/templates')
def upload_template(file:UploadFile=File(...),x_dev_user:str|None=Header(None)):
    auth(x_dev_user); allowed={'.txt':'TXT','.docx':'DOCX','.pptx':'PPTX'}; ext=Path(file.filename or '').suffix.lower();
    if ext not in allowed: raise HTTPException(400,'Only TXT, DOCX, and PPTX templates are accepted.')
    data=file.file.read();
    if len(data)>MAX_UPLOAD: raise HTTPException(413,'Template exceeds 20 MB limit.')
    safe=Path(file.filename or ('template'+ext)).name; target=TEMPLATE_DIR/safe; target.write_bytes(data); kind=allowed[ext]; version=datetime.now().strftime('v%Y%m%d%H%M%S'); execute('UPDATE templates SET active=0 WHERE file_type=?',(kind,)); execute('INSERT INTO templates(file_type,filename,version,path,active,created_at) VALUES(?,?,?,?,1,?)',(kind,safe,version,str(target),now())); return {'filename':safe,'file_type':kind,'version':version,'active':True}
