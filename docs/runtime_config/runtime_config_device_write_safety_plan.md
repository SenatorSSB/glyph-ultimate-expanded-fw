# Runtime Config Device-Write Safety Plan

Status label: SAFETY_PLAN_BLOCKED_BEFORE_IMPLEMENTATION.

## Purpose

This Step 16 safety packet records the required safety boundary for any future
write-capable runtime-config or configurator workflow.

It does not implement WebSerial, serial/device write, runtime-loaded config,
firmware parser integration, protobuf binary write, firmware flashing
automation, UF2 flashing, bootloader automation, or hardware validation.

## Implementation Stop Line

`DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`

Device-write implementation is stopped in this branch. The Step 15
source-authority packet records missing WebSerial/device-write authority, and
the Step 14 manual-load packet records missing firmware-consuming manual-load
authority.

No Step 16 implementation may proceed until a future branch has:

- official or repo-authoritative WebSerial/browser transport source;
- official or repo-authoritative packet-framing source;
- explicit product approval for a write-capable workflow;
- approved payload target and scope;
- validation-before-write policy;
- backup, rollback, and recovery policy;
- readback/round-trip policy;
- hardware plan and later hardware result.

## Explicit User Action Requirement

Any future write-capable path must require explicit user action.

Minimum requirements:

- no default write mode;
- no background write;
- no automatic save;
- no hidden device mutation;
- no write during dry-run, validation, preview, import, export, or readback;
- explicit target device or port selection;
- explicit payload selection;
- explicit confirmation immediately before mutation;
- visible result reporting after write or failure.

## No Hidden Writes

Hidden writes are forbidden.

Forbidden write forms include:

- automatic writes during app load;
- automatic writes during validation;
- automatic writes during preview;
- automatic writes during readback;
- implicit writes when a serial/WebSerial connection opens;
- implicit writes when a config file is parsed;
- recovery writes not explicitly selected by the user;
- firmware flashing or UF2 copy as part of a config workflow.

## Payload Validation Before Write

Any future payload must validate before write.

Minimum future validation requirements:

- approved source authority for the payload format;
- schema/version check;
- mode-scope check;
- maximum size check;
- checksum/CRC or integrity check if the selected format defines one;
- table count and point count checks for runtime-config payloads;
- table ID completeness and uniqueness checks;
- coordinate validation before narrowing;
- current protobuf `Config` reference checks when the target is current
  `Config`;
- rejection of scripts, macros, turbo, timing automation, one-shot behavior,
  toggles, hidden writes, serial transport payloads embedded in config,
  firmware patches, and unproven hardware claims.

Validation failure must prevent the write.

## Readback Round Trip Validation

Readback/round-trip validation is required when source-backed.

Current firmware source supports readback for the current protobuf `Config`
through `CMD_GET_CONFIG`. That readback authority does not extend to
runtime-config payloads because no runtime-config command or storage slot is
defined.

Future readback policy must identify:

- exact command/API used for readback;
- exact bytes or decoded object compared;
- whether the comparison is byte-exact or semantically normalized;
- failure behavior;
- whether reboot or power-cycle persistence is part of validation;
- how results are recorded without claiming hardware validation prematurely.

## Backup Rollback And Recovery Plan

Any future write-capable implementation must define backup, rollback, and
recovery before mutation.

Minimum requirements:

- read current source-backed state before write when the source supports it;
- preserve a user-visible backup artifact when a backup path is in scope;
- define whether rollback writes the prior config or instructs a manual
  recovery route;
- avoid hidden rollback writes;
- define what happens on validation failure, write failure, readback failure,
  disconnect, timeout, partial write, corrupted stored payload, unsupported
  version, and reboot failure;
- define how to return to the source-owned known-good baseline;
- define when firmware flashing is out of scope and what manual recovery docs
  are referenced instead.

No rollback mutation is implemented here.

## Failure Modes

Future implementation must explicitly handle:

- unsupported browser transport;
- missing or ambiguous target device;
- permission denied;
- disconnect before write;
- disconnect during write;
- timeout waiting for response;
- `CMD_ERROR` response;
- unexpected command response;
- invalid readback payload;
- readback mismatch;
- partial write or unknown write result;
- invalid saved config after write;
- invalid runtime-config payload after reboot if runtime config is ever
  implemented;
- user cancellation;
- recovery path unavailable.

## Hardware Test Matrix

Hardware testing is not required for this branch because no firmware source,
runtime-load code, or device-write code is changed.

Any future implementation branch must include a hardware plan with rows for:

| Row | Scenario | Expected result |
| --- | --- | --- |
| 1 | Boot | Device boots and current profile remains usable. |
| 2 | No runtime config baseline | Source-owned known-good baseline remains active when no runtime config exists. |
| 3 | Valid manual-loaded config if implemented | Valid payload is accepted only after validation and explicit user action. |
| 4 | Invalid payload rejected | Invalid payload is rejected before write or before use. |
| 5 | No hidden write | No mutation occurs during dry-run, readback, validation, connection, or preview. |
| 6 | Readback/round-trip if implemented | Readback matches accepted payload by the approved comparison rule. |
| 7 | Recovery/rollback | Device can return to known-good state through the approved path. |
| 8 | Profile regression | Existing profile/config behavior still works. |
| 9 | Nunchuk scope | `NOT_TESTED` unless nunchuk hardware is actually tested and recorded. |

No hardware result is recorded by this branch.

## Non-Claims

- Device-write implementation is not implemented.
- WebSerial implementation is not implemented.
- Runtime-loaded config is not implemented.
- Step 14 manual firmware load is not implemented.
- Firmware parser implementation is not implemented.
- Runtime-config storage is not implemented.
- Hidden device write is not implemented.
- Firmware flashing automation is not implemented.
- UF2 flashing automation is not implemented.
- Bootloader automation is not implemented.
- Official configurator compatibility is not claimed.
- Universal official configurator compatibility is not claimed.
- Hardware validation is not claimed.
- Nunchuk validation is not claimed.
- Senscope neutral profile schema is not changed.
- Super Smash Bros. Ultimate game semantics are not changed.

## Future Gate Checklist

Step 16 remains blocked unless a future branch can prove all of the following:

- source-backed WebSerial or serial transport authority;
- source-backed device-write command/API authority;
- source-backed payload schema authority;
- explicit user product approval;
- explicit user action requirement;
- no hidden writes;
- payload validation before write;
- readback/round-trip validation if source-backed;
- rollback/recovery plan;
- hardware test plan before implementation claims;
- hardware result before validation claims;
- no firmware flashing automation;
- nunchuk remains `NOT_TESTED` unless separately validated.
