# G12m Official Source Corroboration

Status: docs-only source corroboration. This document records official web/manual/RP2040 references. It does not authorize flashing or copy-to-device workflows.

Access date for web sources: 2026-05-23.

## Purpose

Upgrade the previous user-provided-only update-procedure evidence by recording independently sourced official Glyph and Raspberry Pi references. This helps future custom-firmware testing distinguish:

- official Glyph user-facing update behavior;
- official RP2040 UF2/BOOTSEL behavior;
- repo-source bootloader entry paths;
- remaining unknowns.

## Official Glyph Evidence

### Limit Labs Glyph Resources

Source: <https://limitlabs.com/pages/glyph-resources>

Supported claims:

- The page is the official Glyph resources page for firmware, configuration, profiles, and docs.
- Firmware installation has two user-facing options: Update and Fresh Install.
- Update keeps profiles.
- Fresh Install wipes/restores default profiles.
- The user-facing procedure says to connect while holding the illuminated Menu button.
- The programming volume appears as `RPI-RP2`.
- The firmware file is a `.uf2`.
- The page lists `v1.0.7 (9a78c7e)` for Glyph Firmware Update and Clean Install, release date April 19, 2026.

Short source snippets:

- “USB drive named RPI-RP2”
- “downloaded .uf2 firmware file”
- “v1.0.7 (9a78c7e)”

Classification: official Glyph webpage evidence.

### Glyph Manual v1.0

Source: <https://cdn.shopify.com/s/files/1/0926/5597/6818/files/Glyph_Manual_v1.0.pdf?v=1775239160>

Supported claims:

- Manual version is v1.0, April 2026.
- Manual firmware update flow describes a Manual FW Update mode.
- The controller appears as USB storage during update mode.
- A `.UF2` firmware file is used.
- The manual describes an alternative using the illuminated Menu button while connecting.
- The manual also describes a physical BOOTSEL button under the top plate/artwork sheet.
- The About menu can be used to verify the firmware version after update.

Short source snippets:

- “Press the BOOTSEL button”
- “confirm the update was successful”

Classification: official Glyph manual evidence.

## Official RP2040 Evidence

### Raspberry Pi Pico-Series Documentation

Source: <https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html>

Supported claims:

- RP2040/Pico BOOTSEL mode exposes a USB mass-storage volume named `RPI-RP2`.
- Copying a UF2 file to the mounted volume causes automatic eject and reboot.
- BOOTSEL mode resides in read-only memory and cannot be rewritten.
- Raspberry Pi presents this as protection against ordinary software bricking where BOOTSEL remains accessible.

Short source snippets:

- “USB mass storage device named RPI-RP2”
- “volume automatically ejects”
- “BOOTSEL mode resides in read-only memory”

Classification: official Raspberry Pi behavior.

### RP2040 Datasheet

Source: <https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf>

Supported claims:

- RP2040 Bootrom provides USB mass-storage bootloader behavior.
- RP2040 appears as a FAT16 drive named `RPI-RP2`.
- UF2 contents are recognized and written to RAM or Flash.
- A complete valid UF2 transfer causes automatic reboot.
- Invalid UF2 files may fail without obvious host notification or may partially write.
- Required RP2040 UF2 family ID is `0xe48bff56`.
- RP2040 flash UF2 target range is `0x10000000..0x11000000`.

Short source snippets:

- “standard USB bootloader”
- “drive named RPI-RP2”
- “Invalid UF2 files may not write”

Classification: official RP2040 behavior.

## Repo Source Corroboration

| Source | Relevant local fact |
| --- | --- |
| `platformio.ini` | Pico/RP2040-style build surface, Earle Philhower core, TinyUSB, `board_build.filesystem_size = 0.5m`. |
| `config/glyph/common/src/config.cpp` | Early `inputs.mb1` path shows update splash and calls `reboot_bootloader()`. |
| `HAL/pico/src/reboot.cpp` | `reboot_bootloader()` maps to `rp2040.rebootToBootloader()`. |
| `HAL/pico/src/display/DefaultConfigMenu.cpp` | `Manual FW.Update` menu action calls `reboot_bootloader()`. |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp` | Configurator command path can call `reboot_bootloader()`. |

## Evidence Classification Update

| Claim | Previous status | Updated status |
| --- | --- | --- |
| Official process uses `.uf2` files | USER_PROVIDED | Official Limit Labs corroborated |
| Update keeps profiles | USER_PROVIDED | Official Limit Labs corroborated |
| Fresh Install wipes/restores defaults | USER_PROVIDED | Official Limit Labs corroborated |
| Menu-hold while connecting enters programming mode | USER_PROVIDED | Official Limit Labs and manual corroborated |
| Programming volume is `RPI-RP2` | USER_PROVIDED | Official Limit Labs plus official RP2040 docs corroborated |
| Physical BOOTSEL fallback exists on Glyph | UNKNOWN | Official manual indicates a physical BOOTSEL button; safe accessibility still requires human review |
| Generated custom UF2 is safe to flash | UNKNOWN | Still unknown / not approved |

## Remaining Unknowns

- Whether the Menu-hold path in official firmware is hardware-wired BOOTSEL, firmware-mediated reboot, or both.
- Whether the repo `inputs.mb1` path is exactly the same physical illuminated Menu button described by official docs.
- Whether custom firmware preserves Menu-hold and Manual FW Update paths until tested.
- Whether official release `v1.0.7 (9a78c7e)` was built exactly from this repo state.
- Whether Glyph validates firmware identity beyond RP2040 UF2 structure.
- Whether the Clean high-flash segment covers all and only profile/config storage.

## Safety Implications

- RP2040 BOOTSEL evidence improves recovery confidence only if a BOOTSEL entry path remains accessible.
- The manual’s physical BOOTSEL mention is important, but future human review should confirm the exact Glyph hardware procedure before relying on it.
- The RP2040 datasheet warning about invalid UF2 writes means generated custom UF2 files must be parsed before any human device write.
- Official Glyph source corroboration does not make custom firmware flash-ready.
