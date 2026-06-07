# Glyph Offline Remapper Ultimate Diff Report - 2026-06-04

## CORRECTION / SOURCE MISATTRIBUTION

User clarification on 2026-06-06 supersedes external-remapper attribution for
the `GlyphUserProfilesDefault.json` and `GlyphUserProfilesBackAndForth.json`
files. They are official Glyph configurator app artifacts, not user-executed
external remapper artifacts. This historical packet is quarantined as
non-authoritative pending independent source support and must not be used as
primary corpus evidence.

## Purpose and scope

This records a docs/tools-only `MODE_ULTIMATE` profile-level diff between the committed active Glyph profile artifact and the committed offline remapper exported `GlyphUserProfiles.json` fixture.

This is profile-level representation only. Runtime-owned behavior not represented. It is not gameplay correctness, not official compatibility, and not hardware validation.

## Source artifacts

Input artifact:

- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- SHA-256: `0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707`

Exported artifact:

- `docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json`
- SHA-256: `0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b`

Checker:

- `tools/check_glyph_offline_remapper_ultimate_diff_report.py`

## MODE_ULTIMATE profile-level diff

Profile presence and retained structure:

- `MODE_ULTIMATE` is present in both artifacts.
- Profile name is `Ultimate` in both artifacts.
- Extra/missing profile fields: none.
- `rgbConfig`, `layoutPlate`, `applicableBackends`, and `menuButtonIcon` are exact matches.
- Exported profile retains profile-level structure.

`socdPairs`:

- Input count: `4`
- Exported count: `6`
- Exact value equality: `false`
- Missing from exported: `BTN_LF5/BTN_LF2/SOCD_2IP`
- Added in exported: `BTN_LF2/BTN_RF4/SOCD_2IP`, `BTN_LF8/BTN_LF6`, `BTN_RF7/BTN_RF8`

`buttonRemapping`:

- Input count: `42`
- Exported count: `17`
- Exact value equality: `false`
- Disabled entries: input `0`, exported `0`
- Entries with `activates`: input `42`, exported `0`
- Exported entries omit `activates`, so the exported `buttonRemapping` entries are not exact value matches for the input profile-level mappings.

## Interpretation boundary

The exported profile keeps the same top-level `MODE_ULTIMATE` profile shape and several matching profile-level fields, but it does not preserve the committed `socdPairs` values or the committed `buttonRemapping` value set.

Runtime-owned behavior not represented: the exported JSON does not carry the firmware-owned runtime behavior that sits beyond this profile-level JSON view. Even where the profile-level JSON looks similar, that does not mean the exported artifact represents firmware-owned runtime behavior.

This report is not gameplay correctness, not official compatibility, and not hardware validation. It does not validate firmware behavior, does not authorize adapter generation or artifact transformation, and does not promote external-remapper behavior to source authority.
