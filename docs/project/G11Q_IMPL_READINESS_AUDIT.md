# G11q Implementation Readiness Audit (Audit-Only, Docs-Only)

Status: audit-only and docs-only.  
Scope: readiness assessment for a future digital output runtime batch only.  
This document does not enable digital outputs.

## Purpose

Audit whether the repository is currently prepared for a later, separately approved selected-runtime digital output implementation batch, without changing current behavior.

## Current selected-runtime baseline (confirmed)

From inspected source:

1. `outputs.buttons = 0` in selected runtime:
   - `src/modes/SenscopePrototype.cpp`.
2. No selected-runtime digital behavior beyond neutral is active:
   - selected runtime does not call digital composition helpers.
3. Selected runtime remains left-stick table resolver only:
   - direction -> modifier mask -> `ResolveSenscopePrototypeExampleLeftStickRawCoordinate(...)`.

## Relevant file inventory

Digital helper files:

- `include/prototypes/senscope/SenscopePrototypeDigital.hpp`
- `src/prototypes/senscope/SenscopePrototypeDigital.cpp`

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

1. Digital helper surface exists.
2. Source-backed self-test coverage exists for digital neutral/default behavior:
   - `DigitalNeutralDefaultsToNoOutputs`.
3. Source-backed self-test coverage exists for invalid-bit diagnostics:
   - `DigitalUnknownDirectOutputBitDiagnostic`.
4. Output composition helper failure propagation coverage exists:
   - `OutputCompositionDigitalFailurePropagates`.
5. Runtime expansion readiness gate artifact already exists:
   - `docs/project/G11V_RUNTIME_EXPANSION_READINESS_GATE.md`.

## What is not yet ready (intentionally deferred)

1. No selected-runtime digital call-site plan is approved.
2. No output-bit UX/config authority is approved.
3. No config/protobuf/default activation path exists for `SenscopePrototype`.
4. No hardware-test approval is present in this batch scope.

## Minimum requirements for any future G11q implementation prompt

A future implementation prompt should require all of:

1. Selected-path-only source edits.
2. Fail-closed neutral behavior when digital rules are missing/invalid/unsupported.
3. Invalid-bit diagnostics preserved or strengthened.
4. Additive self-test updates for positive and fail-closed paths.
5. Build verification requirement (only when non-doc code changes occur).
6. Required grep/boundary checks:
   - `kEnableSenscopePrototypeManualSelection`
   - `kRunSenscopePrototypeConstructorSelfTest`
   - `SenscopePrototype`
   - `GameModeId`
   - `mode_id`
   - `activation_binding`
   - `default_mode_config`
7. Final report with a behavior-change matrix that explicitly states:
   - digital behavior delta;
   - Force Up-B side effects (expected none unless separately approved);
   - reachability/config/protobuf/default changes (expected none unless separately approved).

## Mandatory stop-before boundaries for future G11q implementation

Stop before:

1. Enabling non-neutral digital output behavior by default.
2. Making Force Up-B behavior changes.
3. Making mode reachability or config/protobuf/default activation changes.
4. Hardware flashing.
5. Gameplay semantic claims.

## Audit conclusion

Repository readiness for a future digital output implementation batch is partial and controlled:

- helper/self-test/readiness-gate scaffolding exists;
- selected-runtime enablement and UX/config/default-activation authority remain intentionally deferred.

