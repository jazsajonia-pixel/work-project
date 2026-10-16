from pathlib import Path
from docx import Document
from docx.shared import Inches
from pptx import Presentation
from pptx.util import Emu
from PIL import Image
import re
DAILY_HEADER='RHPU12 / GSCHPT DAILY REPORT\nWHAT: {what}\nWHEN: {when}\nWHERE: {where}\nWHO: {who}\nHOW: {how}\n\nVEHICLE RECORDS (MC/MV)\n'
def validate_batch(batch, vehicles, uploads=None, template_types=None):
    blocking=[]; review=[]
    for field,label in [('incident_date','incident date'),('incident_time','incident time'),('location','incident location')]:
        if not batch.get(field): blocking.append(f'Missing required {label}.')
    if not batch.get('period_start') or not batch.get('period_end'): review.append('Weekly reporting period is incomplete; required for weekly templates.')
    if batch.get('period_start') and batch.get('period_end') and batch['period_start']>batch['period_end']: blocking.append('Reporting period start must not be after its end.')
    if not vehicles: blocking.append('No vehicle records have been added.')
    for i,v in enumerate(vehicles,1):
        if v.get('category') not in {'MC','MV'}: blocking.append(f'Vehicle {i} is missing a valid MC/MV category.')
        if not v.get('recovery_date') or not v.get('recovery_place'): blocking.append(f'Vehicle {i} is missing recovery date or place.')
        if not v.get('plate_or_sticker') and not v.get('chassis_number'): review.append(f'Vehicle {i} has no plate/sticker or chassis number; review identity fields.')
        files=[u for u in (uploads or []) if u.get('vehicle_id')==v.get('id')]
        if not files: review.append(f'Vehicle {i} has no attached photographs.')
        if not any(u.get('kind')=='DOCUMENT' for u in files): review.append(f'Vehicle {i} has no possessor ID/license attachment.')
    plates=[(v.get('plate_or_sticker') or '').strip().upper() for v in vehicles if (v.get('plate_or_sticker') or '').strip()]
    if len(plates)!=len(set(plates)): review.append('Duplicate plate or conduction-sticker numbers detected within this batch.')
    stated=batch.get('operational_info','')
    for category,label in [('MC','motorcycles'),('MV','motor vehicles')]:
        m=re.search(rf'(\d+)\s+{label}',stated,re.I); actual=sum(v.get('category')==category for v in vehicles)
        if m and int(m.group(1))!=actual: review.append(f'Stated {label} total ({m.group(1)}) disagrees with listed records ({actual}).')
    if template_types is not None:
        for kind in ('TXT','DOCX','PPTX'):
            if kind not in template_types: review.append(f'No active {kind} template is available; safe fallback will be used.')
    return {'blocking':blocking,'review':review,'can_generate':not blocking}
def daily_txt(batch,vehicles):
    text=DAILY_HEADER.format(what='Vehicle impoundment / recovery',when=f"{batch['incident_date']} {batch['incident_time']}",where=batch['location'],who=batch.get('operational_info') or 'Not provided',how=batch.get('notes') or 'Manual record entry')
    for i,v in enumerate(vehicles,1): text+=f"{i}. {v.get('category','')} | Make/Type/Model: {v.get('make','')} {v.get('vehicle_type','')} {v.get('model','')} | Plate/Sticker: {v.get('plate_or_sticker','')} | Color: {v.get('color','')} | Recovery: {v.get('recovery_date','')} at {v.get('recovery_place','')} | Unit: {v.get('recovering_unit','')} | Violation: {v.get('violation','')}\n"
    return text
def _photo_for_vehicle(vehicle,uploads):
    photos=[u for u in (uploads or []) if u.get('kind')=='PHOTO' and u.get('vehicle_id')==vehicle.get('id') and Path(u.get('path','')).is_file()]
    photos.sort(key=lambda u:(-int(u.get('primary_image') or 0),u.get('id',0)))
    for photo in photos:
        try:
            with Image.open(photo['path']) as image: image.verify()
            return photo['path']
        except Exception:
            continue
    return None

def _fit_dimensions(path,max_width,max_height):
    with Image.open(path) as image: width,height=image.size
    scale=min(max_width/width,max_height/height)
    return max(1.0,width*scale),max(1.0,height*scale)

def _insert_docx_photo(cell,path):
    cell.text=''
    width,height=_fit_dimensions(path,1.15,0.78)
    run=cell.paragraphs[0].add_run(); run.add_picture(path,width=Inches(width),height=Inches(height))

def _replace_pptx_photo(slide,placeholder,path):
    width,height=_fit_dimensions(path,placeholder.width,placeholder.height)
    width,height=int(width),int(height)
    left=placeholder.left+(placeholder.width-width)//2; top=placeholder.top+(placeholder.height-height)//2
    replacement=slide.shapes.add_picture(path,left,top,width=width,height=height)
    placeholder._element.getparent().remove(placeholder._element)
    return replacement

