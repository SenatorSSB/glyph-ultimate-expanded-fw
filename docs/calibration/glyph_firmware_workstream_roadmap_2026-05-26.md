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
| Identity runtime role/case canonicalization | COMPLETE | `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`, `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`, `docs/calibration/glyph_identity_runtime_behavior_evaluator_harness_2026-05-28.md` | Source-backed role map, representative behavior-case matrix, and bounded Python evaluator are documented with fixtures/checkers. |
| Export corpus capture | BLOCKED_CORPUS | `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`, `tools/check_glyph_profile_config_export_corpus.py` | Protocol/framework exist; captured corpus is not populated. |
| Adapter policy and prewrite validation | PARTIAL | `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`, `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`, `tools/check_glyph_profile_adapter_prewrite.py` | Read-only policy/checking is present; no approved write-capable adapter. |
| Physical/logical mapping and RF5 transcription | PARTIAL | `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`, `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md` | Printed/base RF5 location is recorded; old RF5 negative smoke row remains ambiguous. |
| Identity runtime table source sync | COMPLETE | `docs/calibration/glyph_identity_runtime_table_source_sync_2026-05-28.md`, `tools/extract_glyph_identity_runtime_tables.py`, `tools/check_glyph_identity_runtime_table_source_sync.py` | Source-parsed table extraction now guards the evaluator's mirrored table constants against drift from `src/modes/Ultimate.cpp`. |
| Identity runtime generated-config prototype | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md`, `tools/generate_glyph_identity_runtime_config_prototype.py`, `tools/check_glyph_identity_runtime_generated_config_prototype.py` | Docs/tools-only prototype generates declarative intermediate config and C++-shaped review text from source-parsed tables and role metadata; not firmware input. |
| Identity runtime generated-config evaluator input | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_config_evaluator_input_2026-05-28.md`, `tools/check_glyph_identity_runtime_generated_config_evaluator_input.py` | Docs/tools-only checker proves the generated-config prototype can supply evaluator table input for all current behavior cases; not runtime-loaded config or hardware validation. |
| Identity runtime generated C++ diff artifact | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_cpp_diff_artifact_2026-05-28.md`, `docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt`, `tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py` | Docs/tools-only checker parses generated C++-shaped table constants and confirms all 25 declarations exactly match source-parsed `src/modes/Ultimate.cpp` tables; not firmware source. |
| Identity runtime generated-config contract | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md`, `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`, `tools/check_glyph_identity_runtime_config_contracts.py` | Docs/tools-only contract pins the generated-config prototype review shape and caveats; not firmware source, runtime-loaded config, serial/device write behavior, or hardware validation. |
| Senscope-to-Glyph export contract draft | DESIGN_ONLY | `docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md`, `docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json`, `tools/check_glyph_identity_runtime_config_contracts.py` | Draft package boundary for future Senscope exports targeting the generated-config contract; no Senscope app changes, runtime-loaded config, device writing, or schema changes. |
| Runtime-loaded config design | DESIGN_ONLY | `docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md`, `docs/calibration/fixtures/glyph_runtime_loaded_config_design_v0_2026-05-28.json`, `tools/check_glyph_runtime_loaded_config_design.py` | Future architecture boundary for runtime-loaded config ownership and non-goals; no runtime-loaded config, serial/device write behavior, firmware behavior change, or hardware validation. |
| Runtime-loaded config validation contract | DESIGN_ONLY | `docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md`, `docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json`, `tools/check_glyph_runtime_loaded_config_design.py` | Future validator requirements/rejections for bounded data classes; design-only and not implemented as firmware validator or device transport. |
| Preimplementation go/no-go index | DOCS_TOOLS_GATE_INDEX | `docs/calibration/glyph_preimplementation_go_nogo_index_2026-05-28.md`, `docs/calibration/fixtures/glyph_preimplementation_go_nogo_index_2026-05-28.json`, `tools/check_glyph_preimplementation_go_nogo_index.py` | Consolidates generated constants, runtime-loaded config, device write/transport, hardware-validation, nunchuk-validation, and Senscope export gates; no firmware behavior change or hardware validation. |
| Generated constants refactor readiness packet | BLOCKED_EXPLICIT_APPROVAL | `docs/calibration/glyph_generated_constants_refactor_readiness_packet_2026-05-28.md`, `docs/calibration/fixtures/glyph_generated_constants_refactor_readiness_packet_2026-05-28.json`, `tools/check_glyph_preimplementation_go_nogo_index.py` | Defines required invariants and approvals before any future generated constants firmware refactor; not approval to edit firmware source. |
| Runtime-loaded config implementation readiness packet | BLOCKED_EXPLICIT_APPROVAL_AND_DESIGN_RESOLUTION | `docs/calibration/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.md`, `docs/calibration/fixtures/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.json`, `tools/check_glyph_preimplementation_go_nogo_index.py` | Defines design, validator, storage/transport, fallback, performance, and hardware-validation blockers before runtime-loaded config implementation. |
| Generated constants refactor implementation plan v0 | PLAN_ONLY_BLOCKED_EXPLICIT_APPROVAL | `docs/calibration/glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.md`, `docs/calibration/fixtures/glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.json`, `tools/check_glyph_implementation_planning_packets.py` | Defines a future implementation boundary, invariants, checker sequence, hardware-validation requirement, and rollback plan; docs/tools-only and no firmware source edits. |
| Generated constants refactor execution packet | BLOCKED_EXPLICIT_APPROVAL | `docs/calibration/glyph_generated_constants_refactor_execution_packet_2026-05-28.md`, `docs/calibration/fixtures/glyph_generated_constants_refactor_execution_packet_2026-05-28.json`, `tools/check_glyph_generated_constants_refactor_execution_packet.py` | Defines the future execution boundary, allowed/forbidden file touches, pre/post checks, hardware gate, rollback, and stop conditions; docs/tools-only and no firmware source edits. |
| Generated constants refactor future agent prompt | BLOCKED_EXPLICIT_APPROVAL | `docs/calibration/glyph_generated_constants_refactor_agent_prompt_2026-05-28.md`, `tools/check_glyph_generated_constants_refactor_execution_packet.py` | Self-contained future prompt template that must not be run without explicit approval for generated constants firmware source touch. |
| Generated constants refactor hardware test matrix | TEMPLATE_NOT_EXECUTED | `docs/calibration/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.md`, `docs/calibration/fixtures/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.json`, `tools/check_glyph_generated_constants_refactor_execution_packet.py` | Minimum future hardware-test matrix template for a generated constants refactor; not executed and not a hardware result. |
| Runtime-loaded config implementation plan v0 | PLAN_ONLY_BLOCKED_EXPLICIT_APPROVAL_AND_DESIGN_RESOLUTION | `docs/calibration/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.md`, `docs/calibration/fixtures/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.json`, `tools/check_glyph_implementation_planning_packets.py` | Defines future architecture decisions, validator/storage/fallback/transport gates, latency evidence, nunchuk handling, and approval requirements; no runtime-loaded config implementation. |
| Identity runtime hardware validation and rollback plan | PLANNING_ONLY_NOT_EXECUTED | `docs/calibration/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.md`, `docs/calibration/fixtures/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.json`, `tools/check_glyph_implementation_planning_packets.py` | Defines required validation classes, evidence format, rollback plan, and merge gates for future firmware behavior work; not a hardware result. |
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
| Identity runtime behavior case matrix and evaluator | COMPLETE | `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`, `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`, `docs/calibration/glyph_identity_runtime_behavior_evaluator_harness_2026-05-28.md`, `tools/check_glyph_identity_runtime_behavior_cases.py`, `tools/check_glyph_identity_runtime_behavior_evaluator.py` |
| Identity runtime table source-sync guardrail | COMPLETE | `docs/calibration/glyph_identity_runtime_table_source_sync_2026-05-28.md`, `tools/extract_glyph_identity_runtime_tables.py`, `tools/check_glyph_identity_runtime_table_source_sync.py` |
| Identity runtime generated-config prototype | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md`, `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`, `tools/generate_glyph_identity_runtime_config_prototype.py`, `tools/check_glyph_identity_runtime_generated_config_prototype.py` |
| Identity runtime generated-config evaluator input | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_config_evaluator_input_2026-05-28.md`, `tools/check_glyph_identity_runtime_generated_config_evaluator_input.py` |
| Identity runtime generated C++ diff artifact | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_cpp_diff_artifact_2026-05-28.md`, `docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt`, `tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py` |
| Identity runtime generated-config contract | COMPLETE | `docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md`, `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`, `tools/check_glyph_identity_runtime_config_contracts.py` |
| Senscope-to-Glyph export contract draft | COMPLETE | `docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md`, `docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json`, `tools/check_glyph_identity_runtime_config_contracts.py` |
| Runtime-loaded config design and validation contract | COMPLETE | `docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md`, `docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md`, `tools/check_glyph_runtime_loaded_config_design.py` |
| Preimplementation gate index and readiness packets | COMPLETE | `docs/calibration/glyph_preimplementation_go_nogo_index_2026-05-28.md`, `docs/calibration/glyph_generated_constants_refactor_readiness_packet_2026-05-28.md`, `docs/calibration/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.md`, `tools/check_glyph_preimplementation_go_nogo_index.py` |
| Implementation planning packets | COMPLETE | `docs/calibration/glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.md`, `docs/calibration/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.md`, `docs/calibration/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.md`, `tools/check_glyph_implementation_planning_packets.py` |

## Current Source-Confirmed Facts

- `MODE_ULTIMATE` runtime exists and is active in source (`src/modes/Ultimate.cpp`).
- Tilt1/Tilt2 are native Ultimate left-stick-only behavior in the current patch scope.
- Tilt1/Tilt2 consume post-remap logical `inputs.lt1` and `inputs.lt2`.
- The canonical identity runtime role map for Smash Box has been documented in
  `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`.
- The representative source-backed identity runtime behavior case matrix has been documented in
  `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`.
- A bounded source-backed Python evaluator now mechanically checks the representative behavior-case fixture with the current `src/modes/Ultimate.cpp` phase order.
- Source-parsed table extraction now verifies that the evaluator's mirrored identity runtime table constants match the current `constexpr StickPoint` tables in `src/modes/Ultimate.cpp`.
- A docs/tools-only generated-config prototype now emits deterministic declarative intermediate config and C++-shaped review text from source-parsed identity runtime tables and role-map metadata.
- A docs/tools-only generated-config evaluator-input checker now proves that generated-config tables can drive the current evaluator for all representative behavior cases without changing firmware runtime source.
- A docs/tools-only generated C++ diff artifact checker now parses generated C++-shaped table declarations and confirms all 25 generated declarations exactly match source-parsed `src/modes/Ultimate.cpp` tables.
- A docs/tools-only generated-config contract now pins the current prototype shape, hard overrides, table list, and boundary caveats.
- A docs/tools-only Senscope export draft now records a possible future package boundary targeting the generated-config contract without implementing app schema, runtime-loaded config, or device writing.
- A docs/tools-only runtime-loaded config design and validation contract now record future ownership, rejection, storage/transport, and implementation blocker boundaries without implementing runtime-loaded config.
- A docs/tools-only preimplementation go/no-go index and readiness packets now consolidate generated constants, runtime-loaded config, device write/transport, hardware-validation, nunchuk-validation, and Senscope export gates without changing firmware runtime behavior.
- Docs/tools-only implementation planning packets now define blocked future plans for generated constants refactor, runtime-loaded config implementation, and hardware validation/rollback without editing firmware source or validating hardware.
- A docs/tools-only generated constants refactor execution packet, future prompt template, and hardware matrix now bound any later generated constants source branch before firmware source is touched.
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
- Generated constants firmware refactor is blocked until explicit user approval, a source-backed implementation plan, the execution packet guardrails, and future hardware result before merge.
- Runtime-loaded config implementation is blocked until explicit user approval, design resolution, validator design, fallback policy, storage/transport source authority, and hardware validation planning.

## Next Recommended Roadmap Steps

| Candidate branch | Purpose | Status | Why it comes next | Stop condition |
| --- | --- | --- | --- | --- |
| `glyph/gfw2-current-tilt-table-fixture-seed` | Seed a current-state native Ultimate Tilt fixture instance from existing source/hardware-evidenced behavior without changing runtime. | NOT_STARTED | Creates a concrete baseline artifact for later regression/design review in Phase B. | Stop if any entry would require inferred or undocumented behavior. |
| `glyph/gfw2-controller-output-contract-v0` | Draft a source-backed controller output contract for native Ultimate runtime invariants (left-stick/right-stick/trigger boundaries). | NOT_STARTED | Tightens controller/backend contract clarity before runtime design changes. | Stop if contract text drifts into game-semantic claims. |
| `glyph/gfw2-runtime-implementation-plan-v0` | Produce a bounded implementation plan for a potential native Ultimate patch, scoped by existing checkers and stop conditions. | NOT_STARTED | Converts design docs into an explicit reviewable implementation path, still no code changes. | Stop unless explicit user approval authorizes runtime implementation work. |
| `glyph/gfw2-user-requirements-input-packet` | Collect missing user/domain decisions for full layout roles, chord policy, default behavior, and disabled-remap policy. | BLOCKED_USER_INPUT | Unblocks Phase C decisions that design/readiness docs currently mark unresolved. | Stop if user requirements are incomplete or ambiguous for core behavior fields. |
| `glyph/gfw2-preimplementation-blocker-index` | Publish a single blocker ledger combining user-input, corpus, hardware, and approval gates. | NOT_STARTED | Keeps go/no-go state explicit before any runtime patch branch is attempted. | Stop if blocker status cannot be source-backed or is contradicted by current docs/checkers. |
| `glyph/gfw2-preimplementation-go-nogo-index` | Publish docs/tools-only go/no-go gates and readiness packets for generated constants, runtime-loaded config, device transport, and hardware-validation boundaries. | COMPLETE | Consolidates current implementation blockers before any future firmware-source branch. | Stop if gate status cannot be source-backed or would approve implementation work. |
| `glyph/gfw2-implementation-planning-packets` | Publish docs/tools-only implementation planning packets for generated constants refactor, runtime-loaded config, and hardware validation/rollback. | COMPLETE | Converts existing blocked readiness gates into explicit future implementation planning packets without firmware source edits. | Stop if planning text would approve implementation work or claim hardware validation. |
| `glyph/gfw2-generated-constants-refactor-execution-packet` | Publish docs/tools-only execution packet, future prompt, and hardware matrix for a possible generated constants refactor. | COMPLETE | Makes the future generated constants implementation scope reviewable and bounded before any firmware source is touched. | Stop if packet text would approve source edits, allow behavior/table changes, or imply hardware validation. |

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
  - aggregate dry-run and final operator preparation should use `tools/run_glyph_prehardware_dry_run_checks.py` and `docs/calibration/glyph_manual_hardware_owner_checklist_2026-05-27.md`.
  - prehardware branch hygiene should include `tools/check_glyph_no_forbidden_artifacts.py`.

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
| `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md` | Canonical source-backed role-map for Smash Box identity runtime behavior in `MODE_ULTIMATE`. |
| `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json` | Declarative fixture candidate for current identity runtime role map (docs-only, no runtime parser changes in this branch). |
| `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md` | Representative source-backed behavior case matrix for the current identity runtime (docs/fixture/checker-only, not a new hardware result). |
| `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json` | Machine-readable expected-behavior case fixture keyed by the identity runtime role map. |
| `docs/calibration/glyph_identity_runtime_behavior_evaluator_harness_2026-05-28.md` | Bounded Python mirror evaluator scope, caveats, and future migration path for the current representative identity runtime behavior cases. |
| `docs/calibration/glyph_identity_runtime_table_source_sync_2026-05-28.md` | Source-parsed identity runtime table extraction and evaluator table-sync guardrail. |
| `docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md` | Docs/tools-only generated-config prototype scope, caveats, and migration path for current source-backed identity runtime data. |
| `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json` | Declarative intermediate config prototype generated from source-parsed tables and role-map metadata; not firmware input. |
| `docs/calibration/glyph_identity_runtime_generated_config_evaluator_input_2026-05-28.md` | Docs/tools-only generated-config evaluator-input checker scope, caveats, and migration path; not firmware input or hardware validation. |
| `docs/calibration/glyph_identity_runtime_generated_cpp_diff_artifact_2026-05-28.md` | Docs/tools-only generated C++-shaped constants diff artifact scope, caveats, and migration path; not firmware source or hardware validation. |
| `docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt` | Plain-text generated C++-shaped constants review artifact; not included by firmware and not placed in a build path. |
| `docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md` | Docs/tools-only generated-config contract scope, required fields, table contract, hard overrides, caveats, and migration path. |
| `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json` | Machine-readable generated-config contract target for aggregate checker validation; not runtime config. |
| `docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md` | Docs/tools-only draft package boundary for future Senscope exports targeting Glyph generated config; not implementation. |
| `docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json` | Machine-readable Senscope export draft contract target for aggregate checker validation. |
| `docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md` | Docs/tools-only runtime-loaded config future architecture boundary; not implementation, serial/device write behavior, or hardware validation. |
| `docs/calibration/fixtures/glyph_runtime_loaded_config_design_v0_2026-05-28.json` | Machine-readable design/checker target for runtime-loaded config ownership, non-goals, and storage/transport boundaries; not runtime config. |
| `docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md` | Docs/tools-only future validator requirements and rejection contract; not a firmware validator implementation. |
| `docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json` | Machine-readable validation-contract checker target for accepted data classes, rejection rules, and forbidden payload content. |
| `docs/calibration/glyph_preimplementation_go_nogo_index_2026-05-28.md` | Docs/tools-only preimplementation gate index for generated constants, runtime-loaded config, device write/transport, hardware-validation, nunchuk-validation, and Senscope export boundaries. |
| `docs/calibration/fixtures/glyph_preimplementation_go_nogo_index_2026-05-28.json` | Machine-readable go/no-go gate fixture for required statuses and preconditions. |
| `docs/calibration/glyph_generated_constants_refactor_readiness_packet_2026-05-28.md` | Docs/tools-only blocker/readiness packet for a future generated constants firmware refactor; not approval to edit firmware source. |
| `docs/calibration/fixtures/glyph_generated_constants_refactor_readiness_packet_2026-05-28.json` | Machine-readable generated constants readiness packet fixture for invariants, forbidden changes, approvals, and blockers. |
| `docs/calibration/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.md` | Docs/tools-only blocker/readiness packet for a future runtime-loaded config implementation; not implementation, storage, transport, or hardware validation. |
| `docs/calibration/fixtures/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.json` | Machine-readable runtime-loaded config implementation readiness packet fixture for unresolved design, validator, storage/transport, fallback, performance, and hardware gates. |
| `docs/calibration/glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.md` | Docs/tools-only future implementation plan for generated constants refactor scope, invariants, checker sequence, hardware-validation requirement, rollback, and stop conditions. |
| `docs/calibration/fixtures/glyph_generated_constants_refactor_implementation_plan_v0_2026-05-28.json` | Machine-readable generated constants implementation planning fixture; blocked until explicit user approval and not firmware source. |
| `docs/calibration/glyph_generated_constants_refactor_execution_packet_2026-05-28.md` | Docs/tools-only execution packet for a future generated constants refactor; blocked until explicit approval and not firmware source. |
| `docs/calibration/fixtures/glyph_generated_constants_refactor_execution_packet_2026-05-28.json` | Machine-readable execution packet fixture for future generated constants file-touch boundaries, invariants, checks, hardware gate, rollback, and stop conditions. |
| `docs/calibration/glyph_generated_constants_refactor_agent_prompt_2026-05-28.md` | Future generated constants refactor agent prompt template; must not be run without explicit user approval for firmware source touch. |
| `docs/calibration/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.md` | Template-only hardware test matrix for a future generated constants firmware refactor; not executed and not a hardware result. |
| `docs/calibration/fixtures/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.json` | Machine-readable hardware matrix template fixture for required future test categories and result/rollback gates. |
| `docs/calibration/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.md` | Docs/tools-only future implementation plan for runtime-loaded config architecture decisions, validator/storage/fallback/transport gates, latency evidence, and nunchuk handling. |
| `docs/calibration/fixtures/glyph_runtime_loaded_config_implementation_plan_v0_2026-05-28.json` | Machine-readable runtime-loaded config implementation planning fixture; blocked until explicit approval and design resolution. |
| `docs/calibration/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.md` | Docs/tools-only hardware validation and rollback planning requirements for future identity-runtime firmware changes; not a hardware result. |
| `docs/calibration/fixtures/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.json` | Machine-readable hardware validation and rollback planning fixture for required change classes, evidence, rollback, no-regression areas, and merge gates. |
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
| `docs/calibration/glyph_no_forbidden_artifacts_checker_2026-05-27.md` | Prehardware branch hygiene checker policy for generated/build artifacts. |
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
| `tools/check_glyph_identity_runtime_behavior_cases.py` | Behavior-case fixture/doc/source checker for the current identity runtime case matrix. |
| `tools/extract_glyph_identity_runtime_tables.py` | Source-parsed extraction of required `constexpr StickPoint` tables from `src/modes/Ultimate.cpp`. |
| `tools/check_glyph_identity_runtime_table_source_sync.py` | Exact comparison of source-parsed identity runtime tables against the behavior evaluator's mirrored table constants. |
| `tools/generate_glyph_identity_runtime_config_prototype.py` | Generates docs-only JSON intermediate config and C++-shaped review text from source-parsed identity runtime tables and role-map metadata. |
| `tools/check_glyph_identity_runtime_generated_config_prototype.py` | Validates the generated-config prototype shape, caveats, hard overrides, and exact source-table match. |
| `tools/check_glyph_identity_runtime_generated_config_evaluator_input.py` | Validates that generated-config tables can be consumed as evaluator input for all current behavior cases with exact parity. |
| `tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py` | Parses generated C++-shaped table declarations and validates exact source-table parity plus artifact caveats. |
| `tools/check_glyph_identity_runtime_config_contracts.py` | Validates generated-config contract and Senscope export draft fixtures, required caveats, and generated-config prototype alignment. |
| `tools/check_glyph_runtime_loaded_config_design.py` | Validates runtime-loaded config design and validation-contract fixtures, required caveats, generated-config contract compatibility, and Senscope export draft non-goals. |
| `tools/check_glyph_preimplementation_go_nogo_index.py` | Validates preimplementation go/no-go index and readiness packet fixtures, required blocker statuses, cross-checks runtime-loaded design-only status, and required caveat phrases. |
| `tools/check_glyph_implementation_planning_packets.py` | Validates implementation planning packet fixtures, blocked statuses, required invariants/decisions/rollback gates, go/no-go cross-checks, readiness packet blockers, and required caveat phrases. |
| `tools/check_glyph_generated_constants_refactor_execution_packet.py` | Validates generated constants refactor execution packet and hardware matrix fixtures, approval/file-touch/invariant gates, go/no-go blockers, and required caveat phrases. |
| `tools/check_glyph_identity_runtime_behavior_evaluator.py` | Bounded Python mirror evaluator for the current representative identity runtime behavior cases; not hardware validation. |
| `tools/run_glyph_next_runtime_change_readiness_checks.py` | Aggregated readiness checks for next runtime change planning. |
| `tools/check_glyph_merged_state_consistency.py` | Merged-state required-file and stale-phrase consistency checks. |
| `tools/check_glyph_user_requirements_packet.py` | Structure/presence checks for required user requirements packet anchors and blocker language. |
| `tools/check_glyph_preservation_execution_packet.py` | Structure/presence checks for preservation execution packet constraints and required references. |
| `tools/check_glyph_no_forbidden_artifacts.py` | Read-only git-state hygiene check for forbidden tracked artifacts and visible untracked artifact warnings. |

## Non-Goals

- No macros/turbo/timing automation.
- No push/flashing automation.
- No direct claim that Senscope neutral Profile JSON maps to Glyph JSON.
- No game-semantic source-authority changes.
- No unapproved runtime patch.
