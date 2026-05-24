# Glyph Ultimate Tilt Runtime Implementation Handoff

## Branch

- `glyph/ultimate-tilt-runtime-implementation`

## Files Added/Changed

- `src/modes/Ultimate.cpp`
- `tools/check_glyph_ultimate_tilt_runtime_source.py`
- `tools/check_glyph_ultimate_tilt_domain_spec.py`
- `docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json`
- `docs/calibration/fixtures/native_ultimate_analog_static_snapshot.txt`
- `docs/calibration/glyph_ultimate_tilt_runtime_implementation_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_runtime_implementation_handoff.md`
- `docs/calibration/glyph_native_ultimate_tilt_patch_review_checklist.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_smoke_test_protocol_draft_2026-05-24.md`
- `docs/calibration/glyph_native_ultimate_tilt_patch_constraints_2026-05-24.md`

## Runtime Status

- Runtime firmware behavior changed: yes, intentionally.
- Device behavior changed before flashing: no.
- Flashing/push-to-device behavior added: no.
- SOCD behavior changed: no.
- Remapping semantics changed: no.
- Profile/schema changed: no.
- Tilt/Tilt2 runtime implementation added: yes.
- Implementation file: `src/modes/Ultimate.cpp`.

## Runtime Inputs And Tables

Tilt1 / TILT runtime input: post-remap logical `inputs.lt1`.

| Direction | Output |
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

Tilt2 runtime input: post-remap logical `inputs.lt2`.

| Direction | Output |
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

## Preserved Behavior

- Right-stick/C-stick preserved: yes; the new Tilt patch block does not assign right-stick outputs.
- Triggers preserved: yes; the new Tilt patch block does not assign trigger analog outputs.
- Both-held behavior: no new Tilt override when both `inputs.lt1` and `inputs.lt2` are held.
- Nunchuk behavior preserved: yes; existing late nunchuk left-stick overwrite remains after the Tilt block.
- Overflow/wrap dependency avoided: yes.
- Hardware tested: no.

## Verification Commands And Results

Record final command results after branch verification:

```text
.venv/bin/python tools/check_glyph_calibration_fixtures.py: PASS
.venv/bin/python tools/check_glyph_patch_script.py: PASS
.venv/bin/python tools/list_glyph_modifier_symbols.py: PASS
.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py: PASS
.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py: PASS
.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py: PASS
.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator: PASS
.venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py: PASS
.venv/bin/python tools/list_glyph_tilt_button_id_candidates.py: PASS
.venv/bin/python tools/check_glyph_tilt_button_id_probe.py: PASS
.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py: PASS
rg conflict marker check: PASS, no output
find .DS_Store check: PASS, no output
./scripts/build-glyph-mk6-quiet.sh: PASS, glyph_mk6 SUCCESS
```

## Remaining Blockers Before Manual Hardware Use

- Hardware-owner smoke test has not happened.
- Manual flashing remains outside this branch and must use the hardware owner's approved workflow.
- Known-good firmware/profile rollback path must be ready before any manual device test.
