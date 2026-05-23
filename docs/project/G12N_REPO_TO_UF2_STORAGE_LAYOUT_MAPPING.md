# G12n Repo-To-UF2 Storage Layout Mapping

Status: docs-only layout audit. No upload, flash, hardware readback, or runtime behavior change is included.

## Purpose

Map the official Clean/Fresh Install UF2 high-flash zero segment to the repo and local PlatformIO/Earle Philhower Pico flash layout so future custom-firmware work can avoid unintended profile/config wipes.

## Key Conclusion

The official Clean/Fresh Install UF2 segment:

```text
0x1017f000..0x101ff000
```

matches the locally generated `glyph_mk6` LittleFS filesystem region exactly.

Confidence:

- High for local repo/generated layout match.
- Medium-high that the segment is profile/config storage.
- Not exact proof that official shipping firmware uses every same layout detail.

## Source-Backed Build Configuration

`platformio.ini`:

- `board = pico`
- `board_build.core = earlephilhower`
- `board_build.filesystem_size = 0.5m`

`config/glyph/env.ini`:

- `[env:glyph_mk6]` extends `glyph_base`.
- `glyph_base` extends the Pico-style base environment.

## Generated Linker Layout

Generated file: `.pio/build/glyph_mk6/memmap_default.ld`

Important values:

```text
FLASH ORIGIN = 0x10000000
FLASH LENGTH = 1568768 = 0x17f000

_FS_start     = 270004224 = 0x1017f000
_FS_end       = 270528512 = 0x101ff000
_EEPROM_start = 270528512 = 0x101ff000
```

Derived local layout:

| Region | Range | Size | Status |
| --- | --- | ---: | --- |
| App/sketch flash window | `0x10000000..0x1017f000` | 1,568,768 | Source-backed by generated linker map |
| LittleFS filesystem | `0x1017f000..0x101ff000` | 524,288 | Source-backed by generated linker map |
| EEPROM-emulation reserve | `0x101ff000..0x10200000` | 4,096 | Source-backed by builder formula / generated `_EEPROM_start`; exact use not audited here |

## PlatformIO/Earle Formula

Local PlatformIO Raspberry Pi builder computes:

```text
flash_size = board upload.maximum_size
filesystem_size = board build.filesystem_size
eeprom_size = 4096

maximum_sketch_size = flash_size - eeprom_size - filesystem_size
eeprom_start = 0x10000000 + flash_size - eeprom_size
fs_start = 0x10000000 + flash_size - eeprom_size - filesystem_size
fs_end = 0x10000000 + flash_size - eeprom_size
```

Local board config:

- `upload.maximum_size = 2097152`
- Pico board header defines `PICO_FLASH_SIZE_BYTES (2 * 1024 * 1024)`.

Exact calculation:

```text
flash end = 0x10000000 + 0x200000 = 0x10200000
EEPROM start = 0x10200000 - 0x1000 = 0x101ff000
filesystem end = 0x101ff000
filesystem start = 0x101ff000 - 0x80000 = 0x1017f000
sketch/app max end = 0x1017f000
```

## Persistence Source

Runtime persistence is LittleFS-backed:

- `HAL/pico/src/core/Persistence.cpp` calls `LittleFS.begin()`.
- Config is saved and loaded through a file.
- `HAL/pico/include/core/Persistence.hpp` names the persistence file `config.bin`.
- Saved config has a header with size and CRC, followed by protobuf payload.
- `config/glyph/common/src/config.cpp` attempts to load config at boot and saves defaults if loading fails.

Relevant boot behavior:

```text
if (!persistence.LoadConfig(config)) {
    persistence.SaveConfig(config);
}
```

Interpretation: if the filesystem region is zeroed and `LoadConfig` fails, the checked-in repo code falls back to saving default config. That supports, but does not alone prove, the official Fresh Install behavior.

## Official UF2 Segment Match

| UF2 | Segment | Range | Payload bytes | Meaning |
| --- | --- | --- | ---: | --- |
| Update | App | `0x10000000..0x1005df00` | 384,768 | App-only official update artifact |
| Clean | App | `0x10000000..0x1005df00` | 384,768 | Same app payload as Update |
| Clean | Zero segment | `0x1017f000..0x101ff000` | 524,288 | Exact match to local LittleFS region |

## Claims And Confidence

| Claim | Confidence | Basis |
| --- | --- | --- |
| Clean UF2 extra segment is all-zero `0x1017f000..0x101ff000` | Exact | Direct UF2 parsing |
| Local generated LittleFS region is `0x1017f000..0x101ff000` | Exact for local generated files | `.pio/build/glyph_mk6/memmap_default.ld` |
| `board_build.filesystem_size = 0.5m` drives that region | High | PlatformIO config plus builder formula |
| Repo runtime config uses LittleFS `config.bin` | Source-backed | `Persistence.cpp` / `Persistence.hpp` |
| Clean UF2 wipes profile/config storage | Medium-high inference | Exact range match plus official Fresh Install behavior plus persistence source |
| Official shipping firmware uses exactly this repo layout | Unknown | No official build provenance or hardware flash dump |
| Clean segment covers every user-facing profile datum | Unknown | No full hardware storage inventory |

## Risks For Custom Firmware

- A Clean-style custom UF2 would overwrite the configured LittleFS region and likely wipe profiles/config.
- An app-only UF2 that remains below `0x1017f000` is more likely to preserve config, but still requires read-only artifact inspection.
- Future custom app growth may extend beyond official Update’s `0x1005df00`; that is acceptable only while it remains below the filesystem start and passes range review.
- Zeroing LittleFS is not the same as shipping a factory filesystem image; default restoration appears likely to be runtime fallback.
- Any generated artifact writing at or beyond `0x101ff000` carries additional EEPROM-reserve risk.

## Future Checks

- Parse every generated custom UF2 before any hardware decision.
- Reject any first custom artifact that writes `0x1017f000..0x101ff000`.
- Record build log layout lines for every candidate artifact.
- If later explicitly authorized, use hardware readback to confirm LittleFS contents and `config.bin` placement.
- Treat official/source equivalence as unknown until release provenance is reviewed.
