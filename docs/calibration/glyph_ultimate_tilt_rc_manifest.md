# Glyph Ultimate Tilt RC Manifest

## RC Identity
- manifest_generated_from_branch: `configurator`
- firmware_source_commit_sha: `5dc9b122a3188344cef3ba800902b0f3fd2449ce`
- manifest_generation_note: This manifest is generated before the manifest commit exists; it is not self-referential to a final manifest commit SHA.
- build_command: `./scripts/build-glyph-mk6-quiet.sh`
- runtime_implementation_source: `src/modes/Ultimate.cpp`
- hardware_test_status: NOT_TESTED
- flashing_automation: NOT_INCLUDED

## Git Dirty Summary
- git_dirty_state: DIRTY
- firmware_relevant_dirty_state: CLEAN
- staged_entries: 1
- unstaged_entries: 1
- untracked_entries: 0
- firmware_relevant_dirty_entries: none
- non_firmware_dirty_entries:
```text
 M tools/__pycache__/patch_glyph_ultimate_profile.cpython-314.pyc
M tools/__pycache__/glyph_config_model.cpython-314.pyc
```
- git_status_short:
```text
 M tools/__pycache__/patch_glyph_ultimate_profile.cpython-314.pyc
M tools/__pycache__/glyph_config_model.cpython-314.pyc
```

## Artifact Candidates
- artifact_status: FOUND
- artifact_root: `.pio/build/glyph_mk6`
- candidate_suffixes: `.uf2, .bin, .elf, .hex`
- artifact_1_path: `.pio/build/glyph_mk6/firmware.uf2`
- artifact_1_size_bytes: `784384`
- artifact_1_sha256: `3ec423aa2b09ac6c176d8324f66095011d2c77f744a693c3363d533502faee53`
- artifact_2_path: `.pio/build/glyph_mk6/firmware.bin`
- artifact_2_size_bytes: `391960`
- artifact_2_sha256: `707b5912295afb3aa48664eb0d61f6fbac9be6b78c9e6a0e16a8994cf0b0806d`
- artifact_3_path: `.pio/build/glyph_mk6/firmware.elf`
- artifact_3_size_bytes: `5405012`
- artifact_3_sha256: `38b275eecfe668076c1742d3cba755959895e1c7133dc554fae759fe5212fdca`

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

## Prehardware References
- prehardware_aggregator: `tools/run_glyph_ultimate_tilt_prehardware_checks.py`
- readiness_index: `docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md`

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
.venv/bin/python tools/check_glyph_ultimate_tilt_docs_consistency.py
.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py
.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py --include-build --check-artifact --check-hardware-result
.venv/bin/python -m platformio run -e glyph_mk6
.venv/bin/python tools/write_glyph_ultimate_tilt_rc_manifest.py --output docs/calibration/glyph_ultimate_tilt_rc_manifest.md
.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py
grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true
```
