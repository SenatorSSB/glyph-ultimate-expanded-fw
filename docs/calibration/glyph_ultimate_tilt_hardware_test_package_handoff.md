# Glyph Ultimate Tilt Hardware Test Package Handoff

## Branch

- `glyph/ultimate-tilt-hardware-test-package`

## Files Added/Changed

- `tools/inspect_glyph_mk6_build_artifact.py`
- `docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result_TEMPLATE.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_test_package_handoff.md`
- `docs/calibration/glyph_ultimate_tilt_runtime_implementation_handoff.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_smoke_test_protocol_draft_2026-05-24.md`

## Scope Confirmation

- Runtime firmware behavior changed in this branch: no.
- Device behavior changed in this branch: no.
- Flashing/push-to-device behavior added: no.
- SOCD behavior changed: no.
- Remapping semantics changed: no.
- Profile/schema changed: no.
- Build artifact helper added: yes.
- Hardware test package doc added: yes.
- Result template added: yes.
- Hardware test performed: no.

## Build And Artifact Status

- Build run: yes, `./scripts/build-glyph-mk6-quiet.sh` passed.
- Artifact/checksum found: yes.
- Primary local artifact candidate for manual recording: `.pio/build/glyph_mk6/firmware.uf2`.
- Primary local artifact size bytes: `784384`.
- Primary local artifact SHA-256: `52e68ecd9f4549987e7add3a34e56b87106f0f8c9a6b54e6c2b1f9cd073abc63`.
- Artifact helper command:

```bash
.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py
```

## Tests/Checks Run

Record final results after verification:

```text
.venv/bin/python tools/check_glyph_calibration_fixtures.py: PASS
.venv/bin/python tools/check_glyph_patch_script.py: PASS
.venv/bin/python tools/list_glyph_modifier_symbols.py: PASS
.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py: PASS
.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py: PASS
.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py: PASS
.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only: PASS
.venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py: PASS
.venv/bin/python tools/list_glyph_tilt_button_id_candidates.py: PASS
.venv/bin/python tools/check_glyph_tilt_button_id_probe.py: PASS
.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py: PASS
./scripts/build-glyph-mk6-quiet.sh: PASS
.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py: PASS, artifacts found
grep conflict marker check: PASS, no output
find .DS_Store check: PASS, no output
```

## Remaining Blockers Before Manual Hardware Use

- Exact commit SHA must be recorded in the test package/result sheet before manual hardware use.
- Build artifact path, size, and SHA-256 must be recorded in the test package/result sheet before manual hardware use.
- Known-good rollback firmware/profile must be ready.
- Hardware owner must perform any manual flashing using their approved workflow.
- Hardware smoke test has not yet been performed.
