# G12c Official Connect Mode Investigation Plan

Status: docs-only investigation plan. This document is based partly on user-reported official firmware behavior and does not include flashing instructions.

## User-Reported Context

The user reports the following behavior in current official Glyph firmware:

1. Official firmware has a connect mode.
2. When connected to a PC in that mode, the PC opens a Glyph internal directory.
3. Drag-and-drop firmware update reportedly works through that directory.

Status of this report in this repo audit: USER_REPORTED/UNVERIFIED.

The inspected repo files include runtime configurator and bootloader reboot surfaces, but this batch did not source-verify the full official connect-mode behavior, accepted file format, validation behavior, or recovery behavior.

## Investigation Questions

| Question | Current status | Evidence needed |
| --- | --- | --- |
| Is connect mode RP2040 UF2 mass-storage bootloader behavior or vendor-level updater behavior? | UNKNOWN | Official manual/resources, device observation, or repo source/docs that identify the mechanism. |
| What file format does connect mode expect? | UNKNOWN | Official updater documentation or verified device behavior showing accepted file type. |
| Does connect mode validate firmware? | UNKNOWN | Official documentation, source code, or observed rejection/acceptance behavior. |
| What metadata does it validate, if any? | UNKNOWN | Official docs/source or controlled user-confirmed observation. |
| Does it preserve user config? | UNKNOWN | Official docs/source or before/after user-confirmed observation of persisted config. |
| What happens on incompatible or corrupt files? | UNKNOWN | Official docs/source or a safe vendor-described failure model. Do not test destructively without explicit approval. |
| Is official firmware restorable the same way? | UNKNOWN | Official firmware download path and documented restore process. |
| Is there a physical bootloader fallback? | UNKNOWN | Official manual/resources or source-backed hardware procedure. |
| Does configurator `CMD_REBOOT_BOOTLOADER` enter the same mode? | UNKNOWN | Source-backed call exists, but the resulting user-visible mode and file expectations remain unverified. |

## Evidence Sources To Seek

1. Official Glyph manual/resources linked from `README.md`.
2. Repo source/docs that explicitly describe connect mode or updater behavior.
3. User-confirmed device behavior, recorded as user evidence rather than repo source.
4. Build artifacts from local `glyph_mk6` builds, inspected read-only for format/path/name/size/hash.
5. Official firmware file/download location and any release notes that describe restore/update behavior.

## Source-Backed Repo Clues Already Found

- `README.md` links to Glyph resources and a user manual.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` includes `CMD_REBOOT_FIRMWARE` and `CMD_REBOOT_BOOTLOADER` handling.
- `HAL/pico/include/tusb_config_pico.h` enables TinyUSB MSC at the TinyUSB configuration level.
- `HAL/pico/src/core/Persistence.cpp` stores config in LittleFS `config.bin` with CRC.

These clues are not enough to assert official drag-and-drop update compatibility.

## Non-Instructions

This plan deliberately does not include:

- flashing commands;
- mounted-device write commands;
- drag-and-drop steps;
- PlatformIO upload commands;
- artifact copy instructions;
- updater implementation details;
- assumptions that any custom build output is compatible with official connect mode.

## Stop Conditions

Stop if investigation would require:

- writing to a mounted device;
- flashing custom firmware;
- testing corrupt/incompatible firmware on hardware;
- reverse-engineering private/encrypted update formats;
- claiming official behavior as source-backed without official docs/source or explicit user-confirmed evidence;
- deciding a vendor update/export format without source authority.
