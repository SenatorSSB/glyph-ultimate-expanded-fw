# G13f Playtest Build Artifact Inspection

Status: read-only build and artifact inspection for normal and experimental playtest firmware outputs.

No flashing, upload command, copy-to-device command, mounted-device write, or hardware write was performed. This document is not approval to flash. Even `UPDATE_STYLE_APP_ONLY_CANDIDATE` only supports future human review.

## Build Metadata

| Field | Value |
| --- | --- |
| Branch | `docs/g13e-g-playtest-profile-artifact-flash-gate` |
| Base branch for comparison | `configurator` |
| Build source commit | `813b3a353da6ed55a7bfabab0163fa97c0742a58` |
| Initial clean/dirty status | Clean before builds (`git status` reported nothing to commit) |
| Initial diff stat | Empty (`git diff --stat` produced no output) |
| Normal build command | `./scripts/build-glyph-mk6-quiet.sh` |
| Normal build result | Passed; RAM 19.8%; Flash 24.2%; `glyph_mk6 SUCCESS` in 17.07 seconds on required run; repeated pass in 14.95 seconds for normal artifact capture |
| Playtest build command | `./scripts/build-glyph-mk6-senscope-playtest-quiet.sh` |
| Playtest build result | Passed; RAM 19.8%; Flash 24.2%; `glyph_mk6_senscope_playtest SUCCESS` in 15.32 seconds on required run; repeated pass in 15.06 seconds for playtest artifact capture |
| Wrapper checks | `test -x ./scripts/pio-local.sh`, `test -x ./scripts/build-glyph-mk6-quiet.sh`, and `test -x ./scripts/build-glyph-mk6-senscope-playtest-quiet.sh` all passed |

The required `find .pio -maxdepth 6 -type f | sort` command was run after the first normal and playtest builds. In this local build tree, after the playtest build only `.pio/build/glyph_mk6_senscope_playtest` remained present. To capture both env artifacts, normal and playtest builds were then rerun and inspected immediately after each env build. Generated artifacts were not added to Git.

## Read-Only Tooling

Reused existing optional tool:

```text
tools/uf2/inspect_uf2.py
```

The tool reads local UF2 paths, writes nothing, does not touch mounted devices, does not call upload tools, prints stable JSON, and uses Python 3 standard library modules only.

Commands used for UF2 inspection:

```bash
python3 tools/uf2/inspect_uf2.py \
  docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7.uf2 \
  docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2 \
  .pio/build/glyph_mk6/firmware.uf2
```

```bash
python3 tools/uf2/inspect_uf2.py \
  docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7.uf2 \
  docs/sources/raw/glyph_firmware_uf2/1.0.7/GlyphFirmware-1.0.7-Clean.uf2 \
  .pio/build/glyph_mk6_senscope_playtest/firmware.uf2
```

## Artifact Inventory

Candidate firmware artifacts were located under the env build directories immediately after each env build.

| Env | Path | Extension | Size bytes | SHA-256 | File type | Candidate role |
| --- | --- | ---: | ---: | --- | --- | --- |
| `glyph_mk6` | `.pio/build/glyph_mk6/firmware.bin` | `.bin` | 391,864 | `7740089920f1b239a61b6abe98cdf7e6632b9fcd7bbf22d90a9eabe9e68965d5` | data | Generated binary side artifact |
| `glyph_mk6` | `.pio/build/glyph_mk6/firmware.elf` | `.elf` | 5,405,012 | `3b9ece48cb7092b719b52e38bdd094e0425a825c1502da8d555972e7896e52fc` | ELF 32-bit LSB executable, ARM, EABI5, statically linked, with debug_info, not stripped | Generated ELF side artifact |
| `glyph_mk6` | `.pio/build/glyph_mk6/firmware.uf2` | `.uf2` | 783,872 | `708cb8726208112ed428c15247b6728be1a5fc4299a3866a62f70f721279a912` | UF2 firmware image, family Raspberry Pi RP2040, address `0x10000000`, 1,531 total blocks | Normal generated UF2 candidate |
| `glyph_mk6_senscope_playtest` | `.pio/build/glyph_mk6_senscope_playtest/firmware.bin` | `.bin` | 391,984 | `010ba9cd20cf2351efab4ebc5e5c0a1807a7797350f39ad66274c15c8e37ffb1` | data | Generated binary side artifact |
| `glyph_mk6_senscope_playtest` | `.pio/build/glyph_mk6_senscope_playtest/firmware.elf` | `.elf` | 5,405,172 | `291a2efe25c0bf61847a8621eee82d935600e9e29dcd0674a7293329baf4cdb8` | ELF 32-bit LSB executable, ARM, EABI5, statically linked, with debug_info, not stripped | Generated ELF side artifact |
| `glyph_mk6_senscope_playtest` | `.pio/build/glyph_mk6_senscope_playtest/firmware.uf2` | `.uf2` | 784,384 | `57020713e14b992828756af27745241c79cde52ab49287dfcb64c4fd27544b71` | UF2 firmware image, family Raspberry Pi RP2040, address `0x10000000`, 1,532 total blocks | Playtest generated UF2 candidate |

