# Glyph Active Ultimate Profile Binding Path Trace - 2026-05-27

## Scope

- Source-trace why changing `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json` did not make physical LT3 actionable as logical LT3 on flashed hardware.
- Determine source-backed profile/default lifecycle in this repo.
- Do not change runtime tilt logic.

## Summary Answer

- Normal firmware update does not rewrite an already valid stored config/profile in `config.bin`; boot loads persisted config first and only writes defaults when load fails.
- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json` is not firmware build-consumed source; it is used by docs/check tooling only.
- The build-consumed factory/default config source for Glyph mk6 is `config/glyph/common/include/glyph_overrides.hpp` via `glyph_default_config()` in `config/glyph/common/src/config.cpp`.
- For an already-provisioned controller, default source changes apply only after default restoration semantics (for example Fresh Install/wipe or equivalent config reset path), because valid persisted config takes precedence at boot.
- No source-backed profile migration/version-upgrade mechanism was found in firmware persistence/configurator paths.
- Current conclusion for this branch: `FRESH_INSTALL_REQUIRED_FOR_DEFAULT_PROFILE_BINDING` (for default-source edits). For immediate active-profile testing without migration work, use source-backed config import/write path.

## Evidence Table

| Source path | Relevant symbol/function/file | Finding | Confidence |
| --- | --- | --- | --- |
| `config/glyph/common/src/config.cpp` | `Config config = glyph_default_config();` and `if (!persistence.LoadConfig(config)) { persistence.SaveConfig(config); }` | Boot starts from defaults, then loads persisted config; defaults are only saved when load fails. | High |
| `config/glyph/common/include/glyph_overrides.hpp` | `const Config default_config` and `Config glyph_default_config()` | Factory/default profile content is compiled from this C++ config source for Glyph builds. | High |
| `HAL/pico/include/core/Persistence.hpp` | `config_filename = "config.bin"` | Persisted runtime profile/config is stored in LittleFS `config.bin`. | High |
| `HAL/pico/src/core/Persistence.cpp` | `SaveConfig`, `LoadConfig`, CRC/header validation | Stored config is persisted and loaded as protobuf; valid saved config is preserved/used. | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | `HandleSetConfig`, `HandleGetConfig`, `persistence.SaveConfig(_config)` | Source-backed write path exists to import/apply a full config artifact to active storage. | High |
| `rg -n "GlyphUserProfilesUltimateMVP01.json|tilt_button_id_probe" .` | Search results | Fixture path is referenced in `docs/` and `tools/`, not in firmware runtime/build sources. | High |
| `rg -n "GlyphUserProfiles|tilt_button_id_probe" config src include HAL` | Search results (no matches) | No evidence that the edited fixture is compiled into firmware runtime. | High |
| `docs/sources/raw/glyph_firmware_uf2/1.0.7/README.md` and `manifest.json` | User-provided update procedure capture | Update is documented as preserving profiles; Fresh Install as wiping/restoring defaults. | Medium (user-provided source text, captured verbatim) |
| `HAL/pico/src/core/Persistence.cpp`, `HAL/pico/src/comms/ConfiguratorBackend.cpp`, `config/glyph/common/src/config.cpp` | profile/version/migration keywords + inspected logic | No explicit profile migration/version-gated rewrite flow found. | Medium-High |

## Direct Answers To Primary Questions

1. Is `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json` consumed by firmware builds at all?  
   - No source evidence of build/runtime consumption. Repo references are docs/checker/tooling only.

2. Where are real default/factory profiles stored in this repo?  
   - In compiled C++ defaults at `config/glyph/common/include/glyph_overrides.hpp` (`default_config` / `glyph_default_config()`).

3. What source path populates profiles on a fresh install?  
   - Boot path in `config/glyph/common/src/config.cpp`: if `persistence.LoadConfig(config)` fails, defaults are saved via `persistence.SaveConfig(config)`.

4. What source path preserves profiles on a normal update?  
   - Persistence load path (`HAL/pico/src/core/Persistence.cpp`) keeps valid `config.bin`; boot uses it directly.

5. Does firmware update path ever migrate/update existing stored profiles?  
   - No source-backed migration/update mechanism found in runtime persistence/configurator code.

6. Is there an existing source-supported profile version/migration mechanism?  
   - Not found in inspected firmware sources.

7. Minimal safe way to get physical `BTN_LT3 -> BTN_LT3` into the active Ultimate profile?  
   - Use source-backed config import/write path (`ConfiguratorBackend::HandleSetConfig` -> `Persistence::SaveConfig`) with an artifact that keeps `BTN_RF3 -> BTN_LT1` and `BTN_RF4 -> BTN_LT2` while setting `BTN_LT3 -> BTN_LT3`.

## Current Conclusion (Why LT3 Stayed Inactive After Flash)

- Runtime Tilt3 code exists (`inputs.lt3 || (inputs.lt1 && inputs.lt2)`), and LT1+LT2 hardware verification proves runtime path is active.
- The changed file was a fixture-only artifact not consumed by firmware build/runtime.
- The flashed controller continued using stored active profile/config from `config.bin`, which was preserved and did not pick up the fixture edit.
- Therefore no standalone physical button triggered logical LT3 in active config, while LT1+LT2 still triggered Tilt3.

## Safe Implementation Options

1. Update actual factory/default profile source (`config/glyph/common/include/glyph_overrides.hpp`) if approved:
   - Source-backed, build-consumed.
   - Affects default restoration path, not already-stored active configs.
   - Requires default restore/fresh-install semantics to apply on existing devices.

2. Create/import a config artifact manually (source-backed):
   - Use configurator set-config path (`CMD_SET_CONFIG` / `HandleSetConfig` / `SaveConfig`).
   - Can update active stored profile directly without runtime source change.
   - Best fit for targeted dedicated LT3 test enablement.

3. Implement profile migration (only with explicit future approval):
   - Not currently present in source.
   - Higher risk and broader lifecycle impact.

## Recommendation

- Lowest-risk path for dedicated LT3 testing now: **Option 2 (manual config import/write path)** using a validated artifact that explicitly sets:
  - `BTN_RF3 -> BTN_LT1`
  - `BTN_RF4 -> BTN_LT2`
  - `BTN_LT3 -> BTN_LT3`
- Keep runtime source unchanged.
- Treat default-source edits as a separate, deliberate factory-profile change that requires fresh-install/default-restore semantics to affect already-provisioned devices.

## 2026-05-27 Amendment: Implemented Active Artifact Path

- This branch implements the Option 2 path by adding:
  - `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json`
  - `tools/check_glyph_active_ultimate_lt3_config_artifact.py`
  - `docs/calibration/glyph_active_ultimate_lt3_config_artifact_2026-05-27.md`
- Implementation kind in this branch: validated importable config/profile artifact for manual configurator apply path.
- Active application path remains:
  - configurator config write (`CMD_SET_CONFIG`)
  - `ConfiguratorBackend::HandleSetConfig`
  - `Persistence::SaveConfig`
- Caveat remains unchanged:
  - no claim that an active device profile is updated until the artifact is manually imported/applied.
