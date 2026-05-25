# Glyph Ultimate Tilt Prehardware Readiness Index (2026-05-24)

## Scope

This index tracks whether the native Glyph Ultimate Tilt/Tilt2 package is ready for manual hardware testing.

- Runtime firmware behavior changes in this prehardware package: none.
- Flashing automation included: no.
- Push-to-device behavior included: no.
- Hardware smoke test result: not yet performed.

## Readiness Levels

- `R0_NOT_READY`: one or more required automated checks fail.
- `R1_PREHARDWARE_READY`: automated checks pass; hardware test is still pending.
- `R2_HARDWARE_VERIFIED`: manual hardware test result is recorded and accepted.

## Evidence Matrix

| Gate | Evidence command/document | Required status | Current status |
| --- | --- | --- | --- |
| Baseline source/docs checks | `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py` | PASS | PASS |
| Build + artifact + result-structure checks | `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py --include-build --check-artifact --check-hardware-result` | PASS | PASS |
| RC manifest structure | `.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py` | PASS | PASS |
| Docs consistency | `.venv/bin/python tools/check_glyph_ultimate_tilt_docs_consistency.py` | PASS | PASS |
| Conflict markers scan | `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true` | no output | PASS |
| Hardware result file policy | `docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md` | defined | PASS |
| Manual hardware smoke test | `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` | real result file recorded | PENDING |

## Current Classification

- readiness_level: `R1_PREHARDWARE_READY`
- rationale: automated prehardware checks pass, but manual hardware test evidence is still pending.

## References

- `tools/run_glyph_ultimate_tilt_prehardware_checks.py`
- `tools/check_glyph_ultimate_tilt_docs_consistency.py`
- `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result_TEMPLATE.md`
