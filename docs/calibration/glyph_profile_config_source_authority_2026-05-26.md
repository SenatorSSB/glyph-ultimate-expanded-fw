# Glyph Profile/Config Source Authority Audit - 2026-05-26

## Scope

This is a source-tracing audit for Glyph profile/config semantics in this repository, with labels:

- `source-confirmed`: backed by inspected repo source/docs/build config.
- `fixture-observed`: observed in repo-local JSON fixtures only.
- `inferred`: reasoned from source behavior but not explicitly specified as contract text.
- `unknown`: not established by inspected source/fixtures in this repo.

This batch is docs/check-script only. No firmware/configurator runtime behavior was changed.

## 1) Protobuf/config source authority

- `source-confirmed`: Firmware code consumes `Config`, `GameModeConfig`, `ButtonRemap`, and `SocdPair` from generated protobuf headers (`<config.pb.h>`), not from a repo-tracked first-party proto file (`HAL/pico/include/core/Persistence.hpp:22`, `HAL/pico/include/comms/ConfiguratorBackend.hpp:25`, `include/core/InputMode.hpp:7`, `include/core/config_utils.hpp:6`).
- `source-confirmed`: PlatformIO points nanopb proto generation at `.pio/libdeps/${PIOENV}/HayBox-proto/config.proto` (`platformio.ini:18-19`).
- `source-confirmed`: Base deps include `JonnyHaystack/HayBox-proto#5b2bb5d` (`platformio.ini:22-24`), while Glyph env ignores that source and adds `GregTurbo/HayBox-proto#db4e2f6` (`config/glyph/env.ini:13-18`).
- `source-confirmed`: In this workspace, dependency cache resolves to `.pio/libdeps/glyph_mk6/HayBox-proto` at commit `db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8` (local git metadata) and generated nanopb output exists at `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h` and `.c`.
- `source-confirmed`: No repo-tracked `config.proto`, `config.pb.h`, or `config.pb.c` is present (tracked file search returned none; only `.pio` artifacts were found).
- `requires-external-source`: Canonical protobuf schema semantics (field definitions/comments) come from dependency source, not repo-tracked source (`.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:346-351`, `:477-531`, `:585-623`).
- `requires-external-source`: One-based index intent for several config fields is documented in dependency proto comments, not in repo-tracked schema files (`.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:492-503`, `:601-614`).

Conclusion: this repo has partial operational authority (how firmware uses decoded structs) but not full standalone schema authority; stable adapter semantics still depend on external proto/configurator source capture.

## 2) Firmware config persistence (LittleFS/protobuf storage)

- `source-confirmed`: Config persistence filename is `config.bin` and a header (`config_size`, `config_crc`) is prepended (`HAL/pico/include/core/Persistence.hpp:26-43`).
- `source-confirmed`: Save path writes empty header, protobuf-encodes `Config` into file body, computes CRC over protobuf bytes, then rewrites header with final size/CRC (`HAL/pico/src/core/Persistence.cpp:36-77`).
- `source-confirmed`: Load path validates header+size+CRC before decode (`HAL/pico/src/core/Persistence.cpp:80-90`, `:154-178`).
- `source-confirmed`: Load path resets config struct to `Config_init_default` before decode, so loaded config replaces defaults instead of merging (`HAL/pico/src/core/Persistence.cpp:98-107`).
- `source-confirmed`: On boot, config starts from `glyph_default_config()` and if persisted load fails, defaults are immediately saved back (`config/glyph/common/src/config.cpp:34`, `:90-93`).
- `source-confirmed`: Saved file integrity checks are structural (header size + CRC) and do not perform deep semantic/range validation (`HAL/pico/src/core/Persistence.cpp:154-178`).
- `inferred`: A syntactically valid protobuf with semantically bad indices can pass persistence checks unless separately validated at write time.

## 3) Configurator backend transport semantics

