# Glyph Config Parser and Firmware Trace Inventory (2026-05-24)

## Detected repo structure
- Firmware/app code roots:
  - `src/` (core, modes, comms, input, prototypes)
  - `include/` (core headers, mode headers, prototypes)
  - `HAL/` (platform-specific sources)
- Glyph configuration overlays:
  - `config/glyph/common/include/glyph_overrides.hpp`
  - `config/glyph/glyph_mk6/include/` and `config/glyph/glyph_protoA/include/`
- Build/config entrypoints:
  - `platformio.ini`
  - `scripts/pio-local.sh`
  - `scripts/build-glyph-mk6-quiet.sh`
  - `scripts/build-glyph-mk6-senscope-playtest-quiet.sh`
- Calibration and docs:
  - `docs/calibration/`
  - `docs/firmware/`, `docs/project/`, `docs/research/`
- Existing Python/tool scripts:
  - `tools/check_glyph_calibration_fixtures.py`
  - `tools/uf2/inspect_uf2.py`

## Build/test command findings
- Wrapper availability checks:
  - `./scripts/pio-local.sh` exists and is executable.
  - `./scripts/build-glyph-mk6-quiet.sh` exists and is executable.
- Obvious firmware build command exists:
  - `./scripts/build-glyph-mk6-quiet.sh` (quiet wrapper around `pio-local.sh run -e glyph_mk6`)
- Existing CI/workflow files detected:
  - `.github/workflows/build.yml`
  - `.github/workflows/build-device-config.yml`
- Existing repo-local validation script detected:
  - `tools/check_glyph_calibration_fixtures.py`

## Where button enums are found
- Confirmed enum definitions located in dependency proto source:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `enum Button` contains `BTN_LF*`, `BTN_LT*`, `BTN_RF*`, `BTN_RT*`, `BTN_MB*`, and `BTN_UNSPECIFIED`.
- Confirmed usages in tracked firmware/config sources:
  - `config/glyph/common/include/glyph_overrides.hpp` (`ButtonRemap`, `SocdPair`, `MODE_ULTIMATE`, `LAYOUT_PLATE_EVERYTHING`)
  - `config/glyph/glyph_mk6/include/matrix_definition.hpp` (physical matrix entries with `BTN_*`)
  - `config/glyph/glyph_mk6/include/button_positions.hpp` (symbol-to-coordinate table used by firmware UI/layout rendering)
  - `include/core/config_utils.hpp` (switches on `MODE_ULTIMATE` and `SOCD_*`)

## Where mode/config schema is found
- Confirmed schema definitions in proto source:
  - `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - `message Config` with `game_mode_configs`
  - `message GameModeConfig` with `socd_pairs`, `button_remapping`, `layout_plate`, `applicable_backends`
  - `message ButtonRemap`, `message SocdPair`
  - `enum GameModeId`, `enum SocdType`, `enum LayoutPlate`, `enum CommunicationBackendId`
- Confirmed JSON fixture shape in calibration inputs:
  - `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json`
  - `docs/calibration/fixtures/GlyphUltFilled2.json`
  - Uses camelCase keys (`gameModeConfigs`, `modeId`, `buttonRemapping`, `socdPairs`, `layoutPlate`, `applicableBackends`)

## Gaps / unknowns
- Canonical tracked source for `config.proto` is not present under repo-controlled top-level source paths; discovered definitions are in `.pio/libdeps/...` dependency cache.
- `config.pb.h` used by firmware includes is not tracked in `include/` or `src/`; generated headers are present under `.pio/build/...`.
- Exact long-term source authority for proto/enums (if external repo revision changes) should be pinned in documentation before firmware behavior edits.