def weekly_docx(path,batch,vehicles,template=None,uploads=None):
    if template:
        return weekly_docx_aggregate(path,batch.get('period_start',''),batch.get('period_end',''),[batch],vehicles,template,uploads)
    doc=Document(str(template)) if template and template.exists() else Document()
    if not template: doc.add_heading('DRAFT — WEEKLY OPERATIONAL REPORT',0); doc.add_paragraph('SAFE FALLBACK: Original DOCX template was not present in the repository.')
    doc.add_paragraph(f"Batch ID: {batch['batch_id']} | Preparation date: {batch['preparation_date']} | Period: {batch.get('period_start','')} to {batch.get('period_end','')}")
    doc.add_paragraph(f"Incident: {batch['incident_date']} {batch['incident_time']} — {batch['location']}")
    table=doc.add_table(rows=1,cols=6); table.style='Table Grid'
    for cell,label in zip(table.rows[0].cells,['Category','Make / Type / Model','Plate / Sticker','Recovery','Unit','Status']): cell.text=label
    for v in vehicles:
        cells=table.add_row().cells
        for cell,value in zip(cells,[v.get('category',''),f"{v.get('make','')} {v.get('vehicle_type','')} {v.get('model','')}",v.get('plate_or_sticker',''),f"{v.get('recovery_date','')} / {v.get('recovery_place','')}",v.get('recovering_unit',''),v.get('status','')]): cell.text=value
    doc.save(path)
def weekly_pptx(path,batch,vehicles,template=None,uploads=None):
    if template:
        return weekly_pptx_aggregate(path,batch.get('period_start',''),batch.get('period_end',''),[batch],vehicles,template,uploads)
    prs=Presentation(str(template)) if template and template.exists() else Presentation()
    if not template:
        slide=prs.slides.add_slide(prs.slide_layouts[0]); slide.shapes.title.text='DRAFT — WEEKLY OPERATIONAL REPORT'; slide.placeholders[1].text='SAFE FALLBACK: Original PPTX template was not present.'
    slide=prs.slides.add_slide(prs.slide_layouts[0]); slide.shapes.title.text=f"Batch {batch['batch_id']} — Vehicle Recoveries"
    body=slide.shapes.add_textbox(500000,1200000,8500000,5000000).text_frame; body.text=f"Period: {batch.get('period_start','')} to {batch.get('period_end','')}\nLocation: {batch['location']}\n\n"+'\n'.join(f"{i}. {v.get('category','')} — {v.get('make','')} {v.get('model','')} — {v.get('plate_or_sticker','')}" for i,v in enumerate(vehicles,1)); prs.save(path)

def weekly_docx_aggregate(path, period_start, period_end, batches, vehicles, template=None,uploads=None):
    doc=Document(str(template)) if template and template.exists() else Document()
    if not template: doc.add_heading('DRAFT — WEEKLY OPERATIONAL REPORT',0); doc.add_paragraph('SAFE FALLBACK: Original DOCX template was not present in the repository.')
    if template:
        for paragraph in doc.paragraphs:
            paragraph.text=re.sub(r'\(\)|_+',str(len([v for v in vehicles if v.get('category')=='MV'])),paragraph.text) if 'recovered MV' in paragraph.text else paragraph.text
            paragraph.text=re.sub(r'\(\)|_+',str(len([v for v in vehicles if v.get('category')=='MC'])),paragraph.text) if 'recovered MC' in paragraph.text else paragraph.text
        _fill_template_vehicle_tables(doc,batches,vehicles,period_start,period_end,uploads)
        return doc.save(path)
    doc.add_paragraph(f"Reporting period: {period_start} to {period_end} | Batches included: {len(batches)} | Vehicles: {len(vehicles)}")
    by_batch={b['batch_id']:[] for b in batches}
    for vehicle in vehicles: by_batch.setdefault(vehicle['batch_id'],[]).append(vehicle)
    for batch in batches:
        doc.add_heading(f"Batch {batch['batch_id']} — {batch['incident_date']} — {batch['location']}",1)
        doc.add_paragraph(batch.get('title') or batch.get('operational_info') or 'Operation details not provided.')
        table=doc.add_table(rows=1,cols=6); table.style='Table Grid'
        for cell,label in zip(table.rows[0].cells,['Category','Make / Type / Model','Plate / Sticker','Recovery','Unit','Status']): cell.text=label
        for v in by_batch.get(batch['batch_id'],[]):
            cells=table.add_row().cells
            for cell,value in zip(cells,[v.get('category',''),f"{v.get('make','')} {v.get('vehicle_type','')} {v.get('model','')}",v.get('plate_or_sticker',''),f"{v.get('recovery_date','')} / {v.get('recovery_place','')}",v.get('recovering_unit',''),v.get('status','')]): cell.text=value
    doc.save(path)

