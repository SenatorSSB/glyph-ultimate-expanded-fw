# Glyph Ultimate Tilt RC Manifest

## RC Identity
- manifest_generated_from_branch: `glyph/ultimate-tilt-rc-manifest-provenance`
- firmware_source_commit_sha: `b69d91ad3425a8820be0240b060be1cd182e0171`
- manifest_generation_note: This manifest is generated before the manifest commit exists; it is not self-referential to a final manifest commit SHA.
- build_command: `./scripts/build-glyph-mk6-quiet.sh`
- runtime_implementation_source: `src/modes/Ultimate.cpp`
- hardware_test_status: NOT_TESTED
- flashing_automation: NOT_INCLUDED

## Git Dirty Summary
- git_dirty_state: DIRTY
- firmware_relevant_dirty_state: CLEAN
- staged_entries: 1
- unstaged_entries: 5
- untracked_entries: 2
- firmware_relevant_dirty_entries: none
- non_firmware_dirty_entries:
```text
 M docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md
 M docs/calibration/glyph_ultimate_tilt_rc_manifest.md
 M docs/calibration/glyph_ultimate_tilt_rc_manifest_handoff.md
 M tools/check_glyph_ultimate_tilt_rc_manifest.py
 M tools/write_glyph_ultimate_tilt_rc_manifest.py
?? docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_2026-05-24.md
?? docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_handoff.md
M docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md
```
- git_status_short:
```text
 M docs/calibration/glyph_ultimate_tilt_hardware_test_package_2026-05-24.md
 M docs/calibration/glyph_ultimate_tilt_rc_manifest.md
 M docs/calibration/glyph_ultimate_tilt_rc_manifest_handoff.md
 M tools/check_glyph_ultimate_tilt_rc_manifest.py
 M tools/write_glyph_ultimate_tilt_rc_manifest.py
?? docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_2026-05-24.md
?? docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_handoff.md
M docs/calibration/glyph_ultimate_tilt_hardware_result_policy_2026-05-24.md
```

## Artifact Candidates
- artifact_status: FOUND
- artifact_root: `.pio/build/glyph_mk6`
- candidate_suffixes: `.uf2, .bin, .elf, .hex`
- artifact_1_path: `.pio/build/glyph_mk6/firmware.uf2`
- artifact_1_size_bytes: `784384`
- artifact_1_sha256: `0530460c22604dc88c8f2766153bc717ff29e09e228cb319d3f7058894800606`
- artifact_2_path: `.pio/build/glyph_mk6/firmware.bin`
- artifact_2_size_bytes: `391960`
- artifact_2_sha256: `371c3fb99f218410fabb13e6faf2efb7b859a3f9398ba214eff6c889dc77e04b`
- artifact_3_path: `.pio/build/glyph_mk6/firmware.elf`
- artifact_3_size_bytes: `5405012`
- artifact_3_sha256: `ff83197589744133c9b6bc6715ee2d317319578037205656fde9f7946944376c`

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
