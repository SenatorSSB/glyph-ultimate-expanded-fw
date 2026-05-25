# Glyph Ultimate Tilt RC Manifest Handoff

## Provenance Semantics Follow-Up

This handoff reflects the initial RC manifest branch. Provenance semantics were later clarified in:

- `docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_2026-05-24.md`
- `docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_handoff.md`

## Branch

- branch_name: `glyph/ultimate-tilt-rc-manifest`

## Files Added Or Changed

- added: `tools/write_glyph_ultimate_tilt_rc_manifest.py`
- added: `tools/check_glyph_ultimate_tilt_rc_manifest.py`
- added: `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`
- added: `docs/calibration/glyph_ultimate_tilt_rc_manifest_handoff.md`
- changed: `docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md`
- changed: `docs/calibration/glyph_ultimate_tilt_hardware_test_result_TEMPLATE.md`
- changed: `docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md`

## Behavior And Scope Declarations

- runtime_firmware_behavior_changed: NO
- device_behavior_changed: NO
- flashing_or_push_to_device_added: NO
- socd_behavior_changed: NO
- remapping_semantics_changed: NO
- profile_or_schema_changed: NO
- rc_manifest_generated: YES
- artifact_or_checksum_found: YES
- hardware_tested: NO

## RC Manifest Notes

- manifest_path: `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`
- generator: `tools/write_glyph_ultimate_tilt_rc_manifest.py`
- checker: `tools/check_glyph_ultimate_tilt_rc_manifest.py`
- hardware_test_status_in_manifest: `NOT_TESTED`
- flashing_automation_in_manifest: `NOT_INCLUDED`
- primary_artifact_candidates_recorded: `firmware.uf2`, `firmware.bin`, `firmware.elf`
- artifact_status: `FOUND`

## Tests And Checks Run

- `.venv/bin/python tools/check_glyph_calibration_fixtures.py` -> PASS
- `.venv/bin/python tools/check_glyph_patch_script.py` -> PASS
- `.venv/bin/python tools/list_glyph_modifier_symbols.py` -> PASS
- `.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py` -> PASS
- `.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py` -> PASS
- `.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py` -> PASS
- `.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only` -> PASS
- `.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode runtime-implementation` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py` -> PASS
- `.venv/bin/python tools/list_glyph_tilt_button_id_candidates.py` -> PASS
- `.venv/bin/python tools/check_glyph_tilt_button_id_probe.py` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py` -> PASS
- `.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_tables.py` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py` -> PASS (`NO_RESULT_FILE` expected)
- `./scripts/build-glyph-mk6-quiet.sh` -> PASS
- `.venv/bin/python tools/write_glyph_ultimate_tilt_rc_manifest.py --output docs/calibration/glyph_ultimate_tilt_rc_manifest.md` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py` -> PASS
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true` -> PASS (no conflicts found)
- `find . -name .DS_Store -print` -> PASS (none found)

## Remaining Blockers Before Manual Hardware Use

- Human-controlled manual flash has not been performed.
- Human-controlled hardware smoke test has not been performed.
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` has not been produced yet.
- Hardware owner approval and rollback execution still must happen during manual test flow.
