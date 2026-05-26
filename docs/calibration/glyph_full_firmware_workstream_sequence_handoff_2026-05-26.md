# Glyph Firmware Workstream Sequence Handoff - 2026-05-26

This handoff summarizes the pre-hardware Glyph / HayBox-side firmware, configurator, and backend-realization preparation sequence completed on 2026-05-26.

The sequence stayed within the Glyph repository. It did not change Senscope browser-app code, game-semantic source authority, profile schema/proto behavior, configurator runtime behavior, firmware runtime behavior, SOCD semantics, remap semantics, or any push-to-device workflow.

## Branches Completed In This Sequence

| Branch | Purpose | Runtime behavior changed |
| --- | --- | --- |
| `glyph/profile-config-adapter-policy-decisions` | Documented safe adapter policy decisions and unresolved outbound policy gates before any write-capable adapter exists. | No |
| `glyph/profile-config-adapter-prewrite-validation` | Added a read-only prewrite validation checker for future adapter output fixtures. | No |
| `glyph/physical-logical-layout-map` | Documented source/user-evidence mapping across physical buttons, logical remaps, display positions, runtime input fields, and observed roles. | No |
| `glyph/ultimate-preservation-test-matrix` | Added the next manual hardware preservation checklist, template, and result checker. | No |
| `glyph/native-ultimate-table-runtime-design` | Designed future native Ultimate arbitrary table support without implementing it. | No |
| `glyph/native-ultimate-table-fixture-contract` | Defined the fixture contract required before any future native Ultimate table runtime patch. | No |
| `glyph/native-ultimate-table-source-checkers` | Added read-only source-shape checks for the current Tilt/Tilt2 runtime patch scope. | No |
| `glyph/full-layout-requirements-spec` | Created the requirements spec and open question list without inventing missing user requirements. | No |
| `glyph/prehardware-next-runtime-change-readiness` | Added the readiness index and aggregate pre-hardware readiness checker. | No |
| `glyph/long-run-sequence-handoff` | Added this final sequence handoff. | No |

## Docs Added

- `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`
- `docs/calibration/glyph_profile_config_adapter_policy_handoff.md`
- `docs/calibration/glyph_profile_adapter_prewrite_validation_2026-05-26.md`
- `docs/calibration/glyph_profile_adapter_prewrite_handoff.md`
- `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`
- `docs/calibration/glyph_physical_logical_layout_map_handoff.md`
- `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`
- `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`
- `docs/calibration/glyph_ultimate_preservation_hardware_handoff.md`
- `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md`
- `docs/calibration/glyph_native_ultimate_table_runtime_design_handoff.md`
- `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`
- `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`
- `docs/calibration/glyph_native_ultimate_table_fixture_handoff.md`
- `docs/calibration/glyph_native_ultimate_table_source_checker_2026-05-26.md`
- `docs/calibration/glyph_native_ultimate_table_source_checker_handoff.md`
- `docs/calibration/glyph_full_layout_requirements_spec_2026-05-26.md`
- `docs/calibration/glyph_full_layout_requirements_questions_2026-05-26.md`
- `docs/calibration/glyph_full_layout_requirements_handoff.md`
- `docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`
- `docs/calibration/glyph_next_runtime_change_readiness_handoff.md`
- `docs/calibration/glyph_full_firmware_workstream_sequence_handoff_2026-05-26.md`

## Checkers Added

- `tools/check_glyph_profile_adapter_prewrite.py`
- `tools/list_glyph_physical_logical_layout_sources.py`
- `tools/check_glyph_ultimate_preservation_hardware_result.py`
- `tools/check_glyph_native_ultimate_table_fixture.py`
- `tools/check_glyph_native_ultimate_table_runtime_scope.py`
- `tools/run_glyph_next_runtime_change_readiness_checks.py`

All added checkers are intended to be stdlib-only and read-only. None of them writes profile output, rewrites fixtures, performs flashing, or pushes data to hardware.

## Source-Confirmed Facts

The following facts were treated as source-confirmed only where supported by inspected repository source, docs, tests, or fixtures:

