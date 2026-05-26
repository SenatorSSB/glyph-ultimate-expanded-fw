# Glyph Ultimate Tilt Hardware Test Result

## Test Identity

| Field | Value |
| --- | --- |
| Tester | User-provided manual hardware smoke test evidence; tester name not separately provided |
| Date | Recorded 2026-05-26; exact manual test date not separately provided |
| Hardware | Glyph MK6 target controller; exact unit identifier not separately provided |
| Branch | configurator |
| Commit SHA | 919b0306977fda6348addc89881a8ef12adf0142 |
| RC manifest path | `docs/calibration/glyph_ultimate_tilt_rc_manifest.md` |
| Prehardware readiness index path | `docs/calibration/glyph_ultimate_tilt_prehardware_readiness_index_2026-05-24.md` |
| Artifact path | `.pio/build/glyph_mk6/firmware.uf2` |
| Artifact SHA-256 | a828b38c8f4ef4b25a540ce222848725d885585c973d1a36652fb4caac8dbd0c |
| Profile/config used | Ultimate profile first in profile list; no Melee profile present; profiles appeared preserved but were not exhaustively verified |

## Pre-Flash Checks

| Check | Result | Notes |
| --- | --- | --- |
| Python checks passed | PASS | Prehardware verification requested for this result record. |
| Runtime source check passed | PASS | Native Ultimate Tilt/Tilt2 runtime source checker was part of the prehardware aggregate. |
| Firmware build passed | PASS | PlatformIO Core 6.1.19; flashed artifact was `.pio/build/glyph_mk6/firmware.uf2`. |
| Artifact path recorded | PASS | `.pio/build/glyph_mk6/firmware.uf2`. |
| Artifact SHA-256 recorded | PASS | `a828b38c8f4ef4b25a540ce222848725d885585c973d1a36652fb4caac8dbd0c`. |
| RC manifest generated | PASS | Existing RC manifest path: `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`. |
| RC manifest checker passed | PASS | Existing checker-compatible RC manifest remains prehardware-scoped. |
| Prehardware aggregator passed (`tools/run_glyph_ultimate_tilt_prehardware_checks.py`) | PASS | Baseline aggregate and build/artifact/result aggregate requested for verification. |
| Worktree clean | PASS | RC manifest recorded clean prehardware state for the tested source commit. |
| Known-good rollback firmware available | NOT_TESTED | Rollback availability was not separately provided in the hardware evidence. |
| Known-good rollback profile/config available | NOT_TESTED | Rollback profile/config availability was not separately provided in the hardware evidence. |
| Hardware owner approved manual flash workflow | PASS | Manual UF2 bootloader flow was performed by the tester. |

## Flash Method

Manual UF2 bootloader flow through RPI-RP2. RPI-RP2 entry method was holding the illuminated Menu button while connecting to Mac. Firmware was copied by Finder drag-and-drop. RPI-RP2 disappeared/ejected after copy and the controller reconnected.

macOS showed a warning about RPI-RP2 not ejecting properly after UF2 copy, but the device reconnected normally.

## Coordinate Convention

Glyph mini-screen reports center-relative offsets.

Absolute raw coordinate conversion:

```text
raw_x = 128 + offset_x
raw_y = 128 + offset_y
```

## Smoke-Test Rows

