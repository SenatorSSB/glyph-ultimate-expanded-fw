# Glyph Ultimate Tilt Hardware Smoke-Test Protocol Draft (2026-05-24)

## Scope

This is a human-controlled protocol draft for a later runtime firmware test branch. It does not define automated flashing, push-to-device behavior, or final Tilt/Tilt2 runtime behavior.

## 1. Preconditions

- Worktree is clean except for the intended later runtime branch changes.
- Exact branch name and commit SHA are recorded before any hardware action.
- Build passes with:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

- Hardware owner is present and agrees to run the test.
- Current known-good firmware is available for rollback.
- Current profile/config is backed up before flashing.
- Final Tilt/Tilt2 values and activation conditions are approved before testing.
- Any overflow/clamp/flipper dependency is either source-proven or explicitly avoided.

## 2. Build Artifact Handling

- Build command:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

- Record:
  - branch name
  - commit SHA
  - build command
  - build result
  - artifact path if reported by the build system
  - artifact checksum if the artifact path is discoverable

This draft does not assume a specific artifact path. Use the path produced by the local PlatformIO/Glyph build output.

## 3. Manual Flash Step Placeholder

This document does not define automated flashing.

Manual flashing must be performed only by the hardware owner using their approved known-good workflow. Do not add scripts, background services, or push-to-device automation as part of this protocol.

## 4. Smoke-Test Checklist

After manual flashing:

- Board boots.
- Device enumerates as expected for the selected communication backend.
- Baseline buttons still work.
- Menu/back/start controls are unaffected.
- SOCD directions are unaffected.
- Button remapping behavior is unchanged.
- Unmodified Ultimate actions still behave as before.
- Left stick neutral remains neutral with no direction held.
- Existing Ultimate modifier behavior remains unchanged except for the explicitly implemented later test scope.
- C-stick/right-stick behavior is unaffected unless the later runtime branch explicitly changes it.
- Analog triggers still behave as expected.
- New Tilt/Tilt2 buttons are tested only if and when a later runtime branch implements them.
- New Tilt/Tilt2 outputs match the approved observation values for that later branch.

## 5. Rollback

If any stop condition occurs:

- Stop testing immediately.
- Disconnect or reset the device using the hardware owner's normal safe workflow.
- Restore known-good firmware.
- Restore known-good profile/config if needed.
- Record observed failure, branch, commit SHA, and whether rollback succeeded.

## 6. Stop Conditions

Stop immediately on:

- Boot failure.
- Device fails to enumerate.
- Stuck input.
- Unexpected SOCD behavior.
- Menu/start/back broken.
- Profile/config corruption.
- Unexpected analog extremes or wrap-like output.
- Any uncontrolled repeated input or timing behavior.
- Any behavior that looks like macro, turbo, toggle, one-shot, or automation.
- Any deviation from the approved later runtime test scope.

This protocol is only a draft until reviewed by the hardware owner.
