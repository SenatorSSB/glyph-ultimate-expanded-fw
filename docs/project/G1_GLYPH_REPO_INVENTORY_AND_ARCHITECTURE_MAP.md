# G1 — Glyph Repo Inventory and Architecture Map

Status: complete (inventory/design document)  
Date: 2026-05-23  
Branch inspected: `docs/senscope-glyph-baseline`  
Authority scope: source-backed inventory only; this is not capability approval.

## 1) Scope

Inspected:
- Required workflow docs in `AGENTS.md` and `docs/project/*` (active queue, contract, stop conditions, boundaries, integration target, capability model target).
- Required source/config/reference files:
  - `platformio.ini`
  - `include/core/state.hpp`
  - `include/core/InputMode.hpp`
  - `src/core/InputMode.cpp`
  - `include/core/ControllerMode.hpp`
  - `src/core/ControllerMode.cpp`
  - `include/modes/Ultimate.hpp`
  - `src/modes/Ultimate.cpp`
  - `include/modes/CustomControllerMode.hpp`
  - `src/modes/CustomControllerMode.cpp`
  - `config/glyph/*`
  - `HAL/pico/*`
  - `docs/sources/raw/ESAM1.cpp`
  - `docs/sources/raw/ESAM1.hpp`
  - `docs/sources/raw/GlyphUserProfiles.json`
- Supporting architecture/build/docs files, scripts, and CI workflow files.

Intentionally not decided:
- No runtime adapter design/implementation decisions.
- No firmware behavior changes.
- No Senscope semantic-source authority changes.
- No push/export product decisions beyond inventory of existing source evidence.

## 2) Top-level repository structure

Observed major areas:
- Firmware core:
  - `include/core/`
  - `src/core/`
  - `include/modes/`
  - `src/modes/`
  - `include/input/`, `src/input/`
  - `include/comms/`, `src/comms/`
- Device-family overlays and board config:
  - `config/glyph/` (common + env-specific config for `glyph_protoA`, `glyph_mk6`)
- Hardware abstraction layers:
  - `HAL/pico/` (RP2040 path)
  - `HAL/avr/` (AVR path also present)
- Build/automation support:
  - `platformio.ini`
  - `builder_scripts/arduino_pico.py`
  - `scripts/pio-local.sh`
  - `scripts/build-glyph-mk6-quiet.sh`
  - `.github/workflows/*.yml`
- Docs and research:
  - `docs/project/` (workflow/contracts/queue)
  - `docs/architecture/` (design boundaries)
  - `docs/research/` (findings/notes)
  - `docs/firmware/` (build notes)
  - `docs/sources/` and `docs/sources/raw/` (source-material staging)
- Other assets:
  - `dolphin/*.ini` (emulator controller profiles)
  - `glyph_nuker` (artifact post-processing tool used in CI workflow)

Unknown/needs deeper classification later:
- Full behavior impact of all extra mode files under `include/modes/extra/` + `src/modes/extra/`.
- Full runtime significance of all display/RGB/menu subsystems under `HAL/pico/src/display` and `HAL/pico/src/rgb`.

## 3) Build and environment surface

PlatformIO and env layering:
- Root `platformio.ini` defines:
  - `default_envs = glyph_mk6`
  - `extra_configs = config/*/env.ini`
  - base envs for AVR and RP2040/pico families.
- `config/glyph/env.ini` extends `arduino_pico_base` into `glyph_base`, then defines:
  - `env:glyph_protoA`
  - `env:glyph_mk6_Debug`
  - `env:glyph_mk6`
- `config/glyph/meta.yaml` names upstream/revision metadata and build outputs.

Discovered command surface:
- `scripts/pio-local.sh`: repo-local PlatformIO launcher with `.venv/bin/python` fallback, then `python`, then `python3`.
- `scripts/build-glyph-mk6-quiet.sh`: runs `./scripts/pio-local.sh run -e glyph_mk6`, prints only summary/tail behavior.
- `.github/workflows/build.yml`: CI build job for `glyph_mk6` and artifact publish.
- `.github/workflows/build-device-config.yml`: workflow_call build matrix from `meta.yaml`.

Wrapper script executability check:
- `test -x ./scripts/pio-local.sh`: executable
- `test -x ./scripts/build-glyph-mk6-quiet.sh`: executable

Build verification status:
- Build was not run in this G1 task (docs/inventory-only scope).
- No build success is claimed.

## 4) Core firmware architecture map

