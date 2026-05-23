# G12g Official UF2 Source Capture

Status: docs/source capture only. This document does not flash hardware, add an updater, copy files to a device, or authorize custom firmware flashing.

## Purpose

Capture user-provided official Glyph 1.0.7 UF2 firmware files and user-provided official update procedure text, then separate source-backed observations from inferences and unknowns for future firmware-delivery planning.

## Preserved User-Provided Official Update Text

The following text was supplied by the user as official update procedure text. It is preserved verbatim as user-provided source text, not independently repo-verified official documentation:

> “Download the latest Firmware below, there are two options.
> - Update: Keep all controller profiles as is.
> - Fresh Install: Wipes all profiles and restores the factory default profiles.
> Connect your Glyph to a computer while holding the illuminated Menu button.
> The Glyph will enter programming mode, and appear as a USB drive named RPI-RP2.
> Drag and drop the downloaded .uf2 firmware file onto the RPI-RP2 drive.
> The USB drive will disconnect, closing the window and the Glyph will connect to the computer as a controller.”

## Evidence Classification

| Evidence class | Status in this branch | Notes |
| --- | --- | --- |
| USER_PROVIDED_OFFICIAL_WEBPAGE_TEXT | Captured | The quoted procedure above was supplied by the user and labeled as official update procedure text. |
| UPLOADED_OFFICIAL_UF2_FILES | Captured and inspected read-only | `GlyphFirmware-1.0.7.uf2` and `GlyphFirmware-1.0.7-Clean.uf2` are stored under `docs/sources/raw/glyph_firmware_uf2/1.0.7/`. |
| REPO_BUILD_CONFIGURATION | Inspected | `platformio.ini` uses `board = pico`, Earle Philhower Arduino Pico core, TinyUSB, and `board_build.filesystem_size = 0.5m`; `config/glyph/env.ini` defines `glyph_mk6`. |
| REPO_BOOTLOADER_ENTRY_SOURCE | Inspected | In this repo, `config/glyph/common/src/config.cpp` checks `inputs.mb1` early in `setup()` and calls `reboot_bootloader()`; `HAL/pico/src/reboot.cpp` maps that to `rp2040.rebootToBootloader()`. The display menu also has a `Manual FW.Update` action that calls `reboot_bootloader()`. |
| INFERRED_RP2040_BOOTSEL_BEHAVIOR | Inferred | The user-provided procedure says the device appears as `RPI-RP2`, and the repo is configured for Pico/RP2040-family build surfaces. This strongly suggests RP2040 UF2 bootloader behavior. |
| UNKNOWN | Preserved | Official release-binary equivalence, physical fallback, exact profile/config storage layout, and custom firmware safety remain unknown until separately verified. |

## Observed User-Facing Process

Based on the user-provided official update text:

1. Hold the illuminated Menu button while connecting Glyph to a computer.
2. Glyph enters programming mode.
3. The computer sees a USB drive named `RPI-RP2`.
4. The user drags and drops a `.uf2` firmware file onto the `RPI-RP2` drive.
5. The USB drive disconnects.
6. Glyph reconnects to the computer as a controller.

## Likely Model

`RPI-RP2` strongly indicates an RP2040-family UF2 programming mode. The inspected repo also uses Pico/RP2040 build configuration, and repo source contains a firmware-mediated path that calls `rp2040.rebootToBootloader()`.

This is a likely model, not a complete custom flashing approval. The UF2 files prove the official artifacts are UF2 images. The user-provided official text proves, as user-provided evidence, the intended user-facing process. The repo source proves this source tree includes bootloader-entry code paths. None of those facts alone proves a generated custom artifact is safe to flash.

## Confirmed By User-Provided Webpage Text

- There are two user-facing firmware options: Update and Fresh Install.
- Update keeps controller profiles as-is.
- Fresh Install wipes profiles and restores factory default profiles.
- The user-facing programming drive is named `RPI-RP2`.
- The user-facing process uses drag-and-drop `.uf2` firmware files.
- The drive disconnects and Glyph reconnects as a controller after the file copy.

## Confirmed By UF2 File Inspection

- Both stored files have valid UF2 magic.
- Both files use family ID `0xe48bff56`.
- `GlyphFirmware-1.0.7.uf2` contains one app segment at `0x10000000..0x1005df00`.
- `GlyphFirmware-1.0.7-Clean.uf2` contains the same app segment plus an additional all-zero segment at `0x1017f000..0x101ff000`.
- The app segment payload is byte-identical between the two files.

## Confirmed By Repo Source

- `platformio.ini` configures the Pico/RP2040-style build surface with `board = pico`.
- `platformio.ini` declares `board_build.filesystem_size = 0.5m`.
- `config/glyph/env.ini` defines the `glyph_mk6` environment through `glyph_base`.
- `config/glyph/common/src/config.cpp` contains an early `inputs.mb1` bootloader-entry path.
- `HAL/pico/src/reboot.cpp` implements `reboot_bootloader()` as `rp2040.rebootToBootloader()`.
- `HAL/pico/src/display/DefaultConfigMenu.cpp` contains a `Manual FW.Update` menu action that calls `reboot_bootloader()`.

## Inferred From RP2040 Conventions

- `RPI-RP2` is consistent with RP2040 UF2 bootloader presentation.
- The UF2 family ID and target addresses are consistent with RP2040-style flash programming artifacts.
- The Clean-only high-flash zero segment likely clears a profile/config filesystem region.

These are inferences unless tied to explicit official Glyph documentation, exact release-source provenance, or hardware observation.

## Unknowns

- Whether the official shipping Menu-hold `RPI-RP2` path directly triggers hardware BOOTSEL or uses firmware-mediated reboot behavior.
- Whether custom firmware can preserve the same Menu entry path if the official path is firmware-mediated.
- Whether a physical BOOTSEL fallback exists on the Glyph PCB.
- Whether the official release binary was built exactly from this repo state or has downstream patches not present here.
- Whether profile/config storage layout exactly matches the Clean UF2 high-flash zero segment.
- Whether first custom firmware can be treated as recoverable without a separately verified rollback path.

## Boundaries

- No firmware source, header, config, protobuf, or default activation files are changed by this source-capture branch.
- No runtime or default reachability behavior is changed.
- No upload or flashing workflow is added.
- No hardware flashing is performed.
- No custom firmware is declared safe to flash.
