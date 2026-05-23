# G8f8 - Export Push Boundary Assessment

Status: docs-only boundary assessment
Date: 2026-05-24

## Scope

This document is docs-only and does not implement export, push, upload, flashing, host tooling, firmware behavior, app-side TypeScript, or Senscope schema changes.

Audit question:

> What is source-backed on the device side, and what remains missing or unsupported for export and push workflows?

## Status Summary

| surface | status | source refs | caveat |
| --- | --- | --- | --- |
| device-side config get | `SOURCE_BACKED` | `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-158`, `HAL/pico/src/core/Persistence.cpp:125-151` | Requires valid saved config; returns raw protobuf body from device storage |
| device-side config set | `SOURCE_BACKED` | `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-272` | Decodes streamed protobuf `Config`, validates selected references, persists accepted config |
| device-side persistence | `SOURCE_BACKED` | `HAL/pico/src/core/Persistence.cpp:36-180`, `HAL/pico/include/core/Persistence.hpp:24-42` | LittleFS `config.bin` with local size/CRC header |
| reboot/bootloader commands | `SOURCE_BACKED` | `HAL/pico/src/comms/ConfiguratorBackend.cpp:69-73` | Command dispatch exists; update/flashing workflow is not established here |
| host export format | `UNKNOWN` or `UNSUPPORTED_BY_CURRENT_SOURCE` | No host export source inspected or found in this repo batch | Do not generate vendor-specific files |
| Senscope-generated protobuf/config export | `OUT_OF_SCOPE` unless approved | Boundary docs and current prompt | Requires explicit approval and schema/workflow review |
| push-to-device workflow | `UNSUPPORTED_BY_CURRENT_SOURCE` as an approved workflow | Device-side set exists, but no approved host workflow in inspected source | Stop before using configurator commands on hardware |
| firmware update/flashing workflow | `UNSUPPORTED_BY_CURRENT_SOURCE` as an approved workflow | Reboot command exists but no end-to-end flashing source/approval here | Stop before firmware update/flashing |

## What Is Source-Backed

Device-side get-config support:

- `HandleGetConfig` validates the saved config and emits `CMD_SET_CONFIG` plus raw saved protobuf body.
- `LoadConfigRaw` writes the protobuf body after the local persistence header.

Device-side set-config support:

- `HandleSetConfig` decodes streamed protobuf into the active `Config`, validates selected cross-reference bounds, calls `persistence.SaveConfig`, and returns `CMD_SUCCESS` on success.

Device-side persistence:

- `SaveConfig` writes a local header plus protobuf body to LittleFS `config.bin`.
- `CheckSavedConfig` validates header size and CRC32.
- `LoadConfig` resets to `Config_init_default` before decoding.

Reboot/bootloader command dispatch:

- `CMD_REBOOT_FIRMWARE` and `CMD_REBOOT_BOOTLOADER` dispatch to reboot helpers.

## What Is Missing For Export Workflow

Missing or unapproved:

- A Senscope-approved export file format.
- A source-backed mapping from Senscope neutral profile data to protobuf `Config`.
- Proof that existing runtime modes can represent every target profile exactly.
- Host-side UX or CLI source that produces compatible config artifacts.
- Safety validation and diagnostics for unsupported fields.
- Review of schema authority and dependency version pinning for generated artifacts.

Therefore host export format remains `UNKNOWN` or `UNSUPPORTED_BY_CURRENT_SOURCE`, and Senscope-generated protobuf/config export remains `OUT_OF_SCOPE` unless separately approved.

## What Is Missing For Push-To-Device Workflow

Missing or unapproved:

- A reviewed host transport implementation for PacketIO/COBS command exchange.
- Device discovery and target selection rules.
- Safety checks before writing config.
- Backup/restore and recovery plan.
- User confirmation model and failure handling.
- Hardware-tested evidence.
- Approval to send configurator commands to real devices.

Device-side set support does not establish an approved push workflow.

## Stop Conditions

Stop before:

- generating config files;
- writing config to any device;
- using configurator commands against hardware;
- firmware update or flashing;
- schema changes;
- deriving gameplay semantic labels or thresholds;
- changing Senscope neutral profile schema.

## Conclusion

The device has source-backed config get, config set, persistence, and reboot command handlers. Those are necessary but not sufficient for export or push. Current source does not approve Senscope export generation, push-to-device, upload, flashing, or host UX claims.
