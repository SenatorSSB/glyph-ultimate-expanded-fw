# Glyph Ultimate Tilt Runtime Regression Harness (2026-05-24)

## 1) Scope

- Host-side, read-only regression checks only.
- No runtime firmware behavior changes are included by this harness.
- No flashing or push-to-device automation is included.

## 2) Checks Added

- `tools/check_glyph_ultimate_tilt_tables.py`
  - stdlib-only formula/table checker against domain-spec fixture and `src/modes/Ultimate.cpp`
- `tools/check_glyph_ultimate_tilt_runtime_source.py` (enhanced)
  - stronger static checks for the marked Tilt patch block
- `tools/check_glyph_future_tilt_patch_scope.py` (updated)
  - adds `--mode runtime-implementation`
- `tools/check_glyph_ultimate_tilt_hardware_result.py`
  - stdlib-only structure checker for a filled hardware result markdown file

## 3) What Each Check Proves

- Formula/table checker proves the runtime formula constants/signs in the marked patch block match domain-spec Tilt1/Tilt2 tables for directions `1..9`.
- Source checker proves the marked patch block remains left-stick focused, LT1/LT2 post-remap gated, and free of forbidden assignment/timing patterns.
- Scope checker mode proves branch file-diff scope stays within runtime-implementation review boundaries (`src/modes/Ultimate.cpp`, `docs/`, `tools/`) while still flagging risk paths.
- Hardware result structure checker proves a later result document is structurally complete and machine-parseable for metadata and Tilt1/Tilt2 PASS/FAIL/BLOCKED result fields.

## 4) What Each Check Does Not Prove

- No check in this harness proves hardware behavior on a device.
- No check in this harness proves controller transport behavior.
- No check in this harness proves in-game behavior.
- A PASS in these host-side checks is not a hardware pass verdict.

## 5) Required Command Sequence

Run from repo root.

### Before merge

```bash
.venv/bin/python tools/check_glyph_calibration_fixtures.py
.venv/bin/python tools/check_glyph_patch_script.py
.venv/bin/python tools/list_glyph_modifier_symbols.py
.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py
.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py
.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py
.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only
.venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py
.venv/bin/python tools/list_glyph_tilt_button_id_candidates.py
.venv/bin/python tools/check_glyph_tilt_button_id_probe.py
.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py
.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py
.venv/bin/python tools/check_glyph_ultimate_tilt_tables.py
.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode runtime-implementation
.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py
./scripts/build-glyph-mk6-quiet.sh
rg -n "^(<<<<<<<|=======|>>>>>>>)" docs tools config include src HAL || true
find . -name .DS_Store -print
```

### Before hardware use

```bash
.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py
```

- If the result file is missing, checker reports `status=NO_RESULT_FILE` and manual test has not yet been recorded.
- Hardware use must follow the manual protocol and should only be recorded in the real result file after actual testing.
