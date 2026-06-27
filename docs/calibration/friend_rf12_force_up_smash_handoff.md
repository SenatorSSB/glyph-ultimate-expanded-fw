# Friend RF12 Force Up Smash Handoff

Status: firmware candidate pending hardware retest.

Superseded for the final Faifra layout by
`docs/calibration/friend_profile3_final_faifra_layout_handoff.md`. This packet
records the previous `glyph/friend-fw-rf12-force-up-smash` branch where RF12
was Up+A. The current final friend branch intentionally swaps that behavior:
LT2 is Up+A and RF12 is AB.

Branch: `glyph/friend-fw-rf12-force-up-smash`

Base branch: `glyph/friend-fw-swap-lt5-lf5-up-semantics`

This is friend-specific firmware only. It must not be merged into
`configurator`.

## User Request

Faifra wants `RF12` to be forced Up Smash:

- RF12 should force Up plus A.
- Any other RF12 function should be removed or overridden.
- This is friend-specific only.

Static profile JSON fixtures were intentionally left unchanged.

## Old RF12 Role

Source inspection found the current friend Ultimate runtime used RF12 as part
of X2 modifier selection:

- `src/modes/Ultimate.cpp`: `state.x2_active = inputs.rf15 || inputs.rf12;`

The friend WIP document also listed:

- `docs/friend-profile3-wip.md`: `rf12 | y2`

No source-backed current RF12 digital button output was found in
`ApplyDigitalButtonOutputs(...)` before this change. The active conflicting
runtime function was therefore RF12 participating in X2-style modifier
selection through `x2_active`, while documentation called it Y2.

## New RF12 Behavior

RF12 is now an explicit forced Up Smash role in the friend Ultimate runtime:

- `state.rf12_force_up_smash_active = inputs.rf12;`
- `state.direction_plus_a_active = state.rf12_force_up_smash_active;`
- `state.direction_plus_a_force_up = state.rf12_force_up_smash_active;`
- A output includes RF12 through
  `roles.rf12_force_up_smash_active`.
- Digital left-stick direction output is forced to Up only while RF12 is active.
- Analog left-stick output is forced to the Default-table Up point for the
  action through `ApplyDirectionPlusAOverride(...)`.

This is simultaneous Up+A output only. No macro, turbo, or timing automation was
added.

## Functions Removed From RF12

RF12 was removed from X2:

- old: `state.x2_active = inputs.rf15 || inputs.rf12;`
- new: `state.x2_active = inputs.rf15;`

RF15 remains X2. RF12 no longer participates in X2/Y2 modifier selection.

## Source-Confirmed Implementation

Implementation files:

- `src/modes/Ultimate.cpp`
- `docs/friend-profile3-wip.md`
- `tools/check_friend_profile3_smashbox_wip.py`
- `tools/check_friend_rf12_force_up_smash.py`

The runtime change is friend-specific source behavior:

- RF12 has the explicit role `rf12_force_up_smash_active`.
- RF12 contributes to `outputs.a`.
- RF12 forces digital left-stick Up and clears left/right/down digital direction
  flags for the forced action.
- RF12 routes through the existing direction-plus-A analog override and selects
  the Default-table Up point, not LF5-style auxiliary Up and not ModeDefault.
- LT5/LF5 Up semantics remain source-confirmed:
  - `proper_up_active = inputs.lt5`
  - `auxiliary_up_active = inputs.lf5 || inputs.rf6`
  - `state.up = proper_up_active || (auxiliary_up_active && !inputs.lf2)`
  - `state.down = inputs.lf2`
- One-shot Profile 3 default adoption remains unchanged.
- X1/Y1, Tilt1/Tilt2/flipper/Tilt3, RF16 standalone R, and MB7 Start paths are
  preserved by source inspection.

## Hardware Retest Checklist

Hardware retest is required before claiming acceptance.

- Profile 3 still adopts through the one-shot overwrite path.
- A/B remains correct.
- L+R+A remains correct.
- RF12 alone produces A plus forced left-stick Up.
- RF12 + Down still produces forced Up plus A for the action.
- RF12 + left/right does not select left/right for the forced Up Smash action.
- RF12 no longer behaves as X2/Y2.
- RF15 still behaves as X2.
- X1 + up/right displays `30 67`.
- Y1 + up/right displays `67 28`.
- X1+Y1 + up/right displays `30 28`.
- RF4/Tilt1 + up/right displays `59 39`.
- RF3/Tilt2/flipper + up/right displays `-59 40`.
- RF3/Tilt2/flipper + left/up displays `59 40`.
- RF4+RF3/Tilt3 + up/right displays `36 44`.
- LT5 alone produces Up.
- LT5 + Down/LF2 follows source-owned `SOCD_2IP` behavior.
- LF5 alone produces an Up-like left-stick direction.
- LF5 + Down/LF2 no longer forces Up over Down.
- RF16 produces standalone R.
- MB7 produces Start.
- RF16 should not also produce Start.

## Branch Boundary

This branch is friend-specific firmware. It must not be merged into
`configurator`, and it must not be used as a configurator/profile/schema/export
source.
