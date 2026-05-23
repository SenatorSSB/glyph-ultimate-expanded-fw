# G12l Deep UF2 Structural Audit

Status: docs-only read-only audit. No flashing, mounted-device writes, upload commands, source/header/config/protobuf edits, or runtime behavior changes are included.

## Purpose

Record a deeper structural audit of the user-provided official Glyph 1.0.7 UF2 files so future custom-firmware work can compare generated artifacts against known-good official Update and Clean/Fresh Install shapes before any human-controlled device test.

## Inputs

| File | Role | Source status |
| --- | --- | --- |
| `docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7.uf2` | Update | USER_PROVIDED_OFFICIAL_FIRMWARE |
| `docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2` | Clean / Fresh Install | USER_PROVIDED_OFFICIAL_FIRMWARE |

## Methodology

Each UF2 file was parsed as 512-byte blocks. The read-only parser checked:

- block magic words;
- flags;
- block number continuity;
- declared block count consistency;
- payload size consistency;
- family ID field values;
- target-address continuity;
- duplicate and missing block numbers;
- target-address gaps and overlaps;
- full-file SHA-256;
- segment payload SHA-256;
- all-zero payload ranges.

No parser script was committed.

## Header Constants

| Field | Exact observed value |
| --- | --- |
| Magic start 0 | `0x0a324655` |
| Magic start 1 | `0x9e5d5157` |
| Magic end | `0x0ab16f30` |
| Flags | `0x00002000` on every block |
| Payload size | `256` bytes on every block |
| Family/file-size field | `0xe48bff56` on every block |

Exact claim: every inspected block has these values.

Interpretation: `0x00002000` is the UF2 family-ID-present flag, and `0xe48bff56` is the RP2040 family ID per the RP2040 datasheet. That is official RP2040-source-backed behavior, not a Glyph-specific source claim.

## File-Level Summary

| File | Size bytes | Physical UF2 blocks | Declared blocks | Whole-file SHA-256 |
| --- | ---: | ---: | ---: | --- |
| `GlyphFirmware-1.0.7.uf2` | 769,536 | 1,503 | 1,503 on every block | `2fe38be67b68b9f8b9cb8be2f338837785e63a3732e0c1c269380f6c48f70c6d` |
| `GlyphFirmware-1.0.7-Clean.uf2` | 1,818,112 | 3,551 | 3,551 on every block | `22fd7f8f29fb33d9cb601187e9503411e5330e72c7297fbce0df710eec8ff200` |

No short or trailing partial UF2 blocks were found.

## Structural Validity

| File | Magic valid | Payload sizes consistent | Declared count consistent | Duplicate blocks | Missing blocks | File-order numbering |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Update | 1,503 / 1,503 | Yes, all 256 | Yes | None | None | Exact `0..1502` |
| Clean | 3,551 / 3,551 | Yes, all 256 | Yes | None | None | Exact `0..3550` |

## Target Address Segments

Ranges are half-open: start inclusive, end exclusive.

| File | Segment | Target range | Payload bytes | Blocks | Payload SHA-256 | All zero |
| --- | --- | --- | ---: | ---: | --- | --- |
| Update | App | `0x10000000..0x1005df00` | 384,768 | 1,503 | `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8` | No |
| Clean | App | `0x10000000..0x1005df00` | 384,768 | 1,503 | `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8` | No |
| Clean | High-flash zero segment | `0x1017f000..0x101ff000` | 524,288 | 2,048 | `07854d2fef297a06ba81685e660c332de36d5d18d546927d30daad6d7fda1541` | Yes |

Exact finding: Update and Clean app payloads are byte-identical. Their app block headers differ only in the declared total block count because the Clean file contains additional blocks.

## Gaps And Overlaps

| File | Gaps | Overlaps |
| --- | --- | --- |
| Update | None inside represented app segment | None |
| Clean | `0x1005df00..0x1017f000`, 1,184,000 bytes | None |

Exact finding: Clean has one large unrepresented address gap between the app segment and the high-flash zero segment.

## Clean End Address

| Observation | Value |
| --- | --- |
| Clean high-flash zero segment start | `0x1017f000` |
| Clean high-flash zero segment end | `0x101ff000` |
| Clean high-flash zero segment size | `0x80000` / 524,288 bytes |
| Last Clean block target address | `0x101fef00` |
| Last Clean block target end | `0x101ff000` |
| Blocks after `0x101ff000` | None |

Interpretation:

- Exact: Clean writes 512 KiB of zero bytes at `0x1017f000..0x101ff000`.
- Inferred: if assuming a 2 MiB Pico-style flash ending at `0x10200000`, Clean leaves `0x101ff000..0x10200000` unwritten.
- Unknown: the UF2 file alone does not explain the final 4 KiB or prove it is reserved storage.

## Risk Notes

- Do not call Clean a full-flash wipe; it writes app plus one high-flash zero segment.
- Do not claim the final 4 KiB meaning from UF2 structure alone.
- Do not assume a generated custom UF2 is safe because official Update is app-only; generated artifacts must be parsed independently.
- Do not claim the Clean zero segment is profile/config storage as exact unless corroborated by layout/source/hardware evidence.

## Verification

| Command | Result |
| --- | --- |
| `shasum -a 256 docs/sources/raw/glyph_firmware_uf2/1.0.7/*.uf2` | matched manifest hashes |
| temporary read-only UF2 parser | passed structural checks above |
| `git status --short` | clean before doc integration |

## Stop Conditions

Stop before any custom firmware flash if:

- generated UF2 has missing, duplicate, or inconsistent block numbers;
- generated UF2 has unexpected family ID or flags;
- generated UF2 writes into `0x1017f000..0x101ff000` without explicit wipe approval;
- generated UF2 writes at or beyond `0x101ff000` without a reviewed storage-layout reason;
- generated artifact range is not read-only parsed and documented.
