# Glyph Native Ultimate Current Tilt Table Fixture Seed - 2026-05-26

## Why This Fixture Exists

This fixture seeds a concrete, reviewable baseline artifact for current native Ultimate Tilt behavior without adding runtime table code. It is intended for future regression planning and design review, not as approval to implement arbitrary native Ultimate table runtime behavior.

Primary contract and roadmap anchors:

- `docs/calibration/glyph_firmware_workstream_roadmap_2026-05-26.md`
- `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`
- `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`

## Source and Evidence Scope

The seeded rows are constrained to repo-local source and already recorded smoke evidence:

- Source-confirmed current runtime formulas/tables:
  - `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`
  - `src/modes/Ultimate.cpp` (cross-check only; no modifications)
- Hardware-smoke-tested Tilt1/Tilt2 rows:
  - `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md`

## Distinctions Captured in This Seed

- Source-confirmed runtime formula/table:
  - Included as explicit 9-way coordinates for `base_no_modifier`, `tilt1_lt1`, `tilt2_lt2`.
- Hardware-smoke-tested Tilt1/Tilt2 rows:
  - Reflected in fixture `source_evidence` and coordinate rows.
- Observed-only both-held behavior:
  - Both-held LT1+LT2 is kept as observed existing combined behavior metadata only.
  - It is not promoted to a normative named table entry contract in this fixture.
- Unresolved preservation/export/profile blockers:
  - Preservation matrix execution remains outstanding (`docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`).
  - Export corpus remains blocked (`docs/calibration/glyph_profile_config_export_corpus_protocol_2026-05-26.md`).
  - Next runtime readiness remains gated (`docs/calibration/glyph_next_runtime_change_readiness_index_2026-05-26.md`).

## Boundary and Non-Goal Notes

- No runtime table implementation is added.
- No profile/schema/proto/configurator changes are made.
- No flashing or push-to-device automation is added.
- This fixture does not make Smash or game-semantic claims.

## Intended Use

This seeded fixture is a current-state baseline artifact for review and regression planning. It does not authorize production arbitrary-table runtime changes and does not alter source-authority boundaries.
