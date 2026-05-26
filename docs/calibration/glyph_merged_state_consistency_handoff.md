# Glyph Merged State Consistency Handoff

## Branch Purpose

Audit the current merged `configurator` state after branch cleanup and add a read-only consistency helper for stale merged-state claims.

## Added Files

- `docs/calibration/glyph_merged_state_consistency_audit_2026-05-26.md`
- `docs/calibration/glyph_merged_state_consistency_handoff.md`
- `tools/check_glyph_merged_state_consistency.py`

## What This Captures

- Future agent branches should start from current `origin/configurator`, use one fresh feature branch per run, and avoid branch reuse.
- Current major docs/checkers are present on `configurator`.
- Current Tilt/Tilt2 hardware smoke result exists.
- Full printed/base physical ID transcription exists as user-reported hardware observation.
- RF5's printed/base location is transcribed, while the older RF5 negative smoke-test row remains historically `NOT_TESTED_AMBIGUOUS`.
- Adapter policy documentation exists, but no write-capable adapter exists.
- Native Ultimate table runtime work is still design/checker/fixture-contract only.

## How To Run

```bash
.venv/bin/python tools/check_glyph_merged_state_consistency.py
```

The checker is stdlib-only and read-only. It reports warnings for expected template or historical contexts such as `NO_RESULT_FILE`, `TEMPLATE_ONLY`, or older pre-result documentation.

## Boundaries

This branch does not change runtime firmware, configurator behavior, profile schema/proto behavior, remap behavior, SOCD behavior, export behavior, flashing, or push-to-device workflows.

No new hardware verification is claimed.
