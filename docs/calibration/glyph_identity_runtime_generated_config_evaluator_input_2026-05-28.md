# Glyph Identity Runtime Generated Config Evaluator Input - 2026-05-28

## Purpose and scope

This document records a tools/docs-only checker proving that the current
generated intermediate config prototype can supply table data and relevant
metadata to the existing identity runtime behavior evaluator.

The checked path is:

1. generated intermediate config prototype
2. evaluator-compatible table and metadata input
3. exact representative behavior-case evaluation parity

Important scope boundaries:

- This is not firmware source.
- This is not included by firmware.
- This is not runtime-loaded config.
- This is not a device write path.
- This is not hardware validation.
- This does not alter runtime behavior.
- This does not alter table values.

## Source authority

Primary source authority:

- `src/modes/Ultimate.cpp`
- `tools/extract_glyph_identity_runtime_tables.py`
- `tools/generate_glyph_identity_runtime_config_prototype.py`
- `tools/check_glyph_identity_runtime_generated_config_prototype.py`
- `tools/check_glyph_identity_runtime_behavior_evaluator.py`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`

The generated-config checker remains responsible for proving that generated
config table values match the source-parsed `constexpr StickPoint` tables in
`src/modes/Ultimate.cpp`.

## What the checker proves

`tools/check_glyph_identity_runtime_generated_config_evaluator_input.py` proves:

- The committed generated-config prototype passes its existing prototype
  checker first.
- The generated config has the expected schema name, contract version,
  `MODE_ULTIMATE` scope, source status, hardware status, and nunchuk status.
- The generated config carries non-empty `tables`, `role_bindings`,
  `priority_model`, and `hard_overrides` objects.
- The generated config table names exactly match the evaluator's expected table
  names.
- Every generated table has 9 points.
- Every generated point is two non-boolean integers in `[0,255]`.
- The generated table shape can be converted to the evaluator's tuple table
  shape.
- All current behavior cases evaluate successfully with generated-config-backed
  tables.
- Generated-config-backed evaluation matches the current fixture expectations
  and the ordinary evaluator table path.

Unsupported expected fixture fields still fail through the existing evaluator
comparison logic. The checker does not silently accept unknown expected output
fields.

## What the checker does not prove

- It does not prove full firmware behavior.
- It does not prove a runtime-loaded config design.
- It does not prove a firmware refactor to generated constants.
- It does not prove serial transport, persistence, flashing, upload, or device
  write behavior.
- It does not prove hardware behavior.
- It does not validate nunchuk hardware behavior.
- It does not make Senscope or Super Smash Bros. Ultimate game-semantic claims.

## Runtime boundary caveat

The checker imports the current Python evaluator and temporarily replaces its
in-memory `TABLES` object with tables decoded from the generated-config fixture.
The evaluator table object is restored in a `finally` block.

No files under `src/`, `include/`, `HAL/`, `config/`, `.pio`, or build-output
paths are generated or changed. `src/modes/Ultimate.cpp` remains the runtime
source authority and is not modified by this validation path.

## Hardware-status caveat

The checker prints `hardware_status=not_new_hardware_result`.

Passing this checker is only a source/docs/tools consistency signal. It is not
new hardware evidence and must not be cited as hardware validation.

## Nunchuk-status caveat

The checker prints
`nunchuk_status=preserved_but_not_hardware_validated`.

Nunchuk paths are preserved in the evaluator and generated metadata, but this
checker does not validate nunchuk hardware behavior.

## Relation to generated-config prototype

This checker is downstream of
`tools/check_glyph_identity_runtime_generated_config_prototype.py`.

The prototype checker proves generated-config shape, caveats, hard overrides,
and exact source-table matching. This evaluator-input checker then proves that
the committed generated config can be consumed by tools as evaluator table data.

## Relation to table source sync

The existing table-source sync remains in place. This checker does not remove or
weaken the direct guard that compares evaluator table constants against
source-parsed `src/modes/Ultimate.cpp` tables.

The new checker adds a second validation path:

1. `src/modes/Ultimate.cpp` tables are parsed by the extractor.
2. The generated-config prototype checker confirms generated tables match those
   source-parsed tables.
3. The evaluator-input checker confirms those generated tables can drive the
   evaluator for all current behavior cases.

## Relation to behavior evaluator

The ordinary evaluator remains a bounded Python mirror for representative cases.
This checker reuses its `evaluate_case` and `compare_expected` functions instead
of duplicating evaluator logic.

The intentional prototype boundary is that only table data is injected. Runtime
phase order, role resolution, hard override application, and output comparison
still come from the existing evaluator module.

## Relation to future generated C++ constants

This checker does not generate C++ for firmware. It supports a future review
path where generated C++ constants can be diffed against source-backed tables as
a review artifact before any firmware refactor is approved.

Generated C++ constants remain future review material only. They are not
included by firmware in this stage.

## Future migration path

1. Generated config is usable by tools as evaluator input.
2. Evaluator can be fully driven by generated intermediate config.
3. Generated C++ constants review artifact can be diffed against source.
4. Firmware source refactor to generated constants only after explicit approval.
5. Runtime-loaded config design only after separate design approval.
6. Senscope export contract.
