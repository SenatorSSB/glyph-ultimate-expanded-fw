# Friend Profile3 Tilt2 Flipper Fix Handoff

Status: firmware candidate pending hardware retest.

Branch: `glyph/friend-fw-fix-tilt2-flipper`

Base branch: `glyph/friend-fw-modifier-display-convention-fix`

This is friend-specific firmware only. It must not be merged into
`configurator`.

## Source Grounding

Inspected source-owned files:

- `docs/friend-profile3-wip.md`
- `docs/calibration/friend_profile3_modifier_runtime_fix_handoff.md`
- `config/glyph/common/include/glyph_overrides.hpp`
- `src/modes/Ultimate.cpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `tools/check_friend_profile3_modifier_runtime.py`
- `tools/check_friend_profile3_smashbox_wip.py`

Confirmed runtime inputs:

| Physical/logical input | Runtime role |
| --- | --- |
| LT4 | X1 |
| LT3 | Y1 |
| RF4 | Tilt1 |
| RF3 | Tilt2/flipper |
| RF4+RF3 | Tilt3 |

The previous unresolved flipper status was wrong for this friend branch. RF3 is
source-confirmed as Tilt2, and the original Smash Box Profile 3 values include:

- Tilt2 X: `197`
- Tilt2 Y Up: `40`
- Tilt2 Y Down: `40`

Tilt2 X `197` is interpreted as a signed Smash Box-style byte. As signed int8,
`197` is `-59`, so RF3/Tilt2 flips the horizontal sign relative to RF4/Tilt1.

## Implemented Behavior

RF3/Tilt2/flipper uses signed, byte-safe math:

- right axis (`+1`) -> X offset `-59`
- left axis (`-1`) -> X offset `+59`
- neutral X -> X offset `0`
- up axis (`+1`) -> Y offset `+40`
- down axis (`-1`) -> Y offset `-40`
- neutral Y -> Y offset `0`
- raw output is center `128` plus signed offset

The source-owned Tilt2 table now reflects the corrected raw outputs, and the
runtime also applies explicit Tilt2/flipper handling for the single RF3 case.

Expected focused retest values:

| Case | Raw absolute byte output | Miniscreen/origo display output |
| --- | --- | --- |
| RF4/Tilt1 + up/right | raw (187, 167) | 59 39 |
| RF3/Tilt2/flipper + up/right | raw (69, 168) | -59 40 |
| RF3/Tilt2/flipper + left/up | raw (187, 168) | 59 40 |
| X1 + up/right | raw (158, 195) | 30 67 |
| Y1 + up/right | raw (195, 156) | 67 28 |
| X1+Y1 + up/right | raw (158, 156) | 30 28 |

The prior bad field result `left+up with flipper -> -69 40` should not recur.

## Tilt1+Tilt2 / Tilt3 Status

Implemented. Exact source-owned Tilt3 values exist in
`docs/friend-profile3-wip.md` and
`src/modes/UltimateIdentityRuntimeTables.hpp`, so RF4+RF3 selects
`RuntimeTableId::Tilt3` before the generic multi-modifier fallback.

Expected RF4+RF3/Tilt3 up/right:

| Case | Raw absolute byte output | Miniscreen/origo display output |
| --- | --- | --- |
| RF4+RF3/Tilt3 + up/right | raw (164, 172) | 36 44 |

## R Status

Implemented on this branch after inspecting the current confirmed working
runtime role map:

- RF16 is standalone R (`outputs.triggerRDigital`);
- MB7 is Start;
- RF10 remains the explicitly instructed L+R+A composite, including R digital;
- LT1 remains Z on the GameCube/N64 serialized `buttonR` path.

RF14 was inspected but not assigned to R. The friend binding table did not
source-ground RF14 as R, and historical runtime notes record RF14 as
empty/no-output in the native Ultimate role map.

## Hardware Retest Checklist

- Profile 3 still adopts through the one-shot overwrite path.
- A/B remains correct.
- L+R+A remains correct.
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
