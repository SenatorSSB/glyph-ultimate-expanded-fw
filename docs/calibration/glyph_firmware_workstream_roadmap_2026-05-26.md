# Glyph Firmware Workstream Roadmap Index - 2026-05-26

## Scope

- Glyph / HayBox-side firmware, configurator, and backend realization workstream only.
- Not the Senscope browser app repository.
- No macros, turbo, toggles, one-shots, or timing automation.
- No push/flashing automation.
- This roadmap consolidates navigation and status; underlying source docs remain canonical.

## Current Milestone Status

| Milestone | State | Evidence anchor | Notes |
| --- | --- | --- | --- |
| Native Ultimate Tilt/Tilt2 runtime baseline | COMPLETE | `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`, `src/modes/Ultimate.cpp` | Native `MODE_ULTIMATE` implementation exists and is documented. |
| Tilt/Tilt2 hardware smoke evidence | COMPLETE | `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | Smoke PASS recorded for current Tilt1/Tilt2 rows. |
| Preservation hardware matrix execution | BLOCKED_HARDWARE | `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`, `tools/check_glyph_ultimate_preservation_hardware_result.py` | Matrix/template/checker exist; filled result file is still absent. |
| Capability and source-authority mapping | COMPLETE | `docs/calibration/glyph_full_capability_inventory_2026-05-26.md`, `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md` | Source-tracing baseline is in place. |
| Export corpus capture | BLOCKED_CORPUS | `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`, `tools/check_glyph_profile_config_export_corpus.py` | Protocol/framework exist; captured corpus is not populated. |
| Adapter policy and prewrite validation | PARTIAL | `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`, `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`, `tools/check_glyph_profile_adapter_prewrite.py` | Read-only policy/checking is present; no approved write-capable adapter. |
| Physical/logical mapping and RF5 transcription | PARTIAL | `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`, `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md` | Printed/base RF5 location is recorded; old RF5 negative smoke row remains ambiguous. |
| Native Ultimate arbitrary table runtime design | DESIGN_ONLY | `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md` | Design path documented; runtime patch not approved/implemented here. |
| Fixture contract and source-scope guardrails | COMPLETE | `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`, `docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md` | Template and read-only checkers are present. |
| Full layout requirements and runtime readiness | PARTIAL | `docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md`, `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`, `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md` | Requirements questions and readiness blockers are still open. |
| User/domain requirements packet for full desired behavior | BLOCKED_USER_INPUT | `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`, `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md` | Final physical/logical roles, chord policy, and outbound encoding decisions need explicit user input. |
| Runtime patch implementation branch | NOT_STARTED | `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md` | Explicit user approval required before any runtime implementation branch. |
| Senscope browser-app implementation work | OUT_OF_SCOPE | `AGENTS.md` | This workstream does not mutate Senscope app/runtime semantics. |

## Completed Foundation

| Foundation item | State | Primary source(s) |
| --- | --- | --- |
| Tilt/Tilt2 native Ultimate runtime implementation | COMPLETE | `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`, `src/modes/Ultimate.cpp` |
| Tilt/Tilt2 hardware smoke result | COMPLETE | `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` |
| Full capability inventory | COMPLETE | `docs/calibration/glyph_full_capability_inventory_2026-05-26.md` |
| Profile/config source authority audit | COMPLETE | `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md` |
| Export corpus framework/protocol | COMPLETE | `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`, `docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json` |
| Adapter policy + prewrite validation | COMPLETE | `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`, `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md` |
| Physical/logical layout map | COMPLETE | `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md` |
| Preservation hardware matrix/template/checker | COMPLETE | `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`, `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`, `tools/check_glyph_ultimate_preservation_hardware_result.py` |
| Native Ultimate table runtime design | COMPLETE | `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md` |
| Fixture contract + source checker | COMPLETE | `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`, `docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md`, `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json` |
| Requirements/readiness documents | COMPLETE | `docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md`, `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`, `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md` |
| Merged-state consistency audit | COMPLETE | `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md` |

## Current Source-Confirmed Facts

- `MODE_ULTIMATE` runtime exists and is active in source (`src/modes/Ultimate.cpp`).
- Tilt1/Tilt2 are native Ultimate left-stick-only behavior in the current patch scope.
- Tilt1/Tilt2 consume post-remap logical `inputs.lt1` and `inputs.lt2`.
- Current MVP profile evidence records `RF3 -> LT1 -> inputs.lt1 -> Tilt1/TILT`.
- Current MVP profile evidence records `RF4 -> LT2 -> inputs.lt2 -> Tilt2`.
- RF5 printed/base location is now transcribed in layout docs, while the earlier RF5 negative smoke row remains `NOT_TESTED_AMBIGUOUS`.
- Device profile/config transport and persistence are protobuf-backed in firmware source; JSON export semantics are not fully source-authoritative from this repo alone.

## Current Hardware-Observed Facts

- Tilt1/Tilt2 smoke rows are recorded as PASS for the current result file.
- Mini-screen center-relative offset convention is observed in the hardware result.
- Both-held Tilt1+Tilt2 existing combined behavior is observed and recorded.
- RF5 old negative check remains ambiguous (`NOT_TESTED_AMBIGUOUS`).
- Ultimate preservation hardware matrix has not yet been executed into a real filled result file.

## Open Blockers

- User requirements packet/input is still needed for full desired behavior decisions.
- Preservation hardware result (`docs/calibration/glyph_ultimate_preservation_hardware_result.md`) is not executed/present.
- Export corpus framework exists but captured corpus remains absent.
- Write-capable adapter is not implemented or approved.
- Outbound disabled-remap policy (`omitted activates` vs explicit `BTN_UNSPECIFIED`) is unresolved.
- Next runtime patch requires explicit user approval before implementation.
- Hardware testing is required after any runtime patch before preservation claims.

## Next Recommended Roadmap Steps

| Candidate branch | Purpose | Status | Why it comes next | Stop condition |
| --- | --- | --- | --- | --- |
| `glyph/gfw2-current-tilt-table-fixture-seed` | Seed a current-state native Ultimate Tilt fixture instance from existing source/hardware-evidenced behavior without changing runtime. | NOT_STARTED | Creates a concrete baseline artifact for later regression/design review in Phase B. | Stop if any entry would require inferred or undocumented behavior. |
| `glyph/gfw2-controller-output-contract-v0` | Draft a source-backed controller output contract for native Ultimate runtime invariants (left-stick/right-stick/trigger boundaries). | NOT_STARTED | Tightens controller/backend contract clarity before runtime design changes. | Stop if contract text drifts into game-semantic claims. |
| `glyph/gfw2-runtime-implementation-plan-v0` | Produce a bounded implementation plan for a potential native Ultimate patch, scoped by existing checkers and stop conditions. | NOT_STARTED | Converts design docs into an explicit reviewable implementation path, still no code changes. | Stop unless explicit user approval authorizes runtime implementation work. |
| `glyph/gfw2-user-requirements-input-packet` | Collect missing user/domain decisions for full layout roles, chord policy, default behavior, and disabled-remap policy. | BLOCKED_USER_INPUT | Unblocks Phase C decisions that design/readiness docs currently mark unresolved. | Stop if user requirements are incomplete or ambiguous for core behavior fields. |
| `glyph/gfw2-preimplementation-blocker-index` | Publish a single blocker ledger combining user-input, corpus, hardware, and approval gates. | NOT_STARTED | Keeps go/no-go state explicit before any runtime patch branch is attempted. | Stop if blocker status cannot be source-backed or is contradicted by current docs/checkers. |

## Roadmap Phases

### Phase A - Stabilized Baseline

- Status: mostly complete.
- Includes existing native Tilt/Tilt2 implementation, smoke result, capability inventory, source-authority mapping, and merged-state audit.

### Phase B - Contracting and Fixture Formalization

- Status: active/design-only.
- Focus:
  - current Tilt seed fixture,
  - controller output contract,
  - runtime implementation plan.

### Phase C - User Requirements Capture

- Status: blocked on user input.
- Focus:
  - requirements input packet,
  - explicit full desired behavior decisions.

### Phase D - Runtime Implementation Review

- Status: gated.
- Focus:
  - only after explicit user approval,
  - bounded runtime patch scope,
  - no SOCD/remap/profile-schema/configurator semantic drift.

### Phase E - Hardware Validation

- Status: blocked_hardware.
- Focus:
  - execute preservation hardware result,
  - run post-patch hardware validation for any approved runtime change.
  - prehardware RC preparation should follow `docs/calibration/glyph_prehardware_rc_runbook_2026-05-27.md` and `tools/inspect_glyph_mk6_build_artifact.py` before manual hardware execution.

### Phase F - Adapter/Export Work

- Status: blocked_corpus + user policy gates.
- Focus:
  - capture export corpus,
  - finalize adapter write policy decisions,
  - consider write-capable adapter only after prior gates clear.

## Branch/Workflow Policy

- Start each run from current `origin/configurator`.
- Create one fresh feature branch per run.
- Do not reuse stale local/remote feature branches.
- After manual merge, delete completed local and remote feature branches.
- Do not merge into `configurator` from an agent run unless explicitly instructed.

## Canonical Documents Index

| Document | Ownership |
| --- | --- |
| `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md` | Current native Tilt/Tilt2 runtime behavior scope and formulas. |
| `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | Current Tilt/Tilt2 hardware smoke evidence and caveats. |
| `docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md` | Baseline readiness classification for current Tilt package. |
| `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md` | Preservation hardware protocol/checklist to run before broader runtime claims. |
| `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md` | Required template shape for future preservation hardware result capture. |
| `docs/calibration/glyph_full_capability_inventory_2026-05-26.md` | Source-confirmed and hardware-observed capability inventory. |
| `docs/calibration/glyph_remaining_functionality_gap_map_2026-05-26.md` | Remaining functionality grouped by support/readiness class. |
| `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md` | Profile/config source-authority audit and constraints. |
| `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md` | Semantics gaps and stop conditions for adapter safety. |
| `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md` | Export corpus capture protocol and authority boundaries. |
| `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md` | Current adapter policy decisions and unresolved gates. |
| `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md` | Read-only prewrite checker design and error policy. |
| `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md` | Physical/logical/runtime mapping and RF5 nuance tracking. |
| `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md` | Design-only native table runtime options and risks. |
| `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md` | Fixture contract and contract goals for future table data. |
| `docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md` | Source-scope checker intent for native runtime guardrails. |
| `docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md` | Current requirements ledger with evidence status. |
| `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md` | Open user/source/corpus/hardware questions. |
| `docs/calibration/glyph_user_requirements_input_packet_2026-05-27.md` | Fillable user/domain requirements packet with blocker-rule framing. |
| `docs/calibration/glyph_user_requirements_packet_checker_2026-05-27.md` | Structure-only checker policy for user requirements packet presence validation. |
| `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md` | Design-only readiness gate before next runtime patch. |
| `docs/calibration/glyph_preservation_hardware_execution_packet_2026-05-27.md` | Manual preservation test execution preparation packet (no result capture in packet). |
| `docs/calibration/glyph_full_firmware_workstream_sequence_handoff_2026-05-26.md` | Sequence-level handoff and carried-forward caveats. |
| `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md` | Merged-state stale-claim audit and consistency notes. |

