# Glyph Offline Remapper Adapter Blocker Escalation - 2026-06-04

## Purpose and scope

This records a docs/tools/fixtures-only escalation from the committed offline remapper export diff gate, binding-loss classification, and SOCD drift classification.

Adapter implementation remains blocked.

External-remapper-compatible JSON generation remains blocked.

This packet is not official compatibility and not hardware validation.

## Source artifacts

Source packets:

- `docs/calibration/fixtures/glyph_offline_remapper_export_diff_gate_2026-06-04.json`
- `docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json`
- `docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json`

Checker:

- `tools/check_glyph_offline_remapper_adapter_blocker_escalation.py`

Fixture:

- `docs/calibration/fixtures/glyph_offline_remapper_adapter_blocker_escalation_2026-06-04.json`

## Escalated blocker statement

Active profile artifact is not round-trip safe through external remapper export.

Binding-loss and SOCD drift are adapter-blocking until source audit and transformation strategy exist.

No external source authority promotion.

## Required future adapter decisions

Any future adapter must decide whether:

- target external remapper import only, not export round-trip
- use sidecar reports for runtime-owned behavior
- avoid using external remapper as a canonical editor for identity-runtime profiles

## Required flags

- `adapter_implementation_blocked`: true
- `external_json_generation_blocked`: true
- `round_trip_safe_for_active_profile`: false
- `adapter_implemented`: false
- `external_remapper_compatible_json_generated`: false
- `external_source_promoted_to_authority`: false
- `official_compatibility_claimed`: false
- `hardware_validation_claimed`: false
- `hardware_status`: `not_new_hardware_result`

## Non-goals and caveats

- no adapter implementation
- no external-remapper-compatible JSON generation
- no external source authority promotion
- no active profile artifact change
- no exported experiment fixture change
- no firmware runtime behavior change
- no table value change
- no WebSerial, serial, device write, protobuf binary generation, runtime-loaded config, or push-to-device behavior
- not official compatibility
- not hardware validation
