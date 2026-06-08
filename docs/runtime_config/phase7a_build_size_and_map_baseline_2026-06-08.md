# Phase 7A Build Size and Map Baseline

status: `BUILD_SIZE_BASELINE_RECORDED`

branch: `phase7a-build-size-and-map-baseline`

baseline branch: `configurator`

build command: `./scripts/build-glyph-mk6-quiet.sh`

build date (local): `2026-06-08 23:41:49 +0300`

git commit SHA under build: `25fb7fbf93854bc8cda6b5d1a472e8948dfda3da`

platform/env: `glyph_mk6` (discovered from `./.pio/build/glyph_mk6`)

## Artifact Table

| path | type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | available |
| n/a | map | n/a | n/a | unavailable |

## Map / ELF / UF2 / BIN Details

- map file: unavailable (not produced by this build command in this branch)
- elf file: available at `.pio/build/glyph_mk6/firmware.elf`
- uf2 file: available at `.pio/build/glyph_mk6/firmware.uf2`
- bin file: available at `.pio/build/glyph_mk6/firmware.bin`

## Caveats

- no firmware source edits
- no runtime behavior change
- no runtime-loaded config
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
- no hardware result claim
- nunchuk NOT_TESTED

## Intended Use

This baseline is for build-size/map/artifact comparison for future runtime-active
parser activation branches before any hardware testing. It establishes a known-good
firmware artifact baseline from `configurator` lineage.

