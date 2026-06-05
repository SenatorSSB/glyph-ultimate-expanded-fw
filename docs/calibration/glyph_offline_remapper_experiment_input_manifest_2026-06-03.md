# Glyph Offline Remapper Experiment Input Manifest - 2026-06-03

## Purpose and scope

This document records the exact committed repo inputs approved for a future
offline remapper no-device import experiment. This is input manifest only. The
experiment not executed. Adapter not implemented. This is no device write, no
WebSerial write, and not hardware validation.

The manifest status is:

- `input_manifest_only_experiment_not_executed`

This manifest does not execute the experiment, generate an adapter output,
transform artifacts into an external-remapper-compatible JSON candidate, or
promote an external source to authority.

## Input selection rules

The input set is limited to committed repo fixtures/artifacts that already
exist in this repository and can be checksummed without changing runtime
source, profile artifacts, transport code, or schema implementation.

The manifest includes exactly one primary import candidate plus four bounded
reference-only inputs:

- primary import candidate for external remapper no-device import test
- secondary repo fixture reference
- reference-only package, not expected external remapper import unless future
  adapter exists
- reference-only runtime candidate, not expected external remapper import
  unless future adapter exists
- reference-only generated config source

## Manifested inputs

| Label | Path | SHA-256 | Expected import role | Use in experiment | Authority class | Caveats |
| --- | --- | --- | --- | --- | --- | --- |
| `active_profile_artifact` | `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json` | `0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707` | `import_candidate` | `primary import candidate for external remapper no-device import test` | `repo_fixture_evidence` | Current committed active profile artifact only; no device write, no WebSerial write, not hardware validation, and not official compatibility. |
| `tilt_button_probe_fixture` | `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json` | `0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707` | `possible_import_candidate_if_compatible` | `secondary repo fixture reference` | `repo_fixture_evidence` | Secondary reference only; same current hash as the active profile artifact in this repo snapshot does not imply separate authority or proven compatibility. |
| `senscope_export_package_sample` | `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json` | `29bd4e601b8762d068b7fb809707b57537859ba647cb48e578900d9c9111d4b7` | `reference_only` | `reference-only package, not expected external remapper import unless future adapter exists` | `repo_fixture_evidence` | Reference-only package; do not treat as direct import candidate, runtime-loaded config, device write payload, or official compatibility evidence. |
| `runtime_config_candidate_sample` | `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json` | `e4e9b0e47b36f9f8585b37ac0e9f3cba2b6ae2833d79121e99af602c9d48543f` | `reference_only` | `reference-only runtime candidate, not expected external remapper import unless future adapter exists` | `repo_fixture_evidence` | Reference-only runtime candidate; not firmware input, not runtime-loaded config implementation, no device write, and not hardware validation. |
| `generated_config_prototype` | `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json` | `a482b38864a7a927efd5a32b351acff14bc6daea60e6164678a2cab4bc337b0d` | `reference_only` | `reference-only generated config source` | `repo_fixture_evidence` | Reference-only generated config source; docs/tools-only artifact, not external remapper import candidate, not runtime-loaded config, and not hardware validation. |

## Constraints and non-goals

This manifest is input manifest only. The experiment not executed. Adapter not
implemented. No device write. No WebSerial write. Not hardware validation.

The manifest does not:

- approve running the no-device experiment
- approve Save to Device or serial/device write behavior
- approve WebSerial write behavior
- approve adapter generation
- approve artifact transformation into an external-remapper-compatible JSON
  candidate
- claim official compatibility
- promote external observations to source authority

## Source inputs

This manifest is bounded to already committed docs/tools/fixtures:

- `docs/calibration/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_external_remapper_compatibility_experiment_plan_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_manual_experiment_packet_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_manual_experiment_packet_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_target_contract_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_target_contract_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_mapping_plan_2026-06-03.json`
- `docs/calibration/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.md`
- `docs/calibration/fixtures/glyph_offline_remapper_adapter_gap_matrix_2026-06-03.json`
- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`
- `docs/calibration/fixtures/glyph_senscope_export_package_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_runtime_config_candidate_SAMPLE_2026-06-03.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`

## Required fixture fields

The fixture for this manifest must preserve these top-level fields:

- `schema_name=glyph_offline_remapper_experiment_input_manifest`
- `manifest_version=1`
- `status=input_manifest_only_experiment_not_executed`
- `hardware_status=not_new_hardware_result`
- `experiment_executed=false`
- `adapter_implemented=false`
- `external_source_promoted_to_authority=false`
- `device_write_allowed=false`
- `webserial_write_allowed=false`

## Checker output

`tools/check_glyph_offline_remapper_experiment_input_manifest.py` prints:

- `glyph_offline_remapper_experiment_input_manifest`
- `status=PASS` or `status=FAIL`
- `inputs=5`
- `experiment_executed=false`
- `adapter_implemented=false`
- `hardware_status=not_new_hardware_result`

Passing this checker confirms only that the manifest remains input manifest
only, experiment not executed, adapter not implemented, no device write, no
WebSerial write, and not hardware validation.
