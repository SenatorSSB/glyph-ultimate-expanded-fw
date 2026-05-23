# G11q Digital Output Behavior Design (Design-Only)

Status: design-only (no implementation in this batch)

## Purpose

Define a conservative path for possible future selected-runtime digital output behavior while preserving the current neutral baseline until separately approved.

## Current source-backed baseline

- `src/modes/SenscopePrototype.cpp` sets:
  - `outputs.buttons = 0`
- No selected-runtime digital output behavior is currently active beyond neutral.
- Current selected runtime remains left-stick resolver output only, with neutral right-stick/triggers defaults.

## Boundary separation

Keep these concerns separate:

1. Controller digital outputs:
   - firmware output bits emitted to `OutputState` (for example, `outputs.buttons`).
2. Physical input source fields:
   - source-side inputs (`InputState` fields like `rf2`, `rf3`, `rf4`) used as conditions.
3. Game semantics:
   - gameplay meaning of button combinations, thresholds, and action labels.

This design permits discussion of (1) and (2) only. It does not promote (3) into firmware truth.

## Source files for future implementation inspection

Primary selected-runtime and helper files to inspect before any future digital behavior implementation:

- `src/modes/SenscopePrototype.cpp`
- `include/prototypes/senscope/SenscopePrototypeDigital.hpp`
- `src/prototypes/senscope/SenscopePrototypeDigital.cpp`
- `include/prototypes/senscope/SenscopePrototypeOutput.hpp`
- `src/prototypes/senscope/SenscopePrototypeOutput.cpp`
- `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`
- `src/core/mode_selection.cpp`

## Neutral future categories (design-only)

Possible future categories for selected-runtime digital behavior, expressed in neutral terms:

1. Pass-through:
   - selected runtime forwards a source-backed digital mask input without semantic relabeling.
2. Explicitly configured output bits:
   - selected runtime composes output bits from source-backed rule tables.
3. Disabled/neutral:
   - selected runtime forces neutral digital output (`0`) for unsupported or unapproved paths.

No gameplay labels/meanings should be assigned unless already directly source-backed by existing firmware fields.

## Required fail-closed behavior (future)

If digital rules are missing, invalid, ambiguous, or unsupported:

- output remains neutral (`0`);
- selected runtime continues functioning without new digital emissions;
- invalid digital masks do not silently pass unknown bits.

## Risks to control in later implementation

1. Accidental button presses from unintended digital composition.
2. Unintended selected-mode behavior changes from broadened output scope.
3. Conflating modifier-mask input logic with digital output emission logic.
4. Treating game semantics as firmware-level source authority.

## Stop conditions for later digital implementation work

Stop and ask before proceeding if any step would:

1. Enable any non-neutral digital output behavior in checked-in source.
2. Change behavior in `Ultimate`, `CustomControllerMode`, `InputMode`, or `ControllerMode`.
3. Require config/protobuf/default schema changes.
4. Require hardware flashing.

## Future verification checklist (for a later implementation batch)

Baseline and scope checks:

```bash
git status
git diff --stat
grep -R "SenscopePrototype" -n include src docs/project
grep -R "GameModeId" -n include src
grep -R "mode_id" -n include src proto config docs/project
grep -R "activation_binding" -n include src proto config docs/project
grep -R "default_mode_config" -n include src proto config docs/project
```

Selected-path-only checks:

1. Confirm digital behavior changes are limited to selected `SenscopePrototype` runtime path.
2. Confirm mode reachability defaults remain unchanged.
3. Confirm unsupported or invalid digital rules fail closed to neutral.
4. Confirm right-stick/C-stick and trigger neutral baseline is unchanged unless separately approved.

Build check (only when code changes are present):

```bash
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
```

## This batch decision

This document is design-only and keeps current selected-runtime digital behavior neutral.