Core state model:
- `include/core/state.hpp` defines `InputState`, `StickDirections`, and `OutputState`.
- `InputState` uses bitfields within a 64-bit button union plus nunchuk flags/axes.
- `OutputState` contains digital outputs bitfield and analog axis bytes.

Input mode base:
- `include/core/InputMode.hpp` / `src/core/InputMode.cpp`
- Responsibilities:
  - Holds active `GameModeConfig`.
  - Applies SOCD pair handling (`HandleSocd`) from config.
  - Applies button remapping (`HandleRemap`) from config.
  - Prevents macro creation by ignoring duplicate physical remaps (commented intent in source).

Controller mode base:
- `include/core/ControllerMode.hpp` / `src/core/ControllerMode.cpp`
- Responsibilities:
  - `UpdateOutputs`: remap -> SOCD -> digital mapping -> analog mapping.
  - `UpdateDirections`: computes left/right stick direction fields and default analog outputs.

Mode selection/dispatch:
- `include/core/mode_selection.hpp` / `src/core/mode_selection.cpp`
- Responsibilities:
  - Static mode instances (`Melee20Button`, `ProjectM`, `Ultimate`, `FgcMode`, `Rivals*`, `Custom*`, `Smash64`).
  - `set_mode` overloads for `ControllerMode`, `KeyboardMode`, `GameModeConfig`, `GameModeId`.
  - Mode activation through button-hold masks (`setup_mode_activation_bindings`, `select_mode`).

Backend abstraction:
- `include/core/CommunicationBackend.hpp` / `src/core/CommunicationBackend.cpp`
- Responsibilities:
  - Owns input source list and per-backend output state.
  - Scans inputs from `InputSource`.
  - Delegates output computation to currently set `InputMode`.

## 5) Mode/input/output architecture map

### InputMode and SOCD/remap

Known (source-backed):
- SOCD types handled: `SOCD_NEUTRAL`, `SOCD_2IP`, `SOCD_2IP_NO_REAC`, `SOCD_DIR1_PRIORITY`, `SOCD_DIR2_PRIORITY`.  
  Source: `src/core/InputMode.cpp`, `src/core/socd.cpp`.
- SOCD state memory is per-pair (`_socd_states[10]`).  
  Source: `include/core/InputMode.hpp`.
- Remap logic is many-to-one, with explicit anti-macro remap guard.  
  Source: `src/core/InputMode.cpp`.

### ControllerMode

Known (source-backed):
- Direction synthesis for both sticks is centralized in `UpdateDirections`.
- Analog defaults are neutral; active directional booleans push to min/max values.
  Source: `src/core/ControllerMode.cpp`.

### Ultimate mode

Known (source-backed):
- Digital mappings from physical button fields to gamepad outputs are explicitly hardcoded.
- D-pad layer is toggled by `(lt1 && lt2) || nunchuk_c`.
- Analog section applies many hardcoded coordinate offsets for modifier states and stick combinations.
- Nunchuk can override left stick output.
  Source: `src/modes/Ultimate.cpp`.

Inferred:
- `Ultimate` is a mode-specific handcrafted realization table/logic path rather than a generic config-driven directional table system.
  Inference basis: extensive hardcoded coordinate constants in `src/modes/Ultimate.cpp`.

### CustomControllerMode

Known (source-backed):
- Uses `CustomModeConfig` plus `GameModeConfig` via `SetConfig`.
- Supports:
  - button-combo to single digital-output mappings,
  - per-output digital button mappings,
  - stick-direction mapping from configured buttons,
  - analog modifiers with `COMBINATION_MODE_OVERRIDE` and `COMBINATION_MODE_COMPOUND`,
  - analog trigger mappings,
  - nunchuk override behavior.
  Source: `src/modes/CustomControllerMode.cpp`, `include/modes/CustomControllerMode.hpp`.

Unknown:
- Exact externally supported configurator schema/UI affordances for all `CustomModeConfig` fields are not proven by this repo alone.

## 6) Configuration and schema surface

Primary config representation in source:
- Protobuf-backed `Config` / `GameModeConfig` / related types from `config.pb.h` are used throughout.
  Source: multiple core/mode/backend files.

