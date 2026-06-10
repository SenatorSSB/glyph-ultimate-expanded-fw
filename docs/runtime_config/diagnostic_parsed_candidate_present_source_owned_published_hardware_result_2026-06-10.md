# Diagnostic Parsed Candidate Present, Source-Owned Published Hardware Result - 2026-06-10

status: HARDWARE_PASS
overall_result: HARDWARE_PASS

branch_under_test: `runtime-config-diagnostic-parsed-candidate-present-source-owned-published`
result_branch: `runtime-config-diagnostic-parsed-candidate-present-source-owned-published-hardware-result`

operator_report: `tested, everything works`

## Result Scope

This result records that parsed candidate/parser/materialization presence is
hardware-safe for this diagnostic scope when source-owned baseline remains the
published active runtime view.

It does not claim parsed candidate activation is safe. Active publication of
`candidate.view` remains the main suspect for the parsed-candidate opt-in
failure.

## Hardware Result Rows

| Row ID | Scope | Status |
| --- | --- | --- |
| BOOT-001 | Boot and USB stability | PASS |
| BASELINE-001 | Baseline source-owned behavior | PASS |
| RF5-001 | RF5 forced-Up / A carrier behavior | PASS |
| RF6-001 | RF6 Z-airdodge low magnitude behavior | PASS |
| LT6-001 | LT6 down / A carrier behavior | PASS |
| ORDINARY-DIR-001 | Ordinary direction behavior | PASS |
| NEUTRAL-001 | Neutral behavior | PASS |
| UNRELATED-BUTTONS-001 | Unrelated button behavior | PASS |
| MODIFIERS-001 | Modifier behavior | PASS |
| PARSED-CANDIDATE-PRESENT-001 | Parsed candidate present and initialized | PASS |
| SOURCE-OWNED-PUBLISHED-001 | Source-owned baseline published active | PASS |
| HOT-PATH-001 | Hot path remains stable active-view only | PASS |
| NO-CANDIDATE-ACTIVE-PUBLICATION-001 | Candidate view is not active | PASS |
| NO-STORAGE-001 | No runtime-config storage | PASS |
| NO-WRITE-001 | No WebSerial/device/backend write path | PASS |
| NO-FLASH-001 | No flashing automation | PASS |
| NUNCHUK-001 | Nunchuk scope | NOT_TESTED |

## Conclusions

- `parsed_candidate_presence_safe_when_source_owned_published`: `true`
- `candidate_view_active_publication_remains_suspect`: `true`
- `parsed_candidate_opt_in_activation_safe_for_merge`: `false`
- `source_owned_active_state_preselection_remains_repair_baseline`: `true`
- `implementation_branch_merge_allowed`: `true` for this diagnostic branch only
- `failed_opt_in_activation_branch_merge_allowed`: `false`
- `low_level_failure_mechanism_proven`: `false`

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Candidate active publication is not implemented.
- Parsed candidate activation is not claimed safe.
- The low-level failure mechanism is not proven.
- Nunchuk remains NOT_TESTED.
