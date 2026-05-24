# Glyph Ultimate Tilt Button ID Trace (2026-05-24)

## Scope

Purpose: trace the source/user evidence for the provided Ultimate MVP layout's Tilt1/Tilt2 button IDs.

This document distinguishes:

- physical profile buttons: `BTN_RF3`, `BTN_RF4`
- logical post-remap inputs: `BTN_LT1`, `BTN_LT2`
- future native Ultimate runtime references: `inputs.lt1`, `inputs.lt2`

No runtime behavior is implemented here.

## Inspected Evidence

- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`
- `config/glyph/glyph_mk6/include/button_positions.hpp`
- `config/glyph/glyph_mk6/include/matrix_definition.hpp`
- User-supplied screenshot/provenance in the task showing MX/MY positions to be replaced; not committed in this branch.

## Repo Geometry Evidence

`config/glyph/glyph_mk6/include/button_positions.hpp` lists the right-finger same-row buttons in increasing x order:

- `BTN_RF1`
- `BTN_RF2`
- `BTN_RF3`
- `BTN_RF4`

In that display geometry, `BTN_RF4` is the rightmost same-row button, and `BTN_RF3` is immediately left of `BTN_RF4`.

`config/glyph/glyph_mk6/include/matrix_definition.hpp` confirms the same matrix row sequence:

- `BTN_RF1`
- `BTN_RF2`
- `BTN_RF3`
- `BTN_RF4`

This is source-backed geometry/order evidence. It is not a runtime behavior change.

## Uploaded Profile Evidence

In the uploaded/current profile's Ultimate mode, the relevant remaps are:

- physical `BTN_RF3` activates logical `BTN_LT1`
- physical `BTN_RF4` activates logical `BTN_LT2`

The probe checker validates this from the stable fixture copy at:

- `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`

## Confirmed Interpretation

| Target | Physical profile button | Logical post-remap input | Semantic role | Future runtime input |
| --- | --- | --- | --- | --- |
| Tilt1 / TILT | `BTN_RF3` | `BTN_LT1` | replace MX | `inputs.lt1` |
| Tilt2 | `BTN_RF4` | `BTN_LT2` | replace MY | `inputs.lt2` |

`BTN_RF5` is rejected for this layout's Tilt1/Tilt2 target.

## Runtime Boundary

Future native Ultimate runtime logic should target post-remap logical inputs:

- `inputs.lt1` for Tilt1 / TILT
- `inputs.lt2` for Tilt2

Do not describe `RF3`/`RF4` as runtime inputs without qualifying them as physical/profile buttons. Raw physical bypass semantics are not approved.

## Behavior Status

- Runtime firmware behavior changed: no.
- Device behavior changed: no.
- SOCD behavior changed: no.
- Remapping semantics changed: no.
- Tilt/Tilt2 runtime implementation added: no.
