# Phase 7A Diagnostic D5A-N2 Hardware Plan

Status: TEMPLATE_ONLY

Branch: `phase7a-diagnostic-d5a-n2-resolver-without-parse-status-read`

Base branch: `phase7a-diagnostic-d5a-n1-direct-source-view-after-parse-gate`

This plan records pre-hardware intent and required checks for D5A-N2.
Hardware result required: yes, focus on RF5/RF6/LT6 disconnect reproduction.
This branch is evidence-producing only, is not a merge candidate, and is not a
hardware result. Hardware result must be recorded separately.

## 1) Build Artifact Identity

| Field | Value |
| --- | --- |
| Build command used | `pio run -e glyph_mk6` |
| Firmware artifact path | `.pio/build/glyph_mk6/firmware.uf2` (recorded in build report) |
| Firmware artifact SHA-256 | Record from build report when testing |
| Commit SHA under test | Fill after local build/commit |
| Tester | Fill |
| Test date | Fill |

## 2) Intent

- Keep D2B retained payload bytes.
- Keep D3 global parse result and parser call.
- Keep resolver routing call from `UpdateAnalogOutputs(...)`.
- Remove parser-status hot-path read/branch in `ResolveActiveRuntimeConfig()`.
- Keep direct canonical source-owned config return with fallback to known-good.
- Do not materialize parsed tables.
- Do not use parsed tables as runtime data routing in this branch.
- No storage/write/flashing behavior.
- Focus hardware checks on RF5/RF6/LT6 disconnect reproduction.

## 3) Planned Checks (all rows start as `NOT_TESTED`)

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | NOT_TESTED |
| BASELINE-001 | baseline | Baseline behavior preserved | NOT_TESTED |
| RF5-001 | rf5_paths | Representative RF5 behavior does not cause controller disconnect | NOT_TESTED |
| RF6-001 | rf6_paths | Representative RF6 behavior does not cause controller disconnect | NOT_TESTED |
| LT6-001 | lt6_paths | Representative LT6 behavior does not cause controller disconnect | NOT_TESTED |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | NOT_TESTED |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | NOT_TESTED |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | NOT_TESTED |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | NOT_TESTED |
| PAYLOAD-001 | payload_retention | D2B retained payload bytes remain present | NOT_TESTED |
| GLOBAL-PARSE-001 | global_parse_result | Global parse result is present in the diagnostic source | NOT_TESTED |
| PARSER-CALL-001 | parser_behavior | Parser call exists in global/static initialization path | NOT_TESTED |
| RESOLVER-001 | runtime_resolver | Resolver is present | NOT_TESTED |
| PARSE-STATUS-READ-001 | parse_status_read | Resolver hot-path does not branch on `ParseStatus::Ok` | NOT_TESTED |
| SOURCE-OWNED-ROUTING-001 | runtime_routing | Analog runtime output lookup is routed through direct canonical source-owned view after validation fallback | NOT_TESTED |
| FALLBACK-001 | fallback | Fallback remains source-owned baseline or known-good runtime config | NOT_TESTED |
| NO-PARSED-TABLES-001 | parsed_table_scope | Parsed table materialization is not added | NOT_TESTED |
| NO-STORAGE-001 | storage | Runtime-config storage not added | NOT_TESTED |
| NO-WRITE-001 | webserial_or_write | No WebSerial/device write added | NOT_TESTED |
| NO-FLASH-001 | flashing_automation | No firmware flashing automation paths used | NOT_TESTED |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED |

Allowed result statuses:
- `PASS`
- `FAIL`
- `NOT_TESTED`
- `BLOCKED`
- `USER_ACCEPTED_RISK`

## 4) Nunchuk Scope

- Nunchuk scope for this branch: `NOT_TESTED`.
- This branch does not perform nunchuk validation.

## 5) Caveats

- this branch is not a merge candidate
- no hardware-result claim
- no root-cause claim
- no parser safety claim
- no nunchuk validation claim
- no true parsed-result data routing
- no parsed table materialization
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
- artifact hashes are local observations only, not checker gates
- artifact hashes are not checker gates
- nunchuk NOT_TESTED
