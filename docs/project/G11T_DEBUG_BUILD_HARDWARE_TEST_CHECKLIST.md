# G11t Debug Build Hardware Test Checklist

Purpose: document a local-only, human-controlled debug-build preparation flow for intentionally enabling `SenscopePrototype` manual selection in a test build for hardware observation. This checklist is source-backed, conservative, and does not change runtime behavior by itself.

## Purpose

- Provide a pre-flash and pre-build review path for a local debug binary where a human intentionally flips `kEnableSenscopePrototypeManualSelection` to `true` in a private test branch or local edit.
- Record the current G11n2 baseline so reviewers can tell what is already present in source and what is not.
- Keep hardware testing explicitly human-controlled.

## Non-goals

- Do not change source code, headers, protobuf, default config, or runtime reachability.
- Do not make `SenscopePrototype` reachable by default.
- Do not add `GameModeId`, `mode_id`, `activation_binding`, or `default_mode_config` entries.
- Do not enable Force Up-B.
- Do not enable digital output behavior beyond neutral.
- Do not enable right-stick/C-stick behavior.
- Do not add export, push, or flashing workflows.
- Do not add gameplay semantic labels, thresholds, or Super Smash Bros. Ultimate behavior claims.

## Current Baseline

This is the current G11n2 baseline as reflected in the inspected repository source:

1. `SenscopePrototype` is compile-visible as a `ControllerMode` subclass.
2. It has a static instance in `src/core/mode_selection.cpp`.
3. It is unreachable by default because `kEnableSenscopePrototypeManualSelection = false`.
4. Constructor self-test is gated off by default because `kRunSenscopePrototypeConstructorSelfTest = false`.
5. No `GameModeId`/protobuf/config/default activation exists for `SenscopePrototype`.
6. Existing/default modes remain unchanged.

## Safety Boundaries

- Do not flash from agent.
- Do not treat a local debug build as a production-safe or default-reachable build.
- Do not expand runtime scope beyond the selected left-stick table path unless a separate source-backed approval exists.
- Do not assume the manual debug chord path is appropriate for unattended use.
- Treat any build with the manual selection flag changed to `true` as experimental-only.
- If a code file changed unexpectedly, stop before building and correct the source state first.

## Local-Only Debug Preparation Checklist

1. Confirm the branch is the intended local test branch.
2. Confirm the working tree is clean except for the deliberate docs change or the deliberate local debug edit.
3. Confirm the manual-selection flag change, if any, is local and intentional.
4. Confirm no default reachability wiring was added.
5. Confirm no config/protobuf/default-mode changes were introduced.
6. Confirm no flashing will be performed by the agent.
7. Confirm a human will review the selected behavior before any hardware use.

## Source Grep Checklist

Run these checks before any hardware review:

```bash
git status
git diff --stat
grep -R "kEnableSenscopePrototypeManualSelection" -n include src
grep -R "kRunSenscopePrototypeConstructorSelfTest" -n include src
grep -R "SenscopePrototype" -n include src docs/project
grep -R "GameModeId" -n include src
grep -R "mode_id" -n include src proto config docs/project
grep -R "activation_binding" -n include src proto config docs/project
grep -R "default_mode_config" -n include src proto config docs/project
```

Expected grep interpretation:

- `kEnableSenscopePrototypeManualSelection` should remain `false` in the checked-in source unless a human is intentionally preparing a private debug binary.
- `kRunSenscopePrototypeConstructorSelfTest` should remain `false` in the checked-in source unless a human is intentionally preparing a private debug binary.
- `SenscopePrototype` should remain compile-visible, but not default-reachable.
- `GameModeId`, `mode_id`, `activation_binding`, and `default_mode_config` searches should not reveal any new `SenscopePrototype` activation path.

## Build Checklist

If the source tree is unchanged except for docs, do not run a firmware build for this docs-only batch.

If a human intentionally flips the manual-selection flag in a private local test build, use the repository wrapper checks before building:

```bash
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
```

Build interpretation:

