# Glyph Ultimate Tilt RC Manifest

## RC Identity
- branch: `glyph/ultimate-tilt-rc-manifest`
- commit_sha: `52570d2458be593ab88a80defb74f0efd82ef827`
- build_command: `./scripts/build-glyph-mk6-quiet.sh`
- runtime_implementation_source: `src/modes/Ultimate.cpp`
- hardware_test_status: NOT_TESTED
- flashing_automation: NOT_INCLUDED

## Git Dirty Summary
- git_dirty_state: DIRTY
- staged_entries: 1
- unstaged_entries: 2
- untracked_entries: 4
- git_status_short:
```text
 M docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md
 M docs/calibration/glyph_ultimate_tilt_hardware_test_result_TEMPLATE.md
?? docs/calibration/glyph_ultimate_tilt_rc_manifest.md
?? docs/calibration/glyph_ultimate_tilt_rc_manifest_handoff.md
?? tools/check_glyph_ultimate_tilt_rc_manifest.py
?? tools/write_glyph_ultimate_tilt_rc_manifest.py
M docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md
```

## Artifact Candidates
- artifact_status: FOUND
- artifact_root: `.pio/build/glyph_mk6`
- candidate_suffixes: `.uf2, .bin, .elf, .hex`
- artifact_1_path: `.pio/build/glyph_mk6/firmware.uf2`
- artifact_1_size_bytes: `784384`
- artifact_1_sha256: `aa4aabf166eedfb6f7250910ce22f2b8b436d97953df07a3f4f8aa6b6e7f3b97`
- artifact_2_path: `.pio/build/glyph_mk6/firmware.bin`
- artifact_2_size_bytes: `391960`
- artifact_2_sha256: `aff4a08ac08f68c3f65d2d7584a8e06eb267d04bb631fe05e22cccb7cf992ae3`
- artifact_3_path: `.pio/build/glyph_mk6/firmware.elf`
- artifact_3_size_bytes: `5405012`
- artifact_3_sha256: `0e4ccd5419d6e2463fbd2ab8f216b5bd9823e5ffb800c44895e9064bd29b3e12`

## Tilt Input Summary
- tilt1_input: `inputs.lt1` (post-remap logical input)
- tilt2_input: `inputs.lt2` (post-remap logical input)
- implementation_scope: left-stick-only override
- preserved_outputs: right-stick, triggers

## Tilt Table Reference
- domain_spec_fixture: `docs/calibration/fixtures/glyph_ultimate_tilt_domain_spec.json`
- domain_spec_fixture_status: OK

| Direction | Tilt1 (x, y) | Tilt2 (x, y) |
| --- | --- | --- |
| 1 | (187, 87) | (88, 79) |
| 2 | (128, 87) | (128, 79) |
| 3 | (69, 87) | (168, 79) |
| 4 | (187, 128) | (88, 128) |
| 5 | (128, 128) | (128, 128) |
| 6 | (69, 128) | (168, 128) |
| 7 | (187, 169) | (88, 177) |
| 8 | (128, 169) | (128, 177) |
| 9 | (69, 169) | (168, 177) |

## Verification Commands
```bash
.venv/bin/python tools/check_glyph_calibration_fixtures.py
.venv/bin/python tools/check_glyph_patch_script.py
.venv/bin/python tools/list_glyph_modifier_symbols.py
.venv/bin/python tools/list_glyph_tilt_runtime_gate_sources.py
.venv/bin/python tools/list_glyph_native_ultimate_analog_sources.py
.venv/bin/python tools/check_glyph_native_ultimate_snapshot.py
.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode docs-only
.venv/bin/python tools/check_glyph_future_tilt_patch_scope.py --base configurator --mode runtime-implementation
.venv/bin/python tools/check_glyph_ultimate_tilt_domain_spec.py
.venv/bin/python tools/list_glyph_tilt_button_id_candidates.py
.venv/bin/python tools/check_glyph_tilt_button_id_probe.py
.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py
.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py
.venv/bin/python tools/check_glyph_ultimate_tilt_tables.py
.venv/bin/python tools/check_glyph_ultimate_tilt_hardware_result.py
./scripts/build-glyph-mk6-quiet.sh
.venv/bin/python tools/write_glyph_ultimate_tilt_rc_manifest.py --output docs/calibration/glyph_ultimate_tilt_rc_manifest.md
.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py
```
