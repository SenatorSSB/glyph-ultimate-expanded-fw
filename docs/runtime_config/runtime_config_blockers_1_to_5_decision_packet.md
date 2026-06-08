# Runtime Config Blockers 1 To 5 Decision Packet

Status: BLOCKERS_1_TO_5_DESIGN_COMPLETE_NOT_IMPLEMENTED.

## Purpose

This packet completes design work for the five runtime-loaded-config blockers
without implementing firmware/runtime behavior.

Every proposed decision below is `PROPOSED_DECISION_NOT_IMPLEMENTED`.

## Blocker 1 - Storage Location And Ownership

Status: PROPOSED_DECISION_NOT_IMPLEMENTED.

Source-backed facts:

- Current persistence support exists for the existing protobuf `Config` object.
- Step 10 records runtime-config storage/fallback implementation as blocked.
- Runtime-config storage is not implemented.

Proposed decision:

- Prefer a separate mode-scoped runtime-config artifact/slot for
  `MODE_ULTIMATE`, not current `config.bin`, unless a future implementation
  proves extending current `Config` is safer and source-backed.
- Firmware owns storage validation and activation policy.
- Config does not own storage write policy.

Alternatives considered:

- Extend current `config.bin`.
- Store runtime config in a separate global artifact.
- Store runtime config per mode.
- Keep source-owned firmware tables only.

Rejected alternatives:

- Treating `config.bin` as approved runtime-config storage now.
- Profile-scoped or cross-mode runtime config for the first implementation.
- Any hidden write or auto-rewrite recovery path.

Remaining implementation gates:

- source-backed path/slot selection;
- memory and filesystem size review;
- migration policy;
- fallback and recovery policy;
- explicit product approval for firmware/storage changes;
- build and hardware plan/result.

Hardware-test trigger:

- Any branch that reads runtime-config data from storage or writes it to
  storage.

Stop line before implementation:

- Do not edit `Persistence`, boot config code, storage files, or firmware source
  to read/write runtime config on this branch.

## Blocker 2 - Firmware Parser Format

Status: PROPOSED_DECISION_NOT_IMPLEMENTED.

Source-backed facts:

- Step 12 provides an offline-only deterministic `GCFG` preview serializer and
  parser.
- Step 13 records firmware binary/protobuf parser implementation as blocked.
- Firmware parser implementation is not implemented.

Proposed decision:

- Prefer a small deterministic firmware-owned binary format based on the
  existing offline `GCFG` preview shape for the first implementation.
- Treat protobuf extension as a later alternative, not the default.
- Firmware owns parser validation, version acceptance, mode-scope acceptance,
  integrity checks, and bounds checks.

Alternatives considered:

- Extend the current protobuf `Config`.
- Consume the Step 12 `GCFG` preview exactly as-is.
- Add a new protobuf message.
- Keep compiled source-owned data only.

Rejected alternatives:

- Claiming the offline `GCFG` preview is already a firmware ABI.
- Claiming official protobuf compatibility.
- Accepting scripts, macros, turbo, timing automation, transport commands, or
  firmware patches in the payload.

Remaining implementation gates:

- selected firmware-owned format;
- memory/maximum-size review;
- parser test vectors;
- invalid corpus;
- explicit product approval for firmware changes;
- build and hardware plan/result.

Hardware-test trigger:

- Any branch that compiles a parser into firmware or changes runtime-config
  acceptance behavior.

Stop line before implementation:

- Do not add parser symbols, parser integration, or firmware consumption of
  runtime-config bytes on this branch.

## Blocker 3 - Boot/Load Entry Point

Status: PROPOSED_DECISION_NOT_IMPLEMENTED.

Source-backed facts:

- Current boot config path loads the existing `Config` object and falls back to
  defaults when existing config load fails.
- Current runtime config remains source-owned.
- Step 14 records firmware-consuming manual runtime-config load as blocked.

Proposed decision:

- Load existing current `Config` as today.
- Initialize source-owned known-good runtime config.
- Optionally read a runtime-config candidate only after core config is
  available.
