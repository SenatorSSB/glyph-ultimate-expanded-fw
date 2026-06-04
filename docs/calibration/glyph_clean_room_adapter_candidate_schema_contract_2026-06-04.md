# Glyph Clean-Room Adapter Candidate Schema Contract - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only schema contract for a target: future clean-room adapter candidate schema.

Contract status is `schema_contract_only_adapter_not_implemented`.

Target output is not generated.

Target output is not round-trip safe by default.

Active profile round-trip is currently unsafe.

External remapper export is not canonical.

Adapter implementation remains blocked.

External JSON generation remains blocked.

Official compatibility remains unclaimed.

This packet is not official compatibility and not hardware validation.

## Source artifacts

Contract fixture:

- `docs/calibration/fixtures/glyph_clean_room_adapter_candidate_schema_contract_2026-06-04.json`

Checker:

- `tools/check_glyph_clean_room_adapter_candidate_schema_contract.py`

Required source artifacts:

- Active profile artifact: `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- Exported experiment artifact: `docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json`
- Binding-loss classification: `docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json`
- SOCD drift classification: `docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json`
- Export-loss gate: `docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json`

## Schema sections

The contract fixture defines these top-level sections:

- `schema_name`
- `schema_version`
- `status`
- `source_artifacts`
- `target_profile_metadata`
- `profile_level_bindings`
- `runtime_owned_behavior_sidecar`
- `socd_policy_sidecar`
- `loss_warnings`
- `non_round_trip_caveats`
- `source_authority`
- `forbidden_capabilities`
- `validation_report`

## Target profile metadata

- `target = future clean-room adapter candidate schema`
- `target_output_generated = false`
- `target_output_round_trip_safe_by_default = false`
- `active_profile_round_trip_currently_safe = false`
- `external_remapper_export_canonical = false`
- `adapter_implemented = false`
- `external_json_generation_allowed = false`
- `official_compatibility_claimed = false`
- `hardware_status = not_new_hardware_result`

## Profile-level bindings

- Binding-loss classification remains `adapter_blocking_loss`.
- Active profile round-trip is currently unsafe.
- External remapper export is not canonical.
- Target output is not generated.
- Target output is not round-trip safe by default.

## Runtime-owned behavior sidecar

Future schema planning may describe a runtime-owned behavior sidecar, but this packet creates only a schema contract.

- Runtime-owned behavior is not represented by external profile JSON.
- Runtime-owned behavior sidecar content is sidecar-only in this contract.
- Target output is not generated.
- Adapter implementation remains blocked.

## SOCD policy sidecar

- SOCD drift classification remains `adapter_blocking_drift`.
- SOCD policy sidecar content is schema-contract-only in this packet.
- Target output is not generated.
- No gameplay/runtime correctness is inferred.

## Loss warnings

- Active profile round-trip is currently unsafe.
- External remapper export is not canonical.
- Binding-loss classification is adapter-blocking.
- SOCD drift classification is adapter-blocking.
- Target output is not generated.
- Target output is not round-trip safe by default.

## Non-round-trip caveats

- Active profile round-trip is currently unsafe.
- Target output is not generated.
- Target output is not round-trip safe by default.
- External remapper export is not canonical.
- Adapter implementation remains blocked.
- External JSON generation remains blocked.
- Official compatibility remains unclaimed.

## Source authority

- Repo docs, fixtures, and checker outputs are the only contract inputs for this packet.
- External remapper export is not canonical.
- No external source authority promotion.
- no external code reuse
- no external dependency

## Forbidden capabilities

- `adapter_implemented = false`
- `adapter_implementation_blocked = true`
- `external_json_generation_allowed = false`
- `external_json_generation_blocked = true`
- `external_remapper_compatible_json_generated = false`
- `official_compatibility_claimed = false`
- `hardware_validation_claimed = false`
- `external_code_copied = false`
- `external_dependency_added = false`
- `device_write_implemented = false`
- `serial_device_write_behavior_implemented = false`
- `webserial_transport_implemented = false`
- `protobuf_binary_generation_implemented = false`
- `runtime_loaded_config_implemented = false`

## Non-goals and caveats

- no adapter implementation
- no external-remapper-compatible JSON generation
- no output path to generated external JSON
- no external code reuse
- no external dependency
- no device write/WebSerial/protobuf/runtime-loaded config
- no device write
- no WebSerial transport
- no protobuf binary generation
- no runtime-loaded config
- no serial/device write behavior
- no firmware runtime behavior change
- no active profile artifact change
- no exported experiment artifact change
- not official compatibility
- not hardware validation
