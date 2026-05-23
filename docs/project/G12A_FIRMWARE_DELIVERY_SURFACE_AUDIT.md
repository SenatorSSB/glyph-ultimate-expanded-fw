# G12a Firmware Delivery Surface Audit

Status: docs-only audit. This document does not implement flashing, upload, push-to-device, updater, runtime reachability, or hardware workflow changes.

## Scope

This audit inventories build/deployment-relevant surfaces that future human reviewers must understand before any custom firmware delivery test on Glyph hardware. It separates source-backed facts from inferred relationships and unknowns.

Evidence basis inspected for this batch:

- `README.md`
- `platformio.ini`
- `config/glyph/env.ini`
- `scripts/pio-local.sh`
- `scripts/build-glyph-mk6-quiet.sh`
- `builder_scripts/arduino_pico.py`
- `HAL/pico/src/comms/*`
- `HAL/pico/src/core/*`
- `HAL/pico/include/*`
- `docs/project/G11T_DEBUG_BUILD_HARDWARE_TEST_CHECKLIST.md`
- `docs/project/G11V_RUNTIME_EXPANSION_READINESS_GATE.md`
- `docs/project/G8F_J_LONG_SEQUENCE_ROLLUP.md`

## Delivery Surface Categories

| Category | Status | Notes |
| --- | --- | --- |
| Build artifact production | SOURCE_BACKED | `platformio.ini` sets `default_envs = glyph_mk6`; `config/glyph/env.ini` defines `[env:glyph_mk6]`; `scripts/build-glyph-mk6-quiet.sh` runs `./scripts/pio-local.sh run -e glyph_mk6`. |
| Firmware upload/flashing | SOURCE_BACKED/UNKNOWN | `config/glyph/env.ini` sets `upload_protocol = cmsis-dap` in `[glyph_base]`, inherited by `glyph_mk6`. This is a PlatformIO upload setting, not an approval to upload. Actual safe flashing path for custom artifacts remains UNKNOWN. |
| Runtime configurator communication | SOURCE_BACKED | `HAL/pico/src/comms/ConfiguratorBackend.cpp` implements config/device-info commands over a stream using PacketIO COBS and protobuf, and can call `reboot_firmware()` or `reboot_bootloader()` for configurator commands. |
| Official connect/update mode | USER_REPORTED/UNKNOWN | User reports official Glyph firmware has a connect mode where a connected PC opens an internal Glyph directory and drag-and-drop firmware update reportedly works. This batch found README links to official Glyph resources/manual, but did not source-verify this behavior in repo source/docs. |
| Hardware bootloader/recovery | SOURCE_BACKED/UNKNOWN | `ConfiguratorBackend.cpp` has a `CMD_REBOOT_BOOTLOADER` path via `reboot_bootloader()`. The physical fallback procedure, expected file format, and recovery guarantees are UNKNOWN from the inspected repo files. |

## PlatformIO And Build Inventory

| Surface | Status | Source-backed observation | Safety interpretation |
| --- | --- | --- | --- |
| `platformio.ini` `[platformio]` | SOURCE_BACKED | `default_envs = glyph_mk6`, `src_dir = ./`, `extra_configs = config/*/env.ini`. | Build entry point is repo-root PlatformIO with extra config files. |
| `platformio.ini` `[env]` | SOURCE_BACKED | Defines common build flags including `DEVICE_NAME="${PIOENV}"` and `FIRMWARE_NAME="${platformio.name}"`; `platformio.name` is `HayBox`. | Device/firmware metadata may be compiled into firmware info responses. |
| `platformio.ini` `[arduino_pico_base]` | SOURCE_BACKED | Uses Raspberry Pi platform URL, Arduino framework, `board = pico`, Earle Philhower core, `board_build.filesystem_size = 0.5m`, TinyUSB flags, Pico HAL include/source paths, and Pico-related dependencies. | The `glyph_mk6` build is based on RP2040/Pico Arduino surfaces. Artifact format must be checked after an actual build, not assumed. |
| `platformio.ini` upload protocol comment | SOURCE_BACKED | `; upload_protocol = cmsis-dap` is commented in `[arduino_pico_base]`. | Base has commented upload hint only; active Glyph setting is in `config/glyph/env.ini`. |
| `config/glyph/env.ini` `[glyph_base]` | SOURCE_BACKED | Extends `arduino_pico_base`, sets `upload_protocol = cmsis-dap`, adds Glyph config include/source paths, and uses Glyph HayBox-proto dependency. | Upload protocol exists as build config, but this batch does not use it and does not validate hardware flashing. |
| `config/glyph/env.ini` `[env:glyph_mk6]` | SOURCE_BACKED | Extends `glyph_base`. | Primary requested build target inherits Pico/Arduino base and CMSIS-DAP upload protocol. |
| `config/glyph/env.ini` `[env:glyph_mk6_Debug]` | SOURCE_BACKED | Extends `glyph_base`, adjusts optimization flags, and points include paths at `config/glyph/glyph_mk6/include`. | Debug env exists but is not the requested build target for this batch. |
| `scripts/pio-local.sh` | SOURCE_BACKED | Sets `PLATFORMIO_CORE_DIR="$PWD/.platformio-home"`, prefers `.venv/bin/python`, then `python`, then `python3`, and executes `python -m platformio`. | Local wrapper is build-tool orchestration only; it does not flash unless invoked with an upload command. |
| `scripts/build-glyph-mk6-quiet.sh` | SOURCE_BACKED | Runs `./scripts/pio-local.sh run -e glyph_mk6`, logs to temp, prints pass/fail summary, and tails final 80 lines on failure. | Safe build wrapper for future artifact inspection. It does not call upload. |
| `builder_scripts/arduino_pico.py` | SOURCE_BACKED | Adds `FIRMWARE_VERSION` from `git rev-parse --short HEAD` and appends `-DIRTY` if `git status --porcelain` appears dirty. | Build metadata can reflect commit/dirty state; artifact provenance should record branch/commit and dirty status. |

