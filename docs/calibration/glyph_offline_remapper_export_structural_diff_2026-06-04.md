# Glyph Offline Remapper Export Structural Diff - 2026-06-04

## Purpose and scope

This records a docs/tools-only structural diff between the committed active Glyph profile artifact and the committed offline remapper exported `GlyphUserProfiles.json` fixture.

This is structural diff only. It is not official configurator compatibility, not adapter implementation, not hardware validation, not firmware behavior validation, and not device write behavior.

## Source artifacts

Input artifact:

- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
- SHA-256: `0a9c70f6a0c1bb8c347a811df2ec327c176482dc9c35f433c45bd3454e704707`

Exported artifact:

- `docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json`
- SHA-256: `0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b`

The analyzer/checker pair for this packet is:

- `tools/analyze_glyph_offline_remapper_export_diff.py`
- `tools/check_glyph_offline_remapper_export_structural_diff.py`

## Deterministic summary

Top-level keys:

- Added keys in exported artifact: none
- Removed keys from input artifact: none
- Common keys: `communicationBackendConfigs`, `defaultBackendConfig`, `defaultDashboardOption`, `defaultUsbBackendConfig`, `gameModeConfigs`, `keyboardModes`, `rgbBrightness`, `rgbConfigs`

Collection counts:

- `gameModeConfigs`: input `13`, exported `13`
- `communicationBackendConfigs`: input `8`, exported `8`
- `keyboardModes`: input `1`, exported `1`
- `rgbConfigs`: input `13`, exported `13`

`MODE_ULTIMATE` summary:

- Present in input artifact: yes
- Present in exported artifact: yes
- Input index/name/backend: index `2`, name `Ultimate`, `communicationBackendId=null`
- Exported index/name/backend: index `2`, name `Ultimate`, `communicationBackendId=null`

Equality checks:

- Byte-hash equality: false
- Parsed JSON exact equality: false

## Interpretation boundary

The committed exported JSON preserves the same top-level key set and the same summary counts for `gameModeConfigs`, `communicationBackendConfigs`, `keyboardModes`, and `rgbConfigs`, and both artifacts contain a `MODE_ULTIMATE` entry at index `2` named `Ultimate`.

The committed exported JSON is not byte-identical to the input artifact, and the parsed JSON objects are not exactly equal. This packet does not classify accepted versus rejected field-level behavior, does not validate firmware behavior, and does not authorize adapter generation or artifact transformation.

## Non-goals and caveats

- structural diff only
- not official configurator compatibility
- not adapter implementation
- not hardware validation
- not firmware behavior validation
- not device write behavior
