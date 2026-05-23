# G11r Selected-Path Readiness Checks

Status: checklist-only  
Branch: `proto/glyph-runtime-audit-modifier-design-g11m2-n-r`  
Purpose: define required checks before any future selected runtime expansion beyond current G11l scope.

## 1. Readiness checklist

1. `kEnableSenscopePrototypeManualSelection` remains `false` unless intentionally building an explicit hardware debug binary.
2. No `GameModeId` / protobuf / default-config activation path is introduced.
3. Constructor self-test remains off by default (`kRunSenscopePrototypeConstructorSelfTest = false`).
4. Current selected output scope is documented as left-stick table path only.
5. Neutral fallback behavior is preserved for unresolved direction/resolver states.
6. No digital outputs, Force Up-B, or right-stick/C-stick behavior is enabled unless explicitly approved.
7. Build passes on current branch.
8. Source diffs are manually reviewed for mode-selection/config/default behavior changes.
9. Hardware flashing remains explicit user-controlled action (not automated by agent runs).

## 2. Review gate expectation

Before moving to any runtime expansion batch, confirm this checklist in-review and record explicit user approval for scope changes.
