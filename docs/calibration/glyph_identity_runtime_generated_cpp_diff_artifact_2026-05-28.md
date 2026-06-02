# Glyph Identity Runtime Generated C++ Diff Artifact - 2026-05-28

## Purpose and scope

This document records a tools/docs-only generated C++-shaped constants diff
artifact for the current Glyph Smash Box identity runtime tables in native
`MODE_ULTIMATE`.

The checked path is:

1. generated intermediate config
2. generated C++-shaped constants text
3. normalized comparison against current `src/modes/Ultimate.cpp` table
   declarations

Important scope boundaries:

- This is not firmware source.
- This is not included by firmware.
- This is not runtime-loaded config.
- This is not a device write path.
- This is not hardware validation.
- This does not alter runtime behavior.
- This does not alter table values.
- This does not add generated files to build paths.

## Source authority

Primary source authority:

- `src/modes/Ultimate.cpp`
- `tools/extract_glyph_identity_runtime_tables.py`
- `tools/generate_glyph_identity_runtime_config_prototype.py`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`

The generated C++-shaped text is downstream of source-parsed table data. It is a
review representation only, not a new source of runtime truth.

## What the checker validates

`tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py` validates:

- The existing generated-config prototype checker passes first.
- `render_cpp_prototype(build_config_prototype())` can produce deterministic
  C++-shaped review text.
- The generated text contains required caveats:
  - `generated prototype only`
  - `do not include in firmware`
  - `not firmware source`
  - `not runtime-loaded config`
  - `not hardware validation`
- The generated text does not contain forbidden generated-source or device-write
  phrases such as `#include`, `namespace`, `upload`, `flash`,
  `push-to-device`, `macro`, or `turbo`.
- All 25 expected `constexpr StickPoint` table declarations are present.
- Every generated table declaration has exactly 9 points.
- Every generated point matches the current source-parsed
  `src/modes/Ultimate.cpp` table exactly.
- If the committed text fixture is present, it lives under
  `docs/calibration/fixtures/` and exactly matches the generator output.

The committed artifact is:

- `docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt`

## What the checker does not validate

- It does not validate full firmware behavior.
- It does not validate a firmware source refactor.
- It does not validate runtime-loaded config.
- It does not validate serial transport, persistence, flashing, upload, or
  device write behavior.
- It does not validate hardware behavior.
- It does not validate nunchuk hardware behavior.
- It does not make Senscope or Super Smash Bros. Ultimate game-semantic claims.

## Runtime boundary caveat

No generated C++ text is placed under `src/`, `include/`, `HAL/`, `config/`,
`.pio`, or build-output paths.

The generated text has no `#include`, no namespace, and no implementation hook.
It is not referenced by `src/modes/Ultimate.cpp` and is not included by
firmware.

## Hardware-status caveat

The checker prints `hardware_status=not_new_hardware_result`.

Passing this checker is only a source/docs/tools consistency signal. It is not
new hardware evidence and must not be cited as hardware validation.

## Relation to table source sync

The table source-sync checker still directly compares source-parsed
`src/modes/Ultimate.cpp` tables with the evaluator's mirrored table constants.

This generated C++ diff artifact adds a downstream review representation:

1. `src/modes/Ultimate.cpp` tables are parsed by the extractor.
2. The generated-config prototype carries those table values.
3. The generated C++-shaped text renders those values as reviewable constants.
4. The new checker parses that review text and compares it back to the
   source-parsed tables exactly.

## Relation to generated-config prototype

The generated C++ text is rendered from the generated-config prototype. The new
checker runs `tools/check_glyph_identity_runtime_generated_config_prototype.py`
first and fails if that upstream guard fails.

The generated-config fixture remains the intermediate config artifact. The C++
text fixture is a plain-text review artifact only.

## Relation to generated-config evaluator input

The generated-config evaluator-input checker proves the intermediate config can
drive the bounded Python evaluator table input for current behavior cases.

The generated C++ diff artifact does not drive evaluator behavior. It only
checks the rendered C++-shaped table declarations against the current source
tables.

## Relation to future firmware refactor

This branch does not approve or implement a firmware refactor. The generated
C++-shaped text is useful because it can be reviewed and diffed before any
future source refactor proposal.

Any firmware source refactor must be a separate, explicitly approved task.

## Future migration path

1. Generated C++ text is a review artifact.
2. Generated text can be diffed against source tables.
3. Generated constants can be reviewed for a firmware source refactor.
4. Firmware source refactor only after explicit approval.
5. Runtime-loaded config design only after separate approval.
6. Senscope export contract only after a separate reviewed contract.
