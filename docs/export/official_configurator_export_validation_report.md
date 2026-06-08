# Official Configurator Export Validation Report

Status: `OFFLINE_VALIDATION_REPORT_ONLY`

## Purpose

This report records an offline validation pass over the official configurator
export target contract, preview fixture, invalid corpus, and mutation cases.

It is not production export output, not official configurator compatibility, not device write, not WebSerial, not runtime-loaded config, not firmware flashing automation, and not nunchuk validation.

## Source Authority Used

- `docs/export/official_configurator_export_source_authority.md`
- `docs/export/official_configurator_export_target_contract.md`
- `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json`
- `docs/export/fixtures/official_configurator_export_candidate_preview.json`
- `docs/export/fixtures/official_configurator_export_invalid_cases.json`
- `docs/export/fixtures/official_configurator_export_mutation_cases.json`

## Corpus Hashes Checked

- manifest:
  `08c8e43218250ad75f187f3fc5d22dd36fc27b112047f9dfdb612cbb232359a5`
- default fixture:
  `2d24324928f9c0292e3fce74f02083a740272eeb7a271437be10b7b4f6bf025e`
- back-and-forth fixture:
  `0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b`

## Checked Artifacts

- preview fixture checked: yes
- invalid corpus checked: yes
- mutation cases checked: yes
- contract checker reused: yes

## Explicit Non-Claims

- no production export
- no official compatibility claim
- no device write
- no WebSerial
- no runtime-loaded config
- no firmware flashing automation
- no nunchuk validation
- external-remapper evidence remains quarantined

## Result

The validation report is offline validation metadata only. It preserves the
source-backed official corpus hashes and keeps all unsupported, unsafe, and
manual-app-dependent claims blocked.
