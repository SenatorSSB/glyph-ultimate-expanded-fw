# Glyph Phase 7A Diagnostic D5A Hardware Failure - 2026-06-09

status: USER_REPORTED_FAIL

## Purpose and scope

This document records the user-reported hardware failure for Phase 7A diagnostic D5A
parse-status-gated source-owned runtime routing. D5A is the parse-status-gated
source-owned runtime-routing combination (not true parsed-table-data routing) after
retained-payload/parse/init/resolver sequencing.

## Branch and result

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Diagnostic branch tested: `phase7a-diagnostic-d5-parsed-result-runtime-routing`
- Result branch: `phase7a-diagnostic-d5a-parse-status-gated-routing-hardware-failure`
- Result source: user-reported
- Exact user report text: `tested, failed. RF5 and RF6 caused disconnect. Because LT6 had been similarly coded I tested that too, and same disconnect happened. Likely was an issue already at the same time.`
- Result date: `2026-06-09`
- Install method: manual Glyph firmware update
- Build command: `./scripts/build-glyph-mk6-quiet.sh`
- Build report reference:
  `docs/runtime_config/phase7a_diagnostic_d5_parsed_result_runtime_routing_build_report_2026-06-09.md`
- Result fixture:
  `docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_parse_status_gated_routing_hardware_failure_2026-06-09.json`
- Nunchuk: NOT_TESTED

## Hardware result table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | UNKNOWN | Not explicitly reported in this user report. |
| BASELINE-001 | baseline | Baseline behavior preserved | FAIL_OR_PARTIAL | Disconnect occurred in user-reported RF5/RF6/LT6 cases. |
| RF5-001 | rf5_paths | Representative RF5 behavior does not cause controller disconnect | FAIL | User report says RF5 caused disconnect. |
| RF6-001 | rf6_paths | Representative RF6 behavior does not cause controller disconnect | FAIL | User report says RF6 caused disconnect. |
| LT6-001 | lt6_paths | Representative LT6 behavior does not cause controller disconnect | FAIL | User report says LT6 caused disconnect. |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | UNKNOWN | Not explicitly reported. |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | UNKNOWN | Not explicitly reported. |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | UNKNOWN | Not explicitly reported. |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | UNKNOWN | Not explicitly reported. |
| PAYLOAD-001 | payload_retention | D2B retained payload bytes remain present | SOURCE_CHECKED | D2B retained payload evidence was present in the prior branch chain. |
| GLOBAL-PARSE-001 | global_parse_result | Global parse result is present in the diagnostic source | SOURCE_CHECKED | Global/static parse result was retained from D3 evidence in this branch lineage. |
| PARSER-CALL-001 | parser_behavior | Parser call exists in global/static initialization path | SOURCE_CHECKED | Parser call is present as in the D5A branch definition. |
| RESOLVER-001 | runtime_resolver | Resolver present | SOURCE_CHECKED | `ResolveActiveRuntimeConfig()` added in this branch lineage. |
| PARSE-STATUS-GATE-001 | parse_status_gate | Runtime routing is gated by parse status Ok | SOURCE_CHECKED | Routing to source-owned alias remains parse-status-gated. |
| SOURCE-OWNED-ROUTING-001 | runtime_routing | Analog runtime output lookup is routed through resolver-selected source-owned view | SOURCE_CHECKED | Routing uses `kPhase7AD5AParseStatusGatedRuntimeConfigView`. |
| NO-PARSED-TABLES-001 | parsed_table_scope | Parsed table materialization is not added | SOURCE_CHECKED | True parsed-table data routing remains deferred. |
| NO-STORAGE-001 | storage | Runtime-config storage not added | SOURCE_CHECKED | No runtime storage change in this branch set. |
| NO-WRITE-001 | webserial_or_write | No WebSerial/device write added | SOURCE_CHECKED | No runtime write path or WebSerial behavior change. |
| NO-FLASH-001 | flashing_automation | No firmware flashing automation | SOURCE_CHECKED | No flashing automation path change. |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | Not tested in this report. |

## Diagnostic interpretation

- D5A combination now reproduces disconnects for RF5, RF6, and LT6 in user reports.
- This points to the interaction of parse-status-gated resolver/runtime-config lookup and
  special analog override paths.
- H5 combination interaction is elevated.
- True parsed-table-data routing remains untested.
- Root cause is still not proven.
- Failed activation branch remains abandoned and must not merge.
- Next recommended diagnostic: `D5A-N1 direct canonical source-owned view after parse-status gate`.

## Limitations and non-claims

- result is user-reported
- no automated device telemetry
- no public release claim
- no release compatibility claim
- no proof of root cause
- no firmware source change on this result branch
- failed activation branch remains abandoned and must not merge
