# Glyph Phase 7A Diagnostic D5A-N1 Hardware Result - 2026-06-09

status: USER_REPORTED_FAILURE

## Purpose and scope

This document records the user-reported hardware result for the D5A-N1 focused
diagnostic branch.

The branch keeps D2B retained payload bytes, keeps D3 global parser initialization,
keeps parse-status-gated resolver routing, and directly returns
`kSourceOwnedCurrentBaselineRuntimeConfig` after parse-status gate.

## Branch and result

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Diagnostic branch tested: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`
- Result branch:
  `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate-hardware-result`
- Result source: `user-reported`
- Exact user report text: `retest: RF5/RF6/LT6 disconnects reproduced`
- Result date: `2026-06-09`
- Commit SHA under test: `unknown`
- Build command: `pio run -e glyph_mk6`
- Build report reference:
  `docs/runtime_config/phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_build_report_2026-06-09.md`
- Result fixture:
  `docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_result_2026-06-09.json`
- Nunchuk: `NOT_TESTED`

## Hardware result summary

- BOOT-001: FAIL, not recorded in this report.
- BASELINE-001: PASS, unrelated baseline behavior remained intact.
- RF5-001: FAIL, RF5 behavior reproduced controller disconnect.
- RF6-001: FAIL, RF6 behavior reproduced controller disconnect.
- LT6-001: FAIL, LT6 behavior reproduced controller disconnect.
- NUNCHUK-001: NOT_TESTED

## Hardware result table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | NOT_TESTED | Not re-recorded in this template result packet. |
| BASELINE-001 | baseline | Baseline behavior preserved | PASS | User-reported pass. |
| RF5-001 | rf5_paths | Representative RF5 behavior does not cause controller disconnect | FAIL | RF5 disconnect reproduced. |
| RF6-001 | rf6_paths | Representative RF6 behavior does not cause controller disconnect | FAIL | RF6 disconnect reproduced. |
| LT6-001 | lt6_paths | Representative LT6 behavior does not cause controller disconnect | FAIL | LT6 disconnect reproduced. |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | PASS | covered by broader user report. |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | PASS | covered by broader user report. |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | PASS | covered by broader user report. |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | PASS | covered by broader user report. |
| PAYLOAD-001 | payload_retention | D2B retained payload bytes remain present | SOURCE_CHECKED | D2B symbol remains in source. |
| GLOBAL-PARSE-001 | global_parse_result | Global parse result is present in the diagnostic source | SOURCE_CHECKED | D3 global parse result present. |
| PARSER-CALL-001 | parser_behavior | Parser call exists in global/static initialization path | SOURCE_CHECKED | Parser call remains in global/static init. |
| RESOLVER-001 | runtime_resolver | Resolver is present | SOURCE_CHECKED | Resolver remains present. |
| PARSE-STATUS-GATE-001 | parse_status_gate | Runtime routing is gated by parse status Ok | SOURCE_CHECKED | Parse-status gate present. |
| SOURCE-OWNED-ROUTING-001 | runtime_routing | Analog runtime output lookup routed through resolver-selected source-owned view | SOURCE_CHECKED | Direct source-owned baseline return now used. |
| FALLBACK-001 | fallback | Fallback remains known-good runtime config | SOURCE_CHECKED | Fallback retained. |
| NO-STORAGE-001 | storage | Runtime-config storage not added | SOURCE_CHECKED | No storage in firmware source. |
| NO-WRITE-001 | webserial_or_write | WebSerial/device write not added | SOURCE_CHECKED | No write path in firmware source. |
| NO-FLASH-001 | flashing_automation | No firmware flashing automation paths used | SOURCE_CHECKED | No flashing automation in firmware source. |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | Not tested. |

## Source/build checks retained

- D2B retained payload bytes remained present.
- D3 global static parse result remained present.
- Resolver remained parse-status gated.
- No parsed-table materialization added.
- `UpdateDigitalOutputs(...)` unchanged.
- No runtime-config storage/write/WebSerial/flashing behavior added.

## Hardware conclusion

The D5A-N1 branch still reproduces the reported disconnect pattern:
RF5/RF6/LT6 disconnects remain.
No nunchuk validation was performed.

## Limitations and non-claims

- result is user-reported and not a device-automated result
- no automated causality proof
- no root-cause proof
- no parser safety proof
- no public release claim
- no compatibility release claim
- no nunchuk validation
