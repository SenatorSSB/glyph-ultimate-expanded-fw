# Glyph Ultimate Preservation Hardware Handoff

Date: 2026-05-26
Branch: `glyph/ultimate-preservation-test-matrix`

## Changed Files

- `docs/calibration/glyph_ultimate_preservation_hardware_matrix_2026-05-26.md`
- `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`
- `tools/check_glyph_ultimate_preservation_hardware_result.py`
- `docs/calibration/glyph_ultimate_preservation_hardware_handoff.md`

## What Was Added

- A source-grounded manual preservation matrix for native Ultimate behavior before future runtime changes.
- An unfilled result template that mirrors all matrix sections and enforces explicit row-level statuses.
- A stdlib-only read-only checker for a future real result file at `docs/calibration/glyph_ultimate_preservation_hardware_result.md`.
- Explicit RF5 preservation guidance using the newly transcribed test location for future RF5 testing:
  - center-right / RF cluster, far-right upper button = RF5

## What Was Not Tested

- No new hardware session was executed on this branch.
- No filled preservation result file was added.
- No firmware flashing, push automation, or runtime validation execution was performed as part of these docs/tooling-only changes.

## Behavior Change Summary

- Runtime behavior changed: none
- Source behavior changed: none
- Configurator behavior changed: none
- SOCD semantics changed: none
- Remap semantics changed: none
- Profile schema/proto changed: none

## Artifact Hygiene

- No build artifacts committed.
- No firmware binaries committed.
- No `.venv`, `.pio`, `__pycache__`, or `.pyc` files committed.

## Verification Commands Run

- `.venv/bin/python tools/check_glyph_ultimate_preservation_hardware_result.py`
- `.venv/bin/python tools/list_glyph_physical_logical_layout_sources.py`
- `.venv/bin/python tools/check_glyph_profile_adapter_prewrite.py docs/sources/raw/GlyphUserProfiles.json`
- `.venv/bin/python tools/run_glyph_ultimate_tilt_prehardware_checks.py`
- `.venv/bin/python tools/check_glyph_profile_config_semantics.py`
- `.venv/bin/python tools/check_glyph_profile_config_export_corpus.py`
- `grep -R -n -E '^(<<<<<<<|=======|>>>>>>>)' docs tools config include src HAL --exclude-dir=.git --exclude-dir=.venv || true`
- `git diff --check`
- `git status --short`

## Next Branch Recommendation

- `glyph/native-ultimate-table-runtime-design`
