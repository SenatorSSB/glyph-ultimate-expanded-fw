# Phase 7A Diagnostic D2 Build Report

status: DIAGNOSTIC_D2_BUILD_REPORT_PENDING_HARDWARE_RESULT

branch: `phase7a-diagnostic-d2-compiled-payload-header-only`

baseline branch: `configurator`

diagnostic mode: `D2A`

payload-retained-in-image: `false`

build command: `./scripts/build-glyph-mk6-quiet.sh`

git commit SHA under build: `787394eb2c8f2bf5fb9b7b4d5b7f6f4c0f5c4f7f`

build date (local): `2026-06-09 11:32:25 +0300`

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 791552 | 1cda3368a76d0b048317f9738e25480e7318f65955cc595a24923422c255a0c4 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407148 | 5d55679d7b46172b40f0c33dd44f7b36277b097a86d457da146befffe5415f86 | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 395664 | dd371038cffc1c94b2586808abc1ca9ddc9bf901e3d4434a2742225926a14abc | available |

| artifact_type | baseline size_bytes | baseline sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | 791552 | 1cda3368a76d0b048317f9738e25480e7318f65955cc595a24923422c255a0c4 | 0 |
| elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | 5407148 | 5d55679d7b46172b40f0c33dd44f7b36277b097a86d457da146befffe5415f86 | 0 |
| bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | 395664 | dd371038cffc1c94b2586808abc1ca9ddc9bf901e3d4434a2742225926a14abc | 0 |

## Map / Artifact Availability

- uf2 file: available
- elf file: available
- bin file: available
- map file: unavailable (not emitted by this build command)

## Caveats

- compiler build includes the new payload header file in repo but does not include
  it in firmware output in D2A
- no parser/runtime-config behavior change
- no runtime-config resolver, no storage, no WebSerial/device write, no flash
  automation
- no hardware result recorded in this branch
- hardware result required before any conclusion