Default/overlay config surfaces:
- `HAL/pico/include/config_defaults.hpp` defines a baseline `default_config` with multiple game/backends/keyboard mappings.
- `config/glyph/common/include/glyph_overrides.hpp` defines Glyph-specific `default_config` with:
  - `game_mode_configs_count = 13`
  - `communication_backend_configs_count = 8`
  - `keyboard_modes_count = 1`
  - `rgb_configs_count = 13`
  - `default_backend_config = 1`
  - `default_usb_backend_config = 1`
  and returns this via `glyph_default_config()`.

Persistence/config transport:
- `HAL/pico/src/core/Persistence.cpp` saves/loads protobuf config as `config.bin` in LittleFS with CRC header.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` handles `CMD_GET_CONFIG` and `CMD_SET_CONFIG` using protobuf streams and validation checks.

Raw profile artifact:
- `docs/sources/raw/GlyphUserProfiles.json` exists as staged reference material and structurally mirrors many config concepts (mode configs, backend configs, keyboard/rgb blocks).
- This file is treated as reference evidence only in G1; no claim is made that it fully covers exact 9-way modifier realization.

## 7) Hardware/HAL surface

HAL directories present:
- `HAL/pico/`: RP2040-focused runtime including:
  - backend initialization and detection path (`HAL/pico/src/comms/backend_init.cpp`)
  - protocol backends (`DInput`, `XInput`, `NintendoSwitch`, `Gamecube`, `N64`, `NES`, `SNES`, `Configurator`)
  - persistence, input drivers, display, RGB, reboot, serial
- `HAL/avr/`: AVR-specific counterpart also present (not deep-inspected for behavior in this G1 writeup).

Glyph board overlays:
- `config/glyph/glyph_mk6/include/*` and `config/glyph/glyph_protoA/include/*` define pinout/matrix/button-position overlays.
- Example difference: `joybus_data` pin differs between protoA and mk6 (`4` vs `8`).

## 8) Reference/source-staged materials

Observed staged source references:
- `docs/sources/raw/ESAM1.hpp`
- `docs/sources/raw/ESAM1.cpp`
- `docs/sources/raw/GlyphUserProfiles.json`
- Manifest: `docs/sources/source-manifest.json`

Evidence classification:
- `ESAM1.*` appears to represent older behavior/reference code (API shape diverges from current core types in this repo), so it is treated as behavior evidence/reference, not direct modern profile schema authority.
- `GlyphUserProfiles.json` is treated as copied reference material for config-shape analysis, not as sole authority for runtime capability guarantees.

## 9) Existing docs and workflow map

`docs/project/`:
- Agent workflow/control-plane docs: queue, contracts, boundaries, stop conditions, report templates.
- Primary handoff docs for subsequent G2/G3 work.

`docs/research/`:
- Findings and source-context notes (`GLYPH_FINDINGS_2026-05-21.md`, `ESAM1_PROTOTYPE_NOTES.md`, `GLYPH_CONFIG_EXPORT_NOTES.md`, etc.).

`docs/architecture/`:
- Layering and boundary design docs for neutral profile vs capability/evaluation/export separation.

`docs/firmware/`:
- Build and baseline notes, including wrapper-command policy.

Recommended starting points for later agents:
- `docs/project/ACTIVE_AGENT_QUEUE.md`
- `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`
- `docs/architecture/GLYPH_BACKEND_LAYERING.md`
- `src/core/mode_selection.cpp`
- `config/glyph/common/include/glyph_overrides.hpp`
- `HAL/pico/src/comms/backend_init.cpp`

## 10) Source-backed knowns

- `platformio.ini` sets default env `glyph_mk6` and imports extra env config files from `config/*/env.ini`.  
  Source: `platformio.ini`
- Glyph env definitions for `glyph_protoA` and `glyph_mk6` are in `config/glyph/env.ini`.  
  Source: `config/glyph/env.ini`
- Input remap and SOCD resolution are config-driven at the `InputMode` layer.  
  Source: `include/core/InputMode.hpp`, `src/core/InputMode.cpp`
- SOCD algorithm implementations for neutral/2IP/2IP-no-reactivation/dir-priority are in `src/core/socd.cpp`.  
  Source: `src/core/socd.cpp`
- Controller-mode output pipeline order is remap -> SOCD -> digital -> analog.  
  Source: `src/core/ControllerMode.cpp`
- Mode activation by button-hold masks is implemented by `setup_mode_activation_bindings` and `select_mode`.  
  Source: `src/core/mode_selection.cpp`
- `MODE_CUSTOM` and `MODE_KEYBOARD` paths are explicitly handled in mode selection.  
  Source: `src/core/mode_selection.cpp`
- Ultimate mode includes hardcoded directional/analog modifier constants and D-pad layer toggling logic.  
  Source: `src/modes/Ultimate.cpp`
- Custom controller mode supports combo mappings, analog modifiers, and analog trigger mappings.  
  Source: `src/modes/CustomControllerMode.cpp`
- Config persistence uses LittleFS + protobuf encode/decode + CRC validation.  
  Source: `HAL/pico/src/core/Persistence.cpp`
- Configurator backend supports get/set config commands and writes via persistence.  
  Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- Backend initialization supports multiple protocol backends and detection-based selection.  
  Source: `HAL/pico/src/comms/backend_init.cpp`
- Glyph-specific default config is supplied by `glyph_default_config()`.  
  Source: `config/glyph/common/include/glyph_overrides.hpp`, `config/glyph/common/src/config.cpp`

## 11) Inferences (not implementation truth)

- The architecture is split into:
  - core generic mode/input/backend logic,
  - board/env overlays under `config/glyph/*`,
  - transport/HAL implementations under `HAL/pico` and `HAL/avr`.
- `CustomControllerMode` likely represents the intended extensible path for data-driven controller behavior, while `Ultimate` represents a fixed handcrafted mode.
- `docs/sources/raw/*` appears to be a staging area for evidence artifacts used by integration analysis, not necessarily a direct build input.

## 12) Unknowns and source-authority gaps

Open unknowns requiring deeper G2 extraction:
- Exact 9-way directional modifier support as a formal, generic capability model surface.
- Neutral non-center realization guarantees across all modes/backends.
- Flipper transform semantics (formalized runtime model vs mode-specific hardcoding).
- Pre-SOCD Force Up-B override semantics as a reusable capability.
- Dynamic button-layer framework beyond explicit hardcoded mode logic.
- Button chord semantics beyond current combo mapping implementation details.
- Full SOCD/priority/fusion interactions at system level (especially cross-mode guarantees).
- Export/manual-entry/push support boundaries for end-user workflows across toolchains.

Additional gaps:
- No explicit in-repo test suite was found in common `test/tests/spec` locations.
- `docs/sources/README.md` still states task-named raw artifacts were not present, but those files now exist in `docs/sources/raw/` (doc staleness risk).

## 13) Risks

Architectural/source-authority risks:
- Over-interpreting mode-specific constants (for example in `Ultimate.cpp`) as generic backend guarantees.
- Treating staged reference JSON/legacy ESAM files as authoritative runtime contracts.

Firmware-safety risks:
- Changing shared core paths (`InputMode`, `ControllerMode`, backend init, persistence) without precise mode/backend regression checks can alter broad behavior.

Scope risks:
- Blending controller realization concerns with Senscope game semantics violates stated boundaries.
- Premature export/push assumptions may create unsupported integration commitments.

## 14) Recommended next investigation targets

Next phase recommendation:
- Proceed to G2 (`docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`) using this inventory as baseline.

Concrete G2 targets:
- Enumerate mode-level capability surfaces from:
  - `src/modes/Ultimate.cpp`
  - `src/modes/CustomControllerMode.cpp`
  - other mode files in `src/modes/`
- Enumerate config-shape capabilities and constraints from:
  - `config/glyph/common/include/glyph_overrides.hpp`
  - `HAL/pico/include/config_defaults.hpp`
  - `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- Enumerate backend protocol coverage and default-selection behavior from:
  - `HAL/pico/src/comms/backend_init.cpp`
  - `include/core/CommunicationBackend.hpp`
  - backend implementations under `HAL/pico/src/comms/`
- Build an explicit claim table: `source-backed` vs `inferred` vs `unknown`.

## 15) Verification

Commands run:
- `git status --short --branch`
- `git branch --show-current`
- `git remote -v`
- `git diff --stat`
- `find . -maxdepth 3 -type f`
- `find include src config HAL docs scripts -maxdepth 4 -type f`
- `sed -n '1,260p' ...` across required and supporting files
- `rg -n ...` targeted pattern scans
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)' || true`
- `test -x ./scripts/pio-local.sh && echo executable || echo not-executable`
- `test -x ./scripts/build-glyph-mk6-quiet.sh && echo executable || echo not-executable`

Results:
- Branch/remote state is clear for this task (`docs/senscope-glyph-baseline` on `origin`).
- Docs-only inventory file created.
- Build was intentionally not executed for this docs-only G1 task.
