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

## 2026-05-27 Tilt3 Branch Amendment

This amendment applies to branch `glyph/gfw2-ultimate-tilt3-runtime` only and preserves the historical Tilt1/Tilt2 information above.

User-approved Tilt3 runtime behavior:

- Dedicated Tilt3 uses the source-supported post-remap logical `inputs.lt3` path.
- Tilt3 also activates when `inputs.lt1 && inputs.lt2` are both held.
- Tilt3 X offset is `53`.
- Tilt3 Y offset is `42`.
- No macro, turbo, toggle, one-shot, timing, flashing, or push-to-device behavior is added.

Runtime active condition:

```text
tilt3_active = inputs.lt3 || (inputs.lt1 && inputs.lt2)
```

Tilt3 formula:

```text
leftStickX = 128 + directions.x * 53
leftStickY = 128 + directions.y * 42
```

Tilt3 table:

| Direction | Left-stick output |
| --- | --- |
| 1 | `(75, 86)` |
| 2 | `(128, 86)` |
| 3 | `(181, 86)` |
| 4 | `(75, 128)` |
| 5 | `(128, 128)` |
| 6 | `(181, 128)` |
| 7 | `(75, 170)` |
| 8 | `(128, 170)` |
| 9 | `(181, 170)` |

The old both-held observed behavior is superseded for this new runtime branch only after implementation and hardware test: `LT1+LT2` is intended to resolve to Tilt3 instead of falling through to the old combined behavior.

Hardware testing is required before final acceptance. Until that hardware test is complete, this branch only has source/build/checker evidence and no broad preservation PASS claim.
