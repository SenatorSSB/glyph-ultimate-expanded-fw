# Glyph Physical/Logical RF5 Gap Index - 2026-06-06

## Purpose and scope

This packet separates printed physical mapping facts, source-backed runtime
mapping facts, old ambiguous RF5 smoke evidence, and future user/hardware input
requirements.

Status: `physical_logical_rf5_gap_index_docs_tools_only`

This is docs/tools-only. It does not change physical IDs, firmware behavior,
runtime mappings, active profile artifacts, or hardware result records.

## Source inputs

Source-backed and repo-recorded inputs:

- Physical/logical layout map:
  `docs/calibration/glyph_physical_logical_layout_map_2026-05-26.md`
- Merged-state consistency audit:
  `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md`
- Historical Tilt/Tilt2 hardware result:
  `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`
- GFW3 runtime remap hardware result:
  `docs/calibration/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md`
- GFW3 hardware result fixture:
  `docs/calibration/fixtures/glyph_gfw3_runtime_remap_hardware_result_2026-06-06.json`
- Identity runtime role-map fixture:
  `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- Roadmap next-work index:
  `docs/calibration/glyph_roadmap_next_work_index_2026-06-06.md`

## Layer-separated findings

| Layer | Current finding | Status | Caveat |
| --- | --- | --- | --- |
| Printed/base physical marking | RF5 is transcribed as center-right / RF cluster, far-right upper button. | `RECORDED_TRANSCRIPTION` | Repo text records the user-provided transcription; this does not rewrite old smoke rows. |
| Matrix/display source facts | `BTN_RF5` matrix and input-viewer coordinates are recorded in the physical/logical map. | `SOURCE_RECORDED` | Display coordinates are rendering positions, not physical matrix coordinates. |
| Historical RF5 negative smoke row | The old RF5 negative check remains `NOT_TESTED_AMBIGUOUS`. | `UNRESOLVED_HISTORICAL_ROW` | Do not retroactively convert the old row to PASS. |
| Current MVP RF3/RF4 tilt path | RF3/RF4 were confirmed for the earlier Tilt1/Tilt2 MVP mapping. | `SOURCE_AND_HARDWARE_RECORDED` | Profile-specific; not universal physical/logical authority. |
| Later GFW3 RF5 hardware scope | GFW3 result includes `base_rf5_up_a` as PASS in the GFW3 runtime remap scope. | `LATER_SCOPE_LIMITED_RESULT` | This validates the GFW3 row scope only; it does not retcon the historical ambiguous RF5 row. |
| Identity runtime role-map fixture | The identity runtime role-map fixture records RF5 in its own source-confirmed hardware-observed scope. | `SOURCE_RECORDED_SCOPE` | Future use must cite the exact scope and avoid merging old/new role assumptions. |

## Explicit non-claims

- No physical ID mapping changes are made here.
- No firmware behavior changes are made here.
- No active profile artifact changes are made here.
- No hardware validation claim is newly made here.
- No nunchuk hardware validation claim is made here.
- No runtime-loaded config is implemented here.
- No WebSerial/device write is implemented here.
- No external remapper adapter output is generated here.
- No Super Smash Bros. Ultimate game-semantic claim is made here.
- No old RF5 ambiguity is resolved by inference here.

## Future resolution requirements

Future resolution depends on the claim being made:

- To update the historical RF5 negative row, provide a user-reported hardware
  retest or result packet that explicitly targets that row.
- To promote a physical/logical mapping fact beyond the recorded transcription,
  provide source authority or explicit user/domain input.
- To reconcile role-map usage across old Tilt/Tilt2, identity runtime, and GFW3
  scopes, provide exact scope language and deterministic fixture/checker coverage.

Until one of those inputs exists, the future resolution status is
`requires_source_authority_hardware_result_or_user_domain_input`.

## Branch policy

A future branch may refine this packet or add a result template. It must stop
before changing firmware behavior, changing active profile artifacts, claiming
new hardware validation, or deciding new mappings from inference.
