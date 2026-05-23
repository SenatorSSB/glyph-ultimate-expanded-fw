# G11u Selected Runtime Invariant Self-Test Notes

Status: implemented (isolated prototype self-test/doc batch)

## Purpose

Add additive, source-backed invariant self-test coverage for the selected `SenscopePrototype` helper baseline without changing default reachability or selected runtime behavior.

## Self-test coverage added

The following additive self-test coverage was added in `SenscopePrototypeSelfTest`:

1. Full 9-way direction helper resolution coverage (`D1` through `D9`, including neutral `D5`) via explicit direction-role cases.
2. Prototype modifier-bit semantics coverage for current selected-path assumptions:
   - bit 0 <- `rf2`-modeled source mask
   - bit 1 <- `rf3`-modeled source mask
   - bit 2 <- `rf4`-modeled source mask
   - combination checks for `001`, `010`, `100`, `101`, and `111`.
3. Digital helper neutral default coverage:
   - no direct digital outputs + no triggered digital rule composes `0` output mask.
4. Force helper disabled-default coverage:
   - no matching force trigger remains `NoMatchingRule` (disabled path).
5. No-left-stick lookup-path coverage in output composition helper:
   - exact-required unresolved combo reports `NoLeftStickOutput` and keeps neutral packet coordinate (`128,128`).

Existing coverage retained (already present before this batch):

- example profile validation success;
- duplicate exact combo-mask rejection/diagnostic behavior;
- resolver no-match path diagnostics;
- force-rule ambiguity diagnostics;
- digital unknown-output diagnostics.

## Scope boundary confirmation

Code changes for G11u were limited to isolated prototype/self-test files:

- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`

No selected-runtime mode implementation file changes were made.

## Baseline behavior confirmations

- Default reachability did not change.
- Constructor self-test remains gated off by default.
- Force Up-B runtime behavior remains disabled in selected runtime baseline.
- Digital outputs remain neutral in selected runtime baseline.
- Right-stick/C-stick remains centered/neutral in selected runtime baseline.
- Triggers remain zero in selected runtime baseline.
- `rf2`/`rf3`/`rf4` modifier-bit assumptions remain source-backed prototype/debug runtime assumptions, not a product UX/config contract.

## Gaps / non-invasive limits

1. Selected runtime fallback-to-neutral behavior in `src/modes/SenscopePrototype.cpp` is not directly unit-tested in this helper-only batch because mode runtime wiring was intentionally not modified.
2. Constructor self-test execution path remains disabled by default and was not enabled for this batch.
3. No reachability/config/protobuf/default activation path was added or tested because those boundaries are intentionally unchanged.
