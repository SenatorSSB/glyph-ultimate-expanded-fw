# Glyph Identity Runtime Behavior Evaluator Harness - 2026-05-28

## Purpose and scope

`tools/check_glyph_identity_runtime_behavior_evaluator.py` is a source-backed Python mirror evaluator for the current representative Glyph Smash Box identity runtime behavior cases in native `MODE_ULTIMATE`.

The evaluator is bounded to the current fixture at `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`. It is a regression harness for docs/fixture/source consistency, not a complete firmware simulator.

## Source authority

Primary source authority:

- `src/modes/Ultimate.cpp`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_architecture_hardening_2026-05-28.md`
- `docs/calibration/glyph_identity_runtime_table_source_sync_2026-05-28.md`

The evaluator validates key source anchors in `src/modes/Ultimate.cpp` before running cases. If the source shape changes, the evaluator fails and requires review rather than carrying old expectations forward silently.

## What the evaluator validates

- The existing behavior-case fixture still passes `tools/check_glyph_identity_runtime_behavior_cases.py`.
- The evaluator's mirrored table constants still match the source-parsed `constexpr StickPoint` tables in `src/modes/Ultimate.cpp` through `tools/check_glyph_identity_runtime_table_source_sync.py`.
- Representative input rows can be evaluated through a bounded Python mirror of the current `Ultimate.cpp` digital and analog phase order.
- Explicitly asserted output fields in the fixture match the mirror result.
- Unsupported expected fields fail clearly instead of being ignored.
- Nunchuk source-preservation rows remain marked as not hardware validated.

## What it intentionally does not validate

- It does not validate hardware behavior.
- It does not cover the full runtime state space.
- It does not drive the evaluator from source-parsed tables yet; source parsing is currently a sync guardrail for the mirrored constants.
- It does not generate config or runtime-loaded config.
- It does not implement serial write, flashing, or push-to-device behavior.
- It does not make Senscope or Super Smash Bros. Ultimate game-semantic claims.

## Hardware-status caveat

The evaluator prints `hardware_status=not_new_hardware_result`. Passing the evaluator is only a source/fixture regression signal and must not be treated as new hardware evidence.

## Nunchuk-status caveat

Nunchuk paths are source-present in `src/modes/Ultimate.cpp` and preserved by the evaluator, but the latest cited hardware result did not validate nunchuk behavior. The evaluator prints `nunchuk_status=preserved_but_not_hardware_validated`.

## Future migration path

1. Current Python mirror evaluator with source-parsed table sync.
2. Evaluator driven by extracted constants.
3. C++ unit-style harness.
4. Generated-config regression test.
5. Runtime-loaded config validation.
