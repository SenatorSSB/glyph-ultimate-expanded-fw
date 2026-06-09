# Glyph Phase 7A Diagnostic D5A-N2 Hardware Result - 2026-06-09

status: USER_REPORTED_PASS

## Purpose and scope

This document records the user-reported hardware result for Phase 7A
Diagnostic D5A-N2 resolver without parse-status hot-path read. D5A-N2 tests
whether removing the runtime hot-path read/branch on
`kPhase7AD3GlobalParseResult.status` while keeping the resolver call from
`UpdateAnalogOutputs(...)` and the canonical source-owned fallback contract
avoids the RF5/RF6/LT6 disconnect class.

This result narrows the likely trigger to the parse-status hot-path read, but
it does not prove the low-level mechanism, parser safety in every activation
design, failed-branch recoverability, public release compatibility, or nunchuk
behavior.

## Branch and result

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Diagnostic branch tested:
  `phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read`
- Result branch:
  `phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read-hardware-result`
- Result source: user-reported
- Exact user report text: `flashed n2. It works. No disconnects anymore.`
- Result date: `2026-06-09`
- Install method: manual Glyph firmware update
- Build command: `./scripts/build-glyph-mk6-quiet.sh`
- Build report reference:
  `docs/runtime_config/phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_build_report_2026-06-09.md`
- Result fixture:
  `docs/calibration/fixtures/glyph_phase7a_diagnostic_d5a_n2_resolver_without_parse_status_read_hardware_result_2026-06-09.json`
- Source/build provenance: local D5A-N2 branch and build process only
- Nunchuk: NOT_TESTED

## Hardware result table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | PASS | User-reported pass. |
| BASELINE-001 | baseline | Baseline behavior preserved | PASS | User-reported pass. |
| RF5-001 | rf5_paths | Representative RF5 behavior does not cause controller disconnect | PASS | No disconnect reported. |
| RF6-001 | rf6_paths | Representative RF6 behavior does not cause controller disconnect | PASS | No disconnect reported. |
| LT6-001 | lt6_paths | Representative LT6 behavior does not cause controller disconnect | PASS | No disconnect reported. |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | UNKNOWN | Not separately reported. |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | UNKNOWN | Not separately reported. |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | UNKNOWN | Not separately reported. |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | UNKNOWN | Not separately reported. |
| PAYLOAD-001 | payload_retention | D2B retained payload bytes remain present | SOURCE_CHECKED | D2B retained payload bytes remain present. |
| GLOBAL-PARSE-001 | global_parse_result | Global parse result is present in the diagnostic source | SOURCE_CHECKED | Global/static parse result present. |
| PARSER-CALL-001 | parser_behavior | Parser call exists only in global/static initialization path | SOURCE_CHECKED | Parser called by global/static initialization. |
| RESOLVER-001 | runtime_resolver | Resolver is present | SOURCE_CHECKED | Resolver call remains in `UpdateAnalogOutputs(...)`. |
| PARSE-STATUS-READ-001 | parse_status_read | Runtime hot-path read on parse status is removed | SOURCE_CHECKED | Parse-status hot-path read removed from runtime hot path. |
| SOURCE-OWNED-ROUTING-001 | runtime_routing | Canonical source-owned runtime config return remains in place | SOURCE_CHECKED | Canonical source-owned runtime config return remains in place. |
| FALLBACK-001 | fallback | Fallback remains source-owned current baseline or known-good runtime config | SOURCE_CHECKED | Fallback remains source-owned current baseline or known-good runtime config. |
| NO-PARSED-TABLES-001 | parsed_table_scope | Parsed table materialization is not added | SOURCE_CHECKED | No parsed table materialization added. |
| NO-STORAGE-001 | storage | Runtime-config storage not added | SOURCE_CHECKED | No runtime-config storage. |
| NO-WRITE-001 | webserial_or_write | WebSerial/device write not added | SOURCE_CHECKED | No WebSerial/device write. |
| NO-FLASH-001 | flashing_automation | No firmware flashing automation paths used | SOURCE_CHECKED | No firmware flashing automation. |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | Not tested. |

## Source/build checks retained

The following claims are source/build-checked, not hardware telemetry:

- D2B retained payload bytes remain present
- global/static parse result remains present
- parser called by global/static initialization
- resolver call from `UpdateAnalogOutputs(...)` remains present
- parse-status hot-path read removed from runtime hot path
- canonical source-owned runtime config return remains in place
- no parsed table materialization
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
- no runtime-output routing to parsed result

## Diagnostic interpretation

- D5A-N2 passed.
- RF5/RF6/LT6 disconnects were not observed.
- The parse-status hot-path read/branch on `kPhase7AD3GlobalParseResult.status`
  is the likely trigger.
- The separate RuntimeConfigView alias remains reduced as a suspect.
- D3 global/static parse result alone remains safe based on D3.
- D4 resolver alone remains safe based on D4.
- The low-level root cause mechanism is not proven.
- Failed activation branch must not merge.
- Future runtime activation must not read parser result state from
  UpdateAnalogOutputs(...) or the analog hot-path resolver.

## Limitations and non-claims

- result is user-reported
- no automated device telemetry
- no nunchuk validation
- no public release claim
- no release compatibility claim
- no proof of root cause
- no claim that the failed branch is recoverable
