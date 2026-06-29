# Diagnostic Generated Source-Owned Baseline Active Hardware Plan - 2026-06-29

Status: PLAN_ONLY.

Branch under test:
`runtime-config-diagnostic-generated-source-owned-baseline-active`

This plan gates the diagnostic branch that selects the generated source-owned
baseline-equivalent `RuntimeConfigView` as active. It records no hardware
result yet.

## Required Result Boundary

- `hardware_test_required_before_merge`: `true`
- `generated_source_owned_baseline_active`: `true`
- `generated_baseline_equivalent_to_source_owned_baseline`: `true`
- `ram_backed_active_table_publication`: `false`
- `candidate_view_published_active`: `false`
- `candidate_owned_table_pointer_published_active`: `false`
- `parser_payload_path_implemented`: `false`
- `runtime_loaded_config_implemented`: `false`
- `storage_implemented`: `false`
- `webserial_device_write_implemented`: `false`
- `backend_config_pb_write_path_implemented`: `false`
- `flashing_automation_implemented`: `false`
- `nunchuk_status`: `NOT_TESTED`

## Evidence Basis

- Source-owned active-state preselection: `HARDWARE_PASS`.
- Parsed/candidate machinery present while source-owned active view remains
  published: `HARDWARE_PASS`.
- Parsed candidate active view: `HARDWARE_FAIL`.
- Source-owned-materialized candidate active view: `HARDWARE_FAIL`.
- Dedicated active storage active view: `HARDWARE_FAIL`.

## Rows

| Row | Status | Notes |
| --- | --- | --- |
| BOOT-001 | NOT_TESTED | Device boots and enumerates. |
| BASELINE-001 | NOT_TESTED | Baseline movement matches expected non-nunchuk scope. |
| RF5-001 | NOT_TESTED | RF5 forced-Up behavior preserved. |
| RF6-001 | NOT_TESTED | RF6 Z/low-magnitude behavior preserved. |
| LT6-001 | NOT_TESTED | LT6 Down+A behavior preserved. |
| ORDINARY-DIR-001 | NOT_TESTED | Ordinary directions preserved. |
| NEUTRAL-001 | NOT_TESTED | Neutral output preserved. |
| UNRELATED-BUTTONS-001 | NOT_TESTED | Unrelated digital buttons preserved. |
| MODIFIERS-001 | NOT_TESTED | Modifier table behavior preserved. |
| GENERATED-SOURCE-OWNED-BASELINE-ACTIVE-001 | NOT_TESTED | Generated source-owned baseline view is active. |
| GENERATED-BASELINE-EQUIVALENT-001 | NOT_TESTED | Generated baseline remains equivalent to source-owned baseline. |
| RAM-BACKED-ACTIVE-TABLE-NOT-USED-001 | NOT_TESTED | Active table pointers do not target RAM-backed storage. |
| CANDIDATE-NOT-ACTIVE-001 | NOT_TESTED | `candidate.view` is not active. |
| HOT-PATH-001 | NOT_TESTED | Analog hot path consumes only resolved active view. |
| NO-PARSER-001 | NOT_TESTED | No parser payload path is active. |
| NO-STORAGE-001 | NOT_TESTED | No runtime-config storage is implemented. |
| NO-WRITE-001 | NOT_TESTED | No WebSerial/device/backend write path is implemented. |
| NO-FLASH-001 | NOT_TESTED | No firmware flashing automation is implemented. |
| NUNCHUK-001 | NOT_TESTED | Nunchuk remains NOT_TESTED. |

## Merge Gate

Do not merge this diagnostic source into `configurator` unless a later result
packet records a preserved `HARDWARE_PASS` for the applicable non-nunchuk scope.
Nunchuk remains NOT_TESTED unless explicitly exercised.
