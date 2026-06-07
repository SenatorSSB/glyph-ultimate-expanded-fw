# Glyph Runtime Config Firmware Binary Parser Hardware Plan Template

Status label: TEMPLATE_ONLY_NOT_A_RESULT.

## Scope

This is a future hardware-test plan template for a separately approved firmware
branch that implements runtime-config firmware binary/protobuf parser
integration.

It is not a hardware result. It does not implement firmware parser integration,
runtime-loaded config consumption, storage, WebSerial/device write, or firmware
flashing automation.

## Artifact Under Test

- Branch: `UNKNOWN_FUTURE_BRANCH`
- Firmware artifact: `UNKNOWN`
- Parser input format: `UNKNOWN`
- Storage path: `UNKNOWN`
- Operator: `UNKNOWN`
- Date: `UNKNOWN`
- Nunchuk status: `NOT_TESTED` unless actually validated and recorded.

## Test Matrix

| Row | Scenario | Setup | Expected result | Result |
| --- | --- | --- | --- | --- |
| 1 | Boot with no stored runtime config | Device has no approved runtime-config payload available | Firmware uses source-owned known-good baseline; current profile remains usable | NOT_RUN |
| 2 | Boot with valid runtime config if future implementation supports it | Store approved valid payload through approved test-only route | Payload validates before use; outputs match expected runtime table data | NOT_RUN |
| 3 | Invalid checksum fallback | Store payload with checksum/CRC mismatch through approved test-only route | Payload is rejected; firmware uses source-owned known-good baseline | NOT_RUN |
| 4 | Unsupported version fallback | Store payload with unsupported schema/version | Payload is rejected; firmware uses source-owned known-good baseline | NOT_RUN |
| 5 | Missing table fallback | Store payload missing at least one required table | Payload is rejected; firmware uses source-owned known-good baseline | NOT_RUN |
| 6 | Out-of-range coordinate rejection | Store payload with coordinate outside `[0,255]` before narrowing | Payload is rejected; firmware uses source-owned known-good baseline | NOT_RUN |
| 7 | Baseline output preservation | Compare baseline directional/modifier output rows against preimplementation baseline | Current source-owned baseline outputs are preserved when payload is absent or invalid | NOT_RUN |
| 8 | Profile regression | Verify existing profile/config behavior after parser implementation | Existing profile selection and current `Config` persistence still work | NOT_RUN |
| 9 | Recovery/rollback behavior if testable | Trigger approved recovery path for invalid stored payload | Device can recover to source-owned baseline without hidden write or unsafe flashing workflow | NOT_RUN |
| 10 | Nunchuk scope | Only run if nunchuk hardware is available and explicitly in scope | `NOT_TESTED` unless actually validated and recorded | NOT_TESTED |

## Required Result Packet Fields

A future result packet must record:

- exact branch and commit;
- exact firmware artifact and checksum where available;
- parser input fixture or payload hash;
- storage/setup procedure;
- operator and date;
- pass/fail result for each row;
- rollback/recovery notes;
- explicit non-claims for WebSerial/device write, flashing automation, and
  nunchuk if not tested.

## Non-Claims

- This template is not a hardware result.
- Firmware parser implementation is not implemented here.
- Runtime-loaded config consumption is not implemented here.
- Runtime-config storage is not implemented here.
- WebSerial/device write is not implemented here.
- Firmware flashing automation is not implemented here.
- Nunchuk validation is not claimed here.
