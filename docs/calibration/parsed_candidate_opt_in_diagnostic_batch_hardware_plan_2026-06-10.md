# Parsed Candidate Opt-In Diagnostic Batch Hardware Plan - 2026-06-10

status: HARDWARE_PLAN_NOT_TESTED

branch: `runtime-config-parsed-candidate-opt-in-diagnostic-batch`

This is a hardware-test plan only. It records no hardware result. Hardware test
is required before merge because parsed candidate opt-in activation can affect
active output behavior. Runtime-loaded config, storage, WebSerial/device write,
backend/config.pb write behavior, and flashing automation remain not
implemented. Nunchuk remains NOT_TESTED.

## Hardware Plan Rows

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
| ACTIVE-STATE-001 | active_state | Active state selector binds to published active view only | NOT_TESTED |
| PUBLICATION-001 | publication | Published active view is selected before output generation | NOT_TESTED |
| CANDIDATE-BRIDGE-001 | candidate_bridge | Source-owned compiled parser fixture materializes candidate state before publication | NOT_TESTED |
| CANDIDATE-EQUIVALENCE-001 | candidate_equivalence | Candidate state is equivalent to source-owned baseline | NOT_TESTED |
| OPT-IN-ACTIVATION-001 | opt_in_activation | Diagnostic opt-in candidate activation behaves as baseline-equivalent published view | NOT_TESTED |
| HOT-PATH-001 | hot_path | Analog hot path consumes only published active view | NOT_TESTED |
| NO-PARSER-STATUS-READ-001 | invariant | No runtime parser status reads in `UpdateAnalogOutputs` | NOT_TESTED |
| NO-STORAGE-001 | invariant | No storage path introduced | NOT_TESTED |
| NO-WRITE-001 | invariant | No firmware write path introduced | NOT_TESTED |
| NO-FLASH-001 | invariant | No flashing automation introduced | NOT_TESTED |
| NUNCHUK-001 | nunchuk_scope | Nunchuk remains NOT_TESTED | NOT_TESTED |

## Scope Notes

- Build evidence is recorded in
  `docs/runtime_config/parsed_candidate_opt_in_diagnostic_batch_build_report_2026-06-10.md`.
- This plan must not be promoted to a hardware result without an explicit
  operator result packet.
- The diagnostic candidate is source-owned/static and not runtime-loaded.