| Check | Result | Notes |
| --- | --- | --- |
| Board boots | PASS | Controller reconnected normally after UF2 copy. |
| Device enumerates | PASS | Controller reconnected after RPI-RP2 disappeared/ejected. |
| Baseline buttons still work | PASS_SMOKE | All other tested buttons functioned as expected in Ultimate. |
| SOCD directions unaffected | NOT_EXHAUSTIVELY_TESTED | No-modifier baseline directions matched expected offsets; no exhaustive SOCD matrix was reported. |
| Remapping behavior unchanged | NOT_EXHAUSTIVELY_TESTED | Profiles appeared preserved, but this was not exhaustively verified. |
| C-stick/right-stick unchanged | NOT_EXHAUSTIVELY_TESTED | No separate exhaustive C-stick/right-stick report was provided. |
| Triggers unchanged | NOT_EXHAUSTIVELY_TESTED | No separate exhaustive trigger report was provided. |
| Nunchuk behavior, if available, unchanged | NOT_TESTED | No nunchuk evidence was provided. |
| Tilt1 LT1 direction 1 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 2 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 3 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 4 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 5 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 6 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 7 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 8 produces expected table value | PASS | Physical RF3 / logical Tilt1 matched expected Tilt1 offset. |
| Tilt1 LT1 direction 9 produces expected table value | PASS | Physical RF3 / logical Tilt1 up-right observed offset `(-59, 41)`, raw `(69, 169)`. |
| Tilt2 LT2 direction 1 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 2 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 3 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 4 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 5 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 6 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 7 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 8 produces expected table value | PASS | Physical RF4 / logical Tilt2 matched expected Tilt2 offset. |
| Tilt2 LT2 direction 9 produces expected table value | PASS | Physical RF4 / logical Tilt2 up-right observed offset `(40, 49)`, raw `(168, 177)`. |
| Both LT1+LT2 does not apply new Tilt override | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | Senscope Tilt override branch should not apply when both Tilt inputs are active. Stable existing combined-behavior offsets were observed for directions 1, 2, 3, 4, 5, 6, 7, and 9; direction 8 was not separately provided and is recorded as NOT_TESTED below. |

## No-Modifier Baseline

All tested directions matched expected baseline offsets.

## Both-Held LT1+LT2 Observations

No exact expected table was required for both-held Tilt1+Tilt2. This smoke result records observed stable existing combined behavior, not a new expected-table assertion.

| Direction | Result | Observed offset |
| --- | --- | --- |
| 1 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(-35, -53)` |
| 2 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(0, -53)` |
| 3 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(35, -53)` |
| 4 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(-41, 0)` |
| 5 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(0, 0)` |
| 6 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(41, 0)` |
| 7 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(-35, 53)` |
| 8 | NOT_TESTED | Direction 8 was not separately provided. |
| 9 | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR | `(35, 53)` |

## RF5 Negative Check

| Field | Value |
| --- | --- |
| Result | NOT_TESTED_AMBIGUOUS |
| Notes | Tester was not certain which physical button corresponded to RF5. The tested top-row right-most right-side button behaved identically with Tilt2/LT2, and combining it with Tilt2 did not change Tilt2, Tilt1, or Tilt1+Tilt2 offsets. This is not recorded as definitive RF5-negative verification. |

## Switch/Ultimate Behavior

Plugging the controller into Nintendo Switch visualized and Ultimate actualized modifier output results exactly as the observed mini-screen coordinate offsets. All other tested buttons functioned as expected in Ultimate.

## Failures

| Field | Value |
| --- | --- |
| Observed failures | none |
| Failure reproduction notes | none |
| Suspected scope | none |

## Rollback Status

| Field | Value |
| --- | --- |
| Rollback needed | no |
| Rollback firmware restored | not applicable |
| Rollback profile/config restored | not applicable |
| Rollback notes | Final disposition was PASS; rollback was not needed. |

## Caveats

- RF5 physical identity was ambiguous, so RF5 negative check is not source-confirmed.
- Tilt1+Tilt2 direction 8 was not separately provided and is recorded as NOT_TESTED.
- macOS RPI-RP2 disconnect/eject warning occurred after UF2 copy, but the device reconnected normally.
- Profiles appeared preserved, but profile preservation was not exhaustively verified.

## Final Disposition

- [x] PASS
- [ ] FAIL_ROLLBACK
- [ ] BLOCKED_NOT_FLASHED
- [ ] NEEDS_FIRMWARE_FIX
