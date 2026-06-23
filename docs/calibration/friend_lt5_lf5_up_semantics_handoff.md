# Friend LT5/LF5 Up Semantics Handoff

Status: firmware candidate pending hardware retest.

Branch: `glyph/friend-fw-swap-lt5-lf5-up-semantics`

Base branch: `glyph/friend-fw-fix-tilt2-flipper`

This is friend-specific firmware only. It must not be merged into
`configurator`.

## User Request

Faifra's working friend firmware still had an Up/Down issue. The requested
change was to swap the meaningful Up roles so LT5 becomes the proper
left-stick Up input, while LF5 remains usable with modifiers but no longer acts
as a force-up override over Down or other direction inputs.

Static profile JSON fixtures were intentionally left unchanged.

## Old Issue

Source-confirmed old runtime behavior in `src/modes/Ultimate.cpp` collapsed the
friend Up-like inputs into one force-up condition:

- `state.force_up_active = inputs.lf5 || inputs.lt5 || inputs.rf6;`
- `state.up = state.force_up_active;`
- `state.down = inputs.lf2 && !state.force_up_active;`

That meant LF5, LT5, and RF6 forced Up and explicitly suppressed LF2/Down in
the friend Ultimate runtime, regardless of the normal source-owned SOCD path.

The baked Ultimate default profile in
`config/glyph/common/include/glyph_overrides.hpp` remains fixture-matched. It
contains `SOCD_2IP` for `BTN_LF5`/`BTN_LF2`, so LT5 was not distinct as the
proper SOCD-governed Up source through the static profile data alone.

## New Intended Behavior

- LT5 is the proper left-stick Up source.
- LT5 and LF2/Down use the existing source-owned `SOCD_2IP` helper/state.
- LF5 remains an auxiliary Up-like direction for modifier coordinate selection
  when Down is not active.
- LF5 no longer force-suppresses Down.
- RF6 follows the same auxiliary Up-like runtime path as LF5 on this friend
  branch.

## Source-Confirmed Implementation

The implementation is runtime-only:

- `include/modes/Ultimate.hpp` adds a friend Ultimate SOCD state array and
  overrides `HandleSocd(...)`.
- `src/modes/Ultimate.cpp::Ultimate::HandleSocd(...)` walks the active
  configured SOCD pairs, but when it sees the baked friend Ultimate
  `BTN_LF5`/`BTN_LF2` `SOCD_2IP` pair it substitutes `BTN_LT5` for
  `BTN_LF5` before calling `socd::second_input_priority(...)`.
- Other configured SOCD pair handling remains the same dispatch shape as
  `InputMode::HandleSocd(...)`.
- `ResolveEffectiveDirections(...)` now uses:
  - `proper_up_active = inputs.lt5`
  - `auxiliary_up_active = inputs.lf5 || inputs.rf6`
  - `state.up = proper_up_active || (auxiliary_up_active && !inputs.lf2)`
  - `state.down = inputs.lf2`
  - `state.force_up_active = false`

The X1/Y1 modifier override path still receives the resolved `directions.x` and
`directions.y`, so LF5 can still select Up-direction modifier coordinates when
Down is not active.

## SOCD_2IP Status

Exact `SOCD_2IP` for LT5/LF2 was implemented using the existing source-owned
stateful helper:

- `src/core/socd.cpp::socd::second_input_priority(...)`
- `socd::SocdState`

This was not reimplemented with new timing or invented state semantics.

Exact `SOCD_2IP` was not assigned to LF5. LF5 is now an auxiliary Up-like input
that yields to active Down in `ResolveEffectiveDirections(...)`.

## Hardware Retest Checklist

- Profile 3 still adopts through the one-shot overwrite path.
- A/B remains correct.
- L+R+A remains correct.
- LT5 alone produces Up.
- LT5 + Down/LF2 follows source-owned `SOCD_2IP` behavior.
- LF5 alone produces an Up-like left-stick direction.
- LF5 + Down/LF2 no longer forces Up over Down.
- LF5 + X1 produces an Up-direction X1-modified output.
- LF5 + Y1 produces an Up-direction Y1-modified output.
- LT5 + X1 produces the normal Up-direction X1-modified output.
- LT5 + Y1 produces the normal Up-direction Y1-modified output.
- X1 + up/right displays `30 67`.
- Y1 + up/right displays `67 28`.
- X1+Y1 + up/right displays `30 28`.
- RF4/Tilt1 + up/right displays `59 39`.
- RF3/Tilt2/flipper + up/right displays `-59 40`.
- RF3/Tilt2/flipper + left/up displays `59 40`.
- RF4+RF3/Tilt3 + up/right displays `36 44`.
- RF16 produces standalone R.
- MB7 produces Start.
- RF16 should not also produce Start.

Hardware retest is required before claiming acceptance.

## Branch Boundary

This branch is friend-specific firmware. Do not merge it into `configurator`,
and do not use it as a configurator/profile/schema/export source.
