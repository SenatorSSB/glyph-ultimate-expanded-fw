# Official Configurator Manual Capture Instructions

> Retired lane notice: `GP-CONFIG-002` is invalidated by `GLYPH-UD-007`.
> This procedure is retained as historical provenance only. No operator
> capture is required or awaited unless the user explicitly reopens the lane.

Status: `MANUAL_CAPTURE_INSTRUCTIONS_ONLY_NOT_A_RESULT`

## Purpose

This document defines operator-only instructions for a **future** manual official
configurator import/export capture workflow.

It is explicit plan-only documentation. No manual capture is performed by this
document, and no result is recorded here.

The candidate artifact is offline preview metadata only. It is not production
export output and must not be assumed importable by the official configurator.
Attempt it only if explicitly chosen for a manual app-level experiment, and
record rejection if the app rejects it.

## Preconditions

Before starting a future operator capture, verify:

- Baseline artifacts are present:
  - `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
  - `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json`
  - `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json`
  - `docs/export/official_configurator_manual_import_export_result_TEMPLATE.md`
  - `docs/export/official_configurator_manual_import_export_test_plan.md`
- Candidate preview fixture and metadata template are available:
  - `docs/export/fixtures/generated_official_configurator_candidate_preview.json`
  - `docs/export/fixtures/official_configurator_manual_capture_metadata_TEMPLATE.json`

If any item above is missing, note the precondition as `blocked` and do not
proceed with a capture attempt or result artifact creation.

## Operator Flow (Future Run)

1. Create a future capture folder only when the operator is ready to run the
   manual app-level experiment:
   `docs/export/manual_captures/YYYYMMDD_official_configurator_<app-version-or-unknown>/`
2. Copy the metadata template to that folder as `metadata.json` and fill only
   the operator and route fields before the attempt.
2. Prepare one copy of the generated preview candidate from source control.
3. Record the input artifact path and hash in the metadata.
4. Perform only a manual app UI path in the official configurator context.
5. Record the official configurator app/version, operating system, date/time,
   operator, import route attempted, export/download route, whether the app
   accepted or rejected the input, and notes.
6. If accepted and exported, place the captured export as `output_export.json`.
   If rejected, place `rejection_note.md` instead.
7. Record SHA-256 hashes in `hashes.txt` and metadata.
8. Run the future result checker only after artifacts exist.
9. Add reviewer notes and row-level outcome flags for capture path + diff check.

Reviewed metadata is schema version 2. Use exactly one row for import, export,
and capture-local diff. Record `PASS`, `FAIL`, `NOT_TESTED`, or `INCONCLUSIVE`
for each row, with `pass` true only for `PASS`; use the exact overall matrix
and gap rules in the artifact-layout contract. For an output capture, store a
capture-local `comparison.json` binding the input/output hashes and diff-row
status. For a rejection, omit comparison.json and bind the rejection-note
hash instead.

## Required Operator Fields

- official configurator app/version
- operating system
- date/time
- operator
- import route attempted
- export/download route
- whether app accepted/rejected input
- notes

## Hash Commands

From the repository root:

```bash
shasum -a 256 docs/export/manual_captures/YYYYMMDD_official_configurator_<app-version-or-unknown>/input_candidate.json
shasum -a 256 docs/export/manual_captures/YYYYMMDD_official_configurator_<app-version-or-unknown>/output_export.json
shasum -a 256 docs/export/manual_captures/YYYYMMDD_official_configurator_<app-version-or-unknown>/metadata.json
```

If the app rejects the candidate, hash `rejection_note.md` instead of
`output_export.json`.

## Future Pass/Fail/Inconclusive Criteria

- pass: metadata is complete, hashes match artifacts, the app accepted the
  candidate through the recorded route, export/download produced
  `output_export.json`, and reviewer inspection records the result without
  unsupported claims.
- fail: the app rejects the candidate, export/download is unavailable, JSON is
  unparsable, hashes are missing or mismatched, or any unsupported claim would
  be required.
- inconclusive: required operator metadata is unknown, the route cannot be
  reconstructed, artifacts are incomplete, or reviewer inspection cannot decide.

## Forbidden In This Workflow

- Do not treat this packet as a result.
- Do not claim import/export compatibility.
- Do not claim production export.
- Do not claim device-write behavior.
- Do not claim WebSerial behavior.
- Do not claim runtime-loaded config support.
- Do not claim firmware flashing automation.
- Do not claim hardware behavior validation.
- Do not claim nunchuk validation.

## Required Output Paths

Use the directory layout in:
`docs/export/official_configurator_manual_capture_artifact_layout.md`

## Checkpoint Artifact Example

- template to fill: `docs/export/fixtures/official_configurator_manual_capture_metadata_TEMPLATE.json`
- optional checker output: `tools/check_glyph_official_configurator_export_candidate_diff.py`

## Non-Claims to Preserve

- no capture performed
- no result recorded
- no official configurator compatibility claim
- no production export
- no official-configurator importability/exportability claim
- no device write
- no WebSerial
- no runtime-loaded config
- no firmware flashing automation
- no hardware behavior validation
- no nunchuk validation

Stop line: this branch does not perform capture.

Stop line: this branch does not record result.
