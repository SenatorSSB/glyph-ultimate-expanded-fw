# Glyph Runtime Config Validation Report - 2026-06-03

## Purpose and scope

This document records an offline docs/tools report only for the current Glyph
runtime config candidate validator package.

It is not runtime-loaded config, not serial/device write behavior, not hardware
validation, and not nunchuk hardware validation.

## Report status

The committed report fixture records:

- `schema_name=glyph_runtime_config_validation_report`
- `report_version=1`
- `status=docs_tools_validation_report`
- `hardware_status=not_new_hardware_result`
- `nunchuk_status=preserved_but_not_hardware_validated`

The current sample candidate validation status is `PASS`.

## Source authority

The report is regenerated from these committed source-backed docs/tools inputs:

- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_validator_contract_v0_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_invalid_corpus_2026-06-03.json`
- `docs/calibration/fixtures/glyph_offline_generated_config_validator_contract_v0_2026-06-03.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`
- `docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json`

No firmware runtime source is edited or reinterpreted by this report.

## Summary

- Sample candidate schema: `glyph_runtime_config_candidate`
- Sample candidate validation status: `PASS`
- Invalid corpus case count: `26`
- Table count: `25`
- Generated-config validator context status: `tooling_validator_only_not_runtime_loaded`
- Generated-config contract status: `docs_tools_contract_not_runtime_loaded`
- Runtime-loaded validation contract status: `validation_contract_design_only_not_implemented`

## Required non-goals

The report carries forward these required non-goals from the committed runtime
config candidate validator package:

- `does_not_change_table_values_or_behavior`
- `not_firmware_source`
- `not_hardware_validation`
- `not_nunchuk_hardware_validation`
- `not_runtime_loaded`
- `not_senscope_game_semantics`
- `not_serial_device_write`

## Rejected capability summary

The committed report fixture summarizes rejected capability classes from the
candidate validator contract, generated-config validator contract, generated
config contract, and runtime-loaded validation contract.

Rejected content categories include:

- firmware source patches or firmware-source interpretation claims
- serial transport payloads or device write instructions
- runtime-loaded config implementation claims
- macros, turbo behavior, or timing/history-dependent behavior
- phase-order mutation or arbitrary script/code text
- hardware validation claims without a hardware result source
- nunchuk hardware validation claims without a hardware result source

## Caveats

- Offline docs/tools report only.
- Not runtime-loaded config.
- Not serial/device write behavior.
- Not hardware validation.
- Not nunchuk hardware validation.
- Does not change table values or behavior.

## Checker ownership

`tools/generate_glyph_runtime_config_validation_report.py` regenerates the
deterministic text summary or JSON fixture.

`tools/check_glyph_runtime_config_validation_report.py` checks that the committed
fixture exactly matches regenerated output and that this Markdown report keeps
the required caveat phrases.
