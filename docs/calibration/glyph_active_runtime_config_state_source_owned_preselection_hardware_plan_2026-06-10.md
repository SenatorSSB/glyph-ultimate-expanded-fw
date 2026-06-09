# Glyph Active Runtime Config State Source-Owned Preselection Hardware Plan

status: PLAN

branch: `runtime-active-config-state-source-owned-preselection`

This plan is a dedicated hardware-validation template for this branch.
Nunchuk scope is explicitly `NOT_TESTED`.

## 1) Build identity

| Field | Value |
| --- | --- |
| Build command (canonical) | `pio run -e glyph_mk6` |
| Firmware artifact path | unknown |
| Firmware artifact SHA-256 | unknown |
| Commit SHA under test | unknown |
| Commit branch | runtime-active-config-state-source-owned-preselection |
| Test date | unknown |

## 2) Planned checks

All rows start as `NOT_TESTED`.

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | NOT_TESTED |
| BASELINE-001 | baseline | Baseline analog/digital routing remains stable | NOT_TESTED |
| RF5-001 | rf5_routing | RF5 path behavior remains as baseline | NOT_TESTED |
| RF6-001 | rf6_routing | RF6 path behavior remains as baseline | NOT_TESTED |
| LT6-001 | lt6_routing | LT6 path behavior remains as baseline | NOT_TESTED |
| ORDINARY-DIR-001 | ordinary_direction | Ordinary direction outputs remain preserved | NOT_TESTED |
| NEUTRAL-001 | neutral | Neutral output behavior remains preserved | NOT_TESTED |
| UNRELATED-BUTTONS-001 | unrelated_buttons | Unrelated button paths remain preserved | NOT_TESTED |
| MODIFIERS-001 | modifiers | Modifier table routing remains preserved | NOT_TESTED |
| ACTIVE-STATE-001 | active_state | Active state selector binds to `active_view` only in hot path | NOT_TESTED |
| HOT-PATH-001 | hot_path | Analog hot-path has no parser-status read and no branch on parser state | NOT_TESTED |
| NO-PARSER-STATUS-READ-001 | invariant | No runtime parser status reads in `UpdateAnalogOutputs` | NOT_TESTED |
| NO-PARSED-TABLES-001 | invariant | No parsed table materialization introduced | NOT_TESTED |
| NO-STORAGE-001 | invariant | No storage path introduced | NOT_TESTED |
| NO-WRITE-001 | invariant | No firmware write path introduced | NOT_TESTED |
| NO-FLASH-001 | invariant | No flashing automation introduced | NOT_TESTED |
| NUNCHUK-001 | nunchuk_scope | Nunchuk remains NOT_TESTED | NOT_TESTED |

## 3) Rollback and scope notes

- Roll back by reverting to `configurator` or this branch predecessor if any
  required check fails.
- This is a pre-run plan; rows are intentionally not passed until an operator
  executes hardware checks.
- No parser, no runtime table materialization, no storage, no write, and no
  flashing automation should be introduced in this scaffold branch.
