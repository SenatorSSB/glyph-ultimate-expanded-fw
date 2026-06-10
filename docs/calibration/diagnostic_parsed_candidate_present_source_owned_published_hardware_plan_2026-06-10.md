# Diagnostic Parsed Candidate Present, Source-Owned Published Hardware Plan

status: HARDWARE_PLAN_NOT_TESTED

branch: `runtime-config-diagnostic-parsed-candidate-present-source-owned-published`

baseline branch: `configurator`

## Purpose

Test whether parsed-candidate source presence, parser bridge execution,
candidate materialization, and equivalence validation cause hardware disconnects
when the published active runtime view is still source-owned baseline.

This is a plan only. It records no hardware result.

## Required Result Rows

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
| PARSED-CANDIDATE-PRESENT-001 | Parsed candidate present and initialized | NOT_TESTED |
| SOURCE-OWNED-PUBLISHED-001 | Source-owned baseline published active | NOT_TESTED |
| HOT-PATH-001 | Hot path remains stable active-view only | NOT_TESTED |
| NO-CANDIDATE-ACTIVE-PUBLICATION-001 | Candidate view is not active | NOT_TESTED |
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
- Candidate active publication is not implemented.
- Nunchuk remains NOT_TESTED.