- Validate the complete candidate.
- Activate only if fully valid.
- Otherwise keep the known-good source-owned baseline.

Alternatives considered:

- Load runtime config before current config.
- Replace source-owned baseline at compile time.
- Partially activate valid tables from an invalid payload.
- Depend on host/device write before boot validation exists.

Rejected alternatives:

- Booting from unvalidated runtime-config data.
- Partial activation.
- Cross-mode runtime config during the first implementation.

Remaining implementation gates:

- exact boot/load hook;
- source-backed storage path;
- selected parser;
- fallback/recovery policy;
- explicit product approval for firmware changes;
- build and hardware plan/result.

Hardware-test trigger:

- Any branch that changes boot/load ordering or makes firmware consume a
  candidate runtime config.

Stop line before implementation:

- Do not edit boot/load source paths or runtime config initialization on this
  branch.

## Blocker 4 - Fallback, Recovery, And Rollback

Status: PROPOSED_DECISION_NOT_IMPLEMENTED.

Source-backed facts:

- Current source-owned known-good runtime config remains the firmware baseline.
- Existing docs require validation-before-use and fallback-to-known-good before
  future implementation.
- Runtime-config recovery mutation is not implemented.

Proposed decision:

- First implementation fails closed by ignoring invalid runtime config.
- No auto-delete.
- No auto-rewrite.
- No hidden recovery write.
- No partial activation.
- Diagnostics may be recorded only if source-backed later.

Alternatives considered:

- Delete invalid runtime-config storage automatically.
- Rewrite invalid storage with a baseline payload.
- Keep a previous accepted candidate in hidden rollback storage.
- Activate valid subsets of an invalid payload.

Rejected alternatives:

- Any hidden storage mutation.
- Any firmware-owned recovery write without source authority and approval.
- Any config-owned fallback policy.

Remaining implementation gates:

- source-backed recovery/diagnostic support;
- rollback requirements;
- operator-visible recovery plan;
- explicit product approval for mutation paths;
- build and hardware plan/result for behavior changes.

Hardware-test trigger:

- Any branch that changes fallback behavior, records diagnostics, mutates
  storage, or claims rollback/recovery behavior.

Stop line before implementation:

- Do not implement recovery mutation, rollback storage, diagnostics writes, or
  fallback behavior changes on this branch.

## Blocker 5 - Device-Write / WebSerial Authority Boundary

Status: PROPOSED_DECISION_NOT_IMPLEMENTED.

Source-backed facts:

- Step 15 source-authority research is complete.
- Step 16 WebSerial/device-write implementation is blocked before
  implementation.
- Current public/manual workflow docs make no device-write or official
  compatibility claim.

Proposed decision:

- Device-write/WebSerial remains blocked before implementation.
- Any future write path must be explicit and user-visible.
- Future write must validate before write.
- Future write must be readback-capable if source-backed.
- Future write must be rollback/recovery-gated.
- Config cannot own transport commands or device-write policy.

Alternatives considered:

- WebSerial write now.
- Serial command write now.
- Official configurator export/write route now.
- Manual-only offline preview with no device write.

Rejected alternatives:

- Hidden device write.
- Push-to-device workflow without source authority.
- Production vendor-specific export output.
- Official configurator compatibility claim.
- Firmware flashing automation.

Remaining implementation gates:

- source-backed transport authority;
- explicit product approval;
- write protocol and validation-before-write design;
- readback/recovery policy;
- hardware plan/result;
- safety review.

Hardware-test trigger:

- Any branch that writes runtime-config data to a device, adds WebSerial write,
  adds serial write, changes transport commands, or claims readback/write
  behavior.

Stop line before implementation:

- Do not add WebSerial/device-write, serial write, push-to-device, UF2 copy,
  bootloader automation, or flashing automation on this branch.

## Cross-Blocker Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware parser is not implemented.
- Boot/load runtime-config consumption is not implemented.
- Device write / WebSerial is not implemented.
- Firmware flashing automation is not implemented.
- Public release is not claimed.
- Official configurator compatibility is not claimed.
- Nunchuk validation is not claimed.
