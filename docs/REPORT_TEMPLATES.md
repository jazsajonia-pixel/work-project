# Report Templates

- **Purpose:** Define template handling and record what can actually be verified.
- **Status:** VERIFIED source files present; template-specific mapping is partial and requires operational review.
- **Last updated:** 2026-10-16

## Source availability

The repository now contains the supplied source files as `templates/daily_master.txt`, `templates/weekly_master.docx`, and `templates/weekly_master.pptx`. The source masters are preserved unchanged and are used automatically when no newer active uploaded template exists.

Recorded source fingerprints: `daily_master.txt` SHA-256 `793a39377fc6703a2615c23d49f31b31f5eb9a92ad4e1e9ac82d6c60e20a70e1`; `weekly_master.docx` SHA-256 `986699e302eb1cd8273beec8d04aaa57a4a94b131f6285c4176f3e0f8e47f021`; `weekly_master.pptx` SHA-256 `07e72e5f265b26657fde412ec69b9639eb5b38e5b4fe6cf04ff5c554e7662f9a`. The DOCX contains 49 paragraphs, 12 tables, and 4 sections. The PPTX contains 19 slides at 13808075×7772400 EMU.

## Current locations and loading

- Master directory: `templates/`.
- Upload endpoint: `POST /api/templates`.
- Accepted extensions: `.txt`, `.docx`, `.pptx`.
- Version records: SQLite `templates` table.
- Generation: the active server-side template path is selected and passed to the DOCX/PPTX generator. The source file is read; generation writes a new output path.
- Fallback marker: `fallback-safe-v1` only when neither an active upload nor a bundled master exists; bundled masters are recorded as `bundled-master-v1`.

The current TXT generator follows the supplied `RHPU12`, `GSCHPT`, `What`, `When`, `Where`, `Who`, `How`, `MC`, and `MV` record headings.

## Current population behavior

The TXT generator follows the supplied RHPU12/GSCHPT field headings. The DOCX generator preserves the supplied master and populates vehicle recovery tables while retaining the master’s headings and layout. The PPTX generator preserves the supplied 19-slide master and adds data-summary slides for generated vehicle records. For each vehicle, the primary attached photo, or first attached valid photo when no primary is selected, is inserted into the matching DOCX vehicle-table picture cell and PPTX recovery-slide picture slot. Additional photos and documents remain stored and associated for review.

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

- [x] Original TXT supplied and compared.
- [x] Original DOCX supplied and compared.
- [x] Original PPTX supplied and compared.
- [ ] Fixed wording unchanged.
- [ ] Tables and record ordering preserved.
- [ ] Headers, footers, page breaks, and slide dimensions preserved.
- [x] Embedded images and designated placeholders preserved.
- [x] Master templates remain unchanged.
- [x] Generated outputs are labeled drafts.
