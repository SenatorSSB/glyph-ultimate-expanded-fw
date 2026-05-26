# Glyph Profile/Config Source Authority Handoff

## Branch

- Base branch (requested): `configurator`
- Working branch (requested): `glyph/profile-config-source-authority`

## What was inspected

- `platformio.ini`
- `config/glyph/env.ini`
- `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
- `.pio/libdeps/glyph_mk6/HayBox-proto/config.options`
- `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`
- `HAL/pico/include/core/Persistence.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `config/glyph/common/src/config.cpp`
- `HAL/pico/include/comms/ConfiguratorBackend.hpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `src/core/InputMode.cpp`
- `src/core/ControllerMode.cpp`
- `HAL/pico/include/util/state_util.hpp`
- `src/core/config_utils.cpp`
- `src/core/mode_selection.cpp`
- `HAL/pico/src/comms/backend_init.cpp`
- `HAL/pico/src/display/DefaultConfigMenu.cpp`
- `config/glyph/common/src/display/GlyphConfigMenu.cpp`
- `config/glyph/common/src/display/MenuButtonHints.cpp`
- `config/glyph/common/include/glyph_overrides.hpp`
- `HAL/pico/include/config_defaults.hpp`
- `docs/sources/raw/GlyphUserProfiles.json`
- `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json`
- `docs/calibration/fixtures/GlyphUltFilled2.json`
- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`
- `tools/glyph_config_model.py`
- `tools/check_glyph_calibration_fixtures.py`
- `tools/patch_glyph_ultimate_profile.py`
- `tools/check_glyph_profile_config_semantics.py` (new read-only helper)

## What was not inspected

- External/browser configurator host codebase (not checked into this repo).
- Vendor/private/encrypted formats and any reverse-engineered data.
- Push-to-device automation workflows beyond existing firmware command handlers.
- Non-local export corpus beyond repo fixtures.

## Runtime behavior changed

- None.

## Source/configurator behavior changed

- None.

## Files added in this batch

- `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md`
- `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md`
- `docs/calibration/glyph_profile_config_source_authority_handoff.md`
- `tools/check_glyph_profile_config_semantics.py` (read-only checker; no mutation/write path)

## Recommended next branches

- `glyph/profile-config-export-corpus-capture`: capture matched-version configurator export corpus and omission/default edge cases.
- `glyph/profile-config-adapter-policy-decisions`: record user/domain decisions for omitted `activates` vs explicit `BTN_UNSPECIFIED` write policy.
- `glyph/profile-config-adapter-prewrite-validation`: add stricter pre-write validation gates after policy/source capture is complete.

## Verification commands run

- `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py`: `PASS` (`failed_steps=0`, `overall_status=PASS`).
- `.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py`: `PASS` (`final_disposition=PASS`).
- `.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py`: `PASS`.
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true`: no conflict markers found.
- `git diff --check`: clean (no whitespace/conflict-style diff issues).
- `git status --short`: expected additions only (`docs/calibration/glyph_profile_config_source_authority_2026-05-26.md`, `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md`, `docs/calibration/glyph_profile_config_source_authority_handoff.md`, `tools/check_glyph_profile_config_semantics.py`).
- `.venv/bin/python tools/check_glyph_profile_config_semantics.py`: `PASS` (reports fixture summaries and warnings; no structural errors).

## Exact questions needing user/domain input or external source

1. Should write-capable adapter output preserve omission style for disabled remaps, normalize to explicit `BTN_UNSPECIFIED`, or be selectable per target workflow?
2. Which exact configurator/proto revision should be treated as canonical authority for adapter round-trip behavior?
3. Is `applicableBackends` intended as UI-only metadata, or should adapter enforce it as hard eligibility constraint?
4. Should `defaultModeConfig = 0` be considered valid/intentional for any backend in outbound adapter data?
5. Is adapter allowed to reorder/remap entries, or must input ordering be preserved exactly for precedence safety?
6. Is the current mode-count vs activation-mask-capacity mismatch (`13` vs `10`) considered acceptable/known, or should adapter preflight block profiles relying on this surface until runtime authority is clarified?
