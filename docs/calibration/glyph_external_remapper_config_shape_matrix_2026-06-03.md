# Glyph External Remapper Config Shape Matrix - 2026-06-03

## Purpose and scope

This document records a docs/tools-only, non-authoritative comparison between
external Open Glyph Remapper config-shape observations and the import/export
artifacts already committed in this repository.

It is a non-authoritative comparison only. It is not firmware source authority,
not official configurator compatibility, not device write behavior, not
runtime-loaded config, and not hardware validation.

No external source was copied into this repo. No external dependency was added.
This branch does not implement runtime-loaded config, WebSerial, serial/device
write behavior, protobuf/config/schema behavior changes, generated firmware
source, or hardware validation.

## External observation source

This matrix uses the Branch 1 snapshot index as the external observation source:

- `docs/calibration/glyph_external_remapper_source_snapshot_index_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_source_snapshot_index_2026-06-03.json`

The snapshot remains a non-authoritative comparison input. It is not firmware
source authority, not official configurator compatibility, not device write
behavior, not runtime-loaded config, and not hardware validation.

## Repo comparison inputs

The internal comparison side is limited to already committed docs/tools
artifacts, especially:

- `docs/calibration/glyph_configurator_compatibility_source_registry_2026-06-03.md`
- `docs/calibration/fixtures/glyph_configurator_compatibility_source_registry_2026-06-03.json`
- `docs/calibration/glyph_config_json_compatibility_fixtures_2026-06-03.md`
- `docs/calibration/fixtures/glyph_config_json_compatibility_cases_2026-06-03.json`
- `docs/calibration/glyph_import_export_compatibility_validator_2026-06-03.md`
- `docs/calibration/fixtures/glyph_import_export_compatibility_expectations_2026-06-03.json`
- `docs/calibration/glyph_external_remapper_adapter_boundary_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_adapter_boundary_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`

## Compatibility status meanings

- `compatible_observed`: the external observation and committed repo artifacts
  both expose the compared shape concept at a bounded docs/tools level.
- `compatible_internal_only`: the repo shows an internal shape/invariant, but
  the external snapshot did not audit enough detail to compare it directly.
- `partial_gap`: there is some overlap, but the external observation and repo
  artifacts do not yet prove equivalent config shape.
- `unknown_needs_source_audit`: the external snapshot or repo fixture coverage
  is too shallow to classify the shape confidently.
- `out_of_scope`: the compared path is deliberately not implemented or not
  accepted as source authority in this repo.

## Comparison matrix

| Category | Status | Notes |
| --- | --- | --- |
| profile list / profile configs | `partial_gap` | External UI observations show a profile list with create/rename/duplicate actions, while the committed repo side centers on a single active profile artifact plus mode/backend lists rather than a multi-profile configurator payload. |
| game/mode config | `compatible_observed` | External README/UI observations indicate game or mode configuration concepts, and the committed active profile artifact exposes `gameModeConfigs` with per-mode remap, SOCD, RGB, backend, and keyboard references. |
| button remapping entries | `compatible_observed` | External README docs describe per-button remap behavior, and the committed profile/config JSON artifacts preserve list-shaped `buttonRemapping` entries guarded by the compatibility checker. |
| explicit disable entries | `unknown_needs_source_audit` | The current repo checker guards physical-button-only disable-entry shape when present, but the active artifact does not include a committed disable-entry example and the external snapshot did not audit disable serialization. |
| button activation/output semantics | `partial_gap` | External docs describe physical-to-physical remapping, while committed repo artifacts split semantics across `activates`, generated-config role bindings, priority references, and hard overrides without proving exact external equivalence. |
| SOCD pairs | `compatible_observed` | External observations include SOCD UI/data-model references, and the committed active profile artifact carries list-shaped `socdPairs` with existing checker coverage. |
| RGB configs | `compatible_observed` | External observations include button-lighting and palette concepts, and the committed active artifact includes `rgbConfigs`, `rgbBrightness`, and per-mode `rgbConfig` references. |
| RGB config 1-based indexing | `compatible_internal_only` | The committed repo clearly uses integer `rgbConfig` references that align with the 1-based `rgbConfigs` array positions, but the external snapshot did not audit index-base details in `glyph-config.json` or `app.js`. |
| keyboard mode configs | `compatible_observed` | External README docs describe keyboard mode capture, and the committed active artifact includes `MODE_KEYBOARD`, `keyboardModeConfig`, and top-level `keyboardModes` data. |
| keyboard scancodes | `compatible_observed` | External README docs mention HID keycodes, and the committed active artifact contains numeric `buttonsToKeycodes` mappings for the keyboard mode. |
| menu button icon/display metadata | `partial_gap` | The committed active artifact includes `menuButtonIcon` arrays and `defaultDashboardOption`, while the external snapshot only proves controller/menu UI labels rather than audited config-payload metadata fields. |
| default config payload | `partial_gap` | The external root inventory and README note a default `glyph-config.json` payload, while the committed repo side has an active profile artifact plus export/runtime candidate samples instead of a source-audited imported external default payload. |
| protobuf encode/decode path | `out_of_scope` | External README docs describe protobuf encode/decode and inline `PROTO_DEF`, but the committed repo registry explicitly defers official protobuf/schema authority and this branch does not implement or validate that path. |
| JSON import/export path | `compatible_observed` | External observations include config-file import/export, and the committed repo has JSON compatibility fixtures plus an offline import/export compatibility validator around the active artifact and sample export package. |
| WebSerial load/save path | `out_of_scope` | External README docs describe Connect/Load/Save flows, while the committed repo boundary docs explicitly keep WebSerial and serial/device write behavior non-implemented. |
| custom profile/modifier support | `partial_gap` | External README docs describe custom mode/modifier support claims, while the committed repo only has docs/tools modifier-like structures in generated-config artifacts and no source-backed custom profile config contract. |

## Follow-up themes

- Full source audit is still required before claiming exact field-for-field
  compatibility with the external remapper payload.
- Explicit disable-entry serialization, menu icon metadata wiring, RGB index
  basis, and custom profile/modifier representation remain bounded follow-up
  topics rather than accepted source truth.
- JSON import/export comparison stays offline and repo-committed only.
- WebSerial/device write behavior remains out of scope in this repo.

## Required fixture fields

The fixture for this report preserves these top-level fields:

- `schema_name=glyph_external_remapper_config_shape_matrix`
- `matrix_version=1`
- `status=external_non_authoritative_config_shape_matrix`
- `hardware_status=not_new_hardware_result`
- `external_source_promoted_to_authority=false`
- `device_write_implemented=false`
- `runtime_loaded_config_implemented=false`
- `official_configurator_compatibility_claimed=false`

Each category entry preserves:

- `category_id`
- `external_observation_status`
- `external_notes`
- `our_artifact_reference`
- `compatibility_status`
- `authority_status=non_authoritative_external_comparison`
- `required_follow_up`

## Checker output

`tools/check_glyph_external_remapper_config_shape_matrix.py` prints:

- `glyph_external_remapper_config_shape_matrix`
- `status=PASS` or `status=FAIL`
- `comparison_categories=<N>`
- `external_source_promoted_to_authority=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the matrix preserves the required
non-authoritative comparison boundary, keeps WebSerial/device write behavior
non-implemented, does not claim runtime-loaded config, does not claim hardware
validation, and does not promote the external remapper snapshot to source
authority or official configurator compatibility.
