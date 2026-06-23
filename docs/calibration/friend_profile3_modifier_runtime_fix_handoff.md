# Friend Profile3 Modifier Runtime Fix Handoff

Status: firmware candidate pending hardware retest.

Branch: `glyph/friend-fw-fix-profile3-modifiers`

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
| RF4 -> Tilt | `state.tilt1_effective = inputs.rf4;` |
| RF3 -> Tilt2 | `state.tilt2_effective = inputs.rf3;` |

The baked Ultimate profile in `glyph_overrides.hpp` preserves identity
physical-to-logical remaps for these buttons. The friend-specific behavior is
therefore owned by the Ultimate runtime path rather than by a non-identity
profile remap.

## Implemented X1/Y1 Behavior

The source-owned X1 and Y1 tables were split so a single modifier changes only
its intended axis while the other axis remains on the Profile 3 default table.

Expected up+right raw outputs after this fix:

| Case | Raw output |
| --- | --- |
| no modifier + up/right | raw (195, 195) |
| X1 + up/right: raw (158, 195) | horizontal magnitude 30, vertical default magnitude 67 |
| Y1 + up/right: raw (195, 156) | horizontal default magnitude 67, vertical magnitude 28 |
| X1+Y1 + up/right: raw (158, 156) | horizontal magnitude 30, vertical magnitude 28 |
| Tilt + up/right | raw (187, 167), preserving the hardware-visible 59 39 display convention |

The combined X1+Y1 path is handled by
`ApplyFriendProfile3XYModifierOverrides(...)` using signed `int` math before
narrowing back to `uint8_t`. This avoids unsigned overflow or wraparound tricks.

Tilt and Tilt2 constants were intentionally preserved:

- Tilt remains `{69/128/187, 87/128/167}`.
- Tilt2 remains `{59/128/197, 88/128/168}`.

## Flipper Status

Flipper remains unresolved. The current friend WIP source confirms RF4 as Tilt,
RF3 as Tilt2, LT4 as X1, and LT3 as Y1. The only flipper-named runtime field is
`rf4_layer_flipper_active`, but it is initialized false in this friend branch
and no source-grounded friend binding or intended flipper table was found.

No flipper behavior was invented in this fix.

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
- no modifier + up/right remains the existing base output.
- X1 + up/right is distinct from Y1 + up/right.
- X1 + up/right preserves the normal vertical component.
- Y1 + up/right preserves the normal horizontal component.
- X1+Y1 + up/right produces the combined low X/Y magnitudes.
- Tilt + up/right remains the currently passing 59 39 display convention.
- Flipper remains documented unresolved unless a source-grounded intended
  behavior is supplied.
