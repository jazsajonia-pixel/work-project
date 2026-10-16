# Weekly Report Aggregation and Validation Workflow

## Presentation Script

**Suggested duration:** 7–10 minutes  
**Audience:** GSCHPT report preparers, reviewers, and supervisors  
**Purpose:** Explain how daily operation batches become one validated weekly DOCX or PPTX report.

---

## Slide 1 — The Weekly Reporting Problem

**Speaker script:**

"The main purpose of the weekly report builder is to combine multiple operations into one reporting-period document or presentation.

An operation may happen every other day, on different dates, or at different locations. Instead of creating one unrelated weekly file for each operation, the system collects all qualifying batches within the scheduled reporting period and produces one weekly DOCX or PPTX snapshot.

For example, if the reporting period is October 12 through October 18, operations recorded on October 12, October 14, and October 17 can all be included in the same weekly report."

**Key message:**

> One reporting period can contain many operation batches, but the final weekly submission is one aggregated report per format.

---

## Slide 2 — Batch-Based Data Collection

**Speaker script:**

"The system still records information batch by batch. A batch represents one operation or one coherent group of records.

A batch normally includes its incident date, time, location, reporting period, operational information, and notes. Each vehicle is recorded separately within that batch.

This means the user can upload all materials collected during one operation—vehicle photos, licenses, OR/CR documents, and other supporting files—and then associate each file with the correct vehicle record.

The batch structure prevents records from different operations or locations from being mixed together. The weekly builder later combines those separate batches only when they belong to the requested period."

**Example:**

```text
Batch 001 — October 12 — Manila
Batch 002 — October 14 — Pasig
Batch 003 — October 17 — Quezon City
```

---

## Slide 3 — Starting a Weekly Report

**Speaker script:**

"To generate a weekly report, the user supplies three values: the start date, the end date, and the output format.

The endpoint is:

`POST /api/reports/weekly`

The request identifies the reporting period and chooses either DOCX or PPTX.

For example:

```json
{
  \"period_start\": \"2026-10-12\",
  \"period_end\": \"2026-10-18\",
  \"file_type\": \"DOCX\"
}
```

The same request can use `PPTX` when the presentation format is required.

The report is rebuilt from the current database contents each time. It is not a file that gets permanently appended day after day."

---

## Slide 4 — How Batches Are Selected

**Speaker script:**

"The selection rule is based on date overlap.

A batch is included when its reporting interval overlaps the requested weekly period. If the batch does not have a reporting interval, the system falls back to the batch incident date.

For a requested period of October 12 through October 18:

- A batch covering October 12 through October 18 is included.
- A batch covering October 14 through October 16 is included.
- A batch with an incident date of October 17 and no explicit period is included.
- A batch covering October 20 is excluded.

Selected batches are ordered chronologically by incident date. Their vehicles are loaded in batch order so the generated report remains understandable and auditable."

**Key message:**

> The weekly report is period-based, not limited to the batch that happens to be selected on screen.

---

## Slide 5 — Validation Before Generation

**Speaker script:**

"Before creating the DOCX or PPTX, the system validates every selected batch independently.

Blocking problems stop weekly generation. Examples include:

- Missing incident date
- Missing incident time
- Missing location
- No vehicle records
- Invalid MC or MV category
- Missing vehicle recovery date or recovery place
- An invalid reporting period where the start is after the end

The system also records review warnings. Warnings do not necessarily stop generation, but they must be reviewed before official submission.

Examples include:

- Missing plate or chassis number
- Missing attached photographs
- Missing possessor ID or license attachment
- Duplicate plate or conduction-sticker numbers
- Stated motorcycle or motor-vehicle totals that disagree with the listed records
- Missing official templates"

---

## Slide 6 — Validation Across Multiple Batches

**Speaker script:**

"Validation is not performed only on the total weekly count. Each included batch is checked on its own, and every validation message is prefixed with the batch ID.

For example:

```text
BATCH-001: Vehicle 1 has no attached photographs.
BATCH-002: Stated motorcycles total disagrees with listed records.
```

This makes it clear which operation needs correction.

If any batch has a blocking error, the weekly report is rejected with a validation response. The user should correct the source batch and generate the weekly report again. This prevents an incomplete operation from silently disappearing inside a larger weekly file."

---

## Slide 7 — DOCX Aggregation

