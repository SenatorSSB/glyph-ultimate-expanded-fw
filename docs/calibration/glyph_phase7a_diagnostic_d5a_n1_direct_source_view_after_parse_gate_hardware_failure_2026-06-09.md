# Glyph Phase 7A Diagnostic D5A-N1 Hardware Failure - 2026-06-09

status: USER_REPORTED_FAIL

## Purpose and scope

This document records the user-reported hardware failure for Phase 7A
Diagnostic D5A-N1 direct source-owned view after parse gate. It reproduces the
same disconnect class as D5A and is scoped only to the D5A-N1 hypothesis
narrowing. It does not prove root cause, parser safety, resolver safety, public
release compatibility, or any nunchuk behavior.

## Branch and result

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Diagnostic branch tested:
  `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`
- Result branch:
  `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate-hardware-failure`
- Result source: user-reported
- Exact user report text: `flashed, same disconnects happen`
- Result date: `2026-06-09`
- Install method: manual Glyph firmware update
- Result fixture:
  `docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n1_direct_source_view_after_parse_gate_hardware_failure_2026-06-09.json`
- Nunchuk: NOT_TESTED

## Hardware result summary

D5A-N1 failed.
Same disconnects as D5A.
RF5/RF6/LT6 disconnect class reproduced.
The separate RuntimeConfigView alias is reduced as suspect.
parse-status hot-path read remains primary suspect.
D3 global parse result alone passed.
D4 resolver alone passed.
D5A and D5A-N1 both failed.

## Hardware result table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | PASS | Firmware was flashed and the branch reached testable state. |
| BASELINE-001 | baseline | Baseline behavior preserved | FAIL | Same disconnects as D5A. |
| RF5-001 | rf5_paths | Representative RF5 behavior does not cause controller disconnect | FAIL | RF5 disconnect reproduced. |
| RF6-001 | rf6_paths | Representative RF6 behavior does not cause controller disconnect | FAIL | RF6 disconnect reproduced. |
| LT6-001 | lt6_paths | Representative LT6 behavior does not cause controller disconnect | FAIL | LT6 disconnect reproduced. |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | NOT_TESTED | Not separately reported in the user result. |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | NOT_TESTED | Not separately reported in the user result. |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | NOT_TESTED | Not separately reported in the user result. |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | NOT_TESTED | Not separately reported in the user result. |
| PAYLOAD-001 | payload_retention | D2B retained payload bytes remain present | SOURCE_CHECKED | D2B retained payload bytes kept. |
| GLOBAL-PARSE-001 | global_parse_result | Global parse result is present in the diagnostic source | SOURCE_CHECKED | Global/static parse result kept. |
| PARSER-CALL-001 | parser_behavior | Parser call exists only in global/static initialization path | SOURCE_CHECKED | Parser call remains in global/static initialization. |
| RESOLVER-001 | runtime_resolver | Resolver is present | SOURCE_CHECKED | Resolver call remains in `UpdateAnalogOutputs(...)`. |
| PARSE-STATUS-GATE-001 | parse_status_gate | Runtime routing is gated by parse status `Ok` | SOURCE_CHECKED | Parse-status gate remains in resolver. |
| SOURCE-OWNED-ROUTING-001 | runtime_routing | Analog runtime output lookup is routed through resolver-selected source-owned view | SOURCE_CHECKED | Direct canonical source-owned view returned after `ParseStatus::Ok`. |
| NO-PARSED-TABLES-001 | parsed_table_scope | Parsed table materialization is not added | SOURCE_CHECKED | Separate RuntimeConfigView alias removed; no parsed table materialization. |
| FALLBACK-001 | fallback | Fallback remains source-owned current baseline or known-good runtime config | SOURCE_CHECKED | Fallback path unchanged. |
| NO-STORAGE-001 | storage | Runtime-config storage not added | SOURCE_CHECKED | No runtime-config storage. |
| NO-WRITE-001 | webserial_or_write | WebSerial/device write not added | SOURCE_CHECKED | No WebSerial/device write. |
| NO-FLASH-001 | flashing_automation | No firmware flashing automation paths used | SOURCE_CHECKED | No firmware flashing automation. |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | Not tested. |

## Source/build checks retained

- D2B retained payload bytes remain present.
- D3 global/static parse result remains present.
- parse-status gate remains in resolver.
- resolver call from `UpdateAnalogOutputs(...)` remains present.
- direct canonical source-owned return after parse OK remains present.
- separate `RuntimeConfigView` alias/copy removed.
- no parsed table materialization.
- no true parsed-result data routing.
- no runtime storage.
- no WebSerial/device write.
- no firmware flashing automation.

## Diagnostic interpretation

- D5A-N1 failed.
- Same disconnects as D5A.
- RF5/RF6/LT6 disconnect class reproduced.
- The separate RuntimeConfigView alias is reduced as suspect.
- parse-status hot-path read inside `ResolveActiveRuntimeConfig()` remains the
  primary suspect.
- D3 global parse result alone passed.
- D4 resolver alone passed.
- D5A and D5A-N1 both failed.
- Root cause remains unproven.
- Failed activation branch remains abandoned and must not merge.
- Next diagnostic: D5A-N2 resolver without parse-status hot-path read.

## Limitations and non-claims

- result is user-reported
- no automated device telemetry
- no nunchuk validation
- no public release claim
- no release compatibility claim
- no proof of root cause
- no claim that the failed branch is recoverable
