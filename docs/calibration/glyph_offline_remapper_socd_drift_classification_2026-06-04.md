# Glyph Offline Remapper SOCD Drift Classification - 2026-06-04

## CORRECTION / SOURCE MISATTRIBUTION

User clarification on 2026-06-06 supersedes external-remapper attribution for
the `GlyphUserProfilesDefault.json` and `GlyphUserProfilesBackAndForth.json`
files. They are official Glyph configurator app artifacts, not user-executed
external remapper artifacts. This historical packet is quarantined as
non-authoritative pending independent source support and must not be used as
primary corpus evidence.

## Purpose and scope

This records a docs/tools-only SOCD drift classification derived from the committed offline remapper `MODE_ULTIMATE` diff report.

Drift severity is `adapter_blocking_drift`.

This packet is not official compatibility, not hardware validation, and not evidence of gameplay/runtime correctness.

## Source artifact

Source report fixture:

- `docs/calibration/fixtures/glyph_offline_remapper_ultimate_diff_report_2026-06-04.json`

Checker:

- `tools/check_glyph_offline_remapper_socd_drift_classification.py`

Fixture:

- `docs/calibration/fixtures/glyph_offline_remapper_socd_drift_classification_2026-06-04.json`

## SOCD drift summary

- Input SOCD count = 4
- Exported SOCD count = 6
- Added exported pairs include `BTN_LF2/BTN_RF4`, `BTN_LF8/BTN_LF6`, and `BTN_RF7/BTN_RF8`
- Missing from exported includes `BTN_LF5/BTN_LF2`
- The exported profile-level `socdPairs` list is not an exact value match

## Interpretation boundary

External remapper export changes profile-level SOCD structure.

No gameplay/runtime correctness can be inferred.

No official compatibility claim.

## Required false flags

- `adapter_implemented`: false
- `official_compatibility_claimed`: false
- `hardware_validation_claimed`: false
- `external_source_promoted_to_authority`: false

## Non-goals and caveats

- not official compatibility
- not hardware validation
- not evidence of gameplay/runtime correctness
- no adapter implementation
- no external source promotion to authority
- no external-remapper-compatible JSON generation
