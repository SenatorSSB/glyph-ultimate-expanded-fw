# Glyph Import Export Compatibility Validator - 2026-06-03

## Purpose and scope

This document records an offline import/export compatibility boundary only for
the current committed Glyph export-package sample, runtime-candidate sample,
active profile artifact, and compatibility fixtures already checked into this
repository.

It is not official configurator source authority, not WebSerial implementation,
not device write behavior, not runtime-loaded config, and not hardware
validation.

The validator is limited to committed docs/tools boundaries. It does not claim
official configurator import/export behavior beyond repo-committed fixtures.

## Compatibility boundary

`tools/check_glyph_import_export_compatibility.py` confirms all of the
following stay aligned:

- configurator compatibility source registry passes
- config JSON compatibility fixtures pass
- generated export artifact round-trip passes
- candidate export package validates against the committed docs/tools-only
  export boundary
- runtime candidate sample validates
- active profile artifact JSON compatibility cases remain present in the
  committed compatibility fixture scope
- serial dry-run still accepts the active profile artifact
- no device-write claim appears in the candidate export package
- no device-write claim appears in the compatibility expectations
- no official configurator compatibility claim is made beyond repo-committed
  fixtures
- no runtime-loaded config claim is made
- no hardware validation or nunchuk validation claim is made

The checker defaults to the committed sample export package and active profile
artifact, while still allowing a different candidate export package path to be
validated against the same offline boundary.

## Required fixture fields

The expectations fixture for this document must preserve these top-level fields:

- `schema_name=glyph_import_export_compatibility_expectations`
- `expectation_version=1`
- `status=offline_import_export_compatibility_expectations`
- `hardware_status=not_new_hardware_result`
- `official_configurator_compatibility_claimed=false`
- `device_write_implemented=false`
- `runtime_loaded_config_implemented=false`

## Checker inputs

`tools/check_glyph_import_export_compatibility.py` validates:

- `docs/calibration/fixtures/glyph_import_export_compatibility_expectations_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- `docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json`
- `tools/check_glyph_configurator_compatibility_source_registry.py`
- `tools/check_glyph_config_json_compatibility_fixtures.py`
- `tools/check_glyph_export_artifact_round_trip.py`
- `tools/glyph_serial_config_tool.py`
- `tools/check_glyph_senscope_export_package_validator.py`
- `tools/glyph_runtime_config_candidate_validator.py`

Passing this checker confirms an offline import/export compatibility boundary
only. It is not official configurator source authority, not WebSerial
implementation, not device write behavior, not runtime-loaded config, and not
hardware validation.

## Checker output

`tools/check_glyph_import_export_compatibility.py` prints:

- `glyph_import_export_compatibility`
- `status=PASS` or `status=FAIL`
- `checked_components=<N>`
- `official_configurator_compatibility_claimed=false`
- `device_write_implemented=false`
- `hardware_status=not_new_hardware_result`

## Non-goals

- not official configurator source authority
- not WebSerial implementation
- not device write behavior
- not runtime-loaded config
- not hardware validation
- not nunchuk hardware validation
