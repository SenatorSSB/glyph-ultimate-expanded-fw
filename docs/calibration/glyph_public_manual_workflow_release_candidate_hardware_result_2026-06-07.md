# Public / Manual Workflow Release Candidate Hardware Result - 2026-06-07

This document records the user-reported hardware result for the
public/manual workflow release-candidate preparation. It is scoped to
applicable doable rows only and does not claim runtime-loaded config,
runtime-config storage, firmware binary/protobuf parser integration,
WebSerial/device write, push-to-device, firmware flashing automation, official
configurator compatibility, public release, or nunchuk validation.

## Result Identity

- status: USER_REPORTED_PASS
- result source: user-reported
- exact user report text: "everything works as expected"
- result date: 2026-06-07
- branch tested: configurator
- result branch: public-manual-workflow-release-candidate-hardware-result
- commit SHA under test: d085c0f80ea1578a378bce2ab75f8005727c2dde
- build command: ./scripts/build-glyph-mk6-quiet.sh
- firmware artifact path/hash: unknown
- profile file: none / no new profile file used
- scope: applicable doable public/manual workflow release-candidate rows
- nunchuk: NOT_TESTED

## Source Authority

The record is based on the user-reported result text and the plan-scoped
manual workflow boundary. Unknown artifact details remain unknown.

## Caveats

- user-reported result
- manual/operator-run firmware update path only
- no new profile file used
- no runtime-loaded config
- no runtime-config storage
- no firmware binary/protobuf parser integration
- no WebSerial/device write
- no push-to-device
- no firmware flashing automation
- no hidden write
- no official configurator compatibility claim
- no public release claim yet
- no nunchuk validation
- no Senscope/game-semantic change

## Hardware Result Table

| Row ID | Category | Planned check | Result | Notes |
| --- | --- | --- | --- | --- |
| BOOT-001 | boot | Normal boot after the manual workflow update path reaches expected boot state | PASS | User-reported pass under applicable doable public/manual workflow scope. |
| PROFILE-001 | profile | Current profile remains usable after the workflow preparation | PASS | User-reported pass; no new profile file used. |
| BASELINE-001 | baseline | Source-backed baseline outputs remain preserved | PASS | User-reported pass; baseline outputs preserved. |
| MODIFIERS-001 | modifiers | Representative modifier tables remain preserved | PASS | User-reported pass; representative modifier tables preserved. |
| SPECIAL-001 | special_tables | Special tables remain preserved | PASS | User-reported pass; special tables preserved. |
| OVERRIDE-001 | override_paths | Representative override paths remain preserved | PASS | User-reported pass; representative override paths preserved. |
| CSTICK-001 | cstick_interaction | C-stick interaction is not regressed where doable | PASS | PASS where doable / no regression observed. |
| DOCS-001 | docs_navigation | Docs/navigation/checklist links remain synchronized | PASS | Docs/navigation/checklist links remained synchronized. |
| NO-WRITE-001 | no_write | No hidden write, runtime-loaded config, or WebSerial/device write occurs | PASS | No hidden write, runtime-loaded config, push-to-device, or WebSerial/device write was used. |
| NO-FLASH-AUTO-001 | no_flash_automation | No flashing automation, UF2 copy automation, or bootloader automation occurs | PASS | No flashing automation, UF2 copy automation, or bootloader automation was used. |
| RECOVERY-001 | recovery | Manual recovery/rollback path remains operator-run only | USER_ACCEPTED_RISK | Manual recovery/rollback path was not directly exercised; operator-run docs are available, so this row is conservatively marked USER_ACCEPTED_RISK. |
| PROFILE-REG-001 | profile_regression | No profile regression observed | PASS | PASS / no regression observed. |
| NUNCHUK-001 | nunchuk_scope | Explicitly mark nunchuk as not tested in this branch | NOT_TESTED | No nunchuk validation was performed or claimed. |