## HAL Pico Communication And Persistence Surfaces

| Surface | Status | Source-backed observation | Delivery relevance |
| --- | --- | --- | --- |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | SOURCE_BACKED | Sets USB ID with `TinyUSBDevice.setID(0x2E8A, 0x1092)` and implements `CMD_GET_DEVICE_INFO`, `CMD_GET_CONFIG`, `CMD_SET_CONFIG`, `CMD_REBOOT_FIRMWARE`, and `CMD_REBOOT_BOOTLOADER`. | Runtime configurator communication and reboot commands exist; this is not the same as artifact flashing or official drag-and-drop update compatibility. |
| `HAL/pico/include/comms/ConfiguratorBackend.hpp` | SOURCE_BACKED | Declares PacketIO COBS stream/print members and config handlers. | Indicates packetized runtime config communication, not file-copy firmware delivery. |
| `HAL/pico/src/core/Persistence.cpp` | SOURCE_BACKED | Uses LittleFS; stores `config.bin` with a header containing config size and CRC; loads/saves protobuf `Config`. | Config preservation across firmware update is an important unknown until official update behavior is verified. |
| `HAL/pico/include/core/Persistence.hpp` | SOURCE_BACKED | Declares `config_filename[] = "config.bin"` and config persistence API. | Names the persistence file used by runtime config, but does not prove updater behavior. |
| `HAL/pico/src/comms/backend_init.cpp` | SOURCE_BACKED | Initializes communication backends, chooses backend from button holds/default USB detection/watchdog override, and may save config after watchdog override. | Runtime backend selection can affect how a PC sees the device, but does not define firmware delivery format. |
| `HAL/pico/src/comms/console_detection.cpp` | SOURCE_BACKED | Uses USB connection state to detect backend context. | Relevant to runtime enumeration and backend detection, not artifact flashing by itself. |
| `HAL/pico/include/tusb_config_pico.h` | SOURCE_BACKED | Enables TinyUSB device stack, CDC, MSC, HID, and MIDI; defines MSC endpoint buffer size. | MSC support is present in TinyUSB config, but this audit does not find a source-backed claim that the application exposes an official firmware drag-and-drop updater volume. |
| Other comms backends | SOURCE_BACKED | DInput, XInput, Nintendo Switch, GameCube, N64, NES, SNES, and related backend headers/sources exist. | Relevant to runtime output/host behavior, not direct firmware delivery compatibility. |

## Distinctions To Preserve

### Build Artifact Production

Status: SOURCE_BACKED.

A `glyph_mk6` build can be produced by PlatformIO using the repo wrapper. The inspected build wrapper runs `platformio run -e glyph_mk6` only. It does not upload or flash.

### Firmware Upload Or Flashing

Status: SOURCE_BACKED/UNKNOWN.

`upload_protocol = cmsis-dap` is configured for Glyph environments. That proves a PlatformIO upload protocol setting exists. It does not prove a safe or intended custom firmware delivery path for this batch. No upload command is run or added here.

### Runtime Configurator Communication

Status: SOURCE_BACKED.

The runtime configurator backend exchanges device info/config packets over a stream, can save/load config through LittleFS, and has firmware/bootloader reboot commands. This is runtime communication, not by itself a firmware artifact compatibility guarantee.

### Official Connect/Update Mode

Status: USER_REPORTED/UNKNOWN.

The user reports official Glyph firmware has a connect mode that opens an internal directory on the connected PC and supports drag-and-drop firmware updates. This audit records that as user-provided context only. Repo source/docs inspected in this batch do not source-verify the complete official behavior, expected file format, validation model, or rollback behavior.

### Hardware Bootloader/Recovery

Status: SOURCE_BACKED/UNKNOWN.

A bootloader reboot command path exists in the configurator backend. The physical bootloader fallback, user-facing recovery sequence, accepted artifact formats, and official restoration workflow remain unknown until verified against official docs or hardware/user evidence.

## Unknowns

- UNKNOWN: Exact artifact path and extension emitted by a successful local `glyph_mk6` build in the current environment.
- UNKNOWN: Whether the produced artifact is UF2, BIN, ELF, HEX, or another format until build output is inspected.
- UNKNOWN: Whether any produced custom artifact is appropriate for the user-reported drag-and-drop updater path.
- UNKNOWN: Whether official connect mode is RP2040 UF2 mass storage bootloader behavior or a vendor-level updater/storage behavior.
- UNKNOWN: Whether official connect mode validates firmware metadata, board ID, signature, checksum, or file layout.
- UNKNOWN: Whether official firmware update preserves `config.bin`/LittleFS configuration.
- UNKNOWN: Whether incompatible/corrupt firmware files are rejected safely.
- UNKNOWN: Whether official firmware can be restored through the same path.
- UNKNOWN: Physical bootloader fallback sequence and its effect on config persistence.

## Stop Conditions

Stop before any future hardware action if:

- artifact format is unknown;
- artifact compatibility with the intended delivery path is unknown;
- official rollback path is not verified;
- official firmware file is unavailable;
- source/config/protobuf/default runtime reachability changes appear unexpectedly;
- a future step requires deciding a vendor export/update format without source or official evidence;
- a future step would require copying artifacts to a mounted device from an agent-run command;
- a future step would require flashing hardware without explicit user approval.
