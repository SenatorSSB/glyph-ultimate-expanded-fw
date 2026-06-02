# Glyph Generated Constants Refactor Future Agent Prompt - 2026-05-28

## Do-not-run warning

Do not run without explicit user approval.

This prompt is a future implementation template only. It must not be used until
the user explicitly authorizes touching firmware source for a generated
constants refactor. That approval does not authorize runtime-loaded config,
serial/device write behavior, profile artifact changes, schema/protobuf changes,
behavior changes, or table value changes.

## Repository and branch setup

Repository: `SenatorSSB/glyph-ultimate-expanded-fw`

Base branch: `origin/configurator`

Proposed implementation branch:
`glyph/gfw2-generated-constants-refactor`

Required setup:

```bash
git fetch origin
git checkout configurator
git pull --ff-only origin configurator
git branch --list glyph/gfw2-generated-constants-refactor
git ls-remote --heads origin glyph/gfw2-generated-constants-refactor
```

Stop if the implementation branch already exists locally or remotely. Stop if
local `configurator` is not fast-forward clean with `origin/configurator`.

Only after explicit user approval and clean setup:

```bash
git checkout -b glyph/gfw2-generated-constants-refactor origin/configurator
```

## Source authority

Use only current repository sources:

- `src/modes/Ultimate.cpp`
- generated-config prototype docs/fixtures
- generated C++ diff artifact docs/fixtures
- generated constants readiness packet
- generated constants implementation plan
- generated constants execution packet
- generated constants hardware test matrix
- hardware validation and rollback plan
- preimplementation go/no-go index
- current identity-runtime checkers in `tools/`

Do not use external sources. Do not make hardware claims.

## Objective

Replace or isolate the current 25 identity-runtime `constexpr StickPoint` table
constants with generated or generated-like constants while preserving exact
current table values and current firmware runtime behavior.

The implementation must preserve:

- current evaluator phase order;
- current role bindings;
- current hard overrides;
- current generated-config review artifact behavior;
- current generated C++ review artifact behavior;
- all existing behavior-evaluator cases.

## Exact allowed changes

Allowed only if explicitly approved:

- `src/modes/Ultimate.cpp`
- optionally one generated constants file under an explicitly approved path such
  as `include/` or `src/`, only if the user approval and this prompt permit it;
- relevant docs/tools/checkers needed to verify the refactor.

No profile artifacts may change unless a separate future prompt explicitly
approves them.

## Non-goals

Do not implement runtime-loaded config.

Do not implement serial/device write behavior.

Do not change firmware runtime behavior.

Do not change table values.

Do not change profile artifacts.

Do not change profile/config/protobuf schema behavior.

Do not touch HAL/device transport paths.

Do not add macros, turbo, timing automation, toggles, one-shot behavior,
scripting, or history-dependent input behavior.

Do not claim hardware validation.

## Stop conditions

Stop if:

- explicit user approval for generated constants firmware source touch is missing;
- the proposed implementation branch already exists locally or remotely;
- `origin/configurator` is missing required readiness, planning, execution, or
  hardware-matrix docs/fixtures/checkers;
- local `configurator` is not fast-forward clean with `origin/configurator`;
- a behavior claim lacks source authority;
- an implementation step would change a table value;
- an implementation step would change runtime behavior;
- an implementation step would require runtime-loaded config;
- an implementation step would require serial/device write behavior;
- an implementation step would require profile artifact changes without
  explicit approval;
- an implementation step would require schema/protobuf changes;
- hardware matrix wording or final reporting would imply completed hardware validation;
- checker results contradict the go/no-go index or execution packet.

## Pre-edit verification

Run before editing firmware source:

