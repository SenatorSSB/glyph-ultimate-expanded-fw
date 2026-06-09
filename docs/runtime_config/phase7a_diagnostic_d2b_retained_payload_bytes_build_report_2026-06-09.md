# Phase 7A Diagnostic D2B Build Report

status: DIAGNOSTIC_D2B_BUILD_REPORT_PENDING_HARDWARE_RESULT

branch: `phase7a-diagnostic-d2b-retained-payload-bytes`

base branch: `configurator`

diagnostic mode: `D2B`

payload-retained-in-image: `true`

retained-payload-size-bytes: `530`

payload-sequence-scan-performed: `true`

retention-proof-status: `proven_full_payload_sequence_present`

build command: `./scripts/build-glyph-mk6-quiet.sh`

git commit SHA under build: `bc0525dba8ecbdc62251a3b9d4bb2fc54a9a1a35`
build date (local): `2026-06-09 14:59:05 +0300`

## Artifact Table

| path | artifact_type | size_bytes | sha256 | availability |
| --- | --- | ---: | --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | uf2 | 792576 | c3196352f508e999e9c4f1d5a8a5de96409e9591f4f71c64817cdc06a4b985b4 | available |
| `.pio/build/glyph_mk6/firmware.elf` | elf | 5407276 | b7aa9b045c1b55e2674e880afc801d2e1cbf23af7f8026d95a4b0519e8b92118 | available |
| `.pio/build/glyph_mk6/firmware.bin` | bin | 396208 | ee3c37855e6d53ce18b32a5c32c3f9faa6525014f7bea93d99ddd6756655e37d | available |

| artifact_type | baseline size_bytes | baseline sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | bcb1bba8803e8383fc97464812ab5dc66c1e6f11b2b42625f5f8984d05f97085 | 792576 | c3196352f508e999e9c4f1d5a8a5de96409e9591f4f71c64817cdc06a4b985b4 | 1024 |
| elf | 5407148 | dbdb3537c23a1c0c420fed600165b4602d98af061720bcb5d53213a6a6e52d83 | 5407276 | b7aa9b045c1b55e2674e880afc801d2e1cbf23af7f8026d95a4b0519e8b92118 | 128 |
| bin | 395664 | 4f095fbe57dc1a8a40a62ede36ddd291402966635c41049f7f0b13beb4ca9a45 | 396208 | ee3c37855e6d53ce18b32a5c32c3f9faa6525014f7bea93d99ddd6756655e37d | 544 |

| artifact_type | D2A size_bytes | D2A sha256 | current size_bytes | current sha256 | size delta bytes |
| --- | ---: | --- | ---: | --- | ---: |
| uf2 | 791552 | 1cda3368a76d0b048317f9738e25480e7318f65955cc595a24923422c255a0c4 | 792576 | c3196352f508e999e9c4f1d5a8a5de96409e9591f4f71c64817cdc06a4b985b4 | 1024 |
| elf | 5407148 | 5d55679d7b46172b40f0c33dd44f7b36277b097a86d457da146befffe5415f86 | 5407276 | b7aa9b045c1b55e2674e880afc801d2e1cbf23af7f8026d95a4b0519e8b92118 | 128 |
| bin | 395664 | dd371038cffc1c94b2586808abc1ca9ddc9bf901e3d4434a2742225926a14abc | 396208 | ee3c37855e6d53ce18b32a5c32c3f9faa6525014f7bea93d99ddd6756655e37d | 544 |

## Payload Sequence Scan

Scanned fixture:
`docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin`

| artifact path | full payload sequence found | offsets decimal | offsets hex |
| --- | --- | ---: | --- |
| `.pio/build/glyph_mk6/firmware.bin` | true | 369868 | `0x5a4cc` |
| `.pio/build/glyph_mk6/firmware.elf` | true | 435404 | `0x6a4cc` |
| `.pio/build/glyph_mk6/firmware.uf2` | false | none | none |

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

Retention is proven by an artifact-level scan for the full committed 530-byte
payload fixture sequence. The full sequence is present in `.pio/build/glyph_mk6/firmware.bin`
at offset 369868 (`0x5a4cc`) and in `.pio/build/glyph_mk6/firmware.elf` at
offset 435404 (`0x6a4cc`). The raw sequence is not found in `.uf2`; `.bin` and
`.elf` are the required proof artifacts. Size/hash deltas versus baseline and
D2A remain recorded above, while all runtime behavior-sensitive files remain
unchanged and no parser/resolver/runtime-config flow is added.