**Speaker script:**

"For DOCX generation, the system creates one weekly document for the requested period.

The document begins with the reporting period, the number of included batches, and the total vehicle count. It then groups the vehicle tables by batch.

Each batch section identifies:

- Batch ID
- Incident date
- Location
- Operation details
- Vehicle category
- Make, type, and model
- Plate or sticker
- Recovery information
- Recovering unit
- Status

When an official DOCX template is supplied, the generator uses that template. Until the authoritative template is provided, the system uses a clearly marked safe fallback and does not claim official formatting fidelity."

---

## Slide 8 — PPTX Aggregation

**Speaker script:**

"For PPTX generation, the same selected batches and validated vehicles are used, but the output is organized as a presentation.

The presentation includes a weekly title slide and a batch-level vehicle recovery slide for each included operation. Each batch slide shows the period, incident information, location, vehicle count, and the listed vehicle details.

As with DOCX generation, the original PPTX template should be supplied before the output is treated as an official presentation. The current fallback is for testing and review, not a claim that the official layout has been preserved."

---

## Slide 9 — Regeneration During the Week

**Speaker script:**

"The weekly report can be generated more than once during the week.

Suppose the user generates a report on October 13. It may contain only the batches known at that time. On October 15, a new batch is submitted. When the user generates the same period again, the new report is rebuilt from the current records and includes the new batch.

This is safer than editing the previous file because it avoids duplicate rows, outdated totals, and accidental loss of earlier records.

Each generation is stored as a report snapshot. The weekly output should therefore be treated as a point-in-time draft or version. The final report should be generated after the last scheduled operation and after all validation warnings have been reviewed."

---

## Slide 10 — Gemini and Make.com Boundaries

**Speaker script:**

"Gemini and Make.com support the workflow, but they do not replace human review.

Gemini can be explicitly triggered to provide suggestions from a vehicle photo. It can help identify visible characteristics, but it does not automatically decide which document belongs to which vehicle and does not create official facts.

After a DOCX or PPTX draft is generated, the system sends a metadata-only event to Make.com. The event identifies the batch or weekly period, file type, filename, validation status, and counts. It does not send license images, addresses, or document contents.

The Make callback is non-blocking. If Make is unavailable, report generation still completes."

---

## Slide 11 — Example End-to-End Week

**Speaker script:**

"Here is a complete example.

On October 12, the team creates Batch 001 for Manila and adds two vehicles.

On October 14, the team creates Batch 002 for Pasig and adds one vehicle.

On October 17, the team creates Batch 003 for Quezon City and adds three vehicles.

The user requests:

```text
Period: October 12–18
Format: DOCX
```

The system selects all three batches, loads six vehicles, validates every batch, and generates one weekly DOCX organized by operation.

If the same request is made as PPTX, it generates one weekly presentation using the same validated data.

If Batch 002 has a blocking error, neither weekly format is generated until Batch 002 is corrected."

---

## Slide 12 — Operational Checklist

**Speaker script:**

"Before final submission, the preparer should complete this checklist:

1. Confirm the start and end dates of the scheduled reporting period.
2. Confirm that every operation has its own batch.
3. Confirm that every vehicle has the correct photos and documents attached.
4. Review missing-field and inconsistent-count warnings.
5. Resolve all blocking validation errors.
6. Review non-blocking warnings.
7. Generate the weekly DOCX.
8. Generate the weekly PPTX if required.
9. Compare the output with the authoritative templates.
10. Treat the final generation as the official period snapshot.

The central principle is simple: daily operations remain separate in the database, while the weekly report compiles all qualifying operations into one validated period-based document or presentation."

---

## Closing Statement

"The weekly report builder gives the team a repeatable process: collect records by operation, validate every batch, aggregate the selected reporting period, and regenerate a complete snapshot whenever new batches arrive. This provides a single weekly DOCX or PPTX without losing the traceability of the individual daily operations."

---

## Technical Reference

- Weekly endpoint: `POST /api/reports/weekly`
- Supported formats: `DOCX`, `PPTX`
- Selection rule: reporting-period overlap, with incident-date fallback
- Validation behavior: any blocking batch error stops generation
- Output storage: generated report snapshot record
- Current fallback behavior: clearly marked output when authoritative templates are absent
- Current security boundary: Gemini and Make credentials remain server-side; Make receives metadata only
