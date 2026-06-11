# Diagnostic Source-View Candidate Published Hardware Failure - 2026-06-10

status: HARDWARE_FAIL
overall_result: HARDWARE_FAIL

branch_under_test: `runtime-config-diagnostic-source-view-candidate-published`
result_branch: `runtime-config-diagnostic-source-view-candidate-published-hardware-failure`

operator_report: `tested, failed. same disconnects happen. I reflashed an older working version for use.`

## Result Scope

This result records that publishing a candidate-backed `RuntimeConfigView` /
candidate-backed runtime table pointers as the active runtime view reproduces
the disconnect class, even when the candidate is materialized from
`kSourceOwnedCurrentBaselineRuntimeConfig`, validated, and checked equivalent to
the source-owned baseline before publication.

Candidate-backed active runtime view publication is unsafe.

Parser payload parsing is not required to reproduce the failure. No parser
payload path is used, no `ParseUltimateRuntimeConfigPayload(...)` call exists,
and no `UltimateRuntimeConfigParser` include/use exists on the implementation
branch under test.

Candidate materialization presence alone is not sufficient to reproduce the
disconnect based on the prior parsed-candidate-present/source-owned-published
diagnostic hardware pass on
`runtime-config-diagnostic-parsed-candidate-present-source-owned-published`,
where parsed candidate machinery was present but the source-owned baseline
remained the published active view.

The low-level failure mechanism is not proven.

## Hardware Result Rows

| Row ID | Scope | Status |
| --- | --- | --- |
| BOOT-001 | Boot and USB stability | UNKNOWN |
| BASELINE-001 | Baseline source-owned behavior | FAIL |
| RF5-001 | RF5 forced-Up / A carrier behavior | UNKNOWN |
| RF6-001 | RF6 Z-airdodge low magnitude behavior | UNKNOWN |
| LT6-001 | LT6 down / A carrier behavior | UNKNOWN |
| ORDINARY-DIR-001 | Ordinary direction behavior | UNKNOWN |
| NEUTRAL-001 | Neutral behavior | UNKNOWN |
| UNRELATED-BUTTONS-001 | Unrelated button behavior | UNKNOWN |
| MODIFIERS-001 | Modifier behavior | UNKNOWN |
| SOURCE-VIEW-CANDIDATE-MATERIALIZED-001 | Source-owned baseline materialized into RAM-backed candidate | PASS |
| CANDIDATE-EQUIVALENCE-001 | Candidate view equivalent to source-owned baseline | PASS |
| CANDIDATE-ACTIVE-PUBLICATION-001 | Candidate view published active after validation/equivalence | FAIL |
| SOURCE-OWNED-FALLBACK-001 | Source-owned baseline fallback remains available | UNKNOWN |
| HOT-PATH-001 | Hot path remains stable active-view only | INVESTIGATE |
| NO-PARSER-001 | No parser payload activation path | PASS |
| NO-STORAGE-001 | No runtime-config storage | PASS |
| NO-WRITE-001 | No WebSerial/device/backend write path | PASS |
| NO-FLASH-001 | No flashing automation | PASS |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |

## Conclusions

- `source_view_candidate_publication_safe_for_merge`: `false`
- `candidate_backed_active_runtime_view_safe`: `false`
- `candidate_view_active_publication_reproduces_disconnect`: `true`
- `parser_payload_required_to_reproduce_disconnect`: `false`
- `candidate_materialization_presence_alone_sufficient_to_reproduce_disconnect`: `false`
- `source_owned_active_state_preselection_remains_repair_baseline`: `true`
- `parsed_candidate_presence_source_owned_published_remains_hardware_pass`: `true`
- `low_level_failure_mechanism_proven`: `false`
- `implementation_branch_merge_allowed`: `false`
- `requires_new_publication_model`: `true`

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Parser payload activation is not implemented.
- No runtime-loaded, storage, write, WebSerial, or flashing behavior is claimed.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.
