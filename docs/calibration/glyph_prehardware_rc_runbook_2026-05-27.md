# Glyph Prehardware RC Runbook - 2026-05-27

Purpose: manual runbook for preparing an RC artifact and preparing later manual hardware validation without claiming outcomes.

## Scope

- manual prehardware preparation only
- no firmware runtime change
- no flashing automation
- no push-to-device automation
- no result claim
- no preservation claim

## Preconditions

- branch/commit under test is known
- local worktree is clean
- `.venv` is available locally or created locally
- PlatformIO is available through `.venv`
- rollback firmware/profile/config readiness has been considered
- target Glyph hardware identity is known
- profile/config state under test is known

## Prehardware Command Sequence

Run from repository root:

```bash
git status --short
.venv/bin/python tools/check_glyph_user_requirements_packet.py
.venv/bin/python tools/check_glyph_preservation_execution_packet.py
.venv/bin/python tools/check_glyph_preimplementation_blockers.py
.venv/bin/python tools/check_glyph_firmware_workstream_roadmap.py
.venv/bin/python -m platformio run -e glyph_mk6
.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py
```

Notes:
- Required build command anchor: `.venv/bin/python -m platformio run -e glyph_mk6`.
- The default artifact path inspected by `tools/inspect_glyph_mk6_build_artifact.py` is `.pio/build/glyph_mk6/firmware.uf2`.
- Artifact absence is not a repository failure; build first if an RC artifact is required.

## Manual UF2 Note

- manual UF2 flow only
- perform manual UF2 copy only after explicit hardware-owner approval
- no script in this repo performs flashing or device push

## Result Recording

- Use the existing template: `docs/calibration/glyph_ultimate_preservation_hardware_result_TEMPLATE.md`
- Intended filled output path after real hardware execution: `docs/calibration/glyph_ultimate_preservation_hardware_result.md`
- Do not fill or fabricate a result in this branch
- Run `tools/check_glyph_ultimate_preservation_hardware_result.py` only after a real result file exists

## Preservation Focus For Later Manual Hardware Execution

- board boots
- device enumerates
- baseline buttons
- SOCD directions
- remap behavior
- C-stick/right-stick
- triggers
- optional nunchuk
- current Tilt1/Tilt2
- both-held observed-only unless explicitly promoted

## Failure And Rollback Notes

- record failure reproduction details exactly as observed
- record whether rollback is needed or not needed
- do not hide ambiguous RF5 evidence
- RF5 negative remains NOT_TESTED_AMBIGUOUS unless specifically retested using the now-known RF5 location

## Final Boundary

- PASS from docs/checkers does not mean hardware passed
- preservation claims require reviewed filled result file
