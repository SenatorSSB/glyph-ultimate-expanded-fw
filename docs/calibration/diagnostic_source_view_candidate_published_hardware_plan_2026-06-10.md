# Diagnostic Source-View Candidate Published Hardware Plan

status: HARDWARE_PLAN
overall_result: NOT_TESTED

branch_under_test: `runtime-config-diagnostic-source-view-candidate-published`

baseline branch: `configurator`

## Purpose

Test whether a RAM-backed candidate `RuntimeConfigView`, materialized from the
already-safe source-owned baseline and published only after validation and
equivalence, is safe on hardware.

This is a hardware plan, not a result. All rows are NOT_TESTED.

## Hardware Plan Rows

| Row ID | Scope | Status |
| --- | --- | --- |
| BOOT-001 | Boot and USB stability | NOT_TESTED |
| BASELINE-001 | Baseline source-owned behavior | NOT_TESTED |
| RF5-001 | RF5 forced-Up / A carrier behavior | NOT_TESTED |
| RF6-001 | RF6 Z-airdodge low magnitude behavior | NOT_TESTED |
| LT6-001 | LT6 down / A carrier behavior | NOT_TESTED |
| ORDINARY-DIR-001 | Ordinary direction behavior | NOT_TESTED |
| NEUTRAL-001 | Neutral behavior | NOT_TESTED |
| UNRELATED-BUTTONS-001 | Unrelated button behavior | NOT_TESTED |
| MODIFIERS-001 | Modifier behavior | NOT_TESTED |
| SOURCE-VIEW-CANDIDATE-MATERIALIZED-001 | Source-owned baseline materialized into RAM-backed candidate | NOT_TESTED |
| CANDIDATE-EQUIVALENCE-001 | Candidate view equivalent to source-owned baseline | NOT_TESTED |
| CANDIDATE-ACTIVE-PUBLICATION-001 | Candidate view published active after validation/equivalence | NOT_TESTED |
| SOURCE-OWNED-FALLBACK-001 | Source-owned baseline fallback remains available | NOT_TESTED |
| HOT-PATH-001 | Hot path remains stable active-view only | NOT_TESTED |
| NO-PARSER-001 | No parser payload activation path | NOT_TESTED |
| NO-STORAGE-001 | No runtime-config storage | NOT_TESTED |
| NO-WRITE-001 | No WebSerial/device/backend write path | NOT_TESTED |
| NO-FLASH-001 | No flashing automation | NOT_TESTED |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |

## Non-Claims

- No hardware result is claimed.
- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Parser payload activation is not implemented.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.
