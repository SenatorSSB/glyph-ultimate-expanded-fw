# Glyph Ultimate Preservation Hardware Result

## 1. Test Identity And Setup

| Field | Value |
| --- | --- |
| Tester | User-provided manual hardware smoke evidence; tester identity not separately recorded |
| Test date (YYYY-MM-DD) | 2026-05-27 |
| Branch tested | configurator (inferred from current workflow context; exact tested ref not separately recorded) |
| Commit SHA tested | UNKNOWN_NOT_RECORDED |
| Firmware artifact path | UNKNOWN_NOT_RECORDED |
| Firmware artifact hash (SHA-256) | UNKNOWN_NOT_RECORDED |
| Profile/config used | Ultimate profile context; exact profile/config snapshot not separately recorded |
| Controller model / hardware ID | Glyph MK6 target controller; exact unit identifier not separately recorded |
| Flash method | UNKNOWN_NOT_RECORDED |
| Glyph mini-screen offsets used (yes/no) | UNKNOWN_NOT_RECORDED |
| Switch controller visualization used (yes/no) | UNKNOWN_NOT_RECORDED |
| Ultimate Training Mode used (yes/no) | UNKNOWN_NOT_RECORDED |

## 2. Baseline No-Modifier Checks

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| BNM-01 | No-modifier direction 1 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-02 | No-modifier direction 2 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-03 | No-modifier direction 3 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-04 | No-modifier direction 4 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-05 | No-modifier direction 5 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-06 | No-modifier direction 6 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-07 | No-modifier direction 7 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-08 | No-modifier direction 8 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-09 | No-modifier direction 9 | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-10 | Basic movement sanity | NOT_TESTED | Not separately reported in current smoke observation. |
| BNM-11 | No stuck inputs | PASS_SMOKE_USER_REPORTED | Broader smoke note says tested buttons worked as expected; no stuck condition was reported in tested scope. |

## 3. Existing Tilt/Tilt2 Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| TLT-01 | Tilt1 spot-check or full table | PASS_MATCHED_PREVIOUS_RESULT | User observation states all Tilt1 directions 1..9 remained the same as previous recorded result. |
| TLT-02 | Tilt2 spot-check or full table | PASS_MATCHED_PREVIOUS_RESULT | User observation states all Tilt2 directions 1..9 remained the same as previous recorded result. |
| TLT-03 | Both-held Tilt1+Tilt2 existing combined behavior | PASS_SMOKE_OBSERVED_EXISTING_COMBINED_BEHAVIOR_MATCHED_PREVIOUS_RESULT | Both-held directions 1..9 matched prior observed combined behavior. This remains observed-only and non-contractual. |

## 4. C-Stick/Right-Stick Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| CST-01 | Neutral | NOT_TESTED | No explicit C-stick/right-stick smoke evidence provided in current notes. |
| CST-02 | Cardinal directions | NOT_TESTED | No explicit C-stick/right-stick smoke evidence provided in current notes. |
| CST-03 | Diagonals (if practical) | NOT_TESTED | No explicit C-stick/right-stick smoke evidence provided in current notes. |
| CST-04 | D-pad/right-stick interaction path | NOT_TESTED | No explicit C-stick/right-stick smoke evidence provided in current notes. |

## 5. Trigger Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| TRG-01 | L/R/Z or profile-relevant trigger buttons | NOT_TESTED | Current notes report broad button smoke behavior but do not enumerate trigger-specific observations. |
| TRG-02 | Analog trigger observation (if available) | NOT_TESTED | No analog trigger observation provided. |
| TRG-03 | Digital trigger behavior (if visible) | NOT_TESTED | No trigger-specific digital behavior observation provided. |

## 6. SOCD/Opposite Direction Behavior

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| SCD-01 | Left + Right | NOT_TESTED | No explicit SOCD smoke evidence provided in current notes. |
| SCD-02 | Up + Down | NOT_TESTED | No explicit SOCD smoke evidence provided in current notes. |
| SCD-03 | Left + Right with Tilt1 | NOT_TESTED | No explicit SOCD smoke evidence provided in current notes. |
| SCD-04 | Left + Right with Tilt2 | NOT_TESTED | No explicit SOCD smoke evidence provided in current notes. |
| SCD-05 | Up + Down with Tilt1 | NOT_TESTED | No explicit SOCD smoke evidence provided in current notes. |
| SCD-06 | Up + Down with Tilt2 | NOT_TESTED | No explicit SOCD smoke evidence provided in current notes. |

