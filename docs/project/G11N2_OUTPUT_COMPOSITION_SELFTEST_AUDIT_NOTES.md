# G11n2 Output Composition Self-Test Audit Notes

Status: implemented (isolated prototype self-test expansion + audit cleanup only)  
Date: 2026-05-23  
Branch: `proto/glyph-output-selftest-audit-g11n2`

## 1. Title and status

This batch expands the isolated `SenscopePrototype` self-test helper with deterministic
output-composition vectors and updates audit wording to reflect actual verification outcomes.

## 2. Files changed

- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`
- `docs/project/G11L_N_OUTPUT_COMPOSITION_AND_TEST_STRATEGY_NOTES.md`
- `docs/project/G11N2_OUTPUT_COMPOSITION_SELFTEST_AUDIT_NOTES.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md`

## 3. New self-test cases

Added case IDs and assertions for:

- `OutputCompositionForceWins`
  - force-triggered request with direct digital output
  - expects `Composed`, force override selected, table resolver not used, force coordinate selected, and digital OR includes direct output plus force `B`
- `OutputCompositionTableResolverUsedWhenNoForce`
  - no force trigger, active modifier `0b001`, direction roles left+up
  - expects `Composed`, no force override, table resolver used, left stick resolves to table 1 direction 7 (`44,212`), and digital composition executes
- `OutputCompositionDigitalFailurePropagates`
  - request includes unknown direct digital output bit
  - expects `DigitalFailed` + `DigitalInvalidDirectOutputMask`
- `OutputCompositionDirectionFailurePropagates`
  - request includes unknown direction role bits
  - expects `DirectionFailed` + `DirectionUnknownRoleBitsMasked`
- `OutputCompositionNoLeftStickWhenNoMatchingCombo`
  - no force trigger, exact-required undefined combo
  - expects `NoLeftStickOutput` + `TableResolverNoMatchingComboProfile`, with resolver no-match diagnostic

Also increased case result capacity:

- `kSenscopePrototypeSelfTestMaxCaseResults`: `16 -> 24`

## 4. Runtime behavior boundary

Runtime behavior changes: none.

Explicitly unchanged:

- `src/core/mode_selection.cpp`
- mode selection reachability / activation bindings
- `GameModeId` set
- default config behavior
- `Ultimate` / `CustomControllerMode` behavior
- `InputMode` / `ControllerMode` behavior
- output report runtime paths
- firmware `OutputState` write paths
- protobuf/config schemas
- persistence/configurator paths
- export/push workflows
- gameplay semantics

## 5. Verification commands and actual results

- `git status`: passed; branch is `proto/glyph-output-selftest-audit-g11n2` with expected in-scope edits
- `git diff --stat`: passed; in-scope prototype self-test and docs edits present
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)|package.json|pytest|CMakeLists|platformio.ini' || true`: returned expected inventory matches including `platformio.ini`
- `test -x ./scripts/pio-local.sh`: passed
- `test -x ./scripts/build-glyph-mk6-quiet.sh`: passed
- `./scripts/build-glyph-mk6-quiet.sh`: passed (`glyph_mk6 build passed`)

## 6. Recommended next batches

1. Human inspection of G11n2 self-test expectations and diagnostics.
2. If approved, keep next work isolated to additional helper/audit refinement only.
3. Do not proceed to selected runtime output behavior implementation without explicit approval.
