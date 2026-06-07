# Glyph Generated Constants Phase 3 Integration Hardware Result - 2026-06-07

## Purpose and scope

This document records the user-reported hardware result for the Phase 3
generated constants firmware-integration branch
`phase3-generated-constants-firmware-integration`.

This result is scoped to applicable non-nunchuk planned hardware checks only.
It does not validate nunchuk hardware behavior, runtime-loaded config,
WebSerial/device write, protobuf binary write, firmware flashing automation,
universal official configurator compatibility, or any intentional firmware
behavior change claim.

## Branch and implementation under test

- Repository: `SenatorSSB/glyph-ultimate-expanded-fw`
- Branch under test: `phase3-generated-constants-firmware-integration`
- Result branch: `phase3-generated-constants-hardware-result`
- Result status: `USER_REPORTED_PASS`
- Result source: user-reported
- Exact user report text: `all test doable work as expected`
- Result date: 2026-06-07
- Commit SHA under test: `76e4f6c234b88a12ba311f2c8076fa3303ffd711`
- Build command used: `./scripts/build-glyph-mk6-quiet.sh`
- Firmware artifact path: unknown
- Firmware artifact SHA-256: unknown
- Tester/source: user-reported
- Result fixture:
  `docs/calibration/fixtures/glyph_generated_constants_phase3_integration_hardware_result_2026-06-07.json`

## Source authority

The hardware result record is based on the user-reported branch result text and
the branch-scoped Phase 3 generated constants hardware plan. Unknown hardware
artifact details remain unknown.

## Result summary

All applicable doable planned checks are recorded as `PASS`. Nunchuk is
recorded as `NOT_TESTED`.

## Hardware result table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Build + flash path reaches normal boot state | PASS | User-reported pass. |
| PROFILE-001 | identity_profile | Current identity profile remains usable | PASS | User-reported pass. |
| DEFAULT-001 | default_table | Default/neutral points match prior source-backed behavior | PASS | User-reported pass. |
| MODES-001 | mode_default | Mode default/center behavior preserved | PASS | User-reported pass. |
| MODS-001 | modifier_tables | Representative X/Y/Tilt/Layer tables preserved | PASS | User-reported pass. |
| RT1RF4-001 | custom_modifier_table | RT1+RF4 custom raw points match prior hardware observations | PASS | User-reported pass. |
| LT5-001 | low_magnitude | LT5 RF11 low-magnitude override preserved | PASS | User-reported pass. |
| NULL-001 | null_override | RF9 null behavior preserved | PASS | User-reported pass. |
| PROFILE-REG-001 | profile_regression | No profile artifact behavior regression observed | PASS | User-reported pass; no regression observed. |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | No nunchuk validation claim. |

## Caveats

- user-reported result
- no nunchuk validation
- no runtime-loaded config
- no WebSerial/device write
- no protobuf binary write
- no firmware flashing automation
- no universal official configurator compatibility claim
- no intentional firmware behavior change claim
- no Senscope/game-semantic change

## Rollback status

No rollback was triggered by the reported result rows. If a future checker,
build, or hardware retest contradicts this result, stop merge preparation and
use the normal Git-history rollback path for the implementation branch.

