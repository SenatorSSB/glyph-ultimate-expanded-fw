# Reconstructed source-authority evidence

Status: `NO_DISTINCT_AUTHORIZED_PRODUCTION_DELTA_FOUND`.

This packet reconstructs repository evidence only. It does not create source authority, prepare or install a candidate, modify active source, build firmware, or claim hardware correctness for an untested delta.

## Current baseline

- Starting configurator commit: `7fde661303dd836918b4c54008a47b89c478fc09`.
- Baseline: `current_source_owned_baseline`.
- Semantic digest: `9ea314bd17680d8353198ac174e59faf84c419fcd95a4ef3db24b3bd7e0f2970`.
- Table count/order: `28` / `dbf84342023124d0ce63414d3efe28db7f8cd3bcf950c7e1a9addcedbcff51cb`.
- Source: `src/modes/UltimateIdentityRuntimeTables.hpp`; interpreter: `src/modes/UltimateRuntimeConfigInterpreter.hpp`.
- Interpretation: the current source-owned 28-table firmware profile, whose Y2/Tilt3 source state is covered by the recorded latest-Y2 HARDWARE_PASS. Hardware acceptance is evidence for the current source state, not automatic authority for future replacements.

## Direct answers

1. The current production profile is the source-owned 28-table baseline identified above.
2. Coordinate-native contract, bridge, positive, negative, and dry-run fixtures are inactive design/test artifacts. The Y2-inspired sketch is illustrative only.
3. Firmware `RuntimeTableId::<name>` to `k<Name>Table` mappings are explicit in `src/modes/UltimateRuntimeConfigInterpreter.hpp`; the matrix records direct line evidence for all 28.
4. `y2_primary -> kY2Table` and `y2_tilt -> kTilt3Table` remain inferred-only from coordinate equality and source inspiration. No direct repository record connects those abstract IDs to symbols.
5. No complete repository-resident target with production intent and an authorized semantic delta was found.
6. No distinct target is production-authorized. The recorded `merge_approved: true` applies to the hardware-passed current source-owned port and is not an intake approver identity.
7. The source-equivalence packet is submitted for review and cannot be emitted. The required action is an explicit human approval-or-rejection decision, not merely supplying an identifier.
8. No production changeset or production generator-input can be emitted.
9. If a human approves the empty equivalence proof, they must set `authority.status` to `approved`, provide the exact approved `authority.approver`, replace `authority.statement` with an affirmative statement, and explicitly confirm or replace `authority.approval_reference`. A production delta additionally needs explicit target intent, owned symbols, exact replacements, ownership references, and production-authorized approval.

## Candidate decisions

| Candidate | Status | Eligibility | Reason |
| --- | --- | --- | --- |
| `current_source_owned_baseline` | `current` / `HARDWARE_PASS` | `SOURCE_EQUIVALENCE_ONLY` | the empty source-equivalence proof remains submitted for human approval; it is not approved or emittable |
| `coordinate_native_y2_inspired_sketch` | `inactive_design_only` / `NOT_TESTED` | `BLOCKED` | y2_primary and y2_tilt are illustrative IDs with no direct source-symbol mapping |
| `alternative_b_source_aligned_alias` | `historical` / `HARDWARE_PASS` | `SOURCE_EQUIVALENCE_ONLY` | historical source-aligned alias evidence is not a distinct production target |
| `generated_canonical_grid_candidate` | `failed_unmerged` / `HARDWARE_FAIL` | `BLOCKED` | hardware failure recorded for commit e643017c1577c9ca2b94581fa6f18c0dfb1bac9b |
| `coordinate_native_design_fixture_corpus` | `inactive_design_only` / `NOT_APPLICABLE` | `BLOCKED` | contract, positive, negative, and dry-run fixtures are design/test corpus, not production-authorized targets |

## Y2 equality and mapping boundary

- `y2_primary` exactly matches the current `Y2` table points and therefore has one equality match: `Y2` / `kY2Table`.
- `y2_tilt` exactly matches the current `Tilt3` table points and therefore has one equality match: `Tilt3` / `kTilt3Table`.
- This is `SUBSET_MATCH_ONLY`, not a complete no-op. Equality is supporting evidence only. The sketch contains no `table_symbol`; the converter emits the current canonical layout-spec fixture with table symbols, but does not derive a source mapping from those abstract IDs.
- The Y2 hardware result is source-owned firmware evidence; it does not prove the coordinate-native fixture’s identity or authorize a production replacement.

## Failed-candidate exclusion

The canonical-grid candidate at `e643017c1577c9ca2b94581fa6f18c0dfb1bac9b` remains `FORBIDDEN_FAILED_CANDIDATE` after `HARDWARE_FAIL`. Its canonical 0/128/255 content is not used as ownership, mapping, replacement, or hardware evidence in this packet. No production artifact is emitted.

## Source-equivalence packet

`docs/runtime_config/intakes/current_source_owned_baseline_equivalence.intake.json` is `submitted_for_review`, `overlay_preserve`, `source_equivalence_proof`, `source_baseline_derived`, with empty `owned_tables`, `declarations`, and `replacements`. Validation is blocked by `NOT_APPROVED`: a human must explicitly approve or reject before the approval fields can be updated. No generator-input v2 file is produced.

## Evidence inventory

### active_source

- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`

### canonical_extraction

- `tools/extract_glyph_identity_runtime_tables.py`
- `tools/generate_source_owned_runtime_config.py`
- `tools/source_owned_generator_modes.py`

### authority_workflow

- `tools/source_owned_source_authority_intake.py`
- `tools/manage_source_owned_source_authority_intake.py`
- `tools/check_glyph_source_owned_source_authority_intake.py`
- `docs/runtime_config/source_authority_intake_workflow.md`

### profile_and_bridge

- `docs/runtime_config/coordinate_native_runtime_profile_contract.md`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_source_owned_layout_spec_bridge.example.json`
- `tools/convert_coordinate_native_profile_to_source_owned_spec.py`

### generated_and_failed

- `docs/runtime_config/fixtures/generated_source_owned_layout_spec.json`
- `docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp`
- `docs/calibration/generated_canonical_grid_candidate_hardware_result_2026-07-19.md`

### hardware_and_lineage

- `docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md`
- `docs/calibration/alt_b_generated_table_alias_candidate_hardware_result_2026-07-09.md`
- `docs/runtime_config/latest_y2_layout_source_owned_port.md`

### current_docs

- `docs/AGENT_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/runtime_config/README.md`
- `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`
- `docs/runtime_config/source_owned_table_symbol_map.md`

### lineage_commits

- `9842724b12b92988acfd7ed870512e055d79e3b5`
- `2fc0ce3d5149565b3b52202cb234e359e8c84b28`
- `83c8dba989605f7d0cf591858ffa336ab10dea61`
- `5d6d0f3ca215584915b93dbf9e8836468cc17b94`
- `4924f7bd6a946d14ff9a68d5cbdc76a550b7b1e2`