No `.hex` candidate was found in the env build directory listings.

## UF2 Range Comparison

Ranges are half-open: start inclusive, end exclusive.

| Artifact | Magic valid | Blocks | Family ID(s) | Target range(s) | Payload bytes | Segment SHA-256 | Any all-zero segment | Clean high-flash overlap |
| --- | ---: | ---: | --- | --- | ---: | --- | ---: | ---: |
| Official Update `GlyphFirmware-1.0.7.uf2` | Yes | 1,503 | `0xe48bff56` | `0x10000000..0x1005df00` | 384,768 | `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8` | No | No |
| Official Clean `GlyphFirmware-1.0.7-Clean.uf2` | Yes | 3,551 | `0xe48bff56` | `0x10000000..0x1005df00`; `0x1017f000..0x101ff000` | 909,056 | App `207a0073251e87aaa70490acfc2812e10fe1c724dd76e7a816c205c1e29e79f8`; zero segment `07854d2fef297a06ba81685e660c332de36d5d18d546927d30daad6d7fda1541` | Yes | Yes |
| Generated normal `.pio/build/glyph_mk6/firmware.uf2` | Yes | 1,531 | `0xe48bff56` | `0x10000000..0x1005fb00` | 391,936 | `baddd3c06524bf15107632fca8e23222f4d63c4c2ad66cc9dd0e387c705fe7a2` | No | No |
| Generated playtest `.pio/build/glyph_mk6_senscope_playtest/firmware.uf2` | Yes | 1,532 | `0xe48bff56` | `0x10000000..0x1005fc00` | 392,192 | `99c1af70a30e59ce6d8a19e736ea1ce1903d8ac0b3f2633294d0353460518409` | No | No |

## Official-Vs-Generated Range Findings

| Check | Result |
| --- | --- |
| Official Update range | `0x10000000..0x1005df00` |
| Official Clean high-flash wipe range | `0x1017f000..0x101ff000` |
| Normal generated range | `0x10000000..0x1005fb00` |
| Playtest generated range | `0x10000000..0x1005fc00` |
| Normal generated extends beyond official Update end | Yes, by `0x1c00` / 7,168 bytes |
| Playtest generated extends beyond official Update end | Yes, by `0x1d00` / 7,424 bytes |
| Normal generated overlaps official Clean high-flash wipe range | No |
| Playtest generated overlaps official Clean high-flash wipe range | No |
| Normal generated contains all-zero segment | No |
| Playtest generated contains all-zero segment | No |
| Playtest generated writes outside local app-like range used by the parser | No |

## Playtest Classification

The generated playtest UF2 is classified as:

```text
UPDATE_STYLE_APP_ONLY_CANDIDATE
```

Basis:

- valid UF2 magic;
- RP2040 family ID `0xe48bff56`;
- single generated app-like target range `0x10000000..0x1005fc00`;
- no all-zero segment;
- no overlap with the official Clean/Fresh Install high-flash wipe range `0x1017f000..0x101ff000`;
- no parser-reported write outside the local app-like range.

This classification is not approval to flash. It only supports future human review under the G12K/G13G gates.

## Safety Boundary

This batch did not:

- run PlatformIO upload;
- copy any artifact to `RPI-RP2`;
- copy any artifact to mounted devices;
- flash hardware;
- commit generated firmware artifacts;
- add export, push-to-device, upload, or flashing workflow.
