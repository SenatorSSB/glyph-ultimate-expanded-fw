# Glyph Ultimate Tilt Button ID Confirmation (2026-05-24)

## Scope

This document confirms Tilt1/Tilt2 activation IDs for the provided Ultimate MVP layout only.

This branch remains docs, fixtures, and read-only validation tooling only. It does not add runtime firmware behavior, device behavior, flashing, SOCD changes, remap semantic changes, or Tilt/Tilt2 runtime implementation.

## Status

Status: **CONFIRMED** for IDs in the provided Ultimate MVP layout.

Evidence:

- User-uploaded/current profile fixture: `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`
- User-supplied screenshot/provenance in the task identifying the MX/MY positions to replace. The screenshot is not committed in this branch.
- Repo geometry source: `config/glyph/glyph_mk6/include/button_positions.hpp`
- Repo matrix source: `config/glyph/glyph_mk6/include/matrix_definition.hpp`

## Final Button Conclusions

| Target | Physical profile button | Logical post-remap input | Semantic role | Future runtime input |
| --- | --- | --- | --- | --- |
| Tilt1 / TILT | `BTN_RF3` | `BTN_LT1` | replaces current MX button in this layout | `inputs.lt1` |
| Tilt2 | `BTN_RF4` | `BTN_LT2` | replaces current MY button in this layout | `inputs.lt2` |

`BTN_RF5` is explicitly rejected as a Tilt1/Tilt2 target for this uploaded MVP layout.

## Profile Interpretation

The uploaded/current profile already routes the intended physical buttons to the current MX/MY logical inputs in Ultimate mode:

- `BTN_RF3 -> BTN_LT1`
- `BTN_RF4 -> BTN_LT2`

Therefore, no JSON remap change is required for this layout.

## Runtime Interpretation

Future native Ultimate runtime implementation should use post-remap logical inputs:

- Tilt1 / TILT: `inputs.lt1`
- Tilt2: `inputs.lt2`

It should not implement raw physical `BTN_RF3`/`BTN_RF4` bypass semantics unless separately approved.

## Output Scope

Future Tilt1/Tilt2 output scope remains left stick only unless separately approved.

Preserve unchanged:

- C-stick/right-stick behavior.
- Trigger behavior.
- SOCD behavior.
- Remap semantics.

## Caveat

A future runtime patch is still behavior-changing and requires separate approval. No runtime implementation is added here.
