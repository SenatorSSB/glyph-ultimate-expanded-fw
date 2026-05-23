# G12j Glyph Function Preservation Risk Audit

Status: docs-only risk audit. No firmware source, runtime behavior, config, protobuf, upload workflow, or hardware state is changed by this document.

## Current Expected Answer

The current `SenscopePrototype` work should not affect normal Glyph functions while it remains unreachable by default and while display, menu, config, persistence, communication, default mode, and backend source files remain unchanged.

This is a preservation expectation, not a hardware guarantee. Custom firmware built from this repo still requires artifact inspection, recovery planning, and explicit human approval before any flash.

## Function Preservation Matrix

| Function area | Touched by current `SenscopePrototype` work? | Source areas likely involved | Preservation strategy | First-test observation |
| --- | --- | --- | --- | --- |
| 1. Normal controller enumeration | No, if backend code and default config stay unchanged | `HAL/pico/src/comms/*`, `HAL/pico/include/comms/*`, `config/glyph/common/src/config.cpp`, `HAL/pico/include/config_defaults.hpp` | Do not alter backend initialization, descriptors, default USB backend, or communication backend config. | Confirm host sees the expected controller backend after boot. |
| 2. Menu button behavior | No, if menu/input/display code stays unchanged | `config/glyph/common/src/config.cpp`, `HAL/pico/src/display/*`, `HAL/pico/include/display/*`, input matrix config | Do not alter menu button mapping, early boot button handling, or menu display actions. | Confirm normal menu entry and navigation still work. |
| 3. Mini-screen/OLED behavior | No, if display code and assets stay unchanged | `config/glyph/common/src/config.cpp`, `HAL/pico/src/display/*`, `HAL/pico/include/display/*`, display assets | Do not alter display initialization, display modes, splash/update assets, or OLED pins. | Confirm splash, menu, and expected display views appear. |
| 4. Profile/config persistence | No, if persistence/config/defaults stay unchanged | `HAL/pico/src/core/Persistence.cpp`, `HAL/pico/include/core/Persistence.hpp`, `HAL/pico/include/config_defaults.hpp`, protobuf config dependency | Use Update-style app-only UF2 for first custom artifact; avoid Clean-style high-flash wipe segment unless wipe is intended. | Confirm existing profiles persist after an Update-style flash. |
| 5. Official update/BOOTSEL entry path | No, if bootloader-entry code and hardware path stay unchanged | `config/glyph/common/src/config.cpp`, `HAL/pico/src/reboot.cpp`, `HAL/pico/src/display/DefaultConfigMenu.cpp`, hardware BOOTSEL wiring if present | Preserve early `inputs.mb1` path and `Manual FW.Update` action; separately verify physical fallback. | Confirm Menu-hold or manual update path still reaches `RPI-RP2`. |
| 6. Configurator communication | No, if Configurator backend and config validation stay unchanged | `HAL/pico/src/comms/ConfiguratorBackend.cpp`, `HAL/pico/include/comms/ConfiguratorBackend.hpp`, protobuf config schema | Do not alter packet command handling, device info, config save/load, or reboot commands. | Confirm configurator can connect and read/write config as before. |
| 7. Default game modes | No, if mode selection and default config stay unchanged | `src/core/mode_selection.cpp`, `include/core/mode_selection.hpp`, `HAL/pico/include/config_defaults.hpp`, mode sources | Do not add `GameModeId`, `mode_id`, `activation_binding`, or `default_mode_config` entries for `SenscopePrototype` without approval. | Confirm default modes and activation bindings behave as before. |
| 8. Recovery behavior | No, if bootloader/recovery paths and official UF2 restore files remain available | Official UF2 files, `HAL/pico/src/reboot.cpp`, `config/glyph/common/src/config.cpp`, potential hardware BOOTSEL fallback | Archive official Update and Clean UF2s; verify recovery path before treating custom flash as recoverable. | Confirm official Update restore path works before relying on custom recovery. |

## Source-Backed Preservation Notes

- `platformio.ini` defines a Pico/RP2040-style build surface and `board_build.filesystem_size = 0.5m`.
- `HAL/pico/src/core/Persistence.cpp` stores runtime config through LittleFS as `config.bin`.
- `config/glyph/common/src/config.cpp` checks `inputs.mb1` early and calls `reboot_bootloader()`.
- `HAL/pico/src/reboot.cpp` maps `reboot_bootloader()` to `rp2040.rebootToBootloader()`.
- `HAL/pico/src/display/DefaultConfigMenu.cpp` has a `Manual FW.Update` menu action that calls `reboot_bootloader()`.
- `docs/project/G11T_DEBUG_BUILD_HARDWARE_TEST_CHECKLIST.md` records that checked-in `SenscopePrototype` is compile-visible but default-unreachable.

## Unknowns

- Whether Menu-hold `RPI-RP2` entry in official shipping firmware is hardware-level or firmware-mediated.
- Whether a physical BOOTSEL fallback exists on the Glyph PCB and is accessible to the user.
- Whether custom firmware built from this repo exactly matches the official feature set.
- Whether official release has downstream patches not present in this repo.
- Whether the Clean/Fresh Install high-flash zero segment exactly maps to all profile/config storage.
- Whether a first custom firmware artifact preserves recovery behavior until tested.

## Stop Conditions

Stop and do not flash if any of the following occurs:

- A custom branch touches display, menu, config, persistence, communication, backend, or default mode files unexpectedly.
- Menu-hold update path fails after a custom flash.
- Profiles are wiped unexpectedly.
- Controller enumeration fails.
- Configurator communication fails unexpectedly.
- Generated artifact contains a Clean-style high-flash wipe segment without explicit wipe approval.
- `SenscopePrototype` becomes default-reachable without explicit approval.
- Force Up-B, digital output, or right-stick/C-stick behavior changes without explicit approval.
- Recovery path is not verified or risk-accepted before custom hardware use.
