# G11i-j Self-Test and Wiring Design Notes

Status: implemented (isolated helper + docs-only wiring design)  
Date: 2026-05-23  
Branch: `proto/glyph-prototype-selftest-and-wiring-design-g11i-j`

## 1. Title and status

This document records the G11i-j batch:
- G11i: isolated prototype self-test/vector helper.
- G11j: mode-selection wiring design doc only.

## 2. Files added/changed

Added:
- `include/prototypes/senscope/SenscopePrototypeSelfTest.hpp`
- `src/prototypes/senscope/SenscopePrototypeSelfTest.cpp`
- `docs/project/G11J_MODE_SELECTION_WIRING_DESIGN.md`
- `docs/project/G11I_J_SELFTEST_AND_WIRING_DESIGN_NOTES.md`

Changed:
- `include/modes/SenscopePrototype.hpp`
- `src/modes/SenscopePrototype.cpp`
- `docs/project/ACTIVE_AGENT_QUEUE.md` (minimal queue status update)

## 3. Self-test helper summary

Added a prototype-scoped self-test helper API:
- `RunSenscopePrototypeSelfTest()`
- `SenscopePrototypeSelfTestStatus`
- `SenscopePrototypeSelfTestCaseId`
- `SenscopePrototypeSelfTestResult`

Deterministic vectors cover:
- validation helper success on example profile;
- direction helper cases (`D5`, `D7`, opposite-policy resolution, left-priority, up-priority);
- left-stick resolver exact + exact-required no-match + subset fallback;
- digital OR composition (`A` + triggered `B+Y`) and unknown direct-output diagnostic;
- force helper fixed-rule coordinate + `B`, upward-Y/post-SOCD-horizontal behavior, and local equal-priority ambiguity.

No external test framework was added.

## 4. Shell integration summary

`SenscopePrototype` constructor smoke path now calls the unified self-test helper through:
- `RunPrototypeStaticSmokeCheck()` -> `RunSenscopePrototypeSelfTest()`

The shell remains inactive and unregistered in mode selection.

## 5. Runtime behavior boundary

Runtime behavior changes: none.

Explicitly unchanged:
- mode selection and activation paths;
- existing `GameModeId` set;
- default config behavior;
- `Ultimate`/`CustomControllerMode` behavior;
- `InputMode`/`ControllerMode` behavior;
- output report behavior;
- config/protobuf schemas;
- persistence/configurator paths;
- evaluator/export/push workflows;
- gameplay semantics.

## 6. Wiring design summary

`docs/project/G11J_MODE_SELECTION_WIRING_DESIGN.md` documents:
- current mode-selection source inventory;
- future wiring options;
- recommended staged safe path;
- constructor smoke-test caveat before any runtime wiring;
- stop conditions and approval gates for any future implementation batch.

No wiring was implemented in G11j.

## 7. Verification

Commands run:
- `git status`
- `git diff --stat`
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)|package.json|pytest|CMakeLists|platformio.ini' || true`
- `test -x ./scripts/pio-local.sh`
- `test -x ./scripts/build-glyph-mk6-quiet.sh`
- `./scripts/build-glyph-mk6-quiet.sh`

## 8. Recommended next batches

1. G11i-jR human review.
2. G11k mode-selection wiring implementation only after explicit approval.
3. G11l first output behavior only after explicit approval.
4. G11m prototype helper test expansion if a test convention is selected.
