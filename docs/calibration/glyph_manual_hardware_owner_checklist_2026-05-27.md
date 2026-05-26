# Glyph Manual Hardware Owner Checklist - 2026-05-27

Purpose: concise operator checklist for the hardware owner to follow after dry-run checks pass and before/while doing manual hardware testing.

## Pre-Run Local Sanity

- confirm clean worktree
- confirm correct branch/commit identified
- confirm aggregate dry-run checker passes
- confirm build command available
- confirm artifact inspector available

## Branch Hygiene

- run `tools/check_glyph_no_forbidden_artifacts.py`
- confirm no tracked generated firmware/build artifacts are present
- confirm explicitly allowlisted source/reference firmware artifacts may exist
- confirm new firmware artifacts from local builds are not committed
- local `.pio` and `.venv` may exist but must not be committed
- before committing any hardware result later, run `git status --short`

## Build / Artifact

- run `.venv/bin/python -m platformio run -e glyph_mk6` only when ready to create RC artifact
- run `tools/inspect_glyph_mk6_build_artifact.py`
- record artifact path, size, SHA-256

## Manual UF2

- manual only
- only after explicit hardware-owner approval
- no repo script performs flashing or push-to-device
- record any macOS/RPI-RP2 disconnect behavior exactly as observed

## Result Recording

- copy/use template manually
- filled result target path is `docs/calibration/glyph_ultimate_preservation_hardware_result.md`
- do not mark PASS unless all required rows are observed and reviewed
- ambiguous rows should stay ambiguous
- old RF5 negative remains NOT_TESTED_AMBIGUOUS unless specifically retested with known RF5 location

## Post-Run

- run `tools/check_glyph_ultimate_preservation_hardware_result.py`
- commit result only after review decision
- if failure, document rollback status and do not claim preservation
