# Glyph Ultimate Tilt Hardware Test Package (2026-05-24)

## 1. Scope

This package is for manual hardware testing of the native Ultimate Tilt/Tilt2 runtime implementation only.

- Flashing automation: not included.
- Push-to-device behavior: not included.
- Runtime firmware behavior changes in this package branch: none intended.
- Device behavior changes before manual flashing: none.
- Manual hardware test result: not yet performed.

## 2. Target Runtime Branch And Commit

Record these fields before any manual hardware action.

| Field | Value |
| --- | --- |
| Runtime branch | `glyph/ultimate-tilt-hardware-test-package` |
| Commit SHA | `TODO: record exact commit SHA` |
| Build command | `./scripts/build-glyph-mk6-quiet.sh` |
| Build result | `TODO: PASS / FAIL / BLOCKED` |

## 3. Artifact Identity

Build the local firmware artifact:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

Inspect likely local `glyph_mk6` build artifacts and checksums:

```bash
.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py
```

Record the artifact identity before any manual flash:

| Field | Value |
| --- | --- |
| Artifact path | `TODO` |
| Size bytes | `TODO` |
| SHA-256 | `TODO` |

Generate and validate the RC manifest for this candidate:

```bash
.venv/bin/python tools/write_glyph_ultimate_tilt_rc_manifest.py --output docs/calibration/glyph_ultimate_tilt_rc_manifest.md
.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py
```

RC manifest reference:

- `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`
- `tools/write_glyph_ultimate_tilt_rc_manifest.py`
- `tools/check_glyph_ultimate_tilt_rc_manifest.py`
- `docs/calibration/glyph_ultimate_tilt_rc_manifest_provenance_2026-05-24.md`

## 4. Required Pre-Flash Checks

- Python checks listed in the hardware-test branch handoff have passed.
- Runtime source check passed:

```bash
.venv/bin/python tools/check_glyph_ultimate_tilt_runtime_source.py
```

- Firmware build passed:

```bash
./scripts/build-glyph-mk6-quiet.sh
```

- Artifact path, size, and SHA-256 were recorded from:

```bash
.venv/bin/python tools/inspect_glyph_mk6_build_artifact.py
```

- RC manifest generated and validated:

```bash
.venv/bin/python tools/write_glyph_ultimate_tilt_rc_manifest.py --output docs/calibration/glyph_ultimate_tilt_rc_manifest.md
.venv/bin/python tools/check_glyph_ultimate_tilt_rc_manifest.py
```

- RC manifest reports:
  - `firmware_relevant_dirty_state: CLEAN`
  - `git_dirty_state` may still be `DIRTY` when dirty entries are docs/tools-only.
- Known-good rollback firmware is available.
- Known-good rollback profile/config is available.
- Hardware owner has approved the manual flash workflow.

## 5. Manual Flash Placeholder

This package does not automate flashing.

Manual flashing must be performed only by the hardware owner using their approved workflow. Do not add scripts, background services, automatic device discovery, or push-to-device behavior as part of this package.

## 6. Smoke-Test Checklist

Record PASS, FAIL, BLOCKED, or N/A for each row.

| Check | Result | Notes |
| --- | --- | --- |
| Board boots | `TODO` |  |
| Device enumerates | `TODO` |  |
| Baseline buttons still work | `TODO` |  |
| SOCD directions unaffected | `TODO` |  |
| Remapping behavior unchanged | `TODO` |  |
| C-stick/right-stick unchanged | `TODO` |  |
| Triggers unchanged | `TODO` |  |
| Nunchuk behavior, if available, unchanged | `TODO` |  |
| Tilt1 LT1 direction 1 produces `(187, 87)` | `TODO` |  |
| Tilt1 LT1 direction 2 produces `(128, 87)` | `TODO` |  |
| Tilt1 LT1 direction 3 produces `(69, 87)` | `TODO` |  |
| Tilt1 LT1 direction 4 produces `(187, 128)` | `TODO` |  |
| Tilt1 LT1 direction 5 produces `(128, 128)` | `TODO` |  |
| Tilt1 LT1 direction 6 produces `(69, 128)` | `TODO` |  |
| Tilt1 LT1 direction 7 produces `(187, 169)` | `TODO` |  |
| Tilt1 LT1 direction 8 produces `(128, 169)` | `TODO` |  |
| Tilt1 LT1 direction 9 produces `(69, 169)` | `TODO` |  |
| Tilt2 LT2 direction 1 produces `(88, 79)` | `TODO` |  |
| Tilt2 LT2 direction 2 produces `(128, 79)` | `TODO` |  |
| Tilt2 LT2 direction 3 produces `(168, 79)` | `TODO` |  |
| Tilt2 LT2 direction 4 produces `(88, 128)` | `TODO` |  |
| Tilt2 LT2 direction 5 produces `(128, 128)` | `TODO` |  |
| Tilt2 LT2 direction 6 produces `(168, 128)` | `TODO` |  |
| Tilt2 LT2 direction 7 produces `(88, 177)` | `TODO` |  |
| Tilt2 LT2 direction 8 produces `(128, 177)` | `TODO` |  |
| Tilt2 LT2 direction 9 produces `(168, 177)` | `TODO` |  |
| Both LT1+LT2 does not apply new Tilt override | `TODO` |  |

## 7. Result Recording

| Field | Value |
| --- | --- |
| Overall result | `TODO: PASS / FAIL / BLOCKED` |
| Observed failures | `TODO` |
| Rollback needed | `TODO: yes / no` |
| Rollback result | `TODO` |
| Notes | `TODO` |