- `source-confirmed`: Backend command dispatch supports device info, get config, set config, reboot firmware, reboot bootloader (`HAL/pico/src/comms/ConfiguratorBackend.cpp:58-79`).
- `source-confirmed`: Transport wraps a `Stream` with PacketIO COBS stream/print wrappers (`HAL/pico/include/comms/ConfiguratorBackend.hpp:21-23`, `:49-52`).
- `source-confirmed`: Device info is protobuf-encoded (`pb_encode`) and returned with `CMD_SET_DEVICE_INFO` (`HAL/pico/src/comms/ConfiguratorBackend.cpp:127-146`).
- `source-confirmed`: Get-config checks persisted config validity and then emits raw protobuf bytes from `config.bin` with `CMD_SET_CONFIG` (`HAL/pico/src/comms/ConfiguratorBackend.cpp:148-159`, `HAL/pico/src/core/Persistence.cpp:125-151`).
- `source-confirmed`: Set-config decodes protobuf (`pb_decode`) into `_config`, validates selected index constraints, then saves to LittleFS (`HAL/pico/src/comms/ConfiguratorBackend.cpp:161-273`).
- `source-confirmed`: Decode failure restores old persisted config (`HAL/pico/src/comms/ConfiguratorBackend.cpp:166-175`).
- `source-confirmed`: Validation failure after decode returns error but does not explicitly restore previous in-memory config (`HAL/pico/src/comms/ConfiguratorBackend.cpp:177-263`).
- `unknown`: Browser configurator JSON import/export rules are not implemented in inspected firmware transport source and are not proven by repo source code.

## 4) Remap semantics (firmware path)

- `source-confirmed`: Remap runs before SOCD and before digital/analog output synthesis (`src/core/ControllerMode.cpp:8-15`).
- `source-confirmed`: Remap logic allows many-to-one physical-to-logical mapping via OR behavior on target logical button state (`src/core/InputMode.cpp:73-79`).
- `source-confirmed`: Duplicate remaps from the same physical button are ignored after the first mapping entry (`src/core/InputMode.cpp:63-71`, `:80-81`).
- `source-confirmed`: Physical buttons without remap entries retain original state (`src/core/InputMode.cpp:84-85`).
- `source-confirmed`: `BTN_UNSPECIFIED` is an explicit no-op target in button bit helpers (`HAL/pico/include/util/state_util.hpp:10-24`).
- `source-confirmed`: Default Glyph config contains many explicit `BTN_UNSPECIFIED` remap targets (`config/glyph/common/include/glyph_overrides.hpp`, many entries including `:31`, `:70`, `:111`, `:217`, `:578-585`).

## 5) Repo-local JSON fixture semantics

Inspected fixtures:

