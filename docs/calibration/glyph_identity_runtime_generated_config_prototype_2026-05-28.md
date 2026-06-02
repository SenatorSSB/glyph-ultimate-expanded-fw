# Glyph Identity Runtime Generated Config Prototype - 2026-05-28

## Purpose and scope

This document records a tools/docs-only generated-config prototype for the
current Glyph Smash Box identity runtime in native `MODE_ULTIMATE`.

The prototype proves a review path from current source-backed identity runtime
data to a declarative intermediate config and deterministic C++-shaped constants
text. It does not change firmware runtime behavior.

Important scope boundaries:

- This is not firmware source.
- This is not included by firmware.
- This is not runtime-loaded config.
- This is not a serial/device write path.
- This is not hardware validation.
- This does not alter table values or behavior.

## Source authority

Primary source authority:

- `src/modes/Ultimate.cpp`
- `tools/extract_glyph_identity_runtime_tables.py`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`
- `docs/calibration/glyph_identity_runtime_behavior_evaluator_harness_2026-05-28.md`
- `docs/calibration/glyph_identity_runtime_table_source_sync_2026-05-28.md`

The table values come from source-parsed `constexpr StickPoint` tables in
`src/modes/Ultimate.cpp`. Role metadata comes from the existing role-map fixture.
Behavior-case fixture metadata is used only for coverage metadata, not as table
truth.

## Generated outputs

`tools/generate_glyph_identity_runtime_config_prototype.py` provides three
review outputs:

- Default text summary with status, table count, role binding count, source
  paths, and `hardware_status=not_new_hardware_result`.
- Deterministic JSON intermediate config through `--json`.
- Deterministic C++-shaped constants text through `--cpp`.

The committed fixture
`docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
is the declarative intermediate config. It is not generated C++ output.

`tools/check_glyph_identity_runtime_generated_config_prototype.py` validates the
generator output and confirms the generated tables exactly match the
source-parsed runtime tables.

## What the generator proves

- The current 25 source-parsed identity runtime stick tables can be represented
  in a deterministic declarative config prototype.
- The prototype can carry role bindings, priority stage names, hard override
  constants, nunchuk status, and source authority without touching firmware
  runtime code.
- The C++-shaped text can be generated as a review artifact containing all 25
  `StickPoint` table declarations.
- The generated tables match the current source-parsed `src/modes/Ultimate.cpp`
  tables exactly.

## What the generator does not prove

- It does not prove a runtime-loaded config design.
- It does not prove a firmware refactor is safe.
- It does not prove device write, serial transport, or persistence behavior.
- It does not prove hardware behavior.
- It does not validate nunchuk hardware behavior.
- It does not make Senscope or Super Smash Bros. Ultimate game-semantic claims.

## Hardware-status caveat

The generator and checker print `hardware_status=not_new_hardware_result`.
Passing them is only a source/docs/tools consistency signal. It must not be
treated as new hardware evidence.

Nunchuk behavior remains marked
`nunchuk_status=preserved_but_not_hardware_validated`.

## Runtime-boundary caveat

No files under `src/`, `include/`, `HAL/`, `config/`, `.pio`, or build-output
paths are generated or changed by this prototype.

The C++-shaped output is deliberately not a firmware source file. It has no
includes, is not placed in a build path, and is not referenced by
`src/modes/Ultimate.cpp`.

## Relation to role map

The role map fixture remains the source for role metadata, including:

- `source_authority`
- `nunchuk_status`
- `direction_convention`
- `bindings`
- `layering.priority`
- `suppression_rules`
- `table_ids_and_selection`
- `analog_constants`

The prototype preserves those field names instead of redesigning the role-map
schema in this branch.

## Relation to behavior cases

The behavior-case fixture contributes coverage metadata such as case count and
category names. It does not supply table truth, and generated table values do not
derive from behavior-case expected output rows.

## Relation to behavior evaluator

The current behavior evaluator remains a bounded Python mirror for representative
cases. This generated-config prototype is a separate review artifact. The
readiness runner invokes the generated-config checker before the behavior
evaluator so source-table sync and generated prototype structure are checked
before case evaluation.

## Relation to table source sync

`tools/extract_glyph_identity_runtime_tables.py` still owns extraction of the 25
required source table symbols. The generated-config checker compares the
prototype tables against that extractor output exactly.

This keeps the generated prototype downstream of the source-table sync path
without making it firmware input.

## Future migration path

1. Current docs/tools generated-config prototype.
2. Generated C++ constants review artifact.
3. Behavior evaluator uses generated intermediate config.
4. Firmware source refactor to generated constants, only after explicit approval.
5. Runtime-loaded config design, only after separate design approval.
6. Senscope export contract.
