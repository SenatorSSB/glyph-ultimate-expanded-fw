# Runtime Config Storage/Fallback Architecture

Status label: DESIGN_ONLY_BLOCKED_BY_SOURCE_AUTHORITY.

## Purpose

This document defines the Step 10 architecture boundary for future
runtime-config storage/fallback work.

Because `runtime_config_storage_fallback_source_authority.md` records
`IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`, this architecture is design-only
and does not modify firmware source.

## Storage Purpose

A future runtime-config storage path would store bounded, validated
`MODE_ULTIMATE` runtime table data that can be compared against the
source-owned current baseline.

That future path is not implemented here.

The current repository already has source-backed Pico persistence for the
current protobuf `Config` object in LittleFS `config.bin`. That existing path is
a precedent and constraint, not an approved runtime-loaded config storage
decision.

## Known-Good Fallback Invariant

The known-good fallback must remain the source-owned current baseline:

- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `kKnownGoodRuntimeConfig`
- `kSourceOwnedCurrentBaselineRuntimeConfig`

Invalid, missing, corrupt, unsupported, or untrusted future runtime-loaded data
must not become controller output.

## Validation Before Use

Any future storage-backed runtime config must validate before use.

Minimum future validation requirements:

- schema name is recognized;
- schema version is supported;
- mode scope is `MODE_ULTIMATE`;
- table count is exactly 27;
- point count per table is exactly 9;
- table IDs are complete, ordered, and unique;
- coordinates are integers in `[0,255]`;
- fallback table exists;
- checksum/hash is valid;
- provenance is present;
- forbidden classes are absent.

Forbidden classes include macros, turbo, timing automation, arbitrary scripts,
one-shot or toggle behavior, hidden device-write behavior, WebSerial/device
write instructions, serial transport payloads, firmware patches, unsupported
roles, unsupported priority classes, and unproven nunchuk validation claims.

## Missing Config Behavior

Future missing runtime config must resolve to the source-owned known-good
baseline.

This branch does not define a storage filename, filesystem path, flash address,
or boot-time read path for the missing-config case.

## Corrupt Config Behavior

Future corrupt runtime config must fail closed to the source-owned known-good
baseline.

Corruption includes malformed binary data, length mismatch, checksum mismatch,
truncated payload, duplicate table IDs, missing tables, and out-of-range
coordinates.

## Unsupported Version Behavior

Unsupported schema versions must fail closed to the source-owned known-good
baseline unless a separately approved migration path exists.

This branch does not define migration behavior.

## Fallback Source

Fallback source:

- source-owned firmware constants in `src/modes/UltimateIdentityRuntimeTables.hpp`;
- source-owned interpreter metadata and fallback helpers in
  `src/modes/UltimateRuntimeConfigInterpreter.hpp`;
- checker-backed fixtures under `docs/runtime_config/fixtures/`.

The fallback source is not an active profile artifact, not official
configurator output, and not an external-remapper artifact.

## Recovery Path

Recovery path status: deferred.

Future recovery design must decide whether recovery means ignoring the invalid
runtime config, deleting or replacing a storage artifact, preserving diagnostics,
or restoring a staged known-good copy.

No recovery mutation is implemented here.

## Rollback Policy

Rollback policy status: deferred.

The inspected current `Persistence::SaveConfig` path is not an atomic
two-slot/staged rollback design. It opens `config.bin` for write, writes a
placeholder header, writes protobuf bytes, then updates the header. Do not
promote this to a runtime-loaded config rollback architecture without separate
approval, implementation design, and validation.

## Profile-Scoped Vs Global Config Decision

Decision status: unresolved.

This branch does not decide whether future runtime config is global,
profile-scoped, backend-scoped, mode-scoped, or tied to current persisted
`Config` profile data.

## Maximum Size Decision

Decision status: unresolved.

The Step 12 offline binary preview records a deterministic candidate size for
the current 27-table baseline, but this branch does not approve a firmware
maximum size, storage allocation, or memory budget.

## Hardware Test Trigger Points

Hardware testing becomes required before merge of any future branch that changes
firmware source or firmware behavior for storage-backed runtime config.

Minimum future hardware-plan rows:

- boot;
- current profile usable;
- current baseline behavior preserved;
- missing config fallback;
- invalid/corrupt config fallback if testable;
- normal gameplay regression;
- nunchuk `NOT_TESTED` unless explicitly validated.

No hardware result is recorded by this branch.

## Non-Claims

- Runtime-loaded storage is not implemented.
- Runtime-loaded config consumption from storage is not implemented.
- Firmware binary/protobuf runtime-config parser integration is not implemented.
- Firmware-consuming manual runtime config load path is not implemented.
- WebSerial/device write is not implemented.
- Direct device mutation workflow is not implemented.
- Firmware flashing automation is not implemented.
- Official protobuf compatibility is not claimed.
- Universal official configurator compatibility is not claimed.
- Nunchuk validation is not claimed.
- Senscope neutral profile schema is not changed.
- Super Smash Bros. Ultimate game semantics are not changed.

## Explicit Stop Line

This architecture stops before Step 13 firmware binary/protobuf parser
integration, Step 14 firmware-consuming manual config load, Steps 15-16
WebSerial/device write, and Step 17 firmware flashing automation.
