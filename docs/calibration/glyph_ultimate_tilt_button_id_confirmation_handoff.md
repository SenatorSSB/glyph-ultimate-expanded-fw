# Glyph Ultimate Tilt Button ID Confirmation Handoff

Date: 2026-05-24
Branch: `glyph/ultimate-tilt-button-id-confirmation`
Base branch: `configurator`

## Files Added/Changed

- Added `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_button_id_trace_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_user_domain_spec_2026-05-24.md`
- Added `docs/calibration/glyph_ultimate_tilt_button_id_confirmation_handoff.md`
- Added `docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json`
- Added `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`
- Added `tools/check_glyph_ultimate_tilt_domain_spec.py`
- Added `tools/check_glyph_tilt_button_id_probe.py`
- Added `tools/list_glyph_tilt_button_id_candidates.py`
- Updated `docs/calibration/glyph_native_ultimate_tilt_patch_constraints_2026-05-24.md`
- Updated `docs/calibration/glyph_ultimate_tilt_runtime_patch_spec_template.md`

## Boundary Confirmations

- Runtime firmware behavior changed: no.
- Device behavior changed: no.
- Flashing/push-to-device behavior added: no.
- SOCD behavior changed: no.
- Remapping semantics changed: no.
- Tilt/Tilt2 runtime implementation added: no.
- Firmware runtime source changed: no.

## Evidence Status

- JSON/profile evidence found: yes, `docs/calibration/fixtures/tilt_button_id_probe/GlyphUserProfilesUltimateMVP01.json`.
- Screenshot evidence found: user-supplied screenshot/provenance was referenced in the task; no screenshot artifact is committed.
- Repo geometry evidence found: yes, `button_positions.hpp` and `matrix_definition.hpp`.

## Confirmed Inputs

- Tilt1 / TILT physical button confirmed: `BTN_RF3`.
- Tilt1 / TILT logical post-remap input confirmed: `BTN_LT1`.
- Tilt1 / TILT future runtime input: `inputs.lt1`.
- Tilt2 physical button confirmed: `BTN_RF4`.
- Tilt2 logical post-remap input confirmed: `BTN_LT2`.
- Tilt2 future runtime input: `inputs.lt2`.
- `BTN_RF5` rejected: yes, rejected for this layout's Tilt1/Tilt2 target.

## Runtime/Profile Interpretation

- Future runtime implementation should use post-remap logical inputs: yes.
- Future runtime should bypass remap with physical `RF3`/`RF4`: no.
- Profile remap changes required for this layout: no.
- C-stick/right-stick/triggers preserve unchanged: yes.
- Future runtime output scope: native Ultimate, left-stick only, pending separate approval.

## Collision/Semantics Status

- Prior `RF4`/`RF5` ambiguity is resolved for the uploaded MVP layout by profile evidence: Tilt1 uses physical `BTN_RF3`; Tilt2 uses physical `BTN_RF4`; `BTN_RF5` is rejected.
- Native runtime implementation is still blocked pending separate behavior-changing approval.
- No Super Smash Bros. Ultimate gameplay semantics are invented or promoted by this branch.

## Tests/Checks Run

- `.venv/bin/python tools/check_glyph_calibration_fixtures.py` -> pass.
- `.venv/bin/python tools/check_glyph_patch_script.py` -> pass.
- `.venv/bin/python tools/list_glyph_modifier_symbols.py` -> pass.
- `.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py` -> pass.
- `.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py` -> pass.
- `.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py` -> pass.
- `.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only` -> pass after commit; 11 changed docs/tools files, all allowlisted.
- `.venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py` -> pass.
- `.venv/bin/python tools/list_glyph_tilt_button_id_candidates.py` -> pass.
- `.venv/bin/python tools/check_glyph_tilt_button_id_probe.py` -> pass.
- `rg -n "^(<<<<<<<|=======|>>>>>>>)" docs tools config include src HAL || true` -> no conflict markers found.
- `find . -name .DS_Store -print` -> no `.DS_Store` files found.
- `./scripts/build-glyph-mk6-quiet.sh` -> pass.

## Remaining Blockers Before Runtime Patch

- Separate approval for any runtime firmware behavior change.
- Exact runtime patch review for native Ultimate `inputs.lt1` / `inputs.lt2` handling.
- Preserve SOCD/remap semantics and avoid raw physical bypass behavior.
- Preserve C-stick/right-stick and trigger behavior.
- Continue to avoid uint8 overflow/wrap dependency.
