# Phase 7A Diagnostic D4 Build Report

status: DIAGNOSTIC_D4_BUILD_REPORT_PENDING_HARDWARE_RESULT

branch: `phase7a-diagnostic-d4-runtime-resolver-only`

base branch: `configurator`

diagnostic mode: `D4`

payload-retained-in-image: `false`

build command: `./scripts/build-glyph-mk6-quiet.sh`

git commit SHA under build: `1af6c522b8f15f706072ec88315978281af8f4c4`
build date (local): `2026-06-09 16:04:15 +0300`

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 791552 | 22f7b0df2ca6bf599cc041ef409450787078324fb9d26d559bc9ed0ca70ddfc8 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407148 | fda64557e404b6e8779df4968ad05cad458eaa8700111af7775c5da2704e3054 | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 395672 | 3db10cc529beed3d2ca2b77bd6e9f474238b9217621df57d2e7fb9e8e2931c1b | available |

| artifact_type | baseline size_bytes | baseline sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | 791552 | 22f7b0df2ca6bf599cc041ef409450787078324fb9d26d559bc9ed0ca70ddfc8 | 0 |
| elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | 5407148 | fda64557e404b6e8779df4968ad05cad458eaa8700111af7775c5da2704e3054 | 0 |
| bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | 395672 | 3db10cc529beed3d2ca2b77bd6e9f474238b9217621df57d2e7fb9e8e2931c1b | 8 |

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
