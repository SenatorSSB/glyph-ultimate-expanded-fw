# Glyph Clean-Room Adapter Sidecar Contract - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only sidecar/caveat contract for any future adapter candidate.

Contract status is `sidecar_contract_only_adapter_not_implemented`.

External-remapper export is not round-trip safe and cannot represent runtime-owned behavior.

Any future adapter candidate must include a sidecar/report packet before it can be reviewed.

The required packet is a contract/requirements document only.

No adapter implementation is added.

No external JSON generation is added.

No external-remapper-compatible JSON is generated.

This is not official compatibility.

This is not hardware validation.

No device write, WebSerial, protobuf binary generation, or runtime-loaded config is implemented.

## Source artifacts

Contract fixture:

- `docs/calibration/fixtures/glyph_clean_room_adapter_sidecar_contract_2026-06-04.json`

Checker:

- `tools/check_glyph_clean_room_adapter_sidecar_contract.py`

Required prior clean-room packets:

- `tools/check_glyph_clean_room_adapter_candidate_schema_contract.py`
- `tools/check_glyph_clean_room_adapter_candidate_schema_validator.py`

## Required flags

- `sidecar_required = true`
- `runtime_owned_behavior_warning_required = true`
- `non_round_trip_warning_required = true`
- `adapter_implemented = false`
- `external_json_generated = false`
- `hardware_status = not_new_hardware_result`

## Required sidecar/report sections

Any future adapter candidate must include sidecar/report sections for:

- runtime-owned behavior warning
- non-round-trip warning
- binding-loss warning
- SOCD-drift warning
- profile-level-only warning
- no official compatibility claim
- no device-write/WebSerial claim
- no hardware validation claim
- source-authority classification
- validation report

## Required warnings

- Runtime-owned behavior warning required: external-remapper profile JSON cannot represent runtime-owned behavior.
- Non-round-trip warning required: external-remapper export is not round-trip safe for the active profile artifact.
- Binding-loss warning required: binding-loss classification remains adapter-blocking.
- SOCD-drift warning required: SOCD drift classification remains adapter-blocking.
- Profile-level-only warning required: external-remapper import/export evidence is profile-level only.

## Source-authority classification

- Source-authority classification is required in any future adapter candidate.
- Repo docs, fixtures, and checker outputs are the only authority for this sidecar contract.
- External remapper export is non-authoritative.
- External source was not promoted to authority.
- No external code was copied.
- No dependency was added.

## Validation report

A future adapter candidate must include a validation report that states:

- Sidecar required warnings are present.
- Adapter implementation status remains explicit.
- External JSON generation status remains explicit.
- Hardware status remains explicit.
- Source-authority classification remains explicit.
- Official compatibility is not claimed unless source-backed and explicitly approved.
- Hardware validation is not claimed unless a separate hardware result exists.

## Non-goals and caveats

- no adapter implementation
- no external-remapper-compatible JSON generation
- no generated external JSON path
- no active profile artifact change
- no exported experiment artifact change
- no runtime firmware source change
- no source-authority promotion
- no external code reuse
- no external dependency
- no device write
- no serial/device write behavior
- no WebSerial transport
- no protobuf binary generation
- no runtime-loaded config
- not official compatibility
- not hardware validation
