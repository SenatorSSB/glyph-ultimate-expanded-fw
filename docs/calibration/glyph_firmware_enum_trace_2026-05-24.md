# Glyph Firmware Enum Trace (2026-05-24)

## 1) Confirmed from source

### Enum/schema authority discovered in dependency proto source
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `enum Button` (`BTN_LF*`, `BTN_LT*`, `BTN_RF*`, `BTN_RT*`, `BTN_MB*`, `BTN_UNSPECIFIED`)
  - Meaning: canonical button identifiers used by config serialization and remapping fields.
  - Why it matters: exporter/parser tooling must map `physicalButton` and `activates` to this symbol set.
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `enum GameModeId` (includes `MODE_ULTIMATE`)
  - Meaning: mode identity used by firmware mode selection and persisted configs.
  - Why it matters: Ultimate patch tooling must target the correct mode ID/name pair safely.
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `enum LayoutPlate` (includes `LAYOUT_PLATE_EVERYTHING`)
  - Meaning: profile layout tag used by mode configs.
  - Why it matters: calibration checks and parser trace rely on stable layout plate identity.
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `enum SocdType` (`SOCD_NEUTRAL`, `SOCD_2IP`, `SOCD_2IP_NO_REAC`, `SOCD_DIR1_PRIORITY`, `SOCD_DIR2_PRIORITY`)
  - Meaning: SOCD cleaning mode values for each configured directional pair.
  - Why it matters: parser/patch tools must preserve/modify per-pair SOCD values without guessing behavior.
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `message ButtonRemap` (`physical_button`, `activates`)
  - Meaning: serialized remap descriptor for profile-specific physical-to-logical mapping.
  - Why it matters: patch prototype edits this structure directly and preserves omissions when untouched.
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `message SocdPair` (`button_dir1`, `button_dir2`, `socd_type`)
  - Meaning: serialized SOCD pair descriptor.
  - Why it matters: patch prototype can replace/add/remove pairs only with explicit patch instructions.
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `message GameModeConfig` and `message Config`
  - Meaning: config serialization schema for game modes and global profile container.
  - Why it matters: parser and patch tooling need stable field-level structure boundaries.
- File: `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Symbol: `message AnalogModifier`, `message AnalogTriggerMapping`, `message CustomModeConfig`
  - Meaning: modifier/value schema definitions (buttons, axis, multiplier, trigger values, combination modes).
  - Why it matters: documents where modifier value storage is defined for future firmware test-scope gating.

### Confirmed usages in tracked repo source
- File: `config/glyph/common/include/glyph_overrides.hpp`
  - Symbol usage: `MODE_ULTIMATE`, `LAYOUT_PLATE_EVERYTHING`, `SocdPair`, `ButtonRemap`, `OUT_*`, `BTN_MB7`
  - Meaning: repo-tracked default/override mode definitions and remap/SOCD tables.
  - Why it matters: gives concrete firmware-side examples of how schema enums are consumed in compiled defaults.
- File: `include/core/config_utils.hpp`
  - Symbol usage: `MODE_ULTIMATE`, `SOCD_*`, backend enum switches
  - Meaning: firmware helper naming/lookup paths for mode and SOCD enums.
  - Why it matters: confirms runtime utility code paths that rely on these enum identities.
- File: `src/core/mode_selection.cpp`
  - Symbol usage: `MODE_ULTIMATE` selection handling
  - Meaning: mode-selection switch branch includes Ultimate mode.
  - Why it matters: confirms mode ID is runtime-wired in source, not only present in fixtures.

### Important caveat
- Canonical enum definitions are not currently tracked under repo-local source directories like `include/` or `config/glyph/common/`; they were found in `.pio/libdeps/...` dependency cache and `.pio/build/...` generated artifacts.

## 2) Confirmed from calibration fixtures
- Files:
  - `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json`
  - `docs/calibration/fixtures/GlyphUltFilled2.json`
- Confirmed:
  - Ultimate profile uses `modeId: MODE_ULTIMATE` and `layoutPlate: LAYOUT_PLATE_EVERYTHING`.
  - `buttonRemapping` and `socdPairs` are profile-specific arrays.
  - Omitted `activates` entries exist for `BTN_MB1`, `BTN_MB2`, `BTN_MB3`.
  - Calibration 1 and calibration 2 differ in Ultimate SOCD pairs and selected remaps.
  - Logical target names such as `BTN_MB7` appear in `activates` values.

## 3) Inferred from naming/screenshots
- `BTN_LF*`, `BTN_RF*`, `BTN_LT*`, `BTN_RT*`, `BTN_MB*` names strongly suggest left/right finger/thumb/menu groups.
- `button_positions.hpp` contains coordinate tables, but mapping those values to exact external visual pixels is inferred and out of scope without explicit layout source authority.

## 4) Still unknown
- Which tracked file/path should be treated as long-term canonical source authority for proto enum definitions (vs generated/cache copies).
- Whether all custom Ultimate modifier behavior and overflow/flipper behavior is fully documented in this repo for safe behavior-changing firmware edits.
- Exact approved hardware smoke-test procedure for first firmware test run is not yet captured in this trace document.
