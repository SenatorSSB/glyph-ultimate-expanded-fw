# G11j Mode-Selection Wiring Design

Status: docs-only, not implementation  
Date: 2026-05-23  
Batch: G11i-j

## 1. Title and status

This document is the G11j mode-selection wiring design for `SenscopePrototype`.

This batch is documentation only. It does not implement mode wiring.

## 2. Scope

What was inspected:
- `src/core/mode_selection.cpp`
- `include/core/mode_selection.hpp`
- `include/modes/SenscopePrototype.hpp`
- `src/modes/SenscopePrototype.cpp`
- `include/core/InputMode.hpp`
- `src/core/InputMode.cpp`
- `include/core/ControllerMode.hpp`
- `src/core/ControllerMode.cpp`

What is designed:
- Future staged options for wiring `SenscopePrototype` into mode selection.
- A conservative sequence that keeps default runtime behavior safe.

What is not implemented:
- No `mode_selection` edits.
- No `GameModeId` additions.
- No activation bindings.
- No default config changes.

## 3. Current mode-selection source inventory

Current mode selection is driven by:
- Static mode instances in `src/core/mode_selection.cpp` (`melee_mode`, `projectm_mode`, `ultimate_mode`, `fgc_mode`, `rivals_mode`, `rivals2_mode`, `keyboard_mode`, `custom_mode`, `s64_mode`).
- `set_mode(...)` overloads in `include/core/mode_selection.hpp` and `src/core/mode_selection.cpp`.
- `select_mode(...)` comparing held-button masks against `game_mode_configs`.
- `setup_mode_activation_bindings(...)` building activation masks from config bindings.

`SenscopePrototype` is compile-visible but currently unregistered in `mode_selection`, so it is unreachable through normal runtime mode switching.

No changes were made to this inventory in G11j.

## 4. Future wiring options

1. Compile-visible but unregistered shell (current state).
- `SenscopePrototype` compiles but is not selectable.
- Lowest runtime risk.

2. Static mode instance registered in `mode_selection`.
- Add a static `SenscopePrototype` object in `src/core/mode_selection.cpp`.
- Still requires an explicit path in `set_mode(...)` to become reachable.

3. `GameModeId` addition.
- Add a new mode id in config/protobuf surfaces.
- Requires coordinated schema, config defaults, and migration decisions.

4. Config/default activation binding.
- Add a selectable config entry and activation binding.
- Highest user-facing risk if enabled by default.

5. Manual compile-time debug-only activation.
- Local/manual instantiation path for controlled firmware debugging.
- Avoids config schema changes at first, but still changes runtime reachability and must be explicitly approved.

6. Test-only local instantiation.
- Instantiate shell in isolated local test harness/build experiments only.
- Not a shipping mode-selection path.

## 5. Recommended safe wiring path

Recommended staged path:
1. G11k design review with explicit human approval before any runtime wiring.
2. Add a static mode instance only if required by the selected wiring shape.
3. Add a `GameModeId` only after explicit config/protobuf implications are reviewed.
4. Avoid default activation bindings until behavior is validated.
5. Keep the mode unreachable by default in initial wiring, if possible.

## 6. Constructor smoke-test caveat

Current `SenscopePrototype` constructor calls the prototype self-test helper. This remains isolated today because the mode is not selected/instantiated by mode-selection paths.

Before runtime wiring, decide whether to:
- keep constructor self-test,
- gate it behind a compile-time or debug condition, or
- remove it from constructor flow.

Recommendation: gate or remove constructor self-test before real runtime activation if build cost or side effects become meaningful.

## 7. Stop conditions before implementation

Stop and require explicit approval before G11k implementation if any of these remain undecided:
- final `GameModeId` decision;
- activation binding decision;
- default config decision;
- hardware safety review outcome;
- no-game-semantics boundary review outcome;
- explicit user approval for runtime wiring.

## 8. Verification

Docs-only design batch.

No runtime wiring was implemented.
