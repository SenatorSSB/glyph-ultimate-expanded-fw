# Glyph Ultimate Tilt User Domain Spec (2026-05-24)

## 1. Source Status

- Source kind: user-supplied domain spec from chat (2026-05-24).
- Firmware implementation status in this branch: not implemented.
- Hardware validation status in this branch: not hardware-tested.
- Scope status: documentation, fixtures, and read-only validation tooling only.

## 2. Coordinate Convention

- Coordinate space: absolute raw bytes in `[0, 255]`.
- Neutral point: `(128, 128)`.
- Direction indexing: 9-way numpad keys (`"1"`..`"9"`).
- Convention parity: matches the repository's existing raw-coordinate convention used in Ultimate analog docs.

## 3. Base Table (absolute raw left-stick)

| Direction | Coordinate |
| --- | --- |
| 1 | `(28, 28)` |
| 2 | `(128, 28)` |
| 3 | `(228, 28)` |
| 4 | `(28, 128)` |
| 5 | `(128, 128)` |
| 6 | `(228, 128)` |
| 7 | `(28, 228)` |
| 8 | `(128, 228)` |
| 9 | `(228, 228)` |

## 4. TILT / Tilt1 Table (absolute raw left-stick)

Source Smash Box values provided by user:

- Tilt X = `197`
- Tilt Y Up = `41`
- Tilt Y Down = `41`

Explicit raw coordinate table to preserve:

| Direction | Coordinate |
| --- | --- |
| 1 | `(187, 87)` |
| 2 | `(128, 87)` |
| 3 | `(69, 87)` |
| 4 | `(187, 128)` |
| 5 | `(128, 128)` |
| 6 | `(69, 128)` |
| 7 | `(187, 169)` |
| 8 | `(128, 169)` |
| 9 | `(69, 169)` |

## 5. Tilt1 Flipper Interpretation and Byte Safety

- User-supplied conceptual interpretation: `197` as `uint8` corresponds to signed `-59` as `int8`.
- Runtime requirement for later implementation: use explicit absolute coordinates, not implicit signed/overflow reinterpretation.
- Overflow policy: no dependency on `uint8` overflow/wrap behavior.
- Status in this branch: documented only; no runtime behavior added.

## 6. Tilt2 Table (absolute raw left-stick)

Source Smash Box values provided by user:

- Tilt2 X = `40`
- Tilt2 Y Up = `49`
- Tilt2 Y Down = `49`

Explicit raw coordinate table to preserve:

| Direction | Coordinate |
| --- | --- |
| 1 | `(88, 79)` |
| 2 | `(128, 79)` |
| 3 | `(168, 79)` |
| 4 | `(88, 128)` |
| 5 | `(128, 128)` |
| 6 | `(168, 128)` |
| 7 | `(88, 177)` |
| 8 | `(128, 177)` |
| 9 | `(168, 177)` |

## 7. Output Target Scope

- Intended target output for Tilt1/Tilt2 tables: left stick only.
- C-stick/right-stick output: must remain preserved.
- Trigger output: must remain preserved.
- Runtime status: no implementation in this branch.

## 8. Activation Mapping Status

Status: **confirmed for the uploaded/current Ultimate MVP layout**.

The uploaded/current profile evidence confirms:

- Tilt1 / TILT replaces MX:
  - physical profile button: `BTN_RF3`
  - logical post-remap input: `BTN_LT1`
  - future native Ultimate runtime reference: `inputs.lt1`
- Tilt2 replaces MY:
  - physical profile button: `BTN_RF4`
  - logical post-remap input: `BTN_LT2`
  - future native Ultimate runtime reference: `inputs.lt2`

The profile already routes `BTN_RF3 -> BTN_LT1` and `BTN_RF4 -> BTN_LT2`, so no JSON remap change is required for this layout.

`BTN_RF5` is rejected for this layout's Tilt1/Tilt2 target.

## 9. Remaining Blockers Before Runtime Implementation

- Future runtime implementation remains behavior-changing and requires separate approval.
- Runtime implementation should use post-remap logical inputs `inputs.lt1` and `inputs.lt2`.
- Raw physical `RF3`/`RF4` bypass semantics are not approved.
- Keep implementation explicit-coordinate based and byte-safe with no overflow dependency.
- Preserve C-stick/right-stick and trigger behavior unless future explicit approval changes that scope.
