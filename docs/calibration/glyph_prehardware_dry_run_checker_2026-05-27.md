# Glyph Prehardware Dry-Run Checker - 2026-05-27

Purpose: aggregate structure/readiness dry-run of repo-local docs and checkers before manual hardware preparation.

This checker is a prehardware preparation control only. It is useful before the hardware owner starts manual build/UF2 preparation, but it is not a substitute for the hardware run.

## What It Runs

Run from repository root:

```bash
.venv/bin/python tools/run_glyph_prehardware_dry_run_checks.py
```

Default command list:

- `tools/check_glyph_prehardware_rc_runbook.py`
- `tools/inspect_glyph_mk6_build_artifact.py`
- `tools/check_glyph_user_requirements_packet.py`
- `tools/check_glyph_preservation_execution_packet.py`
- `tools/check_glyph_preimplementation_blockers.py`
- `tools/check_glyph_firmware_workstream_roadmap.py`
- `tools/check_glyph_native_ultimate_table_fixture.py docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`
- `tools/check_glyph_native_ultimate_table_fixture.py docs/calibration/fixtures/glyph_native_ultimate_current_tilt_tables_2026-05-26.json`
- `tools/check_glyph_native_ultimate_table_runtime_scope.py`
- `tools/run_glyph_next_runtime_change_readiness_checks.py`
- `tools/check_glyph_merged_state_consistency.py`
- `tools/check_glyph_ultimate_preservation_hardware_result.py`

## What It Intentionally Does Not Do

- does not build firmware
- does not flash hardware
- does not push to device
- does not create hardware result
- does not approve hardware testing
- does not claim preservation verification
- does not resolve user requirements
- does not promote both-held behavior
- does not resolve RF5 historical ambiguity

## Acceptable Caveats

- `NO_ARTIFACT` is acceptable before a build artifact exists.
- `NO_RESULT_FILE` is acceptable before hardware testing is run.

## Interpretation

A clean dry-run means repo-local structure/readiness checkers passed for prehardware preparation only.

PASS from this aggregate does not mean hardware readiness, firmware safety, flashing approval, or preservation verification.
