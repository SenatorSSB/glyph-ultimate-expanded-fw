# Phase 7A Diagnostic D4 Runtime Resolver Only Hardware Result - 2026-06-09

This document records the user-reported hardware result for Diagnostic D4 on
`phase7a-diagnostic-d4-runtime-resolver-only-clean`. It is scoped to the
resolver/reference wrapper only and does not claim runtime-loaded config,
runtime-config storage, parser activation, compiled payload bytes, WebSerial/
device write, flashing automation, release/public compatibility, nunchuk
validation, or automated telemetry.

## Result Identity

- status: USER_REPORTED_PASS
- result source: user-reported
- exact user report text: `tested, everything works without issues`
- date: 2026-06-09
- diagnostic branch tested: `phase7a-diagnostic-d4-runtime-resolver-only-clean`
- result branch: `phase7a-diagnostic-d4-runtime-resolver-only-hardware-result`
- install method: manual Glyph firmware update
- build command: `./scripts/build-glyph-mk6-quiet.sh`
- build report reference:
  `docs/runtime_config/phase7a_diagnostic_d4_runtime_resolver_only_build_report_2026-06-09.md`
- source/build provenance: local D4 branch and build process only
- nunchuk: NOT_TESTED

## Source Authority

The record is based on the exact user report text and the D4 branch/build
boundary recorded in the local build report. Artifact hashes are treated as
local build observations only, not as automated telemetry.

## Local Build Observations

The D4 build report records these artifact hashes:

| Path | SHA-256 |
| --- | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | `35bc07535bd76e807964334444ed33f051692aa346e16210b79113fb96e526bf` |
| `.pio/build/glyph_mk6/firmware.elf` | `6103821d11e24ddd4a1adf76f2805765bf954547bd7284b306baa0d937232aca` |
| `.pio/build/glyph_mk6/firmware.bin` | `7b9b3da59377fcae309513af5fa7245eb5012cfc853874315c17d8200a73ee6f` |

## Hardware Result Table

| Row ID | Category | Result | Notes |
| --- | --- | --- | --- |
| BOOT-001 | boot | PASS | user-reported pass |
| BASELINE-001 | baseline | PASS | user-reported pass |
| RF5-001 | rf5_paths | PASS | no disconnect reported |
| RF6-001 | rf6_paths | PASS | no disconnect reported |
| ORDINARY-DIR-001 | directions | PASS | covered by "everything works" |
| NEUTRAL-001 | neutral_state | PASS | covered by "everything works" |
| UNRELATED-BUTTONS-001 | buttons | PASS | covered by "everything works" |
| MODIFIERS-001 | modifiers | PASS | covered by "everything works" |
| NO-PARSER-001 | parser_behavior | SOURCE_CHECKED | parser not called by D4 source/checker |
| NO-PAYLOAD-001 | runtime_payload | SOURCE_CHECKED | no compiled payload/payload retention in D4 |
| NO-GLOBAL-PARSE-001 | parser_lifecycle | SOURCE_CHECKED | no global ParseResult in D4 |
| RESOLVER-001 | runtime_resolver | PRESENT | D4 resolver wrapper present |
| NO-STORAGE-001 | storage | SOURCE_CHECKED | no runtime storage |
| NO-WRITE-001 | webserial_or_write | SOURCE_CHECKED | no WebSerial/device write |
| NO-FLASH-001 | flashing_automation | SOURCE_CHECKED | no flashing automation |
| NUNCHUK-001 | nunchuk_scope | NOT_TESTED | not tested |

## Diagnostic Interpretation

- D4 passed
- resolver/reference wrapper alone did not reproduce the RF5/RF6 disconnect
- H3 reduced in likelihood
- H1 and H4 remain open
- H5 remains open only in combination with parser/global parse/resolver changes
- H6 remains open
- D3 global parse result only is the next recommended diagnostic

## Non-Claims

- no root cause proven
- no parser safety proven
- no failed activation branch recovery
- no release/public compatibility claim
- no nunchuk validation
- no automated device telemetry
- no runtime-loaded config
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
- no Senscope/game-semantic change
