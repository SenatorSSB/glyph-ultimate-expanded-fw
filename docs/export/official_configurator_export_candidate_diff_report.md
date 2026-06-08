# Official Configurator Export Candidate Diff Report

Status: `OFFLINE_DIFF_SIMULATION_ONLY`

This report is an offline structural comparison between the official
default fixture, the official back-and-forth fixture, and the generated
offline candidate preview. No manual official configurator app
interaction occurred.

## Inputs

- official default fixture: `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__default-profiles__20260606.json`
- official back-and-forth fixture: `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/fixtures/glyph_export__official-glyph-configurator__glyph-mk6__back-and-forth-custom-profile__20260606.json`
- generated candidate preview: `docs/export/fixtures/generated_official_configurator_candidate_preview.json`

## Classification

- stable top-level keys: 8
- stable counts: `{"communicationBackendConfigs": 8, "gameModeConfigs": 13, "keyboardModes": 1, "rgbConfigs": 13}`
- changed gameModeConfigs entries: 3
- changed rgbConfigs entries: `[2]`
- changed scalar defaults: `[]`
- fields unknown: exact app/version/route and import acceptance remain unknown
- fields unsupported: unobserved fields, transport behavior, runtime behavior, and gameplay semantics
- fields unsafe to model: official import/export success, device write, runtime-loaded config, flashing, gameplay semantics

## Non-Claims

- no compatibility claim
- no production export
- no device write
- no WebSerial
- no runtime-loaded config
- no firmware flashing automation
- no nunchuk validation
