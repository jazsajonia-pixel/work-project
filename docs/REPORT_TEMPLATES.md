# Report Templates

- **Purpose:** Define template handling and record what can actually be verified.
- **Status:** BLOCKED for original-format fidelity.
- **Last updated:** 2026-10-16

## Source availability

The repository contains `templates/.gitkeep` but no authoritative TXT, DOCX, or PPTX files. Their exact headings, fixed wording, tables, images, headers, footers, page breaks, slide structure, and numbering cannot be documented without fabricating information.

## Current locations and loading

- Master directory: `templates/`.
- Upload endpoint: `POST /api/templates`.
- Accepted extensions: `.txt`, `.docx`, `.pptx`.
- Version records: SQLite `templates` table.
- Generation: the active server-side template path is selected and passed to the DOCX/PPTX generator. The source file is read; generation writes a new output path.
- Fallback marker: `fallback-safe-v1` when no active template exists.

The current TXT generator uses known labels `RHPU12`, `GSCHPT`, `WHAT`, `WHEN`, `WHERE`, `WHO`, `HOW`, and an `MC/MV` vehicle-record heading, but the exact source TXT wording is unavailable and therefore not claimed as preserved.

## Current population behavior

The fallback generator writes batch metadata and a vehicle table/list. It does not yet contain authoritative field mappings or image-placement mappings for real templates. Uploaded photos and documents are stored and associated, but are not inserted into generated reports.

## Required template verification procedure

When the original files are supplied:

1. Record filename, hash, version, dimensions, page/slide count, and source date.
2. Inspect fixed wording, headings, field labels, tables, numbering, headers, footers, page breaks, images, placeholders, and reporting date formats.
3. Build an explicit field-mapping table; flag fields that cannot be matched safely.
4. Copy the master to a working output before edits.
5. Generate synthetic reports for MC, MV, missing fields, multiple records, and images.
6. Open DOCX/PPTX with `python-docx`/`python-pptx` and inspect page/slide structure.
7. Compare text, table counts, dimensions, images, formatting, and fixed wording against the original.
8. Confirm the master hash is unchanged.
9. Record limitations and test evidence in this document and the changelog.

## Fidelity checklist

- [ ] Original TXT supplied and compared.
- [ ] Original DOCX supplied and compared.
- [ ] Original PPTX supplied and compared.
- [ ] Fixed wording unchanged.
- [ ] Tables and record ordering preserved.
- [ ] Headers, footers, page breaks, and slide dimensions preserved.
- [ ] Embedded images and designated placeholders preserved.
- [ ] Master templates remain unchanged.
- [ ] Generated outputs are labeled drafts.
