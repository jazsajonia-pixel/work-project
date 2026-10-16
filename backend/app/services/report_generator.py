from pathlib import Path
from typing import Any
from docx import Document
from pptx import Presentation

DAILY_HEADER = "RHPU12 / GSCHPT DAILY REPORT\nWHAT: {what}\nWHEN: {when}\nWHERE: {where}\nWHO: {who}\nHOW: {how}\n\nVEHICLE RECORDS (MC/MV)\n"

def validate_batch(batch: dict, vehicles: list[dict], template_types: set[str] | None = None):
    warnings = []
    for field, label in [("incident_date", "incident date"), ("incident_time", "incident time"), ("location", "incident location")]:
        if not batch.get(field): warnings.append(f"Missing required {label}.")
    if not vehicles: warnings.append("No vehicle records have been added.")
    for i, v in enumerate(vehicles, 1):
        if v.get("category") not in {"MC", "MV"}: warnings.append(f"Vehicle {i} is missing a valid MC/MV category.")
        if not v.get("recovery_date") or not v.get("recovery_place"): warnings.append(f"Vehicle {i} is missing recovery date or place.")
    keys = [((v.get("plate_or_sticker") or "").strip().upper(), (v.get("chassis_number") or "").strip().upper()) for v in vehicles]
    if len(keys) != len(set(keys)): warnings.append("Duplicate vehicle records detected within this batch.")
    stated = batch.get("operational_info", "")
    for category, label in [("MC", "motorcycles"), ("MV", "motor vehicles")]:
        import re
        match = re.search(rf"(\d+)\s+{label}", stated, re.I)
        actual = sum(v.get("category") == category for v in vehicles)
        if match and int(match.group(1)) != actual: warnings.append(f"Stated {label} total ({match.group(1)}) disagrees with listed records ({actual}).")
    if template_types is not None:
        for kind in ("TXT", "DOCX", "PPTX"):
            if kind not in template_types: warnings.append(f"No active {kind} template is available; generation uses the clearly marked safe fallback.")
    return warnings

def daily_txt(batch: dict, vehicles: list[dict]) -> str:
    who = batch.get("operational_info") or "Not provided"
    how = batch.get("notes") or "Manual record entry"
    text = DAILY_HEADER.format(what="Vehicle impoundment / recovery", when=f"{batch['incident_date']} {batch['incident_time']}", where=batch['location'], who=who, how=how)
    for i, v in enumerate(vehicles, 1):
        text += f"{i}. {v.get('category','')} | Make/Type/Model: {v.get('make','')} {v.get('vehicle_type','')} {v.get('model','')} | Plate/Sticker: {v.get('plate_or_sticker','')} | Color: {v.get('color','')} | Recovery: {v.get('recovery_date','')} at {v.get('recovery_place','')} | Unit: {v.get('recovering_unit','')} | Violation: {v.get('violation','')}\n"
    return text

def weekly_docx(path: Path, batch: dict, vehicles: list[dict], template: Path | None = None):
    doc = Document(str(template)) if template and template.exists() else Document()
    if not template:
        doc.add_heading("DRAFT — WEEKLY OPERATIONAL REPORT", 0)
        doc.add_paragraph("SAFE FALLBACK: Original DOCX template was not present in the repository.")
    doc.add_paragraph(f"Batch ID: {batch['batch_id']} | Preparation date: {batch['preparation_date']}")
    doc.add_paragraph(f"Incident: {batch['incident_date']} {batch['incident_time']} — {batch['location']}")
    table = doc.add_table(rows=1, cols=6); table.style = "Table Grid"
    for cell, label in zip(table.rows[0].cells, ["Category", "Make / Type / Model", "Plate / Sticker", "Recovery", "Unit", "Status"]): cell.text = label
    for v in vehicles:
        cells = table.add_row().cells
        values = [v.get('category',''), f"{v.get('make','')} {v.get('vehicle_type','')} {v.get('model','')}", v.get('plate_or_sticker',''), f"{v.get('recovery_date','')} / {v.get('recovery_place','')}", v.get('recovering_unit',''), v.get('status','')]
        for cell, value in zip(cells, values): cell.text = value
    doc.save(path)

def weekly_pptx(path: Path, batch: dict, vehicles: list[dict], template: Path | None = None):
    prs = Presentation(str(template)) if template and template.exists() else Presentation()
    if not template:
        slide = prs.slides.add_slide(prs.slide_layouts[0]); slide.shapes.title.text = "DRAFT — WEEKLY OPERATIONAL REPORT"; slide.placeholders[1].text = "SAFE FALLBACK: Original PPTX template was not present."
    slide = prs.slides.add_slide(prs.slide_layouts[5]); slide.shapes.title.text = f"Batch {batch['batch_id']} — Vehicle Recoveries"
    body = slide.shapes.add_textbox(500000, 1200000, 8500000, 5000000).text_frame
    body.text = f"Incident: {batch['incident_date']} {batch['incident_time']}\nLocation: {batch['location']}\n\n" + "\n".join(f"{i}. {v.get('category','')} — {v.get('make','')} {v.get('model','')} — {v.get('plate_or_sticker','')}" for i,v in enumerate(vehicles,1))
    prs.save(path)
