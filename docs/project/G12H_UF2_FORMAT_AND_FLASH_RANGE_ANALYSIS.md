# G12h UF2 Format And Flash Range Analysis

Status: read-only file analysis. No flashing was performed, no device path was written, and no updater workflow was added.

## Inputs

| File | Source status | Role |
| --- | --- | --- |
| `docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7.uf2` | USER_PROVIDED_OFFICIAL_FIRMWARE | Update |
| `docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2` | USER_PROVIDED_OFFICIAL_FIRMWARE | Clean / Fresh Install |

## Exact File Metadata

| Field | Update UF2 | Clean UF2 |
| --- | --- | --- |
| Filename | `GlyphFirmware-1.0.7.uf2` | `GlyphFirmware-1.0.7-Clean.uf2` |
| Size bytes | 769,536 | 1,818,112 |
| Whole-file SHA-256 | `2fe38be67b68b9f8b9cb8be2f338837785e63a3732e0c1c269380f6c48f70c6d` | `22fd7f8f29fb33d9cb601187e9503411e5330e72c7297fbce0df710eec8ff200` |
| UF2 magic validity | Valid | Valid |
| UF2 block count | 1,503 | 3,551 |
| Declared block count values | 1,503 | 3,551 |
| Family ID(s) | `0xe48bff56` | `0xe48bff56` |
| Total payload bytes | 384,768 | 909,056 |

## Segment Comparison

| Segment | Update UF2 | Clean UF2 | Payload bytes | SHA-256 | All zero bytes |
| --- | --- | --- | --- | --- | --- |
| Shared app segment | `0x10000000..0x1005df00` | `0x10000000..0x1005df00` | 384,768 | `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8` | No |
| Extra Clean segment | Not present | `0x1017f000..0x101ff000` | 524,288 | `07854d2fef297a06ba81685e660c332de36d5d18d546927d30daad6d7fda1541` | Yes |

## Findings

- Both files are valid UF2 images by magic values and block structure.
- Both files use family ID `0xe48bff56`.
- The Update file contains only the app segment at `0x10000000..0x1005df00`.
- The Clean/Fresh Install file contains the same byte-identical app segment.
- The Clean/Fresh Install file adds a 512 KiB all-zero high-flash segment at `0x1017f000..0x101ff000`.
- The app segment SHA-256 is identical between files: `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8`.

## Interpretation

The user-provided official update text says:

- Update keeps controller profiles as-is.
- Fresh Install wipes all profiles and restores factory default profiles.

The file structure strongly supports the following inference:

- Update is app-only and likely preserves profile/config storage because it writes only the app range.
- Clean/Fresh Install writes the same app payload and additionally zeroes a high-flash region.
- The extra all-zero region is likely the profile/config filesystem or storage region that causes the Fresh Install profile wipe.

Confidence levels:

| Claim | Confidence | Basis |
| --- | --- | --- |
| UF2 magic validity, block counts, family ID, ranges, payload bytes, and hashes | Exact | Direct read-only UF2 parsing of stored files. |
| Update and Clean app segments are byte-identical | Exact | Direct byte comparison of app payloads. |
| Clean contains an additional all-zero high-flash segment | Exact | Direct byte inspection of Clean-only segment. |
| Extra Clean segment maps to profile/config wipe behavior | Strong inference | User-provided Fresh Install text, direct UF2 structure, and repo `board_build.filesystem_size = 0.5m`. |
| Exact profile/config storage layout | Unknown | Not proven by the UF2 files alone. |

## Repo Configuration Context

The inspected repo build configuration includes:

- `platformio.ini`: `board = pico`.
- `platformio.ini`: `board_build.filesystem_size = 0.5m`.
- `config/glyph/env.ini`: `glyph_mk6` extends the Glyph Pico base environment.
- `HAL/pico/src/core/Persistence.cpp`: runtime config is stored through LittleFS as `config.bin` with a CRC-bearing header.

The Clean-only segment is 512 KiB, matching the configured `0.5m` filesystem size. That supports the profile/config wipe interpretation, but it does not by itself prove the exact shipping storage map.

## Risk Note

For first custom firmware testing, the safer target is an Update-style app-only UF2. A Clean/Fresh Install-style artifact that writes the high-flash zero segment should be avoided unless a profile/config wipe is intended and explicitly approved.

Do not rely on filename alone. Any generated custom UF2 must be parsed read-only and checked for target address ranges before any human considers flashing it.

## Stop Conditions Before Flashing

Stop before flashing if any of the following is true:

- The generated artifact format is unknown.
- The generated UF2 cannot be parsed.
- The generated UF2 has an unexpected family ID or non-RP2040-compatible structure.
- The generated UF2 writes outside the expected app range.
- The generated UF2 contains a Clean-style high-flash wipe segment.
- The official Update UF2 and recovery path are not archived and documented.
- The recovery path is untested or the risk is not explicitly accepted.
- Firmware source/header/config/protobuf/default activation files changed unexpectedly.
- Custom mode reachability changed without explicit approval.
- Force Up-B, digital output, right-stick/C-stick, or upload/flashing behavior changed without explicit approval.
- A step would require an agent to copy a file to `RPI-RP2` or any mounted device.
