# Active Storage Publication Model Hardware Plan

status: PLAN_ONLY

branch_under_test: `runtime-config-active-storage-publication-model`

baseline branch: `configurator`

hardware_test_required_before_merge: false

## Purpose

Record the hardware-test row set for any later branch that activates dedicated
active storage publication, while marking this branch as source-scaffold-only.

No hardware result is claimed by this plan. No hardware test is required before
merge for this branch because active behavior remains source-owned baseline and
dedicated active storage is not active.

## Evidence Matrix

| Case | Result |
| --- | --- |
| source-owned active-state preselection | HARDWARE_PASS |
| parsed/candidate present, source-owned active view | HARDWARE_PASS |
| parsed candidate.view active | HARDWARE_FAIL |
| source-owned-materialized candidate.view active | HARDWARE_FAIL |

## Hardware Rows

| Row ID | Scope | Status |
| --- | --- | --- |
| BOOT-001 | Boot and USB stability | NOT_TESTED |
| BASELINE-001 | Baseline source-owned behavior | NOT_TESTED |
| RF5-001 | RF5 forced-Up / A carrier behavior | NOT_TESTED |
| RF6-001 | RF6 Z-airdodge low magnitude behavior | NOT_TESTED |
| LT6-001 | LT6 down / A carrier behavior | NOT_TESTED |
| ORDINARY-DIR-001 | Ordinary direction behavior | NOT_TESTED |
| NEUTRAL-001 | Neutral behavior | NOT_TESTED |
| MODIFIERS-001 | Modifier behavior | NOT_TESTED |
| DEDICATED-ACTIVE-STORAGE-001 | Dedicated active storage active publication | NOT_TESTED |
| CANDIDATE-NOT-ACTIVE-001 | Candidate buffer remains non-active | NOT_TESTED |
| SOURCE-OWNED-FALLBACK-001 | Source-owned fallback behavior | NOT_TESTED |
| HOT-PATH-001 | Hot path remains stable active-view only | NOT_TESTED |
| NO-PARSER-ACTIVE-PUBLICATION-001 | No parser/candidate active publication | NOT_TESTED |
| NO-STORAGE-001 | No runtime-config storage | NOT_TESTED |
| NO-WRITE-001 | No WebSerial/device/backend write path | NOT_TESTED |
| NO-FLASH-001 | No flashing automation | NOT_TESTED |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |

## Conclusions

- `candidate_backed_active_runtime_view_safe`: `false`
- `candidate_buffer_may_validate_values`: `true`
- `candidate_buffer_must_not_be_active`: `true`
- `dedicated_active_storage_required`: `true`
- `low_level_failure_mechanism_proven`: `false`
- `runtime_loaded_config_implemented`: `false`
- `storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Candidate active publication is not implemented.
- Dedicated active storage active publication is not implemented on this
  branch.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.
