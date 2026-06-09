# Glyph Phase 7A Diagnostic D3 Hardware Result - 2026-06-09

status: USER_REPORTED_PASS

## Purpose and scope

This document records the user-reported hardware result for Phase 7A
Diagnostic D3 global/static parser initialization only. D3 tests whether adding
only the global/static parser initialization result, while retaining the D2B
payload bytes and not adding resolver/output routing, reproduces the RF5/RF6
disconnect observed on the failed Phase 7A activation branch.

This result is scoped to the D3 isolated diagnostic. It does not prove root
cause, parser safety in every activation design, failed-branch recoverability,
public release compatibility, release compatibility, or nunchuk behavior.

## Branch and result

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Diagnostic branch tested:
  `phase7a-diagnostic-d3-global-parse-result-only`
- Result branch:
  `phase7a-diagnostic-d3-global-parse-result-only-hardware-result`
- Result source: user-reported
- Exact user report text: `tested, everything works without issues`
- Result date: `2026-06-09`
- Install method: manual Glyph firmware update
- Build command: `./scripts/build-glyph-mk6-quiet.sh`
- Build report reference:
  `docs/runtime_config/phase7a_diagnostic_d3_global_parse_result_only_build_report_2026-06-09.md`
- Result fixture:
  `docs/calibration/fixtures/glyph_phase7a_diagnostic_d3_global_parse_result_only_hardware_result_2026-06-09.json`
- Source/build provenance: local D3 branch and build process only
- Nunchuk: NOT_TESTED

## Local build observations

The local D3 build report records artifact observations for the diagnostic
build. These are local build observations only and are not automated device
telemetry.

| Artifact | Size bytes | SHA-256 |
| --- | ---: | --- |
| `.pio/build/glyph_mk6/firmware.uf2` | 793088 | `ee428514a0f00873ab900cc5649b7cec5f3f5a83867e05b613b50fb063cf0a19` |
| `.pio/build/glyph_mk6/firmware.elf` | 5407436 | `23f06368ece84c171c1e3c3ce94f1fefdac236d6fba4d55c4b2b4941eef37d32` |
| `.pio/build/glyph_mk6/firmware.bin` | 396532 | `ded8da7b3e91fa4252f13cf32b8eae4a122987471d7cc77bcc88f9c0ee748a2f` |

## Hardware result table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | PASS | User-reported pass. |
| BASELINE-001 | baseline | Baseline behavior preserved | PASS | User-reported pass. |
| RF5-001 | rf5_paths | Representative RF5 behavior does not cause controller disconnect | PASS | No disconnect reported. |
| RF6-001 | rf6_paths | Representative RF6 behavior does not cause controller disconnect | PASS | No disconnect reported. |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | PASS | Covered by "everything works". |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | PASS | Covered by "everything works". |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | PASS | Covered by "everything works". |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | PASS | Covered by "everything works". |
| PAYLOAD-001 | payload_retention | D2B retained payload bytes remain present | PRESENT | D2B retained payload bytes present. |
| GLOBAL-PARSE-001 | global_parse_result | Global parse result is present in the diagnostic source | PRESENT | Global/static parse result present. |
| PARSER-CALL-001 | parser_behavior | Parser call exists only in global/static initialization path | PRESENT | Parser called by global/static initialization. |
| NO-RESOLVER-001 | runtime_resolver | Runtime resolver not added | SOURCE_CHECKED | No runtime resolver added. |
| NO-RUNTIME-ROUTING-001 | runtime_routing | Parsed result is not routed into runtime output lookup | SOURCE_CHECKED | Parsed result not routed into output lookup. |
| NO-STORAGE-001 | storage | Runtime-config storage not added | SOURCE_CHECKED | No runtime storage. |
| NO-WRITE-001 | webserial_or_write | WebSerial/device write not added | SOURCE_CHECKED | No WebSerial/device write. |
| NO-FLASH-001 | flashing_automation | No firmware flashing automation paths used | SOURCE_CHECKED | No flashing automation. |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | Not tested. |

## Source/build checks retained

The following claims are source/build-checked, not hardware telemetry:

- D2B retained payload bytes present
- global/static parse result present
- parser called by global/static initialization
- no runtime resolver added
- parsed result not routed into output lookup
- no runtime storage
- no WebSerial/device write
- no flashing automation
- no `UpdateAnalogOutputs(...)` behavior change intended
- no `UpdateDigitalOutputs(...)` change
- no RF5/RF6 expression change

## Diagnostic interpretation

- D3 passed.
- Global/static parser initialization alone did not reproduce the RF5/RF6
  disconnect.
- H1 global/static parser initialization is reduced in likelihood.
- H4 parser loop/static-init is reduced in likelihood.
- D2B, D3, and D4 each passed in isolation.
- H5 remains open only in combination.
- H6 remains open.
- Root cause remains unproven.
- Failed activation branch remains abandoned and must not merge.
- Next recommended diagnostic should focus on controlled combinations rather
  than a single isolated component.

## Limitations and non-claims

- result is user-reported
- no automated device telemetry
- no nunchuk validation
- no public release claim
- no release compatibility claim
- no proof of root cause
- no claim that parser is generally safe in every activation design
- no claim that the failed branch is recoverable
- no runtime resolver/output routing validation beyond source/build checks
