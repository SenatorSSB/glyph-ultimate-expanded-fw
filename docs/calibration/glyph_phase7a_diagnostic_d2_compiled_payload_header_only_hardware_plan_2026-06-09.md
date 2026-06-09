# Phase 7A Diagnostic D2 Hardware Plan

Status: TEMPLATE_ONLY

Branch: `phase7a-diagnostic-d2-compiled-payload-header-only`

This plan records pre-hardware intent and required checks for D2.
This branch is evidence-producing only and is not a hardware result.

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

- Isolate static image/rodata/layout effect from compiled payload header bytes only.
- D2A is selected: payload header exists in source only, not included by firmware TU.
- No runtime behavior change intended.

## 3) Planned Checks (all rows start as `NOT_TESTED`)

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | NOT_TESTED |
| BASELINE-001 | baseline | Baseline behavior preserved | NOT_TESTED |
| RF5-001 | rf5_paths | Representative RF5 behaviors remain preserved | NOT_TESTED |
| RF6-001 | rf6_paths | Representative RF6 behaviors remain preserved | NOT_TESTED |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | NOT_TESTED |
| NEUTRAL-001 | neutral_state | Neutral behavior remains preserved | NOT_TESTED |
| UNRELATED-BUTTONS-001 | buttons | Unrelated buttons remain preserved | NOT_TESTED |
| MODIFIERS-001 | modifiers | Representative modifiers remain preserved | NOT_TESTED |
| NO-PARSER-001 | parser_behavior | Parser is not called in firmware runtime path | NOT_TESTED |
| NO-RESOLVER-001 | runtime_resolver | Runtime resolver not added | NOT_TESTED |
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

## 5) Caveats

- no runtime behavior change intent
- no runtime resolver/path changes
- no parser call
- no runtime-config storage
- no WebSerial/device write
- no firmware flashing automation
