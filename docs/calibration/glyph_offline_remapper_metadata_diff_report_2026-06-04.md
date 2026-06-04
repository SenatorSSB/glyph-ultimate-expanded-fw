# Glyph Offline Remapper Metadata Diff Report - 2026-06-04

## Purpose and scope

This records a docs/tools-only metadata diff between the committed active Glyph profile artifact and the committed offline remapper exported `GlyphUserProfiles.json` fixture.

This is metadata diff only. It is not gameplay/runtime validation, not firmware behavior correctness, not official configurator compatibility, and not hardware validation.

## Source artifacts

Input artifact:

- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- SHA-256: `0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707`

Exported artifact:

- `docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json`
- SHA-256: `0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b`

The checker for this packet is:

- `tools/check_glyph_offline_remapper_metadata_diff_report.py`

## Comparison summary

Top-level metadata and comparison scope:

- `rgbConfigs` count and hash/equality: input `13`, exported `13`, exact equality `true`
- `rgbConfigs` empty object entries: none in either artifact
- `buttonColors` entries missing `color`: the same 10 entries are present in both artifacts
- `menuButtonIcon` differences by game mode: none
- `communicationBackendConfigs` differences: none
- `defaultBackendConfig` / `defaultUsbBackendConfig`: exact equality
- `rgbBrightness`: exact equality
- `defaultDashboardOption`: exact equality
- `keyboardModes`: exact equality

Game-mode metadata changes by the exported app:

- `MODE_PROJECT_M` / `Brawl`: `socdPairs` gains `BTN_RF7` / `BTN_RF8`
- `MODE_ULTIMATE` / `Ultimate`: `socdPairs` and `buttonRemapping` change
- `MODE_KEYBOARD` / `Keyboard`: `socdPairs` order changes

Preserved exactly:

- `communicationBackendConfigs`
- `defaultBackendConfig`
- `defaultUsbBackendConfig`
- `defaultDashboardOption`
- `keyboardModes`
- `rgbBrightness`
- `rgbConfigs`
- `gameModeConfigs[*].modeId`
- `gameModeConfigs[*].name`
- `gameModeConfigs[*].layoutPlate`
- `gameModeConfigs[*].applicableBackends`
- `gameModeConfigs[*].menuButtonIcon`
- `gameModeConfigs[*].rgbConfig`

Changed by the exported app:

- `gameModeConfigs[1].socdPairs`
- `gameModeConfigs[2].socdPairs`
- `gameModeConfigs[2].buttonRemapping`
- `gameModeConfigs[12].socdPairs`

## Interpretation boundary

The committed exported JSON preserves the same top-level metadata fields and the same summary counts for `rgbConfigs`, `keyboardModes`, and `communicationBackendConfigs`, and both artifacts contain the same menu/backend defaults and `rgbBrightness`.

The committed exported JSON is not a runtime validation result, does not prove firmware behavior correctness, and does not establish official configurator compatibility. This packet stays in metadata-only scope and does not authorize adapter generation or artifact transformation.

## Non-goals and caveats

- metadata diff only
- not gameplay/runtime validation
- not firmware behavior correctness
- not official configurator compatibility
- not hardware validation
