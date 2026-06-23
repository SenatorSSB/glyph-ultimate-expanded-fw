# Friend Profile3 Smash Box WIP

Branch: `friend-profile3-smashbox-import-wip`

Purpose: temporary friend-specific Glyph firmware/profile fork for hardware
validation. This is a throwaway hardware-test branch and is not intended to
merge back into `configurator` or mainline.

Source values were copied from Smash Box Designer. Modifier values below are
already converted to absolute raw coordinates with center `(128, 128)`. Do not
reconvert them. The active source-of-truth for this branch is the source-owned
Ultimate firmware path in `src/modes/Ultimate.cpp` and
`src/modes/UltimateIdentityRuntimeTables.hpp`.

This branch replaces the active Ultimate WIP behavior because this repo path is
hardcoded firmware source, not a runtime profile loader. It preserves the
existing repo build workflow.

## Button Bindings

| Physical | Binding |
| --- | --- |
| lf4 | L |
| lf3 | left |
| lf2 | down |
| lf1 | right |
| lf5 | up |
| lt5 | up |
| lt1 | z |
| lt4 | x1 |
| lt3 | y1 |
| lt2 | a+b |
| rt1 | a |
| rt5 | c right |
| rt4 | c up |
| rt3 | c left |
| rt2 | c down |
| rf1 | b |
| rf2 | y |
| rf3 | tilt 2 |
| rf4 | tilt |
| rf5 | mode |
| rf6 | up |
| rf7 | x |
| rf8 | left |
| rf9 | mode |
| rf12 | y2 |
| rf15 | x2 |
| rf10 | l+r+a |
| rf16 | start |
| rf13 | dpad up |
| rf11 | dpad down |
| lf7 | dpad left |
| lf6 | dpad right |

Duplicate bindings are intentional: `lf5`, `lt5`, and `rf6` all provide Up;
`lf3` and `rf8` both provide Left; `rf5` and `rf9` both provide Mode.
Composite bindings are intentional: `lt2` is A+B and `rf10` is L+R+A.

## Raw Coordinate Tables

FGC/numpad direction keys are used throughout:

`1=down-left`, `2=down`, `3=down-right`, `4=left`, `5=neutral`,
`6=right`, `7=up-left`, `8=up`, `9=up-right`.

Profile 3 default:

| Dir | Raw |
| --- | --- |
| 1 | (61, 51) |
| 2 | (128, 51) |
| 3 | (195, 51) |
| 4 | (61, 128) |
| 5 | (128, 128) |
| 6 | (195, 128) |
| 7 | (61, 195) |
| 8 | (128, 195) |
| 9 | (195, 195) |

Profile 3 mode center panel:

| Dir | Raw |
| --- | --- |
| 1 | (128, 128) |
| 2 | (128, 128) |
| 3 | (128, 128) |
| 4 | (128, 128) |
| 5 | (128, 128) |
| 6 | (128, 128) |
| 7 | (128, 128) |
| 8 | (128, 128) |
| 9 | (128, 128) |

Normal X1:

| Dir | Raw |
| --- | --- |
| 1 | (98, 51) |
| 2 | (128, 51) |
| 3 | (158, 51) |
| 4 | (98, 128) |
| 5 | (128, 128) |
| 6 | (158, 128) |
| 7 | (98, 195) |
| 8 | (128, 195) |
| 9 | (158, 195) |

Normal Y1:

| Dir | Raw |
| --- | --- |
| 1 | (61, 100) |
| 2 | (128, 100) |
| 3 | (195, 100) |
| 4 | (61, 128) |
| 5 | (128, 128) |
| 6 | (195, 128) |
| 7 | (61, 156) |
| 8 | (128, 156) |
| 9 | (195, 156) |

X1+Y1 together is handled by a friend-specific runtime overlay using the same
signed magnitudes, so direction 9 resolves to `(158, 156)`. X1 and Y1 alone do
not collapse to the same two-axis output.

Normal X2/Y2:

| Dir | Raw |
| --- | --- |
| 1 | (81, 81) |
| 2 | (128, 81) |
| 3 | (175, 81) |
| 4 | (81, 128) |
| 5 | (128, 128) |
| 6 | (175, 128) |
| 7 | (81, 175) |
| 8 | (128, 175) |
| 9 | (175, 175) |

Normal X3/Y3:

| Dir | Raw |
| --- | --- |
| 1 | (69, 69) |
| 2 | (128, 69) |
| 3 | (187, 69) |
| 4 | (69, 128) |
| 5 | (128, 128) |
| 6 | (187, 128) |
| 7 | (69, 187) |
| 8 | (128, 187) |
| 9 | (187, 187) |

