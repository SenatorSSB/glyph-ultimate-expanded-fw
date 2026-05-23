# G11o Validation Hardening and Runtime-Readiness Gate

Status: implemented (prototype validation/self-test/docs only)  
Branch: `proto/glyph-validation-readiness-g11o`  
Implementation boundary: isolated `SenscopePrototype` helper validation/self-test and docs only; no selected runtime output behavior wiring.

## 1. Scope

Files changed in this batch:

- `include/prototypes/senscope/SenscopePrototypeTypes.hpp`
- `src/prototypes/senscope/SenscopePrototypeValidation.cpp`
- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`
- `docs/project/G11O_VALIDATION_HARDENING_AND_RUNTIME_READINESS_GATE.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md` (minimal queue update)

Intentionally not wired:

- no `src/core/mode_selection.cpp` changes;
- no `GameModeId` additions;
- no activation bindings;
- no default config changes;
- no `Ultimate` / `CustomControllerMode` / `InputMode` / `ControllerMode` behavior changes;
- no output report behavior changes;
- no firmware `OutputState` write-path usage of prototype outputs;
- no protobuf/config schema changes;
- no persistence/configurator path changes;
- no export/push workflows;
- no gameplay semantics;
- no evaluator logic.

## 2. Validation Hardening Summary

What changed:

- Added `ComboExactDuplicateDifferentPriority` validation diagnostic code.
- Hardened combo validation to reject enabled exact duplicate combo masks even when priorities differ.
- Preserved existing same-priority duplicate rejection and subset ambiguity checks.

Already covered before G11o (confirmed by source inspection):

- force-rule equal-priority identical trigger-mask conflict diagnostics;
- digital rule empty condition/empty output/unknown output-bit diagnostics;
- layer role-map empty held condition and no-output diagnostics;
- direction-table general entry presence validation without special-casing direction `5`.

Deferred:

- no runtime wiring was introduced to surface diagnostics through selected mode behavior;
- no game-semantic interpretation (`OutputCompositionNoGameSemantics` remains a documented boundary only).

## 3. Self-Test Expansion Summary

Added deterministic self-test cases:

- `ValidationDuplicateExactComboMaskRejectedOrDiagnosed`
  - local profile copy with duplicate enabled exact combo mask (different priority)
  - expects invalid validation with `ComboExactDuplicateDifferentPriority`.
- `ValidationDirectionFiveEntryAllowed`
  - confirms example profile table has direction-5 entry and overall profile validation remains valid.
- `ValidationDigitalRuleUnknownOutputRejected`
  - local profile copy with enabled digital rule containing unknown output bit
  - expects invalid validation with `DigitalRuleUnknownOutputBit`.
- `ValidationForceRuleMissingDigitalOutputRejected`
  - local profile copy with enabled force rule and `digital_outputs = 0`
  - expects invalid validation with `ForceRuleMissingDigitalOutputs`.
- `ValidationLayerRoleMapEmptyRejected`
  - local profile copy with enabled layer role map and no role/direction outputs
  - expects invalid validation with `LayerRoleMapNoRoleOutputs`.
- `OutputCompositionForceSkipsTableResolver`
  - force-triggered output composition
  - expects `Composed` with `used_table_resolver == false`.

Also updated:

- `kSenscopePrototypeSelfTestMaxCaseResults` from `24` to `32` to keep case storage deterministic.

## 4. Runtime-Readiness Gate

Required before any G11l-impl selected runtime output behavior:

- SenscopePrototype reachability path explicitly approved.
- Default config remains unchanged unless separately approved.
- Constructor self-test remains gated/off by default.
- First output behavior scope is left-stick table only.
- Digital outputs remain neutral unless separately approved.
- Force Up-B remains disabled unless separately approved.
- No right-stick behavior.
- No gameplay semantics.
- Build passes.
- Diff reviewed for mode-selection/default-config changes.
- Hardware safety decision recorded before flashing.

## 5. Runtime Behavior Boundary

No selected runtime behavior changed in G11o.

`SenscopePrototype` remains non-selected by normal mode-selection flow, and prototype output composition remains isolated helper code only.

## 6. Verification

Commands run and results:

- `git status`: passed; expected in-scope edits on `proto/glyph-validation-readiness-g11o` plus new G11o doc file.
- `git diff --stat`: passed; only G11o-scoped prototype/doc files changed.
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)|package.json|pytest|CMakeLists|platformio.ini' || true`: returned expected matches including `platformio.ini` and platform package `package.json` files.
- `test -x ./scripts/pio-local.sh`: passed.
- `test -x ./scripts/build-glyph-mk6-quiet.sh`: passed.
- `./scripts/build-glyph-mk6-quiet.sh`: passed (`glyph_mk6 build passed`).

## 7. Recommended Next Batches

1. G11oR human review of validation diagnostics and self-test expectations.
2. G11l-impl only if explicitly approved: first selected left-stick table behavior only.
3. G11p docs cleanup if needed after review.
