# G11p Implementation Readiness Audit (Audit-Only, Docs-Only)

Status: audit-only and docs-only.  
Scope: readiness assessment for a future Force Up-B runtime batch only.  
This document does not enable or implement Force Up-B behavior.

## Purpose

Audit whether the repository is currently prepared for a later, separately approved Force Up-B implementation batch, while preserving the existing selected-runtime baseline.

## Current source-backed baseline (confirmed)

From inspected source:

- Force Up-B runtime remains disabled in the current selected runtime baseline:
  - `src/modes/SenscopePrototype.cpp` has no call-site to Force helper entry points.
- Selected runtime currently uses left-stick table resolver only:
  - `src/modes/SenscopePrototype.cpp` resolves direction -> modifier mask -> `ResolveSenscopePrototypeExampleLeftStickRawCoordinate(...)`.
- Digital outputs remain neutral in selected runtime:
  - `src/modes/SenscopePrototype.cpp` sets `outputs.buttons = 0`.
- Manual selection remains default-unreachable:
  - `src/core/mode_selection.cpp` keeps `kEnableSenscopePrototypeManualSelection = false`.
- Constructor self-test remains default-off:
  - `src/modes/SenscopePrototype.cpp` keeps `kRunSenscopePrototypeConstructorSelfTest = false`.

## Relevant file inventory

Force helper files:

- `include/prototypes/senscope/SenscopePrototypeForce.hpp`
- `src/prototypes/senscope/SenscopePrototypeForce.cpp`

Output helper files:

- `include/prototypes/senscope/SenscopePrototypeOutput.hpp`
- `src/prototypes/senscope/SenscopePrototypeOutput.cpp`

Validation/self-test files:

- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`

Selected runtime and mode-selection files:

- `src/modes/SenscopePrototype.cpp`
- `src/core/mode_selection.cpp`

## What is already ready

1. Force helper surface exists.
2. Output composition helper surface exists.
3. Source-backed self-test coverage exists for:
   - Force no-match disabled path (`ForceNoMatchingRuleRemainsDisabled`).
   - Force resolved path (`ForceFixedRuleResolvesCoordinateAndB`, `ForceUpwardHorizontalRuleResolvesLeftXAndForcedY`).
   - Force ambiguity path (`ForceEqualPriorityAmbiguityDetected`).
   - Output composition helper paths (`OutputCompositionForceWins`, `OutputCompositionForceSkipsTableResolver`, `OutputCompositionTableResolverUsedWhenNoForce`, `OutputCompositionDigitalFailurePropagates`, `OutputCompositionDirectionFailurePropagates`, `OutputCompositionNoLeftStickWhenNoMatchingCombo`, `OutputCompositionNoLeftStickKeepsNeutralPacketCoordinate`).
4. Runtime expansion readiness gate artifact already exists:
   - `docs/project/G11V_RUNTIME_EXPANSION_READINESS_GATE.md`.

## What is not yet ready (intentionally deferred)

1. No selected-runtime Force call-site plan has been explicitly approved for implementation.
2. No runtime enablement approval exists for Force Up-B behavior.
3. No hardware-test approval is present in this batch scope.
4. No config/protobuf/default activation path exists for `SenscopePrototype` reachability.

## Minimum requirements for any future G11p implementation prompt

A future implementation prompt should require all of:

1. Selected-path-only source edits.
2. Explicit fail-closed behavior for no-match and ambiguous Force states.
3. Additive self-test updates for new behavior and failure paths.
4. Build verification requirement (only when non-doc code changes occur).
5. Required grep/boundary checks:
   - `kEnableSenscopePrototypeManualSelection`
   - `kRunSenscopePrototypeConstructorSelfTest`
   - `SenscopePrototype`
   - `GameModeId`
   - `mode_id`
   - `activation_binding`
   - `default_mode_config`
6. Final report with a behavior-change matrix that explicitly states:
   - runtime behavior deltas;
   - reachability/config/protobuf/default changes (expected none unless separately approved);
   - digital-output side effects (expected none unless separately approved).

## Mandatory stop-before boundaries for future G11p implementation

Stop before:

1. Enabling Force Up-B behavior by default.
2. Making digital behavior changes.
3. Making mode reachability or config/protobuf/default activation changes.
4. Hardware flashing.
5. Gameplay semantic claims.

## Audit conclusion

Repository readiness for a future Force Up-B implementation batch is partial and controlled:

- helper/test/readiness-gate scaffolding exists;
- runtime enablement and reachability/config approvals remain intentionally deferred.

