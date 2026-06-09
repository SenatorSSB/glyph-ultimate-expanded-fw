# Phase 7A Diagnostic D2B Build Report

status: DIAGNOSTIC_D2B_BUILD_REPORT_PENDING_HARDWARE_RESULT

branch: `phase7a-diagnostic-d2b-retained-payload-bytes`

base branch: `configurator`

diagnostic mode: `D2B`

payload-retained-in-image: `true`

retained-payload-size-bytes: `530`

build command: `./scripts/build-glyph-mk6-quiet.sh`

git commit SHA under build: `a732fcd0e5bdb59a3bfeb93c5feb70b7cfbe9693`
build date (local): `2026-06-09 14:35:24 +0300`

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 791552 | df5eab6b8e3095e9d34831ab432651ac679d622373289c5b19e74bf4537feb30 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407148 | 515e2d0993dad76e730ae14c7213c973412a9d4baf0cb267cbb2b7e9cae1c11b | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 395672 | 815f5eb0e12807c3b15e34c715bb0dd9cb4b077e51223c7c2c16478cbd949134 | available |

| artifact_type | baseline size_bytes | baseline sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | 791552 | df5eab6b8e3095e9d34831ab432651ac679d622373289c5b19e74bf4537feb30 | 0 |
| elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | 5407148 | 515e2d0993dad76e730ae14c7213c973412a9d4baf0cb267cbb2b7e9cae1c11b | 0 |
| bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | 395672 | 815f5eb0e12807c3b15e34c715bb0dd9cb4b077e51223c7c2c16478cbd949134 | 8 |

| artifact_type | D2A size_bytes | D2A sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | 1cda3368a76d0b048317f9738e25480e7318f65955cc595a24923422c255a0c4 | 791552 | df5eab6b8e3095e9d34831ab432651ac679d622373289c5b19e74bf4537feb30 | 0 |
| elf | 5407148 | 5d55679d7b46172b40f0c33dd44f7b36277b097a86d457da146befffe5415f86 | 5407148 | 515e2d0993dad76e730ae14c7213c973412a9d4baf0cb267cbb2b7e9cae1c11b | 0 |
| bin | 395664 | dd371038cffc1c94b2586808abc1ca9ddc9bf901e3d4434a2742225926a14abc | 395672 | 815f5eb0e12807c3b15e34c715bb0dd9cb4b077e51223c7c2c16478cbd949134 | 8 |

## Map / Artifact Availability

- uf2 file: available
- elf file: available
- bin file: available
- map file: unavailable (not emitted by this build command)

## Caveats

- payload bytes retained in firmware image via dedicated retention anchor TU;
- no parser call;
- no runtime resolver;
- no global parse result;
- no runtime-config storage;
- no WebSerial/device write;
- no firmware flashing automation;
- no runtime behavior change intended;
- no runtime-config runtime activation;
- no hardware result recorded in this branch;
- hardware result required before conclusions.

## Retention verification note

Retention is verified by a non-zero `.bin` size delta (+8 bytes) versus baseline and D2A,
and by presence of the dedicated used symbol `kPhase7AD2BRetainedPayloadAnchor` that
references `kPhase7ACompiledPayload`, while all runtime behavior-sensitive files
remain unchanged and no parser/resolver/runtime-config flow is added.
