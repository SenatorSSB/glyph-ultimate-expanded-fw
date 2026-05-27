# Glyph / Smash Box Profile Output Tables - 2026-05-27

## Scope

This document records the requested Smash Box-style modifier profile values as absolute raw left-stick output tables for future Glyph / HayBox firmware and profile work.

Source basis:

- User-provided Smash Box profile screenshots, 2026-05-27.
- User clarification: `X`, `Y`, and `Tilt` modifier values are center-relative offsets from the current profile center / `5` coordinate.
- User clarification: Mode-prefixed modifiers (`MX`, `MY`, `MTilt`) are relative to the Mode profile center / `5`, which is intentionally off-center.
- User clarification: `MY1` and `MY2` are intentional flipper modifiers.

This document is not a hardware result and does not by itself authorize runtime implementation.

## Coordinate Convention

Raw stick coordinates are absolute bytes in `[0, 255]`.

Numpad directions:

```text
7 8 9
4 5 6
1 2 3
```

For a center-relative modifier value, values are interpreted as signed 8-bit offsets:

```text
signed8(v) = v       if v <= 127
signed8(v) = v - 256 if v >= 128
```

Examples:

```text
197 -> -59
156 -> -100
244 -> -12
175 -> -81
```

For ordinary X offsets:

```text
left  = center_x - signed8(x_offset)
right = center_x + signed8(x_offset)
```

For ordinary Y offsets:

```text
down = center_y - signed8(y_down_offset)
up   = center_y + signed8(y_up_offset)
```

For flipper offsets, the same formula is used. The apparent flip comes from signed overflow values.

## Source Values

### Default absolute values

```text
X Center = 128
Y Center = 128
Left     = 61
Right    = 195
Down     = 51
Up       = 205
```

### Mode default absolute values

```text
X Center = 128
Y Center = 172
Left     = 1
Right    = 255
Down     = 84
Up       = 172
```

### Non-Mode modifier offsets

```text
X1 Value       = 35
X2 Value       = 46
Tilt1 X        = 197 -> signed -59
Tilt2 X        = 40
Tilt3 X        = 53

Y1 Up          = 29
Y1 Down        = 29
Y2 Up          = 46
Y2 Down        = 46
Tilt1 Y Up     = 41
Tilt1 Y Down   = 41
Tilt2 Y Up     = 49
Tilt2 Y Down   = 49
Tilt3 Y Up     = 42
Tilt3 Y Down   = 42
```

### Mode modifier offsets

```text
MX1 Value      = 54
MX2 Value      = 69
MTilt1 X       = 33
MTilt2 X       = 33
MTilt3 X       = 32

MY1 Up         = 156 -> signed -100
MY1 Down       = 244 -> signed -12
MY2 Up         = 175 -> signed -81
MY2 Down       = 7
MTilt1 Y Up    = 3
MTilt1 Y Down  = 91
MTilt2 Y Up    = 3
MTilt2 Y Down  = 91
MTilt3 Y Up    = 2
MTilt3 Y Down  = 90
```

## Absolute 9-Way Output Tables

### Default

| Direction | Raw output |
|---:|---:|
| 1 | `(61, 51)` |
| 2 | `(128, 51)` |
| 3 | `(195, 51)` |
| 4 | `(61, 128)` |
| 5 | `(128, 128)` |
| 6 | `(195, 128)` |
| 7 | `(61, 205)` |
| 8 | `(128, 205)` |
| 9 | `(195, 205)` |

### Mode default

| Direction | Raw output |
|---:|---:|
| 1 | `(1, 84)` |
| 2 | `(128, 84)` |
| 3 | `(255, 84)` |
| 4 | `(1, 172)` |
| 5 | `(128, 172)` |
| 6 | `(255, 172)` |
| 7 | `(1, 172)` |
| 8 | `(128, 172)` |
| 9 | `(255, 172)` |

### X1

| Direction | Raw output |
|---:|---:|
| 1 | `(93, 51)` |
| 2 | `(128, 51)` |
| 3 | `(163, 51)` |
| 4 | `(93, 128)` |
| 5 | `(128, 128)` |
| 6 | `(163, 128)` |
| 7 | `(93, 205)` |
| 8 | `(128, 205)` |
| 9 | `(163, 205)` |

### X2

| Direction | Raw output |
|---:|---:|
| 1 | `(82, 51)` |
| 2 | `(128, 51)` |
| 3 | `(174, 51)` |
| 4 | `(82, 128)` |
| 5 | `(128, 128)` |
| 6 | `(174, 128)` |
| 7 | `(82, 205)` |
| 8 | `(128, 205)` |
| 9 | `(174, 205)` |

### MX1

| Direction | Raw output |
|---:|---:|
| 1 | `(74, 84)` |
| 2 | `(128, 84)` |
| 3 | `(182, 84)` |
| 4 | `(74, 172)` |
| 5 | `(128, 172)` |
| 6 | `(182, 172)` |
| 7 | `(74, 172)` |
| 8 | `(128, 172)` |
| 9 | `(182, 172)` |

