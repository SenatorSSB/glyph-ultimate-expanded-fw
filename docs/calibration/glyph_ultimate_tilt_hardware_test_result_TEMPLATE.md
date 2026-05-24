# Glyph Ultimate Tilt Hardware Test Result Template

Do not fill this template until a human-controlled hardware test is performed.

## Test Identity

| Field | Value |
| --- | --- |
| Tester |  |
| Date |  |
| Hardware |  |
| Branch |  |
| Commit SHA |  |
| RC manifest path | `docs/calibration/glyph_ultimate_tilt_rc_manifest.md` |
| Artifact path |  |
| Artifact SHA-256 |  |
| Profile/config used |  |

## Pre-Flash Checks

| Check | Result | Notes |
| --- | --- | --- |
| Python checks passed |  |  |
| Runtime source check passed |  |  |
| Firmware build passed |  |  |
| Artifact path recorded |  |  |
| Artifact SHA-256 recorded |  |  |
| RC manifest generated |  |  |
| RC manifest checker passed |  |  |
| Worktree clean |  |  |
| Known-good rollback firmware available |  |  |
| Known-good rollback profile/config available |  |  |
| Hardware owner approved manual flash workflow |  |  |

## Smoke-Test Rows

| Check | Result | Notes |
| --- | --- | --- |
| Board boots |  |  |
| Device enumerates |  |  |
| Baseline buttons still work |  |  |
| SOCD directions unaffected |  |  |
| Remapping behavior unchanged |  |  |
| C-stick/right-stick unchanged |  |  |
| Triggers unchanged |  |  |
| Nunchuk behavior, if available, unchanged |  |  |
| Tilt1 LT1 direction 1 produces expected table value |  |  |
| Tilt1 LT1 direction 2 produces expected table value |  |  |
| Tilt1 LT1 direction 3 produces expected table value |  |  |
| Tilt1 LT1 direction 4 produces expected table value |  |  |
| Tilt1 LT1 direction 5 produces expected table value |  |  |
| Tilt1 LT1 direction 6 produces expected table value |  |  |
| Tilt1 LT1 direction 7 produces expected table value |  |  |
| Tilt1 LT1 direction 8 produces expected table value |  |  |
| Tilt1 LT1 direction 9 produces expected table value |  |  |
| Tilt2 LT2 direction 1 produces expected table value |  |  |
| Tilt2 LT2 direction 2 produces expected table value |  |  |
| Tilt2 LT2 direction 3 produces expected table value |  |  |
| Tilt2 LT2 direction 4 produces expected table value |  |  |
| Tilt2 LT2 direction 5 produces expected table value |  |  |
| Tilt2 LT2 direction 6 produces expected table value |  |  |
| Tilt2 LT2 direction 7 produces expected table value |  |  |
| Tilt2 LT2 direction 8 produces expected table value |  |  |
| Tilt2 LT2 direction 9 produces expected table value |  |  |
| Both LT1+LT2 does not apply new Tilt override |  |  |

## Failures

| Field | Value |
| --- | --- |
| Observed failures |  |
| Failure reproduction notes |  |
| Suspected scope |  |

## Rollback Status

| Field | Value |
| --- | --- |
| Rollback needed |  |
| Rollback firmware restored |  |
| Rollback profile/config restored |  |
| Rollback notes |  |

## Final Disposition

Select exactly one:

- PASS
- FAIL_ROLLBACK
- BLOCKED_NOT_FLASHED
- NEEDS_FIRMWARE_FIX
