# Glyph Ultimate Preservation Hardware Result - 2026-06-06

Status: USER_REPORTED_RESULT

This records a user-reported preservation hardware pass for the current
`configurator` firmware artifact.

User report:
- "works as expected"
- "All modifiers, all functionalities, all directions."

Scope notes:
- Applicable non-nunchuk preservation rows are recorded as PASS.
- Nunchuk remains NOT_TESTED / unvalidated / unavailable because the controller
  has no nunchuk port available out of the box.
- No external remapper adapter output, runtime-loaded config, WebSerial/device
  write, or active profile artifact change is claimed by this result.
- No exact measured outputs are claimed beyond the user report.

## 1. Test Identity And Setup

| Field | Value |
| --- | --- |
| Tester | Rasmus (user-reported) |
| Test date (YYYY-MM-DD) | 2026-06-06 |
| Branch tested | configurator |
| Commit SHA tested | UNKNOWN_NOT_PROVIDED |
| Firmware artifact created at | 2026-06-06 03:24:23 +0300 (local artifact mtime; user report gave 03:24 local time) |
| Firmware artifact path | `.pio/build/glyph_mk6/firmware.bin` |
| Firmware artifact hash (SHA-256) | `24f73bdff416bb7aa6ecd1d1147723dfcbd37edbd5a16664299453159e8c93ee` |
| Profile/config used | Current tested profile per user report; exact artifact not recorded from user report |
| Controller model / hardware ID | Glyph MK6; hardware ID not separately recorded |
| Flash method | UNKNOWN_NOT_PROVIDED |
| Glyph mini-screen offsets used (yes/no) | not recorded from user report |
| Switch controller visualization used (yes/no) | not recorded from user report |
| Ultimate Training Mode used (yes/no) | not recorded from user report |
| Observation method | User playtesting / actual use |
| Overall user report | "works as expected"; "All modifiers, all functionalities, all directions" |

Allowed row statuses:

- `PASS`
- `FAIL`
- `NOT_TESTED`
- `BLOCKED`
- `USER_ACCEPTED_RISK`

Rows marked `NOT_TESTED` are not validated. Do not infer them from related
rows. `USER_ACCEPTED_RISK` requires a note that identifies the risk and the
user report source.

## 2. Baseline No-Modifier Checks

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| BNM-01 | No-modifier direction 1 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-02 | No-modifier direction 2 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-03 | No-modifier direction 3 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-04 | No-modifier direction 4 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-05 | No-modifier direction 5 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-06 | No-modifier direction 6 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-07 | No-modifier direction 7 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-08 | No-modifier direction 8 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-09 | No-modifier direction 9 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-10 | Basic movement sanity | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BNM-11 | No stuck inputs | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

## 3. Existing Tilt/Tilt2 Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| TLT-01 | Tilt1 spot-check or full table | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| TLT-02 | Tilt2 spot-check or full table | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| TLT-03 | Both-held Tilt1+Tilt2 existing combined behavior | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

## 4. C-Stick/Right-Stick Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| CST-01 | Neutral | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| CST-02 | Cardinal directions | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| CST-03 | Diagonals (if practical) | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| CST-04 | D-pad/right-stick interaction path | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

## 5. Trigger Preservation

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| TRG-01 | L/R/Z or profile-relevant trigger buttons | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| TRG-02 | Analog trigger observation (if available) | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| TRG-03 | Digital trigger behavior (if visible) | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

## 6. SOCD/Opposite Direction Behavior

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| SCD-01 | Left + Right | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| SCD-02 | Up + Down | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| SCD-03 | Left + Right with Tilt1 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| SCD-04 | Left + Right with Tilt2 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| SCD-05 | Up + Down with Tilt1 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| SCD-06 | Up + Down with Tilt2 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

## 7. RF5 Physical Identity / Negative Check

RF5 location used for this test:
- center-right / RF cluster, far-right upper button = RF5

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| RF5-01 | RF5 alone with neutral and selected directions | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| RF5-02 | RF5 + Tilt1 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| RF5-03 | RF5 + Tilt2 | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| RF5-04 | RF5 + Tilt1+Tilt2 (if safe/practical) | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

Expected interpretation notes:
- RF5-specific behavior is observed and recorded.
- RF5 should not be classified as Tilt1/Tilt2 unless the loaded profile maps it that way.
- This does not overwrite previous historical RF5 ambiguity notes.

## 8. Profile Preservation / Readback

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| PRF-01 | Profile list appears as expected | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| PRF-02 | Default profile behavior | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| PRF-03 | Ultimate profile selected/default as applicable | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| PRF-04 | Configurator readback (if possible) matches expected profile/config | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

## 9. Optional Nunchuk

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| NCK-01 | Nunchuk availability check | NOT_TESTED | Controller has no nunchuk port available out of the box; user did not test nunchuk; no nunchuk validation claimed. |
| NCK-02 | If tested, nunchuk behavior remains source-consistent | NOT_TESTED | Controller has no nunchuk port available out of the box; user did not test nunchuk; no nunchuk validation claimed. |

## 10. Basic Button Regression

| Row | Test | Result (`PASS`/`FAIL`/`NOT_TESTED`/`BLOCKED`/`USER_ACCEPTED_RISK`) | Observation Notes |
| --- | --- | --- | --- |
| BTN-01 | A/B/jump/shield/grab equivalents as mapped in current profile | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BTN-02 | Menu buttons (if relevant) | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BTN-03 | No stuck state | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |
| BTN-04 | No crash/reboot during test | PASS | User reported all applicable modifiers/functionality/directions working as expected; no row-specific measured output claimed. |

## 11. Result Disposition

Select one final disposition:
- [x] PASS
- [ ] FAIL
- [ ] BLOCKED
- [ ] USER_ACCEPTED_RISK

final_disposition: `PASS`

## Notes And Anomalies

- Nunchuk remains NOT_TESTED / unvalidated / unavailable because the controller
  has no nunchuk port available out of the box.
- No external remapper adapter output, runtime-loaded config, WebSerial/device
  write, or active profile artifact change is claimed by this result.
- No exact measured outputs are claimed beyond the user report.
- Failure, blocked, or user-accepted-risk rows would require notes; none are
  present here.

## Required result-recording caveats

- No nunchuk hardware validation is claimed unless nunchuk rows are executed and
  recorded.
- No external remapper adapter, runtime-loaded config, WebSerial write, or
  device write behavior is claimed by this result.
- No active profile artifact change is claimed by this result.
- Failure, blocked, or user-accepted-risk rows require notes.
- Rollback notes are required if a failure indicates rollback is needed.
