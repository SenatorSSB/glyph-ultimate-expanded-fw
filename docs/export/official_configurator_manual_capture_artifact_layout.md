# Official Configurator Manual Capture Artifact Layout

Status: `TEMPLATE_ONLY_NOT_A_RESULT`

## Purpose

Define the fixed relative layout for future official configurator manual
import/export capture artifacts.

This file does not claim a capture was run and does not contain captured
artifacts.

## Directory Layout

```
docs/export/manual_captures/
  .gitkeep
  README.md
  YYYYMMDD_official_configurator_<app-version-or-unknown>/ (future capture folder)
    input_candidate.json
    output_export.json or rejection_note.md
    metadata.json
    hashes.txt
    notes.md
    optional_screenshot_or_log_notes.md

Template used for each capture row:
- `docs/export/fixtures/official_configurator_manual_capture_metadata_TEMPLATE.json`
```

The folder name must use the pattern:

`YYYYMMDD_official_configurator_<app-version-or-unknown>/`

Use `unknown` when the exact app version is unavailable.

The optional screenshot/log notes file must be safe and non-sensitive. Do not
include personal tokens, private browser state, device identifiers, or account
information.

## Baseline Files Required Before Any Capture Record

Capture output should only be prepared after all baseline files in scope are
available:

- `docs/export/fixtures/official_configurator_manual_import_export_test_plan.json`
- `docs/export/official_configurator_manual_import_export_result_TEMPLATE.md`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json`
- `docs/export/fixtures/generated_official_configurator_candidate_preview.json`

If any baseline file is missing, add a precondition note in the operator
packet and do not proceed with capture artifact creation.

## Non-Claims for This Layout

- no capture completed here
- no result packet produced here
- no production export
- no official configurator compatibility claim
- no device-write behavior
- no WebSerial
- no runtime-loaded config
- no firmware flashing automation
- no hardware behavior validation
- no nunchuk validation
