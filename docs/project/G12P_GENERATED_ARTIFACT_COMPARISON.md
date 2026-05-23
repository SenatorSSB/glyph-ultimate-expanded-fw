# G12p Generated Artifact Comparison

Status: read-only local build/artifact inspection. No upload, flash, device copy, source edit, commit, or push was performed as part of the build inspection.

## Purpose

Determine whether the current branch can generate a `glyph_mk6` firmware UF2 and whether that generated UF2 is structurally Update-style app-only when compared to the official Glyph 1.0.7 Update and Clean/Fresh Install UF2 files.

This document is not flash approval.

## Commands

```bash
git branch --show-current
git status --short
git diff --stat
test -x ./scripts/pio-local.sh
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
ls -lh .pio/build/glyph_mk6/firmware.uf2 .pio/build/glyph_mk6/firmware.bin .pio/build/glyph_mk6/firmware.elf
file .pio/build/glyph_mk6/firmware.uf2 .pio/build/glyph_mk6/firmware.bin .pio/build/glyph_mk6/firmware.elf
shasum -a 256 .pio/build/glyph_mk6/firmware.uf2 .pio/build/glyph_mk6/firmware.bin .pio/build/glyph_mk6/firmware.elf
```

## Build Result

`./scripts/build-glyph-mk6-quiet.sh`: passed.

Wrapper-reported summary:

| Metric | Value |
| --- | --- |
| RAM | 19.8% / 51,928 bytes of 262,144 |
| Flash | 24.2% / 379,832 bytes of 1,568,768 |
| Duration | 18.32 seconds |
| Log path | `/var/folders/_f/25t1m0794kb7ms1vx8tdwgr00000gp/T/glyph_mk6_build.log` |

The build log records:

```text
Generating UF2 image
picotool uf2 convert -t elf ".pio/build/glyph_mk6/firmware.elf" ".pio/build/glyph_mk6/firmware.uf2"
Flash size: 2.00MB
Sketch size: 1.50MB
Filesystem size: 0.50MB
Maximium Sketch size: 1568768 EEPROM start: 0x101ff000 Filesystem start: 0x1017f000 Filesystem end: 0x101ff000
```

## Generated Artifacts

| Artifact | Size bytes | SHA-256 | File type |
| --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | 783,872 | `864e4cb088d4eaefcf5ee518c81d60af0951f4c7eb5315d2d667b0d52d7b41fb` | UF2 firmware image, family Raspberry Pi RP2040 |
| `.pio/build/glyph_mk6/firmware.bin` | 391,864 | `0e010cd2858c20d93fb4e2831332792a47380734f56ad2e4e4544ef030df3128` | Raw data |
| `.pio/build/glyph_mk6/firmware.elf` | 5,405,012 | `858a34ebdc43513021e9bb15ce5f36abb21987fa12d11690f150baa84c80d62a` | ELF 32-bit ARM, debug info, not stripped |

## Generated UF2 Structure

| Field | Value |
| --- | --- |
| Size bytes | 783,872 |
| Blocks | 1,531 |
| Flags | `0x00002000` |
| Family ID | `0xe48bff56` |
| Target range | `0x10000000..0x1005fb00` |
| Payload bytes | 391,936 |
| Payload SHA-256 | `082a13364c9bfe5056e814c159249ed0193d3a2f7c4a13bc4458226e2110b75f` |
| All zero | No |
| High-flash Clean segment present | No |

## Comparison To Official UF2s

| Artifact | Target ranges | Payload bytes | Notes |
| --- | --- | ---: | --- |
| Official Update | `0x10000000..0x1005df00` | 384,768 | App-only official Update |
| Official Clean | `0x10000000..0x1005df00`, `0x1017f000..0x101ff000` | 909,056 | Same app plus all-zero filesystem-sized segment |
| Generated current-branch UF2 | `0x10000000..0x1005fb00` | 391,936 | App-only; no Clean high-flash segment |

Delta from official Update:

- Generated UF2 has 28 more 256-byte payload blocks.
- Generated app payload is 7,168 bytes larger.
- Generated app range ends at `0x1005fb00`, while official Update ends at `0x1005df00`.
- Generated end remains far below filesystem start `0x1017f000`.

## Safety Assessment

The generated `firmware.uf2` is structurally comparable to an Update-style app-only UF2:

- same RP2040 family ID as official Update/Clean;
- one contiguous app segment;
- no Clean-only high-flash zero segment;
- no write into `0x1017f000..0x101ff000`;
- no write at or beyond `0x101ff000`.

This is not a flash-ready claim. Recovery path, rollback behavior, updater acceptance, and hardware behavior were not tested.

## Implications

- The repo can currently produce a plausible app-only UF2 candidate.
- The range delta versus official Update should be documented for review before any hardware action.
- The current branch contains docs/prototype work after official `1.0.7`; the generated payload hash is expected to differ.
- First custom-firmware hardware testing remains blocked until recovery and rollback gates are satisfied.

## Stop Conditions

Do not flash if:

- generated artifact is not parsed read-only;
- generated UF2 writes into `0x1017f000..0x101ff000`;
- generated UF2 writes at or beyond `0x101ff000`;
- branch diff includes unapproved source/header/config/protobuf/default activation changes;
- recovery path is not verified or risk-accepted;
- hardware action has not been explicitly approved.