## 7. RF5 Physical Identity / Negative Check

RF5 location used for this test:
- center-right / RF cluster, far-right upper button = RF5

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| RF5-01 | RF5 alone with neutral and selected directions | NOT_TESTED_AMBIGUOUS | RF5 was not explicitly retested in this smoke record using the now-known RF5 physical location. |
| RF5-02 | RF5 + Tilt1 | NOT_TESTED_AMBIGUOUS | RF5 was not explicitly retested in this smoke record using the now-known RF5 physical location. |
| RF5-03 | RF5 + Tilt2 | NOT_TESTED_AMBIGUOUS | RF5 was not explicitly retested in this smoke record using the now-known RF5 physical location. |
| RF5-04 | RF5 + Tilt1+Tilt2 (if safe/practical) | NOT_TESTED_AMBIGUOUS | RF5 was not explicitly retested in this smoke record using the now-known RF5 physical location. |

Expected interpretation notes:
- RF5-specific behavior is observed and recorded only when explicitly tested.
- RF5 should not be classified as Tilt1/Tilt2 unless the loaded profile maps it that way.
- This result does not overwrite previous historical RF5 ambiguity notes.

## 8. Profile Preservation / Readback

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| PRF-01 | Profile list appears as expected | NOT_TESTED | Not explicitly retested in current smoke notes. |
| PRF-02 | Default profile behavior | NOT_TESTED | Not explicitly retested in current smoke notes. |
| PRF-03 | Ultimate profile selected/default as applicable | NOT_TESTED | Not explicitly retested in current smoke notes. |
| PRF-04 | Configurator readback (if possible) matches expected profile/config | NOT_TESTED | Not explicitly retested in current smoke notes. |

## 9. Optional Nunchuk

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| NCK-01 | Nunchuk availability check | NOT_TESTED_UNAVAILABLE | Hardware unavailable for this smoke scope; nunchuk not supported out of the box for current setup. |
| NCK-02 | If tested, nunchuk behavior remains source-consistent | NOT_TESTED_UNAVAILABLE | Not executed because nunchuk hardware is unavailable in this test scope. |

## 10. Basic Button Regression

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`PASS_SMOKE_OBSERVED`) | Observation Notes |
| --- | --- | --- | --- |
| BTN-01 | A/B/jump/shield/grab equivalents as mapped in current profile | PASS_SMOKE_USER_REPORTED | User-reported broader smoke: other tested buttons worked as expected; no exhaustive per-button matrix provided. |
| BTN-02 | Menu buttons (if relevant) | NOT_TESTED | Current notes do not enumerate menu-button-specific checks. |
| BTN-03 | No stuck state | PASS_SMOKE_USER_REPORTED | User-reported broader smoke: tested buttons behaved as expected. |
| BTN-04 | No crash/reboot during test | PASS_SMOKE_USER_REPORTED | No crash/reboot was reported in the current smoke notes. |

## 11. Result Disposition

Select one final disposition:
- [x] PASS
- [ ] FAIL_ROLLBACK
- [ ] BLOCKED_NOT_TESTED
- [ ] NEEDS_FIRMWARE_FIX

final_disposition: PASS

## Notes And Anomalies

- Hardware observation sources used:
  - "Ran hardware checks. All results are the same as previously. All of them. All directions. Tilt1, Tilt2, Tilt1+Tilt2."
  - "I tested other buttons, too, all seemed to work as expected. We can treat it as working (we are not testing nunchuck, don't have the hardware for it, not supported out of the box)."
- PASS disposition applies to the tested smoke scope only and does not claim exhaustive preservation across all categories in this template.
- Smoke-level only (not exhaustive in this record): baseline no-modifier direction matrix, C-stick/right-stick, trigger-specific behavior, SOCD matrix, profile/readback verification, menu-button-specific checks.
- Both-held Tilt1+Tilt2 behavior remains observed-only/non-contractual and is not promoted to a production table contract here.
