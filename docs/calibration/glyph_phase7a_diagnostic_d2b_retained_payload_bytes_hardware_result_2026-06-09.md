# Glyph Phase 7A Diagnostic D2B Hardware Result - 2026-06-09

status: USER_REPORTED_PASS

## Purpose and scope

This document records the user-reported hardware result for Phase 7A diagnostic
D2B retained-payload testing. It is scoped to the retained-payload-bytes
hypothesis only and does not prove a root cause, parser safety, resolver
safety, public release compatibility, or any nunchuk behavior.

## Branch and result

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Diagnostic branch tested: `phase7a-diagnostic-d2b-retained-payload-bytes`
- Result branch: `phase7a-diagnostic-d2b-retained-payload-bytes-hardware-result`
- Result source: user-reported
- Exact user report text: `tested, everything works. Especially RF5-6 do not cause a disconnect.`
- Result date: `2026-06-09`
- Commit SHA under test: `bc0525dba8ecbdc62251a3b9d4bb2fc54a9a1a35`
- Build command: `./scripts/build-glyph-mk6-quiet.sh`
- Build report reference:
  `docs/runtime_config/phase7a_diagnostic_d2b_retained_payload_bytes_build_report_2026-06-09.md`
- Result fixture:
  `docs/calibration/fixtures/glyph_phase7a_diagnostic_d2b_retained_payload_bytes_hardware_result_2026-06-09.json`

## Hardware result summary

The reported hardware scope passed for the retained-payload test branch:

- BOOT-001: PASS
- BASELINE-001: PASS
- RF5-001: PASS, no disconnect observed
- RF6-001: PASS, no disconnect observed
- ORDINARY-DIR-001: PASS, ordinary controls covered by the user report
- NUNCHUK-001: NOT_TESTED

## Hardware result table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after build reaches expected boot state | PASS | User-reported pass. |
| BASELINE-001 | baseline | Baseline behavior preserved | PASS | User-reported pass. |
| RF5-001 | rf5_paths | Representative RF5 behaviors remain preserved | PASS | No disconnect observed. |
| RF6-001 | rf6_paths | Representative RF6 behaviors remain preserved | PASS | No disconnect observed. |
| ORDINARY-DIR-001 | directions | Ordinary direction behavior remains preserved | PASS | Covered by "everything works". |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | No nunchuk validation claim. |

## Source/build checks retained

The following claims remain source/build-checked, not hardware-observed:

- no parser call claim remains source/build-checked, not hardware-observed
- no resolver claim remains source/build-checked, not hardware-observed
- no storage/write/flashing claim remains source/build-checked, not hardware-observed

## Diagnostic interpretation

- Retained payload bytes alone did not reproduce the RF5/RF6 disconnect.
- H2 static payload/rodata-only hypothesis is reduced in likelihood.
- H1 global/static parser initialization remains open.
- H3 runtime resolver/reference path remains open.
- H4 parser loop/static-init remains open.
- H5 RF5/RF6 path interaction remains open only in combination with parser/resolver changes.
- H6 latent/unrelated interaction remains open.
- Failed activation branch remains abandoned and must not merge.

## Limitations and non-claims

- result is user-reported
- no automated device telemetry
- no nunchuk validation
- no public release claim
- no release compatibility claim
- no proof of root cause
- no parser safety proven
- no resolver safety proven

