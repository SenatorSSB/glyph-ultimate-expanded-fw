# Friend Profile3 Modifier Runtime Fix Handoff

Status: firmware candidate pending hardware retest.

Superseded for the final Faifra layout by
`docs/calibration/friend_profile3_final_faifra_layout_handoff.md`. This packet
records an earlier branch where standalone R was RF16. The current final friend
branch intentionally moves standalone R to LF8; RF16 no longer produces R or
Start.

Runtime fix branch: `glyph/friend-fw-fix-profile3-modifiers`

Display convention clarification branch:
`glyph/friend-fw-modifier-display-convention-fix`

Tilt2/flipper correction branch:
`glyph/friend-fw-fix-tilt2-flipper`

Base branch: `glyph/friend-fw-force-default-profile-once`

This is friend-specific firmware work only. It must not be merged into
`configurator`.

This must not be merged into configurator.

## Field Report

Hardware report before this fix:

- no modifier: 67 67
- Y1: 30 28
- X1: 30 28
- flipper: 67 67
- Tilt: 59 39

| Case | Miniscreen / calibration value with up+right |
| --- | --- |
| no modifier | 67 67 |
| Y1 | 30 28 |
| X1 | 30 28 |
| flipper | 67 67 |
| Tilt | 59 39 |

The same report confirmed:

- buttons/functions are correct;
- A/B works;
- L+R+A works;
- Tilt works perfectly;
- X1 and Y1 should not collapse to the same two-axis output;
- Flipper did nothing on the tested artifact.

## Source-Confirmed Runtime Inputs

Inspected sources:

- `config/glyph/common/include/glyph_overrides.hpp`
- `src/modes/Ultimate.cpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `docs/friend-profile3-wip.md`

Confirmed friend runtime inputs:

| Physical/logical input | Runtime role |
| --- | --- |
| LT4 -> X1 | `state.x1_active = inputs.lt4;` |
| LT3 -> Y1 | `state.y1_active = inputs.lt3;` |
| RF4 -> Tilt1 | `state.tilt1_effective = inputs.rf4;` |
| RF3 -> Tilt2/flipper | `state.tilt2_effective = inputs.rf3;` |
| RF4+RF3 -> Tilt3 | `state.tilt3_effective = inputs.rf4 && inputs.rf3;` |

The baked Ultimate profile in `glyph_overrides.hpp` preserves identity
physical-to-logical remaps for these buttons. The friend-specific behavior is
therefore owned by the Ultimate runtime path rather than by a non-identity
profile remap.

## Coordinate Conventions

The firmware/source tables below use raw absolute byte output coordinates with
center `(128, 128)`.

Faifra's observed miniscreen/calibration values are center-relative/origo
offsets, not raw absolute bytes:

- `miniscreen/display_x = raw_x - 128`
- `miniscreen/display_y = raw_y - 128`

Examples:

| Raw absolute byte output | Miniscreen/origo display output |
| --- | --- |
| raw (187, 167) | 59 39 |
| raw (158, 195) | 30 67 |
| raw (195, 156) | 67 28 |
| raw (158, 156) | 30 28 |

## Implemented X1/Y1 Behavior

The source-owned X1 and Y1 tables were split so a single modifier changes only
its intended axis while the other axis remains on the Profile 3 default table.

Expected up+right raw outputs after this fix:

| Case | Raw absolute byte output | Miniscreen/origo display output |
| --- | --- | --- |
| no modifier + up/right | raw (195, 195) | 67 67 |
| X1 + up/right | raw (158, 195) | 30 67 |
| Y1 + up/right | raw (195, 156) | 67 28 |
| X1+Y1 + up/right | raw (158, 156) | 30 28 |
| RF4/Tilt1 + up/right | raw (187, 167) | 59 39 |
| RF3/Tilt2/flipper + up/right | raw (69, 168) | -59 40 |
| RF3/Tilt2/flipper + left/up | raw (187, 168) | 59 40 |
| RF4+RF3/Tilt3 + up/right | raw (164, 172) | 36 44 |

The raw values are the firmware output expectations. The miniscreen/origo
values are the hardware retest expectations as displayed by the controller.

The combined X1+Y1 path is handled by
`ApplyFriendProfile3XYModifierOverrides(...)` using signed `int` math before
narrowing back to `uint8_t`. This avoids unsigned overflow or wraparound tricks.

Tilt1 constants were intentionally preserved:

- Tilt remains `{69/128/187, 87/128/167}`.

## Tilt2 / Flipper Correction

The previous unresolved status was wrong for this friend branch. The current
friend WIP source confirms RF3 as Tilt2, and the original Smash Box Profile 3
modifier values include source-grounded Tilt2 fields:

- Tilt2 X: `197`
- Tilt2 Y Up: `40`
- Tilt2 Y Down: `40`

For this source format, Tilt2 X `197` is interpreted as a signed byte value,
which is signed offset `-59`. RF3/Tilt2 therefore flips the horizontal sign
relative to RF4/Tilt1:

| Case | Raw absolute byte output | Miniscreen/origo display output |
| --- | --- | --- |
| RF4/Tilt1 + up/right | raw (187, 167) | 59 39 |
| RF3/Tilt2/flipper + up/right | raw (69, 168) | -59 40 |
| RF3/Tilt2/flipper + left/up | raw (187, 168) | 59 40 |

The prior bad hardware result `left+up with flipper -> -69 40` came from the
wrong absolute raw `59/197` X interpretation. The corrected implementation uses
signed, byte-safe runtime math and the source-owned Tilt2 table now reflects
the corrected raw outputs. The `-69 40` result should not recur.

## Tilt1+Tilt2 / Tilt3 Status

Implemented on this branch because exact source-owned Tilt3 values already
exist in `docs/friend-profile3-wip.md` and
`src/modes/UltimateIdentityRuntimeTables.hpp`. RF4+RF3 selects
`RuntimeTableId::Tilt3` before the generic multi-modifier fallback.

Expected Tilt3 up/right output:

| Case | Raw absolute byte output | Miniscreen/origo display output |
| --- | --- | --- |
| RF4+RF3/Tilt3 + up/right | raw (164, 172) | 36 44 |

## R Status

Implemented on this branch. The current source-grounded standalone R binding is:

- `inputs.lt1` -> GameCube/N64 serialized Z path (`outputs.buttonR`);
- `inputs.rf16` -> standalone R digital path (`outputs.triggerRDigital`);
- `inputs.mb7` -> Start;
- `inputs.rf10` -> explicit `L+R+A` composite, including
  `outputs.triggerRDigital`.

This follows the current confirmed working runtime role map, where RF16 is R
and MB7 is Start. RF14 was inspected but was not assigned to R: the friend
binding table did not source-ground RF14 as R, and historical runtime notes
record RF14 as empty/no-output in the native Ultimate role map.

## Verification Commands

Run from the repository root:

```bash
.venv/bin/python tools/check_friend_ultimate_default_profile_matches_fixture.py
.venv/bin/python tools/check_friend_default_profile_force_once.py
.venv/bin/python tools/check_friend_profile3_smashbox_wip.py
.venv/bin/python tools/check_friend_profile3_modifier_runtime.py
.venv/bin/python -m platformio run -e glyph_mk6
.venv/bin/python tools/uf2/inspect_uf2.py .pio/build/glyph_mk6/firmware.uf2
```

Then record:

```bash
git status --short
git diff --stat
```

## Hardware Retest

A hardware retest is required. Suggested focused retest:

- Profile 3 boots/adopts as before.
- Buttons/functions remain correct.
- A/B remains correct.
- L+R+A remains correct.
- no modifier + up/right displays `67 67`.
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
