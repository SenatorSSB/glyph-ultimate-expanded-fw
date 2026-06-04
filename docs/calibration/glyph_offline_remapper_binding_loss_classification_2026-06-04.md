# Glyph Offline Remapper Binding-Loss Classification - 2026-06-04

## Purpose and scope

This records a docs/tools-only binding-loss classification derived from the committed offline remapper `MODE_ULTIMATE` diff report.

Loss severity is `adapter_blocking_loss`.

This packet is not official compatibility, not hardware validation, and not evidence of firmware/runtime behavior.

## Source artifact

Source report fixture:

- `docs/calibration/fixtures/glyph_offline_remapper_ultimate_diff_report_2026-06-04.json`

Checker:

- `tools/check_glyph_offline_remapper_binding_loss_classification.py`

Fixture:

- `docs/calibration/fixtures/glyph_offline_remapper_binding_loss_classification_2026-06-04.json`

## Binding-loss summary

- Input buttonRemapping count = 42
- Exported buttonRemapping count = 17
- Input entries with activates = 42
- Exported entries with activates = 0
- All input activates entries are missing or stripped in the exported profile
- The exported profile retains profile-level structure, but the buttonRemapping values are not exact matches

## Interpretation boundary

External remapper export cannot currently preserve active profile artifact identity/activation binding semantics.

Profile-level export is not round-trip safe for our active profile artifact.

This is not evidence of firmware/runtime behavior. It does not validate gameplay correctness, firmware behavior correctness, or any hardware result.

## Required false flags

- `adapter_implemented`: false
- `round_trip_safe_for_active_profile`: false
- `external_source_promoted_to_authority`: false
- `official_compatibility_claimed`: false
- `hardware_validation_claimed`: false

## Non-goals and caveats

- not official compatibility
- not hardware validation
- not evidence of firmware/runtime behavior
- no adapter implementation
- no external source promotion to authority
- no artifact transformation or external-remapper-compatible JSON generation
