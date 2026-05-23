# G12o Official Firmware Payload String Audit

Status: read-only visible-string/metadata inspection. No disassembly, private-format reverse engineering, flashing, or device observation was performed.

## Purpose

Inspect visible strings in the official Glyph 1.0.7 UF2 app payload to improve provenance understanding before later custom-firmware testing. String matches can strengthen lineage evidence, but they do not prove full source equivalence.

## Artifacts

| File | Role | UF2 size | Blocks | Ranges | SHA-256 |
| --- | --- | ---: | ---: | --- | --- |
| `GlyphFirmware-1.0.7.uf2` | Update | 769,536 | 1,503 | `0x10000000..0x1005df00` | `2fe38be67b68b9f8b9cb8be2f338837785e63a3732e0c1c269380f6c48f70c6d` |
| `GlyphFirmware-1.0.7-Clean.uf2` | Clean / Fresh Install | 1,818,112 | 3,551 | `0x10000000..0x1005df00`, `0x1017f000..0x101ff000` | `22fd7f8f29fb33d9cb601187e9503411e5330e72c7297fbce0df710eec8ff200` |

Exact metadata:

- Payload size per UF2 block: 256 bytes.
- UF2 flags: `0x2000`.
- Family ID: `0xe48bff56`.
- Shared app payload SHA-256: `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8`.
- Clean-only high segment is all zero, 524,288 bytes.

## Notable Extracted Strings

Offsets are app-payload offsets from the extracted shared app payload, not source line numbers.

| Offset | Visible string | Repo/source comparison |
| ---: | --- | --- |
| `0x0510d8`, `0x055100` | `HayBox` | Matches `platformio.ini` project name and compiled `FIRMWARE_NAME`. |
| `0x0510f2`, `0x055114` | `9a78c7e` | Matches commit `9a78c7eeec87527b68644573e4c29fbdfb543239`, tagged `1.0.7` in this clone. |
| `0x051111`, `0x055128` | `glyph_mk6` | Matches default env / `DEVICE_NAME="${PIOENV}"`. |
| `0x0511c8` | `HORI CO.,LTD.` | Matches Nintendo Switch backend manufacturer descriptor. |
| `0x0511d8` | `POKKEN CONTROLLER` | Matches Nintendo Switch backend product descriptor. |
| `0x0512a0` | `config.bin` | Matches LittleFS persistence filename. |
| `0x050dfc` | `Failed to encode device info` | Matches configurator backend error string. |
| `0x050e1c` | `Config file is invalid` | Matches configurator backend error string. |
| `0x050e34` | `Failed to decode config: %s` | Matches configurator backend error string. |
| `0x051030` | `Unknown command ID: %d` | Matches configurator backend error string. |
| `0x051fb0` | `Configurator Mode` | Matches UI/configurator mode string family. |
| `0x05202c` | `DInput` | Matches backend/menu naming. |
| `0x052034` | `XInput` | Matches backend/menu naming. |
| `0x05203c` | `GameCube` | Matches backend/menu naming. |
| `0x052058` | `Switch` | Matches backend/menu naming. |
| `0x052060` | `Configurator` | Matches backend/menu naming. |
| `0x0550ec` | `Firmware: Glyph ` | Matches About menu source family. |
| `0x055108` | `Version: ` | Matches About menu source family. |
| `0x05511c` | `Device: ` | Matches About menu source family. |

Source files compared:

- `platformio.ini`
- `builder_scripts/arduino_pico.py`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/src/comms/NintendoSwitchBackend.cpp`
- `config/glyph/common/src/display/AboutMenu.cpp`
- `HAL/pico/include/core/Persistence.hpp`

## Provenance Findings

| Claim | Classification | Evidence |
| --- | --- | --- |
| Update and Clean contain the same app payload | Exact | App payload hashes match |
| App payload visibly embeds `HayBox`, `glyph_mk6`, and `9a78c7e` | Exact | ASCII extraction from shared app payload |
| `9a78c7e` resolves to tag `1.0.7` in this clone | Exact for this checkout | `git show -s 9a78c7e` |
| Visible configurator error strings match current repo source | Exact string match | Source string comparison |
| Official app was likely built from or near commit `9a78c7e` | Inferred | Embedded version string matches builder-script pattern |
| Current branch is fully source-equivalent to official app | Unknown | String matches do not prove full binary/source equivalence |

## Implications For Custom Firmware Testing

- Candidate custom UF2 docs should record embedded commit/version string, branch, dirty status, app range, UF2 flags, family ID, and payload hash.
- A custom build should not be described as equivalent to official `1.0.7` unless built from the exact reviewed source state and compared beyond visible strings.
- Official Update and Clean app payloads being identical strengthens the conclusion that Fresh/Clean behavior is caused by the extra high-flash zero segment, but the profile/config meaning remains inferred without hardware or official storage-map proof.
- Visible string matches improve release-lineage confidence, not hardware safety.

## Limitations

- No disassembly was performed.
- No hardware enumeration was observed.
- No private or encrypted format was reverse-engineered.
- String equality does not prove complete source equivalence.
- Official shipping build provenance remains unknown beyond the embedded `9a78c7e` clue and public release label.

## Follow-Up

For a future candidate custom firmware artifact, repeat this audit and compare:

- `FIRMWARE_VERSION`;
- `DEVICE_NAME`;
- app target range;
- app payload hash;
- visible bootloader/update/config strings;
- whether the artifact remains app-only.