- The current native Ultimate Tilt/Tilt2 behavior is implemented in `src/modes/Ultimate.cpp` inside the existing Senscope Tilt patch marker block.
- The current source-shape checker confirms the patch marker block is present in `src/modes/Ultimate.cpp`.
- The current source-shape checker confirms the `lt1 && !lt2` and `lt2 && !lt1` exclusivity branches remain present.
- The current source-shape checker confirms right-stick and trigger assignments are not written inside the Senscope Tilt patch marker block it inspects.
- Existing profile/config source checks support treating explicit `BTN_UNSPECIFIED` as a source-backed disabled marker where it appears in source or checked fixtures.
- Default index handling is documented as one-based only where existing source/corpus checks confirm it.
- `defaultModeConfig = 0` is documented as not rejected by observed firmware validation, but outbound adapter use remains a policy decision.
- `applicableBackends` remains documented as UI/filter metadata unless stronger source authority appears.

## Hardware-Observed Facts

The sequence did not add new hardware evidence. It carried forward only prior hardware-observed facts from the existing hardware result material:

- Native Ultimate Tilt/Tilt2 behavior had already passed hardware smoke testing before this sequence.
- RF3 maps to LT1 for the current MVP layout.
- RF4 maps to LT2 for the current MVP layout.
- RF5 physical identity remains ambiguous from the current hardware result material.
- The both-held modifier table remains documented as hardware-observed from the existing result, not newly tested in this sequence.

No new hardware verification is claimed by this sequence.

## Open Policy Decisions

- Outbound disabled-remap handling remains unresolved unless source, corpus, or explicit user policy proves the intended behavior.
- Omitted `activates` must remain distinct from explicit `BTN_UNSPECIFIED`.
- A future adapter must not normalize omitted `activates` to `BTN_UNSPECIFIED`.
- Remap entry order must be preserved unless source/corpus proves reordering is safe.
- Many-to-one logical aliases are valid runtime behavior and must not be rejected automatically.
- Duplicate physical remap entries must be treated as first-entry-wins in runtime semantics unless stronger source appears.
- Outbound use of `defaultModeConfig = 0` requires a user/domain policy decision.
- Future conflict/chord behavior for arbitrary native Ultimate tables requires explicit policy metadata and review.
- Any next runtime implementation branch requires explicit user approval before coding firmware behavior changes.

## Open Corpus Requirements

- More profile corpus examples are needed before claiming a canonical Glyph JSON wire format.
- JSON fixtures remain examples and corpus candidates, not canonical write targets.
- Additional corpus is needed before deciding whether omitted `activates` has a safe outbound representation.
- Additional corpus is needed before deciding whether remap ordering can ever be normalized or sorted.
- Additional corpus is needed before deciding whether specific backend metadata fields have stronger semantics than UI/filtering.

## Open Hardware Requirements

- Run the Ultimate preservation hardware matrix on real hardware before any runtime patch is treated as hardware-ready.
- Confirm C-stick/right-stick preservation after any future runtime patch.
- Confirm trigger preservation after any future runtime patch.
- Confirm SOCD/opposite-direction behavior remains unchanged after any future runtime patch.
- Resolve RF5 physical identity using hardware evidence or source-backed documentation.
- Confirm profile preservation/readback if available and source-supported.
- Confirm both-held modifier behavior after any future runtime patch.
- Confirm default profile selection behavior after any future runtime patch.
- Optional nunchuk observations remain explicitly optional.
- Compare Switch visualization, mini-screen observations, and Ultimate Training Mode smoke results where possible.

## Next Branch That Would Require User Input

A branch that resolves adapter outbound policy would require user/domain input before implementation. In particular, outbound disabled-remap handling, omitted `activates`, explicit `BTN_UNSPECIFIED`, `defaultModeConfig = 0`, and arbitrary-table conflict/chord policy still require explicit decisions.

## Next Branch That Would Require Hardware

A branch claiming preservation across the full Ultimate layout would require real hardware execution of `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md` copied to a real result file. Until that exists, preservation readiness remains pre-hardware and cannot be promoted to hardware-verified.

## Next Branch That Would Require Runtime Patch Approval

Any branch implementing native Ultimate arbitrary table behavior, extending the current hard-coded Tilt/Tilt2 branches, using `MODE_CUSTOM` as a production path, or promoting the existing `SenscopePrototype` scaffold into runtime behavior requires explicit user approval before implementation.

The recommended future runtime direction remains a reviewed native table layer only after fixture contracts, source checkers, adapter policy decisions, corpus evidence, and hardware-test expectations are reviewed.

## No New Runtime Behavior Changed

No new runtime behavior was changed in this sequence. The sequence added documentation, fixture contracts, read-only checkers, templates, and readiness aggregation only.

No flashing automation, push-to-device automation, macros, turbo behavior, toggles, one-shots, timing automation, SOCD semantic changes, remap semantic changes, profile schema changes, configurator behavior changes, or Senscope game-semantic source changes were introduced.
