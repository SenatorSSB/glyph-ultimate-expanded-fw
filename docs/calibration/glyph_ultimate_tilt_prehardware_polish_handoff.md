# Glyph Ultimate Tilt Prehardware Polish Handoff

## Branch

- `glyph/ultimate-tilt-prehardware-polish`

## Scope

This handoff packages prehardware verification and documentation polish for the native Ultimate Tilt/Tilt2 implementation.

- Runtime firmware behavior changed: no.
- Device behavior changed: no.
- Flashing/push-to-device automation added: no.
- SOCD behavior changed: no.
- Remapping semantics changed: no.
- Profile/schema changed: no.
- Hardware smoke test performed: no.

## Added Files

- `tools/run_glyph_ultimate_tilt_prehardware_checks.py`
- `tools/check_glyph_ultimate_tilt_docs_consistency.py`
- `docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_prehardware_polish_handoff.md`

## Updated Package References

- Hardware package and result policy/template now reference:
  - `tools/run_glyph_ultimate_tilt_prehardware_checks.py`
  - `docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md`
- RC manifest now includes prehardware references and verification commands for:
  - `tools/check_glyph_ultimate_tilt_docs_consistency.py`
  - `tools/run_glyph_ultimate_tilt_prehardware_checks.py`
- Calibration docs conflict-marker examples now use portable anchored grep:

```bash
grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true
```

## Verification Summary

- existing Python checks listed in the RC manifest verification block: PASS
- `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py`: PASS
- `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py --include-build --check-artifact --check-hardware-result`: PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_docs_consistency.py`: PASS
- `.venv/bin/python -m platformio run -e glyph_mk6`: PASS
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true`: PASS (no output)

## Remaining Blocker

- Manual hardware flashing/smoke testing is intentionally not performed in this package.
