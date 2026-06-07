# Glyph Official Configurator Corpus Diff - 2026-06-06

## Purpose and scope

This packet records deterministic structural JSON differences between the two
user-provided official Glyph configurator export fixtures in
`docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/`.

This is structural JSON evidence, not gameplay semantics. It does not claim
runtime behavior, does not approve device write, and does not approve adapter
implementation.

This does not approve adapter implementation.

## Fixture hashes

- `default_profiles`:
  `2d24324928f9c0292e3fce74f02083a740272eeb7a271437be10b7b4f6bf025e`
- `back_and_forth_custom_profile`:
  `0a782564bd454c50e3fbeccc754acaec6c6ffdc6e0dcff145eef9121b7a3b39b`

## Top-level shape

- Stable top-level key set: true
- Changed top-level keys: `gameModeConfigs`, `rgbConfigs`
- Unchanged top-level keys: `communicationBackendConfigs`, `keyboardModes`,
  `defaultBackendConfig`, `defaultUsbBackendConfig`, `rgbBrightness`,
  `defaultDashboardOption`

## Game mode structural differences

- `Brawl` / `MODE_PROJECT_M`: `socdPairs` changed structurally; count changed
  from 4 to 5.
- `Ultimate` / `MODE_ULTIMATE`: `socdPairs` and `buttonRemapping` changed
  structurally; `socdPairs` count changed from 4 to 6 and `buttonRemapping`
  count changed from 19 to 17.
- `Keyboard` / `MODE_KEYBOARD`: `socdPairs` changed structurally while the
  count stayed 2.

## Ultimate structural observations

- `socdPairs`: default 4, back-and-forth 6.
- `buttonRemapping`: default 19, back-and-forth 17.
- `BTN_LF6` entries changed structurally.
- `BTN_LF8` entries changed structurally.
- A `BTN_LF8` / `BTN_LF6` SOCD pair is present in the back-and-forth fixture
  and not present in the default fixture.
- A `BTN_RF7` / `BTN_RF8` SOCD pair is present in the back-and-forth fixture
  and not present in the default fixture.

## Brawl structural observations

- An extra `BTN_RF7` / `BTN_RF8` pair exists in the back-and-forth fixture when
  compared structurally with the default fixture.

## Keyboard structural observations

- The `MODE_KEYBOARD` game-mode `socdPairs` ordering changed structurally.

## RGB structural observations

- `rgbConfigs` count is 13 in both fixtures.
- RGB config index `2` changed structurally.
- Back-and-forth RGB button-color counts differ at index `2`, changing from 20
  to 28.
- Partial button-color entries are detected structurally in the back-and-forth
  fixture.

## Explicit non-claims

- This is structural JSON evidence, not gameplay semantics.
- This does not claim runtime behavior.
- No device write or adapter implementation is approved.
- No WebSerial/device write, runtime-loaded config, protobuf binary write,
  firmware flashing automation, firmware behavior change, active profile
  artifact change, or nunchuk validation is claimed.