def _fill_template_vehicle_tables(doc,batches,vehicles,period_start,period_end,uploads=None):
    """Populate the supplied master tables without destroying their headings, images, or layout."""
    batch_by_id={b['batch_id']:b for b in batches}; rows_by_kind={'MC':[v for v in vehicles if v.get('category')=='MC'],'MV':[v for v in vehicles if v.get('category')=='MV']}
    candidates=[]
    for table in doc.tables:
        headers=' '.join(cell.text for cell in table.rows[0].cells).lower()
        has_picture_slot=any(cell._element.xpath('.//*[local-name()="drawing"]') for row in table.rows[1:] for cell in row.cells)
        if 'plate' in headers and ('recovery' in headers or 'date' in headers) and has_picture_slot: candidates.append(table)
    for index,table in enumerate(candidates):
        kind='MC' if index==0 else 'MV' if index==1 else None
        if not kind: continue
        records=rows_by_kind[kind]
        for row_index, vehicle in enumerate(records,1):
            row=table.rows[row_index] if row_index < len(table.rows) else table.add_row()
            values=[str(row_index),f"{vehicle.get('make','')} {vehicle.get('vehicle_type','')} {vehicle.get('model','')}",vehicle.get('recovery_date',''),vehicle.get('recovering_unit',''),vehicle.get('plate_or_sticker',''),vehicle.get('mode_of_recovery',''),vehicle.get('recovery_place',''),vehicle.get('violation',''),vehicle.get('status','')]
            for cell,value in zip(row.cells,values): cell.text=value
            photo=_photo_for_vehicle(vehicle,uploads)
            if photo: _insert_docx_photo(row.cells[1],photo)
        for row_index in range(len(records)+1,len(table.rows)):
            for cell in table.rows[row_index].cells: cell.text=''
    for paragraph in doc.paragraphs:
        if 'DETAILS/SYNOPSIS' in paragraph.text: paragraph.text=f'DETAILS/SYNOPSIS OF ACCOMPLISHMENT — {period_start} to {period_end}'

def weekly_pptx_aggregate(path, period_start, period_end, batches, vehicles, template=None,uploads=None):
    prs=Presentation(str(template)) if template and template.exists() else Presentation()
    if not template:
        slide=prs.slides.add_slide(prs.slide_layouts[0]); slide.shapes.title.text='DRAFT — WEEKLY OPERATIONAL REPORT'; slide.placeholders[1].text='SAFE FALLBACK: Original PPTX template was not present.'
    else:
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape,'text') and 'WEEKLY ASSESSMENT' in shape.text:
                    shape.text=f'RHPU 12 WEEKLY ASSESSMENT\n({period_start} to {period_end})'
        _map_pptx_template_photos(prs,vehicles,uploads)
        _add_template_summary_slides(prs,period_start,period_end,batches,vehicles)
        return prs.save(path)
    by_batch={b['batch_id']:[] for b in batches}
    for vehicle in vehicles: by_batch.setdefault(vehicle['batch_id'],[]).append(vehicle)
    for batch in batches:
        slide=prs.slides.add_slide(prs.slide_layouts[5]); slide.shapes.title.text=f"Batch {batch['batch_id']} — Vehicle Recoveries"
        rows=by_batch.get(batch['batch_id'],[])
        body=slide.shapes.add_textbox(500000,1200000,8500000,5000000).text_frame
        body.text=f"Reporting period: {period_start} to {period_end}\nIncident: {batch['incident_date']} {batch['incident_time']} — {batch['location']}\nVehicles: {len(rows)}\n\n"+'\n'.join(f"{i}. {v.get('category','')} — {v.get('make','')} {v.get('vehicle_type','')} {v.get('model','')} — {v.get('plate_or_sticker','')}" for i,v in enumerate(rows,1))
    prs.save(path)

def _add_template_summary_slides(prs,period_start,period_end,batches,vehicles):
    by_category={'MC':[v for v in vehicles if v.get('category')=='MC'],'MV':[v for v in vehicles if v.get('category')=='MV']}
    for category,records in by_category.items():
        slide=prs.slides.add_slide(prs.slide_layouts[0]); slide.shapes.title.text=f'{category} DATA SUMMARY — {period_start} to {period_end}'
        body=slide.shapes.add_textbox(500000,1200000,8500000,5000000).text_frame
        body.text='\n'.join(f"{i}. {v.get('make','')} {v.get('vehicle_type','')} {v.get('model','')} | {v.get('plate_or_sticker','')} | {v.get('recovery_date','')} | {v.get('recovery_place','')}" for i,v in enumerate(records,1)) or 'No records in this category.'

def _map_pptx_template_photos(prs,vehicles,uploads):
    slots={'MV':[slide for slide in prs.slides if any(hasattr(shape,'text') and 'MOTOR VEHICLE RECOVERY' in shape.text for shape in slide.shapes)],'MC':[slide for slide in prs.slides if any(hasattr(shape,'text') and 'MOTORCYCLES RECOVERY' in shape.text for shape in slide.shapes)]}
    counters={'MV':0,'MC':0}
    for vehicle in vehicles:
        category=vehicle.get('category'); photo=_photo_for_vehicle(vehicle,uploads)
        if category not in slots or not photo: continue
        index=counters[category]; counters[category]+=1
        if index>=len(slots[category]): continue
        slide=slots[category][index]; placeholders=[shape for shape in slide.shapes if shape.shape_type==13]
        if placeholders: _replace_pptx_photo(slide,placeholders[0],photo)