- `docs/sources/raw/GlyphUserProfiles.json`
- `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json`
- `docs/calibration/fixtures/GlyphUltFilled2.json`
- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`

Observed via read-only fixture checks (`tools/check_glyph_profile_config_semantics.py`):

- `fixture-observed`: All inspected JSON fixtures represent disabled/unmapped remaps using omitted `activates` keys; explicit `"BTN_UNSPECIFIED"` string was not observed in remap entries (`remaps_explicit_btn_unspecified=0` for all four fixtures).
- `fixture-observed`: Omitted `activates` is common and high-volume in fixtures (for example raw profile: `267` omitted vs `45` present activates).
- `fixture-observed`: Some fixtures contain many-to-one logical target mappings in Ultimate mode, but this is fixture-dependent and not constant across fixtures.
- `fixture-observed`: `communicationBackendConfigs` entry for `COMMS_BACKEND_CONFIGURATOR` omits `defaultModeConfig` in all inspected fixtures.
- `fixture-observed`: Keyboard mode is the only mode without `buttonRemapping` in inspected fixtures.
- `fixture-observed`: Some `socdPairs` entries omit `socdType` in fixtures.

## 6) Existing Python parser/model helper semantics

Primary helper:

- `tools/glyph_config_model.py`

Behavior:

- `source-confirmed`: `GlyphButtonRemap.activates` is modeled as `str | None` (`tools/glyph_config_model.py:13-16`).
- `source-confirmed`: Missing `activates` is preserved as `None`; explicit strings are preserved as strings (`tools/glyph_config_model.py:140-147`).
- `source-confirmed`: Missing `buttonRemapping` becomes `[]` (`tools/glyph_config_model.py:121-125`).
- `source-confirmed`: Missing `modeId`/`name` become empty strings; missing `layoutPlate` remains `None` (`tools/glyph_config_model.py:91-106`).
- `source-confirmed`: Helper resolves Ultimate mode by `name == "Ultimate"` or `modeId == "MODE_ULTIMATE"` (`tools/glyph_config_model.py:72-79`).
- `source-confirmed`: Parser validates basic types but does not validate default index references (`defaultBackendConfig`, `defaultUsbBackendConfig`, `defaultModeConfig`) and does not validate remap duplicate/many-to-one constraints.

Related checks:

- `source-confirmed`: `tools/check_glyph_calibration_fixtures.py` explicitly checks omitted `activates` for selected buttons in calibration fixtures (`tools/check_glyph_calibration_fixtures.py:76-82`, `:146-149`).
- `source-confirmed`: `tools/patch_glyph_ultimate_profile.py` requires `activates` as string for patch updates and does not model omission writes (`tools/patch_glyph_ultimate_profile.py:79-84`, `:96-101`).

## 7) Default profile/index behavior

- `source-confirmed`: `default_mode_config` is treated as one-based index in runtime path (`HAL/pico/src/comms/backend_init.cpp:138-143`).
- `source-confirmed`: `default_usb_backend_config` is treated as one-based index with bounds check in USB-backend getter (`HAL/pico/src/comms/backend_init.cpp:292-296`).
- `source-confirmed`: Helper functions returning config IDs are one-based (`src/core/config_utils.cpp:59`, `:74`).
- `source-confirmed`: Menu-driven default profile changes set watchdog scratch values as one-based (`mode_config_index + 1`) and reboot (`HAL/pico/src/display/DefaultConfigMenu.cpp:298-301`).
- `source-confirmed`: On watchdog override, firmware persists temporary backend/mode selection back into config defaults (`HAL/pico/src/comms/backend_init.cpp:101-120`).
- `source-confirmed`: Configurator set-config rejects `default_mode_config > game_mode_configs_count` (`HAL/pico/src/comms/ConfiguratorBackend.cpp:190-205`).
- `source-confirmed`: Configurator set-config rejects `default_backend_config > communication_backend_configs_count` (`HAL/pico/src/comms/ConfiguratorBackend.cpp:177-188`).
- `source-confirmed`: `default_mode_config == 0` is not rejected by set-config validation and is treated as "no default mode apply" by backend init (`HAL/pico/src/comms/ConfiguratorBackend.cpp:190-205`, `HAL/pico/src/comms/backend_init.cpp:138-144`).
- `source-confirmed`: Glyph default config currently declares `game_mode_configs_count = 13` (`config/glyph/common/include/glyph_overrides.hpp:17`), while mode activation mask storage is fixed at 10 (`src/core/mode_selection.cpp:30`), and setup loop iterates `game_mode_configs_count` (`src/core/mode_selection.cpp:187-193`).
- `inferred`: The 13-vs-10 mismatch is a risk surface for mode activation binding handling and should be treated as unsafe to assume correct without dedicated validation.
- `source-confirmed`: `applicable_backends` is used for menu visibility/filtering (`config/glyph/common/src/display/GlyphConfigMenu.cpp:32-47`) and dashboard icon logic (`config/glyph/common/src/display/MenuButtonHints.cpp:289-313`); enforcement in `set_mode(...)` path is not shown in inspected runtime mode switch code (`src/core/mode_selection.cpp:90-147`).

## 8) Omitted `activates` vs explicit `BTN_UNSPECIFIED`

This distinction must be preserved.

- `source-confirmed`: Firmware runtime semantics for explicit `BTN_UNSPECIFIED` are clear: setting/getting unspecified button is a no-op/false (`HAL/pico/include/util/state_util.hpp:10-24`).
- `source-confirmed`: Firmware defaults use explicit `BTN_UNSPECIFIED` heavily in `default_config` remaps (`config/glyph/common/include/glyph_overrides.hpp`, multiple entries).
- `fixture-observed`: Repo JSON fixtures encode many disabled/unmapped entries as omitted `activates`, not as explicit `BTN_UNSPECIFIED`.
- `unknown`: Host configurator policy for serializing enum-zero protobuf values as omitted field vs explicit `"BTN_UNSPECIFIED"` is not defined in repo source.

Adapter implication:

- Do not conflate omitted `activates` with explicit `BTN_UNSPECIFIED` unless external configurator/proto source authority confirms equivalence for the target workflow.

## 9) Protobuf stored config vs external JSON exports

- `source-confirmed`: Device persistence format is binary protobuf + custom header in `config.bin` on LittleFS (`HAL/pico/include/core/Persistence.hpp:26-43`, `HAL/pico/src/core/Persistence.cpp:49-73`).
- `source-confirmed`: Configurator backend transfers raw protobuf payloads over COBS-framed command stream (`HAL/pico/src/comms/ConfiguratorBackend.cpp:148-159`, `:161-167`).
- `fixture-observed`: Repo contains JSON profile fixtures that resemble config projections.
- `unknown`: Source-of-truth JSON import/export mapping rules for browser configurator are not defined in inspected firmware source.

Adapter implication:

- Treat JSON fixtures as examples/corpus inputs, not as authoritative wire format or canonical serialization contract.

## 10) Adapter safety recommendations (pre-adapter)

Safe from source alone:

- Use firmware runtime ordering assumption: remap then SOCD then output synthesis (`src/core/ControllerMode.cpp:8-15`).
- Preserve explicit `BTN_UNSPECIFIED` semantics as no-op target (`HAL/pico/include/util/state_util.hpp:10-24`).
- Preserve many-to-one and duplicate-physical-first-entry remap behavior (`src/core/InputMode.cpp:63-81`).
- Respect one-based index usage where runtime explicitly subtracts 1 (`HAL/pico/src/comms/backend_init.cpp:138-143`, `src/core/config_utils.cpp:59`, `:74`).

Requires external configurator/proto source and/or captured export corpus:

- Canonical JSON omission policy for enum-zero fields such as `ButtonRemap.activates`.
- Round-trip stability rules between browser JSON and protobuf bytes.
- Host-side validation contract for omitted `socdType`, omitted `defaultModeConfig`, and omitted optional fields.

Requires user/domain policy decisions before adapter writes:

- How to encode disabled remaps on write (`omit activates` vs explicit `BTN_UNSPECIFIED`) when both appear across source surfaces.
- Whether adapter is allowed to normalize field presence or must preserve original omission style.
- Whether to reject or pass through fixture patterns that stress runtime capacity assumptions (for example profile-count vs activation-mask capacity).

Recommended validation fixtures/checkers before write-capable adapter work:

- Keep `tools/check_glyph_profile_config_semantics.py` in preflight.
- Preflight should report omitted `activates` count vs explicit `BTN_UNSPECIFIED` count.
- Preflight should report duplicate physical remap entries.
- Preflight should report many-to-one target aliasing.
- Preflight should report backend default-mode index structural validity.
- Preflight should report profile count vs activation-mask capacity warnings.
- Expand fixture corpus with paired cases that differ only by omission vs explicit `BTN_UNSPECIFIED`, and verify byte-level protobuf outcomes.
- Capture authoritative configurator export corpus from known configurator/proto revision and freeze as regression fixtures before any adapter write implementation.