- Only build after a human has reviewed the source state and confirmed the debug intent.
- If the build is for a hardware test, treat the result as experimental and local-only.

## Pre-Flash Human Review Checklist

Before any hardware flash decision, a human reviewer should confirm:

1. The checked-in baseline still has `kEnableSenscopePrototypeManualSelection = false`.
2. The checked-in baseline still has `kRunSenscopePrototypeConstructorSelfTest = false`.
3. No `GameModeId`/protobuf/config/default activation path was added.
4. The selected-debug behavior is limited to the left-stick table resolver path.
5. Digital outputs remain neutral only.
6. Force Up-B remains disabled.
7. Right-stick/C-stick outputs remain centered.
8. Triggers remain zero.
9. A neutral fallback is preserved for helper/resolver failure.
10. The agent is not flashing hardware.

## Expected Selected-Debug Behavior

If a human intentionally changes `kEnableSenscopePrototypeManualSelection` to `true` in a local test build, the expected selected behavior is:

- left-stick table resolver output only;
- active modifier mask from the current source-backed bindings:
  - bit 0 = `inputs.rf2`
  - bit 1 = `inputs.rf3`
  - bit 2 = `inputs.rf4`
- uses `GetSenscopePrototypeExampleProfile()`;
- digital outputs remain neutral:
  - `outputs.buttons = 0`
- Force Up-B disabled;
- right-stick/C-stick centered;
- triggers zero;
- fallback to neutral on helper/resolver failure.

Source-backed notes:

- The manual debug chord path in `src/core/mode_selection.cpp` is gated behind `kEnableSenscopePrototypeManualSelection`.
- The selected runtime resolver path in `src/modes/SenscopePrototype.cpp` is left-stick-only and returns neutral when direction, modifier, or resolver helpers fail.
- The checked-in constructor self-test gate remains off by default.

## Hardware Test Observations To Record

Record the following after any human-controlled local hardware test:

- branch name and commit SHA;
- whether the local test build intentionally changed `kEnableSenscopePrototypeManualSelection`;
- whether the build used the checked-in default false flag or a private debug edit;
- whether selection behaved only through the intended debug path;
- whether left-stick coordinates matched the expected table output;
- whether digital outputs stayed neutral;
- whether right-stick/C-stick stayed centered;
- whether triggers stayed zero;
- whether any helper/resolver failure fell back to neutral;
- any unexpected input routing, mode-selection, or backend side effects;
- whether the build should be rolled back to the default false-flag state.

## Rollback Checklist

To return to the default checked-in state:

1. Restore `kEnableSenscopePrototypeManualSelection` to `false` in the local test branch or discard the private debug edit.
2. Restore `kRunSenscopePrototypeConstructorSelfTest` to `false` if it was changed locally.
3. Re-run the source grep checklist.
4. Re-run `git status` and `git diff --stat`.
5. Confirm the working tree no longer contains the debug edit before any future build or flash decision.

## Stop Conditions

Stop immediately and do not flash if any of the following is true:

- a code file changed unexpectedly;
- source inspection shows a new `SenscopePrototype` activation/reachability path that was not intentionally approved;
- a source grep reveals a `GameModeId`, `mode_id`, `activation_binding`, or `default_mode_config` change for `SenscopePrototype`;
- the build would rely on undocumented controller behavior;
- the build would require a protobuf/config/default schema decision;
- the build would expand runtime behavior beyond the selected left-stick path;
- the build would enable Force Up-B, digital output behavior, or right-stick/C-stick behavior;
- the user has not explicitly approved hardware flashing;
- the debug build is being treated as a default or production-safe artifact.

## Future Work Deliberately Not Included

- No runtime expansion beyond the current selected left-stick path.
- No default mode-selection wiring.
- No export or push workflow.
- No protobuf/config/default-mode schema work.
- No Force Up-B work.
- No digital output work.
- No right-stick/C-stick work.
- No gameplay semantic labeling or threshold design.
- No flashing instructions or agent-triggered flashing.
