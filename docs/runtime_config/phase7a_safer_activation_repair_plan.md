# Phase 7A Safer Activation Repair Plan

status: REPAIR_PLAN_ONLY_NOT_IMPLEMENTED

This is a plan for a later branch. It does not implement runtime activation,
modify firmware source, create a new firmware build path, or record a hardware
pass.

## Branch To Create Later

- `phase7a-runtime-config-activation-repair-minimal`

Create that branch from `configurator`, not from
`phase7a-runtime-config-compiled-payload-activation`.

## Recommended Design

- no global runtime `ParseResult` object unless proven safe;
- keep the parser scaffold compiled;
- use build-time/generated equivalence checks as much as possible;
- if runtime validation is needed, wrap it in an explicit local function and
  call once in a bounded activation path;
- introduce a compile-time or startup diagnostic flag only if no output behavior
  changes;
- keep runtime view selection behavior identical to `configurator` until the
  validation boundary is independently proven;
- no storage/write/WebSerial/flashing.

## Required Hardware Plan

Any future implementation branch must include a hardware plan before testing and
a hardware result before merge. The plan should include:

- branch and commit SHA under test;
- build command and artifact identity/hash;
- boot/connection result before input checks;
- RF5 forced-Up/direction-plus-A/A output checks;
- RF6 z-airdodge/low-magnitude/buttonR checks;
- representative non-RF5/RF6 baseline checks;
- explicit fail/rollback instructions;
- nunchuk marked `NOT_TESTED` unless actually tested;
- no runtime-loaded config, storage, WebSerial/device write, or flashing
  automation claim.

## Stop Line

Do not merge a future runtime activation branch until hardware confirms that the
candidate preserves the intended baseline scope. Do not infer a low-level
diagnosis from the Phase 7A failure without new source or hardware evidence.
