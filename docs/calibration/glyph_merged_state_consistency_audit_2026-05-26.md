# Glyph Merged State Consistency Audit - 2026-05-26

Scope: audit of the current merged `configurator` state after branch cleanup. This is documentation and read-only checker coverage only. It does not change firmware runtime behavior, configurator behavior, profile schema behavior, remap behavior, or SOCD behavior.

## Workflow State

The current workflow is single-mainline oriented:

- start each future agent run from current `origin/configurator`;
- create one fresh feature branch per run;
- stop if the intended branch already exists locally or remotely;
- delete completed local and remote feature branches after manual merge;
- do not reuse stale feature branch names;
- do not merge feature branches into `configurator` from an agent run unless explicitly instructed.

This audit branch follows that model and is limited to merged-state documentation/checker coverage.

## Current Major Coverage On Configurator

Current merged coverage observed under `docs/calibration` and `tools` includes:

| area | current source files |
| --- | --- |
| Native Ultimate Tilt/Tilt2 runtime implementation and hardware result | `src/modes/Ultimate.cpp`, `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`, `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`, `tools/check_glyph_ultimate_tilt_hardware_result.py`, `tools/run_glyph_ultimate_tilt_prehardware_checks.py` |
| Tilt/Tilt2 release-candidate manifest and provenance | `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`, `docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_2026-05-24.md`, `tools/check_glyph_ultimate_tilt_rc_manifest.py` |
| Profile/config source authority and semantic gap mapping | `docs/calibration/glyph_profile_config_source_authority_2026-05-26.md`, `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md`, `tools/check_glyph_profile_config_semantics.py`, `tools/glyph_config_model.py` |
| Export corpus protocol/framework | `docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`, `docs/calibration/glyph_profile_config_export_corpus_manifest_TEMPLATE.json`, `docs/calibration/export_corpus/README.md`, `tools/check_glyph_profile_config_export_corpus.py` |
| Adapter policy and read-only prewrite validation | `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`, `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`, `tools/check_glyph_profile_adapter_prewrite.py` |
| Physical/logical layout map | `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`, `docs/calibration/glyph_physical_logical_layout_map_handoff.md`, `tools/list_glyph_physical_logical_layout_sources.py` |
| Ultimate preservation hardware matrix/template/checker | `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`, `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`, `tools/check_glyph_ultimate_preservation_hardware_result.py` |
| Native Ultimate table design/fixture/source scope | `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md`, `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`, `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`, `docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md`, `tools/check_glyph_native_ultimate_table_fixture.py`, `tools/check_glyph_native_ultimate_table_runtime_scope.py` |
| Full layout requirements and next-runtime readiness | `docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md`, `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`, `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`, `tools/run_glyph_next_runtime_change_readiness_checks.py` |
| Full firmware workstream handoff | `docs/calibration/glyph_full_firmware_workstream_sequence_handoff_2026-05-26.md` |

## Stale-Statement Review

The merged state should no longer be summarized as though these items are missing:

- "faceplate/base transcription pending" or generic "pending transcription" for the full printed/base physical ID map;
- "RF5 unresolved" without the updated distinction between printed/base transcription and the older ambiguous smoke-test row;
- "adapter policy doc missing";
- "hardware test not performed" for current Tilt/Tilt2, because `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` records the current smoke-tested Tilt/Tilt2 result.

Known valid contexts remain:

- historical pre-result docs may say a manual hardware result was not yet performed at that earlier step;
- template/checker contexts may emit or describe `NO_RESULT_FILE` for missing future result files;
- fixture/template contexts may use `TEMPLATE_ONLY`;
- the preservation hardware matrix still has no filled result file in this repo;
- RF5's old negative smoke-test row remains `NOT_TESTED_AMBIGUOUS`.

Known review warnings found during this audit:

- `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md` still says "RF5 physical identity resolution" as a blocker. That should be read narrowly as future RF5 retest/result resolution, because printed/base RF5 transcription is now recorded.
- `docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md` is a historical pre-result package that says the manual hardware result was not yet performed. That statement is obsolete for the current Tilt/Tilt2 smoke result, but it remains historical branch context.
- Older Tilt handoffs mention `NO_RESULT_FILE` for Tilt hardware result checks. Current Tilt/Tilt2 now has a filled result; future wording should distinguish that from the still-missing preservation hardware result.

## RF5 Nuance

Current evidence must preserve both facts:

- The printed/base physical ID transcription records center-right / RF cluster, far-right upper button as RF5 in `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`.
- The earlier RF5 negative check in `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` remains historically `NOT_TESTED_AMBIGUOUS` and must not be converted to PASS.

Therefore future wording should avoid saying simply "RF5 unresolved" unless it says which layer remains unresolved. The printed/base transcription is present; the old negative smoke-test result remains ambiguous.

## Preserved Caveats

This audit preserves these current caveats:

- Current Tilt/Tilt2 behavior is source-confirmed and hardware-smoke verified for the recorded result file.
- Preservation hardware matrix result is not filled yet; `tools/check_glyph_ultimate_preservation_hardware_result.py` may report `status=NO_RESULT_FILE`.
- Export corpus capture has a protocol/template/framework, but no real captured corpus manifest is present yet.
- No write-capable adapter is implemented or approved.
- Native Ultimate table runtime work remains design/checker/fixture-contract only; no arbitrary table runtime implementation exists.
- Omitted `activates` and explicit `BTN_UNSPECIFIED` must remain distinct for adapter policy.
- Senscope neutral Profile JSON must not be claimed to map directly to Glyph JSON.
- No Smash/game-semantic claims are made from Glyph config data.

## Checker Coverage Consolidation

`tools/check_glyph_merged_state_consistency.py` adds a read-only merged-state audit helper. It checks that key required files exist and scans `docs/calibration` for stale phrases. The checker reports context for expected template/historical phrases and fails only for missing required files or clearly uncontextualized stale phrasing.

The checker intentionally does not:

- mutate files;
- inspect or build firmware artifacts;
- validate runtime equivalence;
- mark hardware verification complete;
- normalize profile/config data;
- implement adapter, push-to-device, or flashing behavior.

## Behavior Change Statement

No runtime/source/configurator behavior changed in this branch. No SOCD, remap, profile schema, proto, configurator, adapter write path, firmware output, macro, turbo, toggle, one-shot, or timing behavior changed.
