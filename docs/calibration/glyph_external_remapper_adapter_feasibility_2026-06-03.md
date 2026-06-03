# Glyph External Remapper Adapter Feasibility - 2026-06-03

## Purpose and scope

This document records a future adapter only feasibility report for a possible
offline JSON adapter that could target an external-remapper-compatible JSON
candidate after source audit.

The feasibility status is:

- `feasible_for_future_offline_json_adapter_after_source_audit`

This is a feasibility report, not an adapter implementation. The adapter is not
implemented, this is not device write behavior, not runtime-loaded config, not hardware validation, and external source not authority.

No external source was copied into this repo. No external dependency was added.
This branch does not implement WebSerial, serial/device write behavior,
protobuf binary generation, runtime-loaded config, custom modifier
representation, generated firmware source, protobuf/config/schema behavior, or
hardware validation.

## Source inputs

This report is limited to already committed docs/tools/fixtures:

- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_config_shape_matrix_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_config_shape_matrix_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_adapter_boundary_2026-06-03.json`
- `docs/calibration/glyph_import_export_compatibility_validator_2026-06-03.md`
- `docs/calibration/fixtures/glyph_import_export_compatibility_expectations_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_runtime_config_validation_report_2026-06-03.json`

These inputs do not promote external observations to firmware authority,
official configurator authority, device-write behavior, runtime-loaded config
authority, or hardware validation.

## Feasibility conclusion

A future offline JSON adapter appears feasible as a reviewed follow-up only if
it stays bounded to committed package/candidate artifacts and waits for the
blocked decisions below.

Possible future adapter input:

- Senscope export package sample
- runtime config candidate
- generated config prototype
- validation report

Possible future adapter output:

- external-remapper-compatible JSON candidate, not device-writeable
- compatibility report

This conclusion is intentionally narrow. It does not claim official
configurator compatibility, does not claim external protobuf compatibility, and
does not claim that the generated candidate can be written to a device.

## Not feasible yet

The following are not feasible yet in this repo:

- WebSerial/device write
- protobuf binary generation
- runtime-loaded config
- custom modifier representation
- official configurator compatibility claims

## Blocked decisions

The following decisions remain blocked before integration or implementation:

- full source audit
- license review
- JSON schema comparison
- protobuf schema comparison
- custom profile/modifier representation comparison
- manual import/export experiment
- user approval before integration

## Required approvals

- user approval before integration
- user approval before external dependency or source reuse
- user approval before device transport or WebSerial work
- user approval before runtime-loaded config implementation
- user approval before protobuf/config/schema behavior changes

## Forbidden interpretations

- external source authority
- firmware source authority from external observations
- official configurator compatibility claim
- adapter implemented
- device write behavior implemented
- WebSerial implemented
- runtime-loaded config implemented
- protobuf binary generation implemented
- custom modifier representation implemented
- hardware validation claimed
- Senscope game-semantic source authority changed

## Checker output

`tools/check_glyph_external_remapper_adapter_feasibility.py` prints:

- `glyph_external_remapper_adapter_feasibility`
- `status=PASS` or `status=FAIL`
- `adapter_implemented=false`
- `external_source_promoted_to_authority=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the fixture and report preserve the
future adapter only boundary, keep the adapter not implemented, keep device
write behavior and runtime-loaded config non-implemented, do not claim hardware
validation, and keep the external source not authority.
