# Phase 7A Diagnostic D4 Hardware Plan

Status: TEMPLATE_ONLY

Branch: `phase7a-diagnostic-d4-runtime-resolver-only`

This branch is evidence-producing only and is not a hardware result. No conclusion can be drawn until a separate hardware-result branch records tests.

## 1) Build Artifact Identity

| Field | Value |
| --- | --- |
| Build command used | `./scripts/build-glyph-mk6-quiet.sh` |
| Firmware artifact path | `.pio/build/glyph_mk6/firmware.uf2` (recorded in build report) |
| Firmware artifact SHA-256 | Record in build report |
| Commit SHA under test | Fill after local build |
| Tester | Fill |
| Test date | Fill |

## 2) Intent

- isolate resolver/reference pathway selection in runtime analog path with no parser/payload/config activation behavior
- no runtime behavior change intended
- no runtime-config storage/WebSerial/device write/bootloader/flash paths
- no nunchuk validation

## 3) Planned Checks (all rows start as `NOT_TESTED`)

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | NOT_TESTED |
| BASELINE-001 | baseline | Baseline behavior preserved | NOT_TESTED |
| RF5-001 | rf5_paths | Representative RF5 behaviors remain preserved; no disconnect expected | NOT_TESTED |
| RF6-001 | rf6_paths | Representative RF6 behaviors remain preserved; no disconnect expected | NOT_TESTED |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | NOT_TESTED |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | NOT_TESTED |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | NOT_TESTED |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | NOT_TESTED |
| NO-PARSER-001 | parser_behavior | Parser is not called in firmware runtime path | NOT_TESTED |
| NO-PAYLOAD-001 | runtime_payload | No compiled payload is added or parsed | NOT_TESTED |
| NO-GLOBAL-PARSE-001 | parser_lifecycle | No global parse result is added | NOT_TESTED |
| RESOLVER-001 | runtime_resolver | Runtime resolver wrapper is present and only selects source-owned baseline or known-good fallback | NOT_TESTED |
| NO-STORAGE-001 | storage | Runtime-config storage not added | NOT_TESTED |
| NO-WRITE-001 | webserial_or_write | No WebSerial/device write added | NOT_TESTED |
| NO-FLASH-001 | flashing_automation | No firmware flashing automation paths used | NOT_TESTED |
| NUNCHUK-001 | nunchuk_scope | Nunchuk behavior is not explicitly tested in this branch | NOT_TESTED |

## 4) Nunchuk Scope

- Nunchuk scope for this branch: `NOT_TESTED`.
- This branch does not perform nunchuk validation.

## 5) Caveats

- no runtime behavior change intended
- no parser call
- no runtime parser activation
- no runtime parser result global
- no runtime resolver side effects beyond table-view selection
- no parsed runtime-config payload bytes retained in firmware image
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
- no hardware-result claim
- nunchuk `NOT_TESTED`
