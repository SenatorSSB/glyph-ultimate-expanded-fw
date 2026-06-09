# Phase 7A Diagnostic D3 Hardware Plan

Status: TEMPLATE_ONLY

Branch: `phase7a-diagnostic-d3-global-parse-result-only`

Base branch: `phase7a-diagnostic-d2b-retained-payload-bytes`

This plan records pre-hardware intent and required checks for D3 global/static
parser initialization evidence. This branch is evidence-producing only, is not a
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

- Isolate global/static parser initialization from the failed Phase 7A
  activation branch.
- Keep the D2B retained payload bytes.
- Add global parse result only.
- No runtime resolver.
- No runtime output routing to parsed result.
- No runtime behavior change intended.

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
| PARSER-CALL-001 | parser_behavior | Parser call exists only in global/static initialization path | NOT_TESTED |
| NO-RESOLVER-001 | runtime_resolver | Runtime resolver not added | NOT_TESTED |
| NO-RUNTIME-ROUTING-001 | runtime_routing | Parsed result is not routed into runtime output lookup | NOT_TESTED |
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

- If D3 passes, static/global parser initialization alone is unlikely.
- If D3 fails, H1/H4 become strong suspects.
- Root cause is not proven until a follow-up narrowing test confirms the exact
  failure mechanism.

## 6) Caveats

- this branch is not a merge candidate
- no hardware-result claim
- no root-cause claim
- no parser safety claim
- no nunchuk validation claim
- no runtime resolver
- no runtime output routing to parsed result
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
