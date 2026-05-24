# Glyph Initial Firmware Test Readiness (2026-05-24)

## 1) Ready now
- Calibration fixture set is in place and checked:
  - `docs/calibration/fixtures/GlyphUserProfilesUlt-filled.json`
  - `docs/calibration/fixtures/GlyphUltFilled2.json`
- Parser/check tooling now exists for read-only config modeling and regression checks:
  - `tools/glyph_config_model.py`
  - `tools/check_glyph_calibration_fixtures.py`
- Profile-specific SOCD model is explicit in parser/check logic (no universal SOCD assumptions).
- Omitted `activates` preservation is explicitly checked for `BTN_MB1..BTN_MB3`.
- JSON patch prototype layer exists for fixture/config JSON (not firmware runtime):
  - `tools/patch_glyph_ultimate_profile.py`
  - `tools/check_glyph_patch_script.py`
  - `docs/calibration/fixtures/example_ultimate_patch.json`

## 2) Not ready / hard blockers
- Exact canonical tracked source authority for enum/schema definitions is not yet pinned; currently discovered in `.pio/libdeps/.../config.proto`.
- Exact modifier-value storage/use behavior for all custom paths is not fully verified end-to-end in this batch.
- Custom Tilt1/Tilt2 implementation location is not explicitly validated in this batch.
- Overflow behavior / flipper modifier behavior is not fully confirmed in this batch.
- A finalized hardware smoke-test procedure document for first custom firmware test is still needed.

## 3) Minimum safe initial test firmware scope
- One small branch, narrow change set, reversible by normal Git history.
- No broad refactor.
- One or two custom Ultimate modifier outputs only.
- No macro/turbo/timing automation.
- Compile/build verification before any hardware test.
- Manual hardware smoke test with explicit rollback path.

## 4) Stop conditions before firmware patch
- Unknown button enum mapping in source authority.
- Unknown modifier value schema or unclear persistence mapping.
- Unclear SOCD interactions for the targeted change.
- Any requirement for timing automation.
- Any unsupported controller behavior assumption.
