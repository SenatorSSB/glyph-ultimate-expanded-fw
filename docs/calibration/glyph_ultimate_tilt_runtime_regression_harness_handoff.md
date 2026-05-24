# Glyph Ultimate Tilt Runtime Regression Harness Handoff

## Branch

- `glyph/ultimate-tilt-runtime-regression-harness`

## Files Added/Changed

- Added `tools/check_glyph_ultimate_tilt_tables.py`
- Added `tools/check_glyph_ultimate_tilt_hardware_result.py`
- Changed `tools/check_glyph_ultimate_tilt_runtime_source.py`
- Changed `tools/check_glyph_future_tilt_patch_scope.py`
- Added `docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_runtime_regression_harness_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_runtime_regression_harness_handoff.md`

## Runtime/Device Behavior Statements

- Runtime firmware behavior changed in this branch: **No**
- Device behavior changed in this branch: **No**
- Flashing or push-to-device behavior added: **No**
- SOCD behavior changed: **No**
- Remapping semantics changed: **No**
- Profile/schema changed: **No**

## Harness Deliverables

- Formula/table checker added: **Yes** (`tools/check_glyph_ultimate_tilt_tables.py`)
- Runtime source checker enhanced: **Yes** (`tools/check_glyph_ultimate_tilt_runtime_source.py`)
- Scope helper changed or deferred: **Changed** (`--mode runtime-implementation` added)
- Hardware result checker added: **Yes** (`tools/check_glyph_ultimate_tilt_hardware_result.py`)
- Hardware result policy doc added: **Yes**

## Tests/Checks Run

- `.venv/bin/python tools/check_glyph_calibration_fixtures.py` -> PASS
- `.venv/bin/python tools/check_glyph_patch_script.py` -> PASS
- `.venv/bin/python tools/list_glyph_modifier_symbols.py` -> PASS
- `.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py` -> PASS
- `.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py` -> PASS
- `.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py` -> PASS
- `.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py` -> PASS
- `.venv/bin/python tools/list_glyph_tilt_button_id_candidates.py` -> PASS
- `.venv/bin/python tools/check_glyph_tilt_button_id_probe.py` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py` -> PASS
- `.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_tables.py` -> PASS
- `.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode runtime-implementation` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py` -> `status=NO_RESULT_FILE` (expected until manual test result is created)
- `./scripts/build-glyph-mk6-quiet.sh` -> PASS
- `rg -n "^(<<<<<<<|=======|>>>>>>>)" docs tools config include src HAL || true` -> no conflict markers
- `find . -name .DS_Store -print` -> none found

## Remaining Blockers Before Manual Hardware Use

- Manual human-controlled hardware flash/test has not been performed.
- Real result file `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` has not yet been produced from an actual hardware run.
- Final disposition remains unknown until manual test evidence is captured.
