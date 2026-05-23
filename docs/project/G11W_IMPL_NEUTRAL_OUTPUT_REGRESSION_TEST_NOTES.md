# G11w Impl Neutral Output Regression Test Notes

Status: implemented helper-level self-test hardening only.

## Scope statement

This batch is isolated helper-level `SenscopePrototypeSelfTest` hardening for neutral-output regression invariants. It does not change selected runtime behavior, mode selection behavior, or default reachability.

## Self-test cases added

Added additive helper-level cases in `SenscopePrototypeSelfTest`:

1. `OutputCompositionNeutralNoInputBaseline`
2. `OutputCompositionDigitalInvalidBitFailClosedNoPassthrough`
3. `OutputCompositionNoForceTriggerKeepsForceDisabled`

Also strengthened existing helper-level case:

4. `OutputCompositionNoLeftStickKeepsNeutralPacketCoordinate` (adds explicit fail-closed packet assertions while preserving behavior expectations)

## Exact files changed

Source files changed:

- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`

Docs files changed:

- `docs/project/G11W_IMPL_NEUTRAL_OUTPUT_REGRESSION_TEST_NOTES.md`

## Boundary confirmations

- No selected runtime file changed (`src/modes/SenscopePrototype.cpp` unchanged).
- No mode-selection file changed (`src/core/mode_selection.cpp` unchanged).
- Default reachability did not change.
- `kEnableSenscopePrototypeManualSelection` did not change.
- `kRunSenscopePrototypeConstructorSelfTest` did not change.
- Force Up-B runtime behavior remains disabled.
- Selected-runtime digital outputs remain neutral.
- Right-stick/C-stick/triggers behavior remains unchanged.
- No config/protobuf/default activation wiring changed.
- No export/push workflow was added.
- No hardware flashing workflow was added.

## Gaps not testable without selected-runtime edits

1. Helper output composition APIs do not model right-stick/C-stick/trigger fields directly, so those runtime fields are verified by unchanged selected-runtime source boundaries rather than helper-level output-packet assertions.
2. Constructor self-test execution remains default-off and was not enabled in this batch by design.
