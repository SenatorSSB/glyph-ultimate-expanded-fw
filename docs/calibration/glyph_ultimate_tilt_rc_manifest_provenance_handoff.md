# Glyph Ultimate Tilt RC Manifest Provenance Handoff

## Branch

- branch_name: `glyph/ultimate-tilt-rc-manifest-provenance`

## Files Added Or Changed

- added: `docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_2026-05-24.md`
- added: `docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_handoff.md`
- changed: `tools/write_glyph_ultimate_tilt_rc_manifest.py`
- changed: `tools/check_glyph_ultimate_tilt_rc_manifest.py`
- changed: `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`
- changed: `docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md`
- changed: `docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md`
- changed: `docs/calibration/glyph_ultimate_tilt_rc_manifest_handoff.md`

## Scope Declarations

- runtime_firmware_behavior_changed: NO
- device_behavior_changed: NO
- flashing_or_push_to_device_added: NO
- socd_behavior_changed: NO
- remapping_semantics_changed: NO
- profile_or_schema_changed: NO
- rc_manifest_generator_changed: YES
- rc_manifest_checker_changed: YES
- rc_manifest_regenerated: YES
- firmware_relevant_dirty_state_clean: YES
- hardware_tested: NO

## Manifest Provenance Notes

- manifest path: `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`
- firmware source commit recorded as: `firmware_source_commit_sha`
- generation branch recorded as: `manifest_generated_from_branch`
- manifest self-reference note recorded as: `manifest_generation_note`
- full git dirty state remains visible via: `git_dirty_state` and `git_status_short`
- firmware relevance split recorded via:
  - `firmware_relevant_dirty_state`
  - `firmware_relevant_dirty_entries`
  - `non_firmware_dirty_entries`

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
- `.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py` -> PASS
- `./scripts/build-glyph-mk6-quiet.sh` -> PASS
- `.venv/bin/python tools/write_glyph_ultimate_tilt_rc_manifest.py --output docs/calibration/glyph_ultimate_tilt_rc_manifest.md` -> PASS
- `.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py` -> PASS
- `rg -n "^(<<<<<<<|=======|>>>>>>>)" docs tools config include src HAL || true` -> PASS

## Remaining Blockers Before Manual Hardware Use

- Human-controlled manual flash has not been performed.
- Human-controlled hardware smoke testing has not been performed.
- `docs/calibration/glyph_ultimate_tilt_hardware_test_result.md` has not been produced from real test evidence.
- Hardware owner approval and rollback execution must still happen during manual test flow.
