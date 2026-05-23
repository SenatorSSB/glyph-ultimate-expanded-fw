# G11p Force Up-B Runtime Design (Design-Only)

Status: design-only (no implementation in this batch)

## Purpose

Define the smallest future, source-backed path to add Force Up-B behavior to `SenscopePrototype` selected runtime behavior, without enabling it now.

## Current source-backed baseline

- `SenscopePrototype` selected runtime currently keeps Force Up-B disabled.
- `src/modes/SenscopePrototype.cpp` selected-path runtime currently resolves direction + modifier mask + left-stick table only.
- `src/modes/SenscopePrototype.cpp` currently leaves digital outputs neutral via `outputs.buttons = 0`.
- `src/modes/SenscopePrototype.cpp` keeps right-stick centered and triggers zeroed before selected left-stick assignment.
- `src/core/mode_selection.cpp` keeps manual debug selection unreachable by default through:
  - `kEnableSenscopePrototypeManualSelection = false`

## Existing Force/helper files and runtime call-site inventory

Force/helper sources present:

- `include/prototypes/senscope/SenscopePrototypeForce.hpp`
- `src/prototypes/senscope/SenscopePrototypeForce.cpp`
- `include/prototypes/senscope/SenscopePrototypeOutput.hpp`
- `src/prototypes/senscope/SenscopePrototypeOutput.cpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`

Selected-runtime call-site status:

- `src/modes/SenscopePrototype.cpp` does not currently call `ResolveSenscopePrototypeForceOverride(...)`.
- `src/modes/SenscopePrototype.cpp` does not currently call `ComposeSenscopePrototypeOutput(...)`.
- Current selected runtime path is still explicit direction/modifier/table-resolver wiring only.

## Future implementation proof requirements before enabling Force Up-B

Any later implementation batch must prove all of the following before enabling Force Up-B behavior:

1. Rule-source authority is explicit and source-backed (no inferred gameplay semantics).
2. Selected-path-only scope is preserved (no effect unless `SenscopePrototype` is selected).
3. No mode/default reachability expansion is introduced.
4. No persistent behavior survives release of the triggering condition.
5. No timing automation, macro behavior, turbo behavior, or latch/toggle behavior is introduced.
6. Failure handling is fail-closed to disabled Force Up-B behavior.

## Candidate data/control boundary (future)

Candidate boundary for a later implementation:

1. A profile/source-backed Force rule indicates Force Up-B should be active.
2. Selected runtime applies the rule only while selected and while the trigger condition is active.
3. Runtime never uses firmware-side gameplay threshold logic.
4. Runtime does not add toggles, timers, or persistent post-release states.
5. Runtime does not alter mode-selection logic, config/protobuf/default activation, or backend flashing/export workflows.

## Required fail-closed behavior (future)

If a Force rule is invalid, missing, ambiguous, or unsupported:

- Force Up-B remains disabled.
- Runtime continues to allow neutral left-stick fallback on helper/resolver failure.
- No additional digital/button behavior is enabled as a side effect.

## Exact stop conditions for later Force implementation work

Stop and ask before proceeding if any step would:

1. Enable Force Up-B in checked-in source.
2. Change button/digital output behavior.
3. Rely on inferred game semantics.
4. Change mode reachability/config/protobuf/default mode.
5. Require hardware flashing.

## Future verification checklist (for a later implementation batch)

Source grep checks:

```bash
grep -R "kEnableSenscopePrototypeManualSelection" -n include src
grep -R "kRunSenscopePrototypeConstructorSelfTest" -n include src
grep -R "SenscopePrototype" -n include src docs/project
grep -R "GameModeId" -n include src
grep -R "mode_id" -n include src proto config docs/project
grep -R "activation_binding" -n include src proto config docs/project
grep -R "default_mode_config" -n include src proto config docs/project
```

Selected-path-only checks:

1. Confirm Force behavior is applied only inside selected `SenscopePrototype` runtime flow.
2. Confirm no changes to `Ultimate`, `CustomControllerMode`, `InputMode`, or `ControllerMode` behavior.
3. Confirm no new default mode activation path (`GameModeId`, config/protobuf/default mode fields).
4. Confirm fallback-to-neutral still holds when direction/modifier/resolver/force status is not resolved.

Build check (only when code changes are present):

```bash
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
```

Final report requirements for future implementation batch:

1. Explicitly state whether Force Up-B is still disabled by default.
2. Report whether any reachability/config/protobuf/default path changed.
3. Report fail-closed behavior observed in tests.
4. Report whether digital output behavior changed.
5. Report whether hardware flashing/export/push workflows were added (expected: no).

## This batch decision

This document records design boundaries only. It does not enable or implement Force Up-B behavior.
