# G11n-impl1 Modifier-Mask Helper Notes

Status: implemented (isolated helper only, no runtime wiring)  
Branch: `proto/glyph-modifier-mask-helper-g11n1`

## 1. Scope and files changed

This batch adds an isolated SenscopePrototype helper for deriving an active modifier mask from
physical button holds plus an explicit prototype binding table.

Files:
- `include/prototypes/senscope/SenscopePrototypeModifier.hpp`
- `src/prototypes/senscope/SenscopePrototypeModifier.cpp`
- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`
- `docs/project/G11N1_MODIFIER_MASK_HELPER_NOTES.md`

## 2. Helper behavior

`BuildSenscopePrototypeActiveModifierMask(...)` evaluates enabled bindings only.

Behavior:
- each binding declares `physical_button_mask` and `modifier_bit_index` (0..2);
- a binding triggers when all bits in `physical_button_mask` are held;
- triggered bindings OR their modifier bit into `active_modifier_mask`;
- duplicate bindings for the same modifier bit are allowed and compose by OR.

Validation/diagnostics:
- binding with `modifier_bit_index >= kSenscopePrototypeModifierRoleCount` returns invalid binding;
- binding with `physical_button_mask == 0` returns invalid binding;
- diagnostics include binding index and code/detail.

## 3. Why no real bindings were chosen

Real/domain binding assignment is intentionally deferred. This helper only supports explicit
prototype bindings supplied by the caller. No firmware/runtime physical-role claim is introduced in
this batch.

## 4. Self-test cases

Added isolated self-test coverage:
- `ModifierNoBindingsReturnsZeroMask`
- `ModifierSingleBindingSetsBit0`
- `ModifierMultipleBindingsSetBits`
- `ModifierDuplicateSourcesOrComposeSameBit`
- `ModifierInvalidBitIndexRejected`
- `ModifierEmptyBindingRejected`

## 5. Runtime behavior boundary

- this helper is not used by selected `SenscopePrototype` runtime behavior yet;
- selected runtime path remains unchanged;
- `active_modifier_mask` in selected runtime behavior remains fixed at `0`.

## 6. Verification

Verification for this batch is run with repo policy commands, including:
- status/diff checks
- boundary grep checks
- wrapper executable checks
- `./scripts/build-glyph-mk6-quiet.sh`

## 7. Recommended next batches

1. `G11n1R` human review/inspection of helper behavior and diagnostics.
2. `G11n-impl2` runtime wiring only after explicit approval and real binding decision.
3. `G11p` Force Up-B remains separate.
4. `G11q` digital outputs remain separate.
