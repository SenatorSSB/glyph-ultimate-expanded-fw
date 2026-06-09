# Phase 7A Diagnostic D4 Build Report

status: DIAGNOSTIC_D4_BUILD_REPORT_PENDING_HARDWARE_RESULT

branch: `phase7a-diagnostic-d4-runtime-resolver-only-clean`

base branch: `configurator`

diagnostic mode: `D4`

payload-retained-in-image: `false`

build command: `./scripts/build-glyph-mk6-quiet.sh`

firmware source commit under build: `5846a3c9a14eadb8d51f7866a148dc614823a60f`
evidence/report commit: `1de8e0da54f33d08a78a2e4a563648e633975be4`
post-build commits scope: `docs/tools-only`
firmware source changed after build: `false`
build date (local): `2026-06-09 16:21:21 +0300`

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 791552 | 2bddbfa0e471b466aa88f90da457ae9e86fcd51cb6896821c972dd1321dcb6c5 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407148 | 1915e8d8497c661f551e51f6b618257757cd009d3fc38f22a30d003eb5784d46 | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 395672 | a37edf89cfa16548d11113d30b40a90ec74501006247a0eb1cce357600f2cc42 | available |

| artifact_type | baseline size_bytes | baseline sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | 791552 | 2bddbfa0e471b466aa88f90da457ae9e86fcd51cb6896821c972dd1321dcb6c5 | 0 |
| elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | 5407148 | 1915e8d8497c661f551e51f6b618257757cd009d3fc38f22a30d003eb5784d46 | 0 |
| bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | 395672 | a37edf89cfa16548d11113d30b40a90ec74501006247a0eb1cce357600f2cc42 | 8 |

## Map / Artifact Availability

- uf2 file: available
- elf file: available
- bin file: available
- map file: unavailable (not emitted by this build command)

## Caveats

- no parsed payload bytes retained in firmware image
- no runtime parser call
- no global parse result
- no compiled payload header
- no payload anchor
- no `.incbin`
- no storage/write/WebSerial/flashing behavior
- no runtime behavior change intended
- no runtime-config activation claim
- no hardware result recorded in this branch
- hardware result required before conclusions.
