# Phase 7A Diagnostic D4 Build Report

status: DIAGNOSTIC_D4_BUILD_REPORT_PENDING_HARDWARE_RESULT

branch: `phase7a-diagnostic-d4-runtime-resolver-only-clean`

base branch: `configurator`

diagnostic mode: `D4`

payload-retained-in-image: `false`

build command: `./scripts/build-glyph-mk6-quiet.sh`

git commit SHA under build: `c82cfda5d5b36713025453e7e43e48c116c82faf`
build date (local): `2026-06-09 16:14:21 +0300`

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 791552 | e48baa2dbcf1f2fec1607bbce8508b0fd6d678963df4b7e5fb2c345ab3a49ae8 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407148 | d03eefe3161aa222276fb735a1905e204f90d473de9a96879b89dc34d7ee820c | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 395672 | cd0880780c15977179fa0f455fe2f53db6535159214c0deca59301da267e0229 | available |

| artifact_type | baseline size_bytes | baseline sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | 791552 | e48baa2dbcf1f2fec1607bbce8508b0fd6d678963df4b7e5fb2c345ab3a49ae8 | 0 |
| elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | 5407148 | d03eefe3161aa222276fb735a1905e204f90d473de9a96879b89dc34d7ee820c | 0 |
| bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | 395672 | cd0880780c15977179fa0f455fe2f53db6535159214c0deca59301da267e0229 | 8 |

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
