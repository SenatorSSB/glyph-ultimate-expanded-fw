# G11l-n Output Composition and Test Strategy Notes

Status: implemented (docs + isolated prototype scaffold only)

## 1. Files added/changed

Added:

- `docs/project/G11L_FIRST_OUTPUT_BEHAVIOR_DESIGN.md`
- `docs/project/G11M_PROTOTYPE_TEST_STRATEGY.md`
- `include/prototypes/senscope/SenscopePrototypeOutput.hpp`
- `src/prototypes/senscope/SenscopePrototypeOutput.cpp`
- `docs/project/G11L_N_OUTPUT_COMPOSITION_AND_TEST_STRATEGY_NOTES.md`

Changed:

- `docs/project/ACTIVE_AGENT_QUEUE.md` (minimal queue status update)

## 2. G11l design summary

- Documents the first selected runtime behavior as left-stick table resolver only.
- Defers right-stick, Force Up-B, and digital output behavior for later approval-gated stages.
- Separates runtime reachability decisions from output behavior decisions.

## 3. G11m test strategy summary

- Documents current test reality as build-based verification plus compile-visible deterministic self-test vectors.
- Recommends no new dependency or framework in this batch.
- Defers framework choice until around first selected runtime behavior work.

## 4. G11n output composition helper summary

Added `SenscopePrototypeOutput` scaffold that composes helper results in this order:

1. direction helper;
2. force override helper;
3. digital OR helper;
4. left-stick table resolver only when force override is not selected.

Behavior:

- if force override resolves, left stick uses force coordinate and force digital contribution is OR-composed;
- if force does not match, resolver output is used for left stick;
- helper returns explicit composition status and diagnostic metadata.

Boundary:

- prototype-only packet/result API;
- no `OutputState` writes;
- no gameplay semantics.

## 5. Runtime behavior boundary

- Runtime behavior changes: none.
- New helper is not called from `SenscopePrototype` shell.
- `SenscopePrototype` remains unselected by normal mode selection.
- No prototype output is written into selected firmware runtime `OutputState` paths.

## 6. Verification

Planned/required commands for this batch:

- `git status`
- `git diff --stat`
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)|package.json|pytest|CMakeLists|platformio.ini' || true`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

## 7. Recommended next batches

1. Human review of G11l/G11m/G11n boundaries and API shape.
2. Optional G11n self-test vector expansion for output composition helper.
3. G11l-impl only after explicit approval, with runtime reachability and safety gates re-confirmed.
