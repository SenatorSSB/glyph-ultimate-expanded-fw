# Glyph Ultimate Preservation Hardware Result TEMPLATE

Status: TEMPLATE_ONLY

Warning: do not fabricate hardware results. This template is not hardware evidence until a human runs and records a real manual test session.

## 1. Test Identity And Setup

| Field | Value |
| --- | --- |
| Tester | |
| Test date (YYYY-MM-DD) | |
| Branch tested | |
| Commit SHA tested | |
| Firmware artifact path | |
| Firmware artifact hash (SHA-256) | |
| Profile/config used | |
| Controller model / hardware ID | |
| Flash method | |
| Glyph mini-screen offsets used (yes/no) | |
| Switch controller visualization used (yes/no) | |
| Ultimate Training Mode used (yes/no) | |

## 2. Baseline No-Modifier Checks

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| BNM-01 | No-modifier direction 1 | NOT_TESTED | |
| BNM-02 | No-modifier direction 2 | NOT_TESTED | |
| BNM-03 | No-modifier direction 3 | NOT_TESTED | |
| BNM-04 | No-modifier direction 4 | NOT_TESTED | |
| BNM-05 | No-modifier direction 5 | NOT_TESTED | |
| BNM-06 | No-modifier direction 6 | NOT_TESTED | |
| BNM-07 | No-modifier direction 7 | NOT_TESTED | |
| BNM-08 | No-modifier direction 8 | NOT_TESTED | |
| BNM-09 | No-modifier direction 9 | NOT_TESTED | |
| BNM-10 | Basic movement sanity | NOT_TESTED | |
| BNM-11 | No stuck inputs | NOT_TESTED | |

## 3. Existing Tilt/Tilt2 Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| TLT-01 | Tilt1 spot-check or full table | NOT_TESTED | |
| TLT-02 | Tilt2 spot-check or full table | NOT_TESTED | |
| TLT-03 | Both-held Tilt1+Tilt2 existing combined behavior | NOT_TESTED | Record observed existing behavior only; not a new table guarantee. |

## 4. C-Stick/Right-Stick Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| CST-01 | Neutral | NOT_TESTED | |
| CST-02 | Cardinal directions | NOT_TESTED | |
| CST-03 | Diagonals (if practical) | NOT_TESTED | |
| CST-04 | D-pad/right-stick interaction path | NOT_TESTED | |

## 5. Trigger Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| TRG-01 | L/R/Z or profile-relevant trigger buttons | NOT_TESTED | |
| TRG-02 | Analog trigger observation (if available) | NOT_TESTED | |
| TRG-03 | Digital trigger behavior (if visible) | NOT_TESTED | |

## 6. SOCD/Opposite Direction Behavior

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| SCD-01 | Left + Right | NOT_TESTED | |
| SCD-02 | Up + Down | NOT_TESTED | |
| SCD-03 | Left + Right with Tilt1 | NOT_TESTED | |
| SCD-04 | Left + Right with Tilt2 | NOT_TESTED | |
| SCD-05 | Up + Down with Tilt1 | NOT_TESTED | |
| SCD-06 | Up + Down with Tilt2 | NOT_TESTED | |

## 7. RF5 Physical Identity / Negative Check

RF5 location used for this test:
- center-right / RF cluster, far-right upper button = RF5

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| RF5-01 | RF5 alone with neutral and selected directions | NOT_TESTED | |
| RF5-02 | RF5 + Tilt1 | NOT_TESTED | |
| RF5-03 | RF5 + Tilt2 | NOT_TESTED | |
| RF5-04 | RF5 + Tilt1+Tilt2 (if safe/practical) | NOT_TESTED | |

Expected interpretation notes:
- RF5-specific behavior is observed and recorded.
- RF5 should not be classified as Tilt1/Tilt2 unless the loaded profile maps it that way.
- This does not overwrite previous historical RF5 ambiguity notes.

## 8. Profile Preservation / Readback

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| PRF-01 | Profile list appears as expected | NOT_TESTED | |
| PRF-02 | Default profile behavior | NOT_TESTED | |
| PRF-03 | Ultimate profile selected/default as applicable | NOT_TESTED | |
| PRF-04 | Configurator readback (if possible) matches expected profile/config | NOT_TESTED | |

## 9. Optional Nunchuk

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| NCK-01 | Nunchuk availability check | NOT_TESTED | If unavailable, keep NOT_TESTED. |
| NCK-02 | If tested, nunchuk behavior remains source-consistent | NOT_TESTED | |

## 10. Basic Button Regression

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| BTN-01 | A/B/jump/shield/grab equivalents as mapped in current profile | NOT_TESTED | |
| BTN-02 | Menu buttons (if relevant) | NOT_TESTED | |
| BTN-03 | No stuck state | NOT_TESTED | |
| BTN-04 | No crash/reboot during test | NOT_TESTED | |

## 11. Result Disposition

Select one final disposition:
- [ ] PASS
- [ ] FAIL_ROLLBACK
- [ ] BLOCKED_NOT_TESTED
- [ ] NEEDS_FIRMWARE_FIX

final_disposition:

## Notes And Anomalies

- None recorded.