Normal Tilt:

| Dir | Raw |
| --- | --- |
| 1 | (69, 87) |
| 2 | (128, 87) |
| 3 | (187, 87) |
| 4 | (69, 128) |
| 5 | (128, 128) |
| 6 | (187, 128) |
| 7 | (69, 167) |
| 8 | (128, 167) |
| 9 | (187, 167) |

Normal Tilt2:

| Dir | Raw |
| --- | --- |
| 1 | (59, 88) |
| 2 | (128, 88) |
| 3 | (197, 88) |
| 4 | (59, 128) |
| 5 | (128, 128) |
| 6 | (197, 128) |
| 7 | (59, 168) |
| 8 | (128, 168) |
| 9 | (197, 168) |

Normal Tilt3:

| Dir | Raw |
| --- | --- |
| 1 | (92, 83) |
| 2 | (128, 83) |
| 3 | (164, 83) |
| 4 | (92, 128) |
| 5 | (128, 128) |
| 6 | (164, 128) |
| 7 | (92, 172) |
| 8 | (128, 172) |
| 9 | (164, 172) |

Mode X1/Y1:

| Dir | Raw |
| --- | --- |
| 1 | (92, 92) |
| 2 | (128, 92) |
| 3 | (164, 92) |
| 4 | (92, 128) |
| 5 | (128, 128) |
| 6 | (164, 128) |
| 7 | (92, 164) |
| 8 | (128, 164) |
| 9 | (164, 164) |

Mode X2/Y2:

| Dir | Raw |
| --- | --- |
| 1 | (71, 71) |
| 2 | (128, 71) |
| 3 | (185, 71) |
| 4 | (71, 128) |
| 5 | (128, 128) |
| 6 | (185, 128) |
| 7 | (71, 185) |
| 8 | (128, 185) |
| 9 | (185, 185) |

Mode X3/Y3:

| Dir | Raw |
| --- | --- |
| 1 | (87, 87) |
| 2 | (128, 87) |
| 3 | (169, 87) |
| 4 | (87, 128) |
| 5 | (128, 128) |
| 6 | (169, 128) |
| 7 | (87, 169) |
| 8 | (128, 169) |
| 9 | (169, 169) |

Mode Tilt:

| Dir | Raw |
| --- | --- |
| 1 | (87, 94) |
| 2 | (128, 94) |
| 3 | (169, 94) |
| 4 | (87, 128) |
| 5 | (128, 128) |
| 6 | (169, 128) |
| 7 | (87, 162) |
| 8 | (128, 162) |
| 9 | (169, 162) |

Mode Tilt2:

| Dir | Raw |
| --- | --- |
| 1 | (87, 78) |
| 2 | (128, 78) |
| 3 | (169, 78) |
| 4 | (87, 128) |
| 5 | (128, 128) |
| 6 | (169, 128) |
| 7 | (87, 178) |
| 8 | (128, 178) |
| 9 | (169, 178) |

Mode Tilt3:

| Dir | Raw |
| --- | --- |
| 1 | (101, 101) |
| 2 | (128, 101) |
| 3 | (155, 101) |
| 4 | (101, 128) |
| 5 | (128, 128) |
| 6 | (155, 128) |
| 7 | (101, 155) |
| 8 | (128, 155) |
| 9 | (155, 155) |

Tilt2 X: 197 was resolved as absolute right-side raw X, not as a
center-relative offset. This branch encodes Tilt2 left/right raw X as 59/197.

## C-Stick Values

Normal:

| Direction | Raw |
| --- | --- |
| C-Up | (128, 255) |
| C-Down | (128, 1) |
| C-Left | (39, 128) |
| C-Right | (217, 128) |

Mode:

| Direction | Raw |
| --- | --- |
| C-Up | (128, 255) |
| C-Down | (128, 1) |
| C-Left | (1, 128) |
| C-Right | (255, 128) |

## Shield Caveat

Light Shield L/R copied from Smash Box Designer values was not applied because
Glyph-side shield coordinate/trigger semantics were not confirmed. Existing WIP
shield behavior preserved.

Provided source values:

| Field | Value |
| --- | --- |
| Normal Light Shield L | 108 |
| Normal Light Shield R | 108 |
| Mode Light Shield L | 255 |
| Mode Light Shield R | 255 |

## Build Artifact

Build with the existing repo workflow:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

The expected firmware artifact path is produced by PlatformIO under:

```text
.pio/build/glyph_mk6/
```

Validated branch artifact from the local build:

```text
.pio/build/glyph_mk6/firmware.uf2
```

Use the generated `.uf2` for the manual hardware validation flow. Do not add
automated flashing or device-write steps on this branch.
