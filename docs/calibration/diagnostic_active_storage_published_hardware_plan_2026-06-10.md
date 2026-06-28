# Diagnostic Active Storage Published Hardware Plan

status: PLAN_ONLY

branch_under_test: `runtime-config-diagnostic-active-storage-published`

baseline branch: `configurator`

hardware_test_required_before_merge: true

## Purpose

Record the hardware-test row set for the diagnostic that publishes only a
source-owned-equivalent dedicated active-storage view as the active runtime
config view.

No hardware result is claimed by this plan. All rows are NOT_TESTED until the
operator executes the diagnostic firmware and records a separate hardware result.

## Evidence Matrix

| Case | Result |
| --- | --- |
| source-owned active-state preselection | HARDWARE_PASS |
| parsed/candidate machinery present, source-owned active view published | HARDWARE_PASS |
| parsed candidate.view published active | HARDWARE_FAIL |
| source-owned-materialized candidate.view published active | HARDWARE_FAIL |

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
| UNRELATED-BUTTONS-001 | Unrelated digital buttons | NOT_TESTED |
| MODIFIERS-001 | Modifier behavior | NOT_TESTED |
| DEDICATED-ACTIVE-STORAGE-MATERIALIZED-001 | Dedicated active storage materialized from source-owned baseline | NOT_TESTED |
| DEDICATED-ACTIVE-STORAGE-EQUIVALENT-001 | Dedicated active storage equivalent to source-owned baseline | NOT_TESTED |
| DEDICATED-ACTIVE-STORAGE-PUBLISHED-001 | Dedicated active storage published active | NOT_TESTED |
| CANDIDATE-NOT-ACTIVE-001 | Candidate buffer remains non-active | NOT_TESTED |
| SOURCE-OWNED-FALLBACK-001 | Source-owned fallback behavior | NOT_TESTED |
| HOT-PATH-001 | Hot path remains stable active-view only | NOT_TESTED |
| NO-PARSER-001 | Parser path absent from this diagnostic | NOT_TESTED |
| NO-STORAGE-001 | No runtime-config storage | NOT_TESTED |
| NO-WRITE-001 | No WebSerial/device/backend write path | NOT_TESTED |
| NO-FLASH-001 | No flashing automation | NOT_TESTED |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |

## Conclusions

- `active_behavior_changed`: `true`
- `hardware_test_required_before_merge`: `true`
- `dedicated_active_storage_active`: `true`
- `candidate_view_published_active`: `false`
- `candidate_owned_table_pointer_published_active`: `false`
- `published_active_view_when_equivalent`: `dedicated active storage view`
- `fallback_active_view`: `kSourceOwnedCurrentBaselineRuntimeConfig`
- `runtime_loaded_config_implemented`: `false`
- `storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Parser payload path is not implemented.
- Candidate active publication is not implemented.
- Nunchuk remains NOT_TESTED.
