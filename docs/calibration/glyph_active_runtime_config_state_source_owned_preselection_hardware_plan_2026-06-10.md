# Glyph Active Runtime Config State Source-Owned Preselection Hardware Result - 2026-06-10

status: HARDWARE_PASS

branch: `runtime-active-config-state-source-owned-preselection`
result branch: `runtime-active-config-state-source-owned-preselection-hardware-result`

This record captures the operator-reported hardware pass for the source-owned
active runtime config preselection scaffold. The scope stays limited to the
rows below and does not claim runtime-loaded config, runtime-config storage,
parser hot-path status reads, parsed table materialization, WebSerial/device
write, flashing automation, or nunchuk validation.

## 1) Result identity

| Field | Value |
| --- | --- |
| Result source | operator-recorded |
| Exact operator report text | `All worked on branch runtime-active-config-state-source-owned-preselection when I built and flashed.` |
| Result date | `2026-06-10` |
| Branch under test | `runtime-active-config-state-source-owned-preselection` |
| Result branch | `runtime-active-config-state-source-owned-preselection-hardware-result` |
| Build command (canonical) | `pio run -e glyph_mk6` |
| Build source | local build artifact already recorded in the build report |
| Build report | `docs/runtime_config/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md` |
| Commit SHA under test | unknown |
| Firmware artifact path | unknown |
| Firmware artifact SHA-256 | unknown |
| Firmware source changed in implementation branch | `true` |
| Firmware source changed in result branch | `false` |
| Parser status read in analog hot path | `false` |
| Parser call added | `false` |
| Parsed table materialization added | `false` |
| Storage/write/WebSerial/flashing added | `false` |
| Nunchuk status | `NOT_TESTED` |

## 2) Hardware result rows

| Row ID | Category | Planned check | Result |
| --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | PASS |
| BASELINE-001 | baseline | Baseline analog/digital routing remains stable | PASS |
| RF5-001 | rf5_routing | RF5 path behavior remains as baseline | PASS |
| RF6-001 | rf6_routing | RF6 path behavior remains as baseline | PASS |
| LT6-001 | lt6_routing | LT6 path behavior remains as baseline | PASS |
| ORDINARY-DIR-001 | ordinary_direction | Ordinary direction outputs remain preserved | PASS |
| NEUTRAL-001 | neutral | Neutral output behavior remains preserved | PASS |
| UNRELATED-BUTTONS-001 | unrelated_buttons | Unrelated button paths remain preserved | PASS |
| MODIFIERS-001 | modifiers | Modifier table routing remains preserved | PASS |
| ACTIVE-STATE-001 | active_state | Active state selector binds to `active_view` only in hot path | PASS |
| HOT-PATH-001 | hot_path | Analog hot-path has no parser-status read and no branch on parser state | PASS |
| NO-PARSER-STATUS-READ-001 | invariant | No runtime parser status reads in `UpdateAnalogOutputs` | PASS |
| NO-PARSED-TABLES-001 | invariant | No parsed table materialization introduced | PASS |
| NO-STORAGE-001 | invariant | No storage path introduced | PASS |
| NO-WRITE-001 | invariant | No firmware write path introduced | PASS |
| NO-FLASH-001 | invariant | No flashing automation introduced | PASS |
| NUNCHUK-001 | nunchuk_scope | Nunchuk remains NOT_TESTED | NOT_TESTED |

## 3) Result notes and caveats

- RF5 did not disconnect.
- RF6 did not disconnect.
- LT6 did not disconnect.
- General baseline behavior remained intact.
- Source-owned active-state indirection is safe enough to become the repair
  architecture basis.
- The build report keeps artifact hashes as local observations only; they are
  not checker gates.
- No nunchuk validation is claimed.

## 4) Rollback and scope notes

- Roll back by reverting to `configurator` or this branch predecessor if any
  required check fails.
- This is a recorded hardware result, not a plan.
- No parser, no runtime table materialization, no storage, no write, and no
  flashing automation were introduced in this scaffold branch.