## Verification/Checker Index

| Checker/tool | What it checks |
| --- | --- |
| `tools/run_glyph_ultimate_tilt_prehardware_checks.py` | Aggregated prehardware baseline checks for current Tilt package. |
| `tools/check_glyph_ultimate_tilt_hardware_result.py` | Structural integrity and required fields for Tilt hardware result doc. |
| `tools/check_glyph_ultimate_tilt_rc_manifest.py` | RC manifest structure/policy checks. |
| `tools/check_glyph_profile_config_semantics.py` | Fixture-level profile/config semantics signals and warnings. |
| `tools/check_glyph_profile_config_export_corpus.py` | Export corpus protocol/template/manifest validation. |
| `tools/check_glyph_profile_adapter_prewrite.py` | Read-only prewrite validation and warning surfacing for adapter candidates. |
| `tools/list_glyph_physical_logical_layout_sources.py` | Source references used by physical/logical mapping doc. |
| `tools/check_glyph_ultimate_preservation_hardware_result.py` | Preservation hardware result presence/shape checker. |
| `tools/check_glyph_native_ultimate_table_fixture.py` | Native table fixture contract validation (`1..9`, raw/offset ranges, metadata). |
| `tools/check_glyph_native_ultimate_table_runtime_scope.py` | Native Ultimate source-scope guardrails for Tilt patch and runtime markers. |
| `tools/run_glyph_next_runtime_change_readiness_checks.py` | Aggregated readiness checks for next runtime change planning. |
| `tools/check_glyph_merged_state_consistency.py` | Merged-state required-file and stale-phrase consistency checks. |
| `tools/check_glyph_user_requirements_packet.py` | Structure/presence checks for required user requirements packet anchors and blocker language. |
| `tools/check_glyph_preservation_execution_packet.py` | Structure/presence checks for preservation execution packet constraints and required references. |

## Non-Goals

- No macros/turbo/timing automation.
- No push/flashing automation.
- No direct claim that Senscope neutral Profile JSON maps to Glyph JSON.
- No game-semantic source-authority changes.
- No unapproved runtime patch.
