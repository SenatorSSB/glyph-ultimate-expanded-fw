# Glyph Ultimate Tilt Runtime Design Gates Handoff

## Branch

- `glyph/ultimate-tilt-runtime-design-gates`

## Files Added/Changed

- Added `docs/calibration/glyph_ultimate_tilt_runtime_gate_matrix_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_implementation_options_2026-05-24.md`
- Added `docs/calibration/glyph_modifier_overflow_clamp_risk_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_hardware_smoke_test_protocol_draft_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_runtime_design_gates_handoff.md`
- Added `tools/list_glyph_tilt_runtime_gate_sources.py`

## Boundary Confirmations

- Runtime firmware behavior changed: no.
- Device behavior changed: no.
- Flashing or push-to-device behavior added: no.
- SOCD behavior changed: no.
- Remapping semantics changed: no.
- Final Tilt1/Tilt2 values selected: no.
- Tilt/Tilt2 runtime implementation added: no.
- Implementation option selected: no. Native `MODE_ULTIMATE` is only documented as a likely safest next runtime experiment requiring user approval.
- Overflow/clamp behavior proven: no. It remains blocked for overflow-dependent behavior.
- Flipper behavior proven: no. It remains blocked.
- Smoke-test protocol draft added: yes, as human-controlled draft only.

## Checks To Run

- `.venv/bin/python tools/check_glyph_calibration_fixtures.py`
- `.venv/bin/python tools/check_glyph_patch_script.py`
- `.venv/bin/python tools/list_glyph_modifier_symbols.py`
- `.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py`
- Targeted conflict-marker scan over `docs tools config include src HAL`
- `find . -name .DS_Store -print`
- `./scripts/build-glyph-mk6-quiet.sh` if local setup remains healthy

## Remaining Blockers Before Runtime Patch

- Approve exact Tilt1/Tilt2 values or source-backed value fixture.
- Decide and approve implementation path.
- Prove or explicitly avoid overflow/clamp-dependent behavior.
- Prove or explicitly design flipper behavior; do not guess it.
- Keep SOCD and remap semantics unchanged unless explicitly approved otherwise.
- Pin/review proto source authority before schema/profile-sensitive changes.
- Add host-side tests before hardware where possible.
- Review the smoke-test protocol with hardware owner before any manual flash.