### MX2

| Direction | Raw output |
|---:|---:|
| 1 | `(59, 84)` |
| 2 | `(128, 84)` |
| 3 | `(197, 84)` |
| 4 | `(59, 172)` |
| 5 | `(128, 172)` |
| 6 | `(197, 172)` |
| 7 | `(59, 172)` |
| 8 | `(128, 172)` |
| 9 | `(197, 172)` |

### Y1

| Direction | Raw output |
|---:|---:|
| 1 | `(61, 99)` |
| 2 | `(128, 99)` |
| 3 | `(195, 99)` |
| 4 | `(61, 128)` |
| 5 | `(128, 128)` |
| 6 | `(195, 128)` |
| 7 | `(61, 157)` |
| 8 | `(128, 157)` |
| 9 | `(195, 157)` |

### Y2

| Direction | Raw output |
|---:|---:|
| 1 | `(61, 82)` |
| 2 | `(128, 82)` |
| 3 | `(195, 82)` |
| 4 | `(61, 128)` |
| 5 | `(128, 128)` |
| 6 | `(195, 128)` |
| 7 | `(61, 174)` |
| 8 | `(128, 174)` |
| 9 | `(195, 174)` |

### MY1

| Direction | Raw output |
|---:|---:|
| 1 | `(1, 184)` |
| 2 | `(128, 184)` |
| 3 | `(255, 184)` |
| 4 | `(1, 172)` |
| 5 | `(128, 172)` |
| 6 | `(255, 172)` |
| 7 | `(1, 72)` |
| 8 | `(128, 72)` |
| 9 | `(255, 72)` |

### MY2

| Direction | Raw output |
|---:|---:|
| 1 | `(1, 165)` |
| 2 | `(128, 165)` |
| 3 | `(255, 165)` |
| 4 | `(1, 172)` |
| 5 | `(128, 172)` |
| 6 | `(255, 172)` |
| 7 | `(1, 91)` |
| 8 | `(128, 91)` |
| 9 | `(255, 91)` |

### Tilt1

| Direction | Raw output |
|---:|---:|
| 1 | `(187, 87)` |
| 2 | `(128, 87)` |
| 3 | `(69, 87)` |
| 4 | `(187, 128)` |
| 5 | `(128, 128)` |
| 6 | `(69, 128)` |
| 7 | `(187, 169)` |
| 8 | `(128, 169)` |
| 9 | `(69, 169)` |

### Tilt2

| Direction | Raw output |
|---:|---:|
| 1 | `(88, 79)` |
| 2 | `(128, 79)` |
| 3 | `(168, 79)` |
| 4 | `(88, 128)` |
| 5 | `(128, 128)` |
| 6 | `(168, 128)` |
| 7 | `(88, 177)` |
| 8 | `(128, 177)` |
| 9 | `(168, 177)` |

### Tilt3

| Direction | Raw output |
|---:|---:|
| 1 | `(75, 86)` |
| 2 | `(128, 86)` |
| 3 | `(181, 86)` |
| 4 | `(75, 128)` |
| 5 | `(128, 128)` |
| 6 | `(181, 128)` |
| 7 | `(75, 170)` |
| 8 | `(128, 170)` |
| 9 | `(181, 170)` |

### MTilt1

| Direction | Raw output |
|---:|---:|
| 1 | `(95, 81)` |
| 2 | `(128, 81)` |
| 3 | `(161, 81)` |
| 4 | `(95, 172)` |
| 5 | `(128, 172)` |
| 6 | `(161, 172)` |
| 7 | `(95, 175)` |
| 8 | `(128, 175)` |
| 9 | `(161, 175)` |

### MTilt2

| Direction | Raw output |
|---:|---:|
| 1 | `(95, 81)` |
| 2 | `(128, 81)` |
| 3 | `(161, 81)` |
| 4 | `(95, 172)` |
| 5 | `(128, 172)` |
| 6 | `(161, 172)` |
| 7 | `(95, 175)` |
| 8 | `(128, 175)` |
| 9 | `(161, 175)` |

### MTilt3

| Direction | Raw output |
|---:|---:|
| 1 | `(96, 82)` |
| 2 | `(128, 82)` |
| 3 | `(160, 82)` |
| 4 | `(96, 172)` |
| 5 | `(128, 172)` |
| 6 | `(160, 172)` |
| 7 | `(96, 174)` |
| 8 | `(128, 174)` |
| 9 | `(160, 174)` |

## Implementation Notes

- `MY1` and `MY2` are intentional flipper modifiers.
- Mode neutral / `5` is intentionally `(128, 172)`, not `(128, 128)`.
- M-prefix modifiers must be computed from the Mode center / `5`, not from the ordinary center.
- No runtime implementation should depend on unsigned overflow. Overflowed source values should be converted to signed offsets explicitly.
- This profile describes left-stick outputs only. C-stick values in the source screenshots are not part of this document's requested implementation set.
