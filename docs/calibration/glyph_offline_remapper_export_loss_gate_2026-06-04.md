# Glyph Offline Remapper Export Loss Gate - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only aggregate gate over the committed offline remapper manual experiment result, binding-loss classification, SOCD drift classification, metadata diff report, and export-diff gate.

Gate decision status is `external_remapper_round_trip_not_safe_adapter_blocked`.

This packet is not official compatibility and not hardware validation.

## Source artifacts

Aggregate fixture:

- `docs/calibration/fixtures/glyph_offline_remapper_export_loss_gate_2026-06-04.json`

Checker:

- `tools/check_glyph_offline_remapper_export_loss_gate.py`

Required aggregate inputs:

- `docs/calibration/fixtures/glyph_offline_remapper_experiment_result_2026-06-04.json`
- `docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json`
- `docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json`
- `docs/calibration/fixtures/glyph_offline_remapper_metadata_diff_report_2026-06-04.json`
- `docs/calibration/fixtures/glyph_offline_remapper_export_diff_gate_2026-06-04.json`

## Gate decision

- `active_profile_round_trip_safe = false`
- `adapter_implementation_allowed = false`
- `external_json_generation_allowed = false`
- `manual_import_experiment_completed = true`
- `manual_export_round_trip_has_blocking_loss = true`
- `runtime_owned_behavior_represented = false`

## Aggregate interpretation

- Manual no-device import/export experiment completed.
- Binding-loss classification is adapter-blocking.
- SOCD drift classification is adapter-blocking.
- Metadata diff report remains metadata-only evidence.
- Export diff gate keeps runtime-owned behavior unrepresented.
- Active profile round-trip is not safe.
- Adapter implementation remains blocked.
- External JSON generation remains blocked.

## Aggregate inputs

Binding-loss classification:

- `loss_severity = adapter_blocking_loss`
- `round_trip_safe_for_active_profile = false`
- Input `buttonRemapping` count remains `42`.
- Exported `buttonRemapping` count remains `17`.
- Input entries with `activates` remain `42`.
- Exported entries with `activates` remain `0`.

SOCD drift classification:

- `drift_severity = adapter_blocking_drift`
- Input SOCD count remains `4`.
- Exported SOCD count remains `6`.
- Added exported pairs remain `BTN_LF2/BTN_RF4`, `BTN_LF8/BTN_LF6`, and `BTN_RF7/BTN_RF8`.
- Missing from exported remains `BTN_LF5/BTN_LF2`.

Metadata diff report:

- Metadata diff remains metadata-only evidence.
- Firmware behavior remains unvalidated by this packet.

Export-diff gate:

- Import/export succeeded with warnings.
- Runtime-owned behavior remains not represented.
- Adapter remains blocked.

## Allowed next work

- docs/tools-only adapter candidate schema planning with explicit non-round-trip caveat
- manual repeat experiment with browser/version recorded
- source audit of external remapper import/export code
- clean-room transform design, not implementation

## Disallowed without approval

- adapter implementation
- external-remapper-compatible JSON generation
- device write/WebSerial
- protobuf binary generation
- runtime-loaded config
- official compatibility claim
- hardware validation claim

## Non-goals and caveats

- no adapter implementation
- no external-remapper-compatible JSON generation
- no device write/WebSerial
- no protobuf binary generation
- no runtime-loaded config
- no official compatibility claim
- no hardware validation claim
- no firmware runtime behavior change
- no table value change
- no existing profile artifact change
- no exported experiment fixture change
