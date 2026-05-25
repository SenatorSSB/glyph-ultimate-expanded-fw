# Glyph Ultimate Tilt RC Manifest

## RC Identity
- manifest_generated_from_branch: `configurator`
- firmware_source_commit_sha: `919b0306977fda6348addc89881a8ef12adf0142`
- manifest_generation_note: This manifest is generated before the manifest commit exists; it is not self-referential to a final manifest commit SHA.
- build_command: `./scripts/build-glyph-mk6-quiet.sh`
- runtime_implementation_source: `src/modes/Ultimate.cpp`
- hardware_test_status: NOT_TESTED
- flashing_automation: NOT_INCLUDED

## Git Dirty Summary
- git_dirty_state: CLEAN
- firmware_relevant_dirty_state: CLEAN
- staged_entries: 0
- unstaged_entries: 0
- untracked_entries: 0
- firmware_relevant_dirty_entries: none
- non_firmware_dirty_entries: none
- git_status_short: CLEAN

## Artifact Candidates
- artifact_status: FOUND
- artifact_root: `.pio/build/glyph_mk6`
- candidate_suffixes: `.uf2, .bin, .elf, .hex`
- artifact_1_path: `.pio/build/glyph_mk6/firmware.uf2`
- artifact_1_size_bytes: `784384`
- artifact_1_sha256: `54b897fbf3f1ece6e7d072e9231b90a38f5d20ddeac4d6c6ad3585c01e2d28f8`
- artifact_2_path: `.pio/build/glyph_mk6/firmware.bin`
- artifact_2_size_bytes: `391952`
- artifact_2_sha256: `fd0fce87e96eeac56f6f6168201a7f9fccc546db08fd7531941ed5781f1fcf77`
- artifact_3_path: `.pio/build/glyph_mk6/firmware.elf`
- artifact_3_size_bytes: `5405012`
- artifact_3_sha256: `96fd2be5b312ffd06228db9aed287148016b20492df03e4412d7182880f75501`

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
