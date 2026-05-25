# Glyph Ultimate Tilt Runtime Preflight Handoff

## Branch Name

- `glyph/ultimate-tilt-runtime-preflight`

## Files Added/Changed

- Added `docs/calibration/glyph_ultimate_tilt_runtime_patch_spec_template.md`
- Added `docs/calibration/glyph_native_ultimate_tilt_patch_review_checklist.md`
- Added `tools/check_glyph_future_tilt_patch_scope.py`
- Added `docs/calibration/glyph_ultimate_tilt_runtime_preflight_handoff.md`

## Boundary Confirmations

- Runtime firmware behavior changed: no.
- Device behavior changed: no.
- Flashing/push-to-device behavior added: no.
- SOCD behavior changed: no.
- Remapping semantics changed: no.
- Final Tilt1/Tilt2 values selected: no.
- Activation mapping selected: no.
- Tilt/Tilt2 runtime implementation added: no.

## Preflight Artifact Confirmations

- Future patch spec template added: yes.
- Future patch review checklist added: yes.
- Future patch scope helper added: yes (read-only).

## Tests/Checks Run

- `.venv/bin/python tools/check_glyph_calibration_fixtures.py` -> pass
- `.venv/bin/python tools/check_glyph_patch_script.py` -> pass
- `.venv/bin/python tools/list_glyph_modifier_symbols.py` -> pass
- `.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py` -> pass
- `.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py` -> pass
- `.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py` -> pass
- `.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only` -> pass
- `grep -R "<<<<<<<\|=======\|>>>>>>>" docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true` -> executed; one known documentation-string match in an existing handoff file
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true` -> no conflict markers found
- `find . -name .DS_Store -print` -> none found
- `./scripts/build-glyph-mk6-quiet.sh` -> pass

## Remaining Blockers Before Runtime Patch

- Final source-backed Tilt1/Tilt2 values are not selected/approved.
- Activation button/chord mapping is not selected/approved.
- Runtime patch scope must stay minimal and explicitly approved.
- Overflow/flipper-dependent behavior remains blocked unless explicitly avoided or proven from source.
- Future behavior-changing branch must pass diff-scope review, scanner snapshot review, build, and hardware-owner smoke-test protocol review.