```bash
.venv/bin/python tools/check_glyph_generated_constants_refactor_execution_packet.py
.venv/bin/python tools/check_glyph_implementation_planning_packets.py
.venv/bin/python tools/check_glyph_preimplementation_go_nogo_index.py
.venv/bin/python tools/check_glyph_runtime_loaded_config_design.py
.venv/bin/python tools/check_glyph_identity_runtime_config_contracts.py
.venv/bin/python tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py
.venv/bin/python tools/check_glyph_identity_runtime_generated_config_evaluator_input.py
.venv/bin/python tools/generate_glyph_identity_runtime_config_prototype.py
.venv/bin/python tools/generate_glyph_identity_runtime_config_prototype.py --json
.venv/bin/python tools/generate_glyph_identity_runtime_config_prototype.py --cpp
.venv/bin/python tools/check_glyph_identity_runtime_generated_config_prototype.py
.venv/bin/python tools/extract_glyph_identity_runtime_tables.py
.venv/bin/python tools/check_glyph_identity_runtime_table_source_sync.py
.venv/bin/python tools/check_glyph_identity_runtime_behavior_cases.py
.venv/bin/python tools/check_glyph_identity_runtime_behavior_evaluator.py
.venv/bin/python tools/check_glyph_no_forbidden_artifacts.py
```

Use `python3` only if `.venv/bin/python` is unavailable and dependencies are
present. Stop and report missing dependencies instead of inventing environment
setup.

## Implementation steps

1. Identify the exact 25 source-parsed identity-runtime table constants in
   `src/modes/Ultimate.cpp`.
2. Introduce the approved generated or generated-like constants boundary without
   changing any table value.
3. Keep evaluator phase order, role bindings, hard overrides, and table
   selection behavior unchanged.
4. Keep generated-config and generated C++ review artifacts aligned with the
   source-parsed table values.
5. Confirm no profile artifact, runtime-loaded config, serial/device writer,
   schema/protobuf, HAL/device transport, or build-output path was changed.

## Post-edit verification

Run after edits:

```bash
.venv/bin/python tools/check_glyph_generated_constants_refactor_execution_packet.py
.venv/bin/python tools/check_glyph_identity_runtime_generated_cpp_diff_artifact.py
.venv/bin/python tools/check_glyph_identity_runtime_generated_config_evaluator_input.py
.venv/bin/python tools/generate_glyph_identity_runtime_config_prototype.py
.venv/bin/python tools/generate_glyph_identity_runtime_config_prototype.py --json
.venv/bin/python tools/generate_glyph_identity_runtime_config_prototype.py --cpp
.venv/bin/python tools/check_glyph_identity_runtime_generated_config_prototype.py
.venv/bin/python tools/extract_glyph_identity_runtime_tables.py
.venv/bin/python tools/check_glyph_identity_runtime_table_source_sync.py
.venv/bin/python tools/check_glyph_identity_runtime_behavior_cases.py
.venv/bin/python tools/check_glyph_identity_runtime_behavior_evaluator.py
.venv/bin/python tools/check_glyph_smashbox_profile_tables.py
.venv/bin/python tools/check_glyph_smashbox_modifiers_runtime_source.py
.venv/bin/python tools/check_glyph_smashbox_identity_runtime_bindings.py
.venv/bin/python tools/check_glyph_no_forbidden_artifacts.py
.venv/bin/python tools/run_glyph_next_runtime_change_readiness_checks.py
```

Also run:

```bash
git diff --check
git status --short
```

## Build verification

Because this future branch would touch firmware source, run the repo-approved
firmware build command after post-edit docs/tools checks pass.

Do not commit `.pio`, `.uf2`, `.bin`, `.elf`, `.map`, or other build artifacts.
Build success is not hardware validation.

## Hardware-test requirement before merge

Hardware testing before merge is required for a future generated constants
firmware refactor.

The hardware matrix is:

- `docs/calibration/glyph_generated_constants_refactor_hardware_test_matrix_2026-05-28.md`

The matrix must be executed only after the future implementation branch and
firmware artifact exist. The result must be recorded separately before merge.

## Commit and push instructions

Commit only after verification passes and no forbidden files changed:

```bash
git add <approved changed files only>
git commit -m "refactor: isolate Glyph identity runtime constants"
git push -u origin glyph/gfw2-generated-constants-refactor
```

Do not push if verification fails, if the branch includes forbidden file touches,
or if the implementation depends on inferred behavior.

## Final response requirements

Report:

- changed files;
- whether `src/modes/Ultimate.cpp` changed;
- whether exact table values stayed unchanged;
- whether runtime behavior is intended unchanged;
- whether runtime-loaded config was not implemented;
- whether serial/device write behavior was not implemented;
- whether profile artifacts and schema/protobuf files stayed unchanged;
- verification commands and results;
- build command and result;
- hardware validation status;
- whether hardware testing before merge remains required;
- any stop conditions hit.
