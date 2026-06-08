# Glyph Phase 7A Runtime Config Compiled Payload Activation Hardware Failure

This hardware failure packet records the corrected user-reported result for the
Phase 7A source-owned compiled/test runtime-config payload activation branch.
It is a result record only and does not diagnose or fix the implementation.

- status: HARDWARE_FAIL
- result source: user-reported
- branch tested: phase7a-runtime-config-compiled-payload-activation
- result branch: phase7a-runtime-config-compiled-payload-activation-hardware-failure
- commit SHA under test: 67e575b87147f1a6e2ce6474a59ac5b418bd1147
- build command: ./scripts/build-glyph-mk6-quiet.sh
- firmware artifact path/hash: unknown
- exact failure report: I dont know what happened after tests, but I was wrong. Some inputs completely cut the connection from the controller. At least pressing rf5 or rf6 disconnect it according to the game console
- exact recovery report: i restored the previous fw, which works fine still
- scope: Phase 7A compiled/test runtime-config payload activation hardware failure
- nunchuk: NOT_TESTED

## Observed Failing Inputs

- RF5 implicated
- RF6 implicated

## Observed Failure

- console/game reports controller disconnect

## Conclusion

- Phase 7A compiled payload activation branch must not merge.
- Previous configurator firmware remains known-good for the tested scope.
- Failure is isolated to the Phase 7A activation branch by the reported
  restoration result.
- Exact low-level disconnect cause is unknown and must not be inferred without
  debugging.

## Hardware Failure Table

| Row ID | Area | Result | Notes |
| --- | --- | --- | --- |
| BOOT-001 | normal boot | UNKNOWN_OR_NOT_RELIABLY_COMPLETE | User report identified disconnect after testing; normal boot completion is not reliable evidence. |
| BASELINE-001 | current baseline preserved | FAIL | User-reported RF5/RF6 disconnect regression means baseline behavior was not preserved. |
| PARSER-001 | compiled valid payload accepted | INCONCLUSIVE | The branch reached testable runtime behavior, but the parser path cannot be isolated from the reported disconnect. |
| FALLBACK-001 | invalid/failure path | NOT_HARDWARE_EXERCISED | No intentionally invalid compiled-payload firmware artifact was reported as tested. |
| MODIFIERS-001 | representative modifiers | FAIL | User-reported input-triggered disconnect is a modifier/profile regression in the tested branch. |
| SPECIAL-001 | special tables | NOT_RELIABLY_TESTED_AFTER_DISCONNECT | Disconnect regression prevents reliable special-table hardware result claims. |
| OVERRIDE-001 | override paths | FAIL | RF5/RF6 path causes disconnect/regression according to the user report. |
| CSTICK-001 | c-stick interaction | NOT_RELIABLY_TESTED_AFTER_DISCONNECT | Disconnect regression prevents reliable c-stick hardware result claims. |
| NO-STORAGE-001 | no storage read/write | PASS_BY_SOURCE_INSPECTION_ONLY | Source inspection shows no runtime-config storage implementation on this branch. |
| NO-WRITE-001 | no device write/WebSerial | PASS_BY_SOURCE_INSPECTION_ONLY | Source inspection shows no WebSerial/device-write runtime-config path on this branch. |
| NO-FLASH-001 | no flashing automation | PASS_BY_SOURCE_INSPECTION_ONLY | Source inspection shows no firmware flashing automation implementation on this branch. |
| PROFILE-REG-001 | profile regression | FAIL | User restored previous configurator firmware and reported it works fine, isolating the regression to this activation branch. |
| NUNCHUK-001 | nunchuk | NOT_TESTED | No nunchuk validation was performed or claimed. |

## Caveats

- user-reported failure
- exact low-level disconnect cause unknown
- do not infer firmware crash mechanism without debugging
- previous configurator firmware restored and works fine
- branch must not merge
- no nunchuk validation
- no runtime-loaded config storage
- no config.bin runtime-config use
- no WebSerial/device write
- no runtime-config command IDs
- no firmware flashing automation
- no official configurator compatibility claim
- no Senscope/game-semantic change

## Source Authority

- User-provided failure report and recovery report in this thread.
- Hardware plan:
  `docs/calibration/glyph_phase7a_runtime_config_compiled_payload_activation_hardware_plan_2026-06-08.md`
- Implementation branch packet:
  `docs/runtime_config/phase7a_runtime_config_compiled_payload_activation.md`
- Active firmware path under test: `src/modes/Ultimate.cpp`

