# Glyph Ultimate Tilt Runtime Implementation (2026-05-24)

## Scope

This branch implements the first native Ultimate runtime Tilt/Tilt2 behavior change.

- Native `MODE_ULTIMATE` only.
- Left-stick output only.
- No profile, schema, remap, or SOCD changes.
- No C-stick/right-stick, trigger, flashing, or push-to-device behavior changes.

## Source Authority

Implementation is based on repo-local source authority:

- `docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json`
- `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_user_domain_spec_2026-05-24.md`
- `docs/calibration/glyph_native_ultimate_analog_baseline_2026-05-24.md`
- `docs/calibration/glyph_native_ultimate_tilt_patch_constraints_2026-05-24.md`
- `docs/calibration/glyph_native_ultimate_tilt_patch_review_checklist.md`

## Implemented Inputs

- Tilt1 / TILT uses post-remap logical `inputs.lt1`.
- Tilt2 uses post-remap logical `inputs.lt2`.
- Physical `BTN_RF3` and `BTN_RF4` are profile-level mappings for the uploaded MVP layout only.
- Runtime code does not bypass remap with raw physical `inputs.rf3` or `inputs.rf4`.

## Implemented Output Tables

Coordinates are absolute raw left-stick byte values in `[0,255]` with neutral `(128,128)`.

### Tilt1 / TILT

| Direction | Left-stick output |
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

Runtime formula for `directions.x` / `directions.y` in `-1,0,1`:

```text
leftStickX = 128 - directions.x * 59
leftStickY = 128 + directions.y * 41
```

### Tilt2

| Direction | Left-stick output |
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

Runtime formula for `directions.x` / `directions.y` in `-1,0,1`:

```text
leftStickX = 128 + directions.x * 40
leftStickY = 128 + directions.y * 49
```

## Both-Held Behavior

No new Tilt1/Tilt2 override is applied when both `inputs.lt1` and `inputs.lt2` are held.

Existing combined-layer behavior is preserved as much as this branch touches: the pre-existing MX/MY analog branches can still run, and the existing D-pad-layer C-stick neutral behavior remains unchanged.

## Preserved Outputs

- C-stick/right-stick outputs are untouched by the new Tilt block.
- Trigger analog and digital behavior are untouched by the new Tilt block.
- Existing nunchuk overwrite behavior is preserved; the new Tilt block runs before the late nunchuk left-stick overwrite, so connected nunchuk values remain authoritative.

## Numeric Safety

- The implementation uses explicit byte-safe signed arithmetic.
- It does not depend on unsigned overflow, wraparound, or flipper tricks.
- All approved Tilt1/Tilt2 outputs are within `[0,255]`.

## Verification

Expected verification for this branch:

```bash
.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py
.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py > docs/calibration/fixtures/native_ultimate_analog_static_snapshot.txt
.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py
./scripts/build-glyph-mk6-quiet.sh
```

Future hardware-owner smoke testing is still required before device use. This branch does not add flashing or push-to-device automation.
