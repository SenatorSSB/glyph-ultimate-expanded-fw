# Phase 7A Diagnostic D5 Hardware Plan

Status: TEMPLATE_ONLY

Branch: `phase7a-diagnostic-d5-parsed-result-runtime-routing`

Base branch: `phase7a-diagnostic-d3-global-parse-result-only`

This plan records pre-hardware intent and required checks for D5 parsed-result
runtime-routing evidence. This branch is evidence-producing only, is not a
merge candidate, and is not a hardware result. Hardware result must be recorded
separately.

## 1) Build Artifact Identity

| Field | Value |
| --- | --- |
| Build command used | `./scripts/build-glyph-mk6-quiet.sh` |
| Firmware artifact path | `.pio/build/glyph_mk6/firmware.uf2` (recorded in build report) |
| Firmware artifact SHA-256 | Record from build report when testing |
| Commit SHA under test | Fill after local build/commit |
| Tester | Fill |
| Test date | Fill |

## 2) Intent

- Test the controlled combination after D2B, D3, and D4 passed in isolation.
- Keep the D2B retained payload bytes.
- Keep the D3 global/static parse result.
- Add resolver logic.
- Route analog runtime-config lookup through the parsed-result
  resolver-selected view.
- No storage/write/flashing behavior.
- No expected output value change.

## 3) Planned Checks (all rows start as `NOT_TESTED`)

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | NOT_TESTED |
| BASELINE-001 | baseline | Baseline behavior preserved | NOT_TESTED |
| RF5-001 | rf5_paths | Representative RF5 behavior does not cause controller disconnect | NOT_TESTED |
| RF6-001 | rf6_paths | Representative RF6 behavior does not cause controller disconnect | NOT_TESTED |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | NOT_TESTED |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | NOT_TESTED |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | NOT_TESTED |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | NOT_TESTED |
| PAYLOAD-001 | payload_retention | D2B retained payload bytes remain present | NOT_TESTED |
| GLOBAL-PARSE-001 | global_parse_result | Global parse result is present in the diagnostic source | NOT_TESTED |
| PARSER-CALL-001 | parser_behavior | Parser call exists in global/static initialization path | NOT_TESTED |
| RESOLVER-001 | runtime_resolver | Resolver is present | NOT_TESTED |
| PARSED-ROUTING-001 | runtime_routing | Analog runtime output lookup is routed through resolver-selected parsed view | NOT_TESTED |
| FALLBACK-001 | fallback | Fallback remains source-owned current baseline or known-good runtime config | NOT_TESTED |
| NO-STORAGE-001 | storage | Runtime-config storage not added | NOT_TESTED |
| NO-WRITE-001 | webserial_or_write | WebSerial/device write not added | NOT_TESTED |
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

## 5) Diagnostic Interpretation

- If D5 passes, the failed branch likely depended on something more specific
  than parsed-result routing alone.
- If D5 fails, parsed-result runtime routing becomes a strong suspect and
  should be narrowed further before any repair.

## 6) Caveats

- this branch is not a merge candidate
- no hardware-result claim
- no root-cause claim
- no parser safety claim
- no nunchuk validation claim
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
- artifact hashes are local observations only, not checker gates
