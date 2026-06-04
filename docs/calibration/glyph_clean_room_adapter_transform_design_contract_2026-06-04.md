# Glyph Clean-Room Adapter Transform Design Contract - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only transform design contract for a possible future clean-room adapter candidate.

Contract status is `transform_design_contract_only`.

Transform implementation does not exist.

External JSON generation does not exist.

Active profile round-trip remains unsafe.

Sidecar is required.

Runtime-owned behavior remains outside external profile JSON.

Source data comes only from repo fixtures and accepted docs/tools evidence.

No external source code copied.

No external dependency.

No device write/WebSerial/protobuf/runtime-loaded config.

This packet is not official configurator compatibility and not hardware validation.

No active profile artifact change is authorized.

No exported experiment artifact change is authorized.

No adapter implementation, transform code, external JSON output, WebSerial transport, serial/device write behavior, protobuf binary generation, or runtime-loaded config is added.

## Source artifacts

Contract fixture:

- `docs/calibration/fixtures/glyph_clean_room_adapter_transform_design_contract_2026-06-04.json`

Checker:

- `tools/check_glyph_clean_room_adapter_transform_design_contract.py`

Required source checkers:

- `tools/check_glyph_offline_remapper_experiment_result.py`
- `tools/check_glyph_offline_remapper_binding_loss_classification.py`
- `tools/check_glyph_offline_remapper_socd_drift_classification.py`
- `tools/check_glyph_clean_room_adapter_schema_readiness_gate.py`
- `tools/check_glyph_clean_room_adapter_negative_corpus_gate.py`

## Design sections

The required design sections are:

- `input_artifacts`
- `profile_level_transform_scope`
- `runtime_owned_behavior_sidecar_scope`
- `socd_policy_sidecar_scope`
- `loss_warning_scope`
- `validation_report_scope`
- `forbidden_outputs`
- `source_authority`
- `approval_gates`

## input_artifacts

Required input artifacts:

- active profile artifact
- exported experiment artifact
- binding-loss classification
- SOCD drift classification
- clean-room schema readiness gate
- clean-room negative corpus gate

The active profile artifact and exported experiment artifact are inputs only. They must not be changed by this contract branch.

## profile_level_transform_scope

The profile-level transform scope is design-only.

- `transform_implemented = false`
- `external_json_generated = false`
- `active_profile_round_trip_safe = false`

Any future transform may only be reviewed after explicit approval and must stay profile-level unless source-backed evidence proves a broader safe scope. This contract does not implement that transform.

## runtime_owned_behavior_sidecar_scope

Runtime-owned behavior sidecar scope is required.

- `sidecar_required = true`
- `runtime_owned_behavior_external_profile_json = false`
- `runtime_owned_behavior_warning_required = true`

Runtime-owned behavior remains outside external profile JSON. A future sidecar/report must warn that external profile JSON cannot own or faithfully encode runtime-owned behavior.

## socd_policy_sidecar_scope

SOCD policy sidecar scope is required.

- `socd_policy_sidecar_required = true`
- `socd_drift_classification_required = true`
- `socd_drift_warning_required = true`

The SOCD drift classification remains an adapter-blocking input. A future candidate must carry SOCD drift warning text in sidecar/report scope.

## loss_warning_scope

Loss warning scope is required.

- `loss_warnings_required = true`
- `binding_loss_warning_required = true`
- `socd_drift_warning_required = true`

Binding-loss classification and SOCD drift classification must both be surfaced as warnings before any future adapter candidate can be reviewed.

## validation_report_scope

Validation report scope is docs/tools/fixtures-only.

The validation report must cite all required input artifacts, source-authority classifications, forbidden outputs, loss warnings, sidecar requirements, approval gates, and the no-implementation/no-generation flags.

## forbidden_outputs

Forbidden outputs:

- external JSON payload
- external JSON output path
- active profile round-trip artifact
- exported experiment artifact mutation
- runtime source change
- device write packet
- WebSerial transport
- protobuf binary
- runtime-loaded config
- official configurator compatibility claim
- hardware validation claim

## source_authority

Source authority is limited to repo fixtures and accepted docs/tools evidence.

- external source promoted to authority: false
- external code copied: false
- external dependency added: false

External app observations remain non-authoritative unless later accepted by explicit source-authority review.

## approval_gates

Explicit approval is required before:

- adapter implementation
- transform implementation
- external JSON generation
- WebSerial/device write
- protobuf binary generation
- runtime-loaded config
- official configurator compatibility claim
- hardware validation claim
- active profile artifact mutation
- exported experiment artifact mutation

## Non-goals and caveats

- no adapter implementation
- no transform implementation
- no transform code
- no external JSON generation
- no active profile artifact change
- no exported experiment artifact change
- no runtime firmware source change
- no device write/WebSerial/protobuf/runtime-loaded config
- no external source authority promotion
- no external source code copied
- no external dependency
- not official configurator compatibility
- not hardware validation
