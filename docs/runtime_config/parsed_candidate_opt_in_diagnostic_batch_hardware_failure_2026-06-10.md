# Parsed Candidate Opt-In Diagnostic Batch Hardware Failure - 2026-06-10

status: HARDWARE_FAIL

branch_under_test: `runtime-config-parsed-candidate-opt-in-diagnostic-batch`

result_branch: `runtime-config-parsed-candidate-opt-in-diagnostic-batch-hardware-failure`

operator_report: "tested, fails. disconnects happen"

## Result

The parsed candidate opt-in activation diagnostic branch failed hardware
testing. The implementation branch must not be merged into `configurator`.

Diagnostic activation was enabled with
`kEnableParsedCandidateActivationDiagnostic = true`. The candidate was intended
and source-checked as equivalent to the source-owned baseline before acceptance.
Candidate publication was namespace-scope, not first-triggered from
`ResolveActiveRuntimeConfig()`. The active output path consumed only published
`active_view`.

No runtime-loaded config, storage, write path, WebSerial/device write,
backend/config.pb write behavior, or flashing automation was added. Failure
still occurred after flashing branch firmware. Nunchuk remains NOT_TESTED.

## Hardware Rows

| Row ID | Category | Result | Notes |
| --- | --- | --- | --- |
| BOOT-001 | boot | UNKNOWN | Operator report did not explicitly confirm normal boot. |
| BASELINE-001 | baseline | FAIL | Operator reported hardware failure and disconnects; no pass is claimed. |
| RF5-001 | rf5_routing | UNKNOWN | Operator report did not identify RF5 as the trigger. |
| RF6-001 | rf6_routing | UNKNOWN | Operator report did not identify RF6 as the trigger. |
| LT6-001 | lt6_routing | UNKNOWN | Operator report did not identify LT6 as the trigger. |
| OPT-IN-ACTIVATION-001 | opt_in_activation | FAIL | Parsed candidate opt-in activation branch failed hardware testing. |
| HOT-PATH-001 | hot_path | INVESTIGATE | Direct resolver boundary was preserved, but activation still failed. |
| NO-PARSER-STATUS-READ-001 | invariant | PASS | Checker/source still prove no direct parser-status hot-path read. |
| NO-STORAGE-001 | invariant | PASS | No storage path was introduced. |
| NO-WRITE-001 | invariant | PASS | No firmware write path was introduced. |
| NO-FLASH-001 | invariant | PASS | No flashing automation was introduced. |
| NUNCHUK-001 | nunchuk_scope | NOT_TESTED | Nunchuk remains NOT_TESTED. |

## Conclusions

- `parsed_candidate_opt_in_activation_safe_for_merge`: false
- `implementation_branch_merge_allowed`: false
- `source_owned_active_state_preselection_remains_repair_baseline`: true
- `candidate_materialization_inactive_path_remains_next_safe_baseline`: true
- `low_level_failure_mechanism_proven`: false
- `requires_new_root_cause_analysis`: true

## Narrow Failure Statement

Parsed candidate publication/activation still triggers the disconnect class even
when publication is namespace-scope and the active output path consumes only
published `active_view`.

Do not claim the root cause is parser status hot-path reads. That was avoided
here. The low-level failure mechanism remains unproven.
