# Runtime Config Manual Load Path Plan

Status label: DESIGN_ONLY_BLOCKED_BY_SOURCE_AUTHORITY.

## Purpose

This packet records the Step 14 manual config-load path audit after the Step 15
transport/source-authority audit.

It does not implement firmware-consuming manual config load, runtime-loaded
config storage, serial/device write, WebSerial, protobuf binary write, firmware
flashing automation, or hardware validation.

## Inspected Source Docs And Tools

- `README.md`
- `AGENTS.md`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`
- `docs/runtime_config/runtime_config_semantics_evaluator_bridge.md`
- `docs/runtime_config/runtime_loaded_config_schema_design.md`
- `docs/runtime_config/firmware_interpreter_architecture_spec.md`
- `docs/runtime_config/runtime_config_storage_fallback_source_authority.md`
- `docs/runtime_config/runtime_config_storage_fallback_architecture.md`
- `docs/runtime_config/runtime_config_binary_representation_design.md`
- `docs/runtime_config/runtime_config_firmware_binary_parser_source_authority.md`
- `docs/runtime_config/runtime_config_firmware_binary_parser_integration_plan.md`
- `docs/runtime_config/runtime_config_webserial_device_write_source_authority.md`
- `docs/calibration/glyph_runtime_config_firmware_binary_parser_hardware_plan_TEMPLATE.md`
- `src/modes/Ultimate.cpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `HAL/pico/include/core/Persistence.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/include/comms/ConfiguratorBackend.hpp`
- `HAL/pico/src/comms/backend_init.cpp`
- `config/glyph/common/src/config.cpp`
- `platformio.ini`
- `tools/glyph_runtime_config_binary_roundtrip.py`
- `tools/check_glyph_runtime_config_binary_offline_roundtrip.py`
- `tools/check_glyph_runtime_config_storage_fallback.py`
- `tools/check_glyph_runtime_config_firmware_binary_parser_plan.py`
- `tools/glyph_serial_config_tool.py`

## Implementation Decision

`MANUAL_LOAD_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`

Step 14 firmware-consuming manual config-load implementation is blocked by
missing byte-source authority, missing storage/boot/load decision, missing
runtime-config parser authority, unresolved fallback/recovery policy, and the
repository stop line before runtime-loaded config implementation.

Offline/manual fixture loading in tools is already source-backed for docs/tools
validation only. This audit does not need new firmware source for that class.

## Possible Manual Load Path Classes

| Path class | Source-backed status | Allowed in this branch | Notes |
| --- | --- | --- | --- |
| Offline fixture load in tools | Source-backed for docs/tools only | Yes, docs/tools/checkers only | `tools/glyph_runtime_config_binary_roundtrip.py` can encode/decode the Step 12 offline preview and check fixtures without device I/O. |
| Compiled test fixture in firmware | Not approved | No | No inspected source defines a test-only compile-time runtime-config fixture injection path. Firmware source changes would require explicit approval and hardware plan/result. |
| Runtime firmware loading from storage | Not approved | No | Step 10 records runtime-config storage/fallback as blocked; current `config.bin` stores the current protobuf `Config` only. |
| Serial/config command payload | Not approved for runtime config | No | Current `CMD_SET_CONFIG` accepts current protobuf `Config`, not Step 12 binary preview or runtime table payloads. |
| WebSerial/device-write path | Not approved | No | Step 15 source-authority audit records `DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`. |

## Source-Backed Manual Path Facts

The source-backed safe manual path is limited to offline tools:

- Step 12 binary preview tools can load source-backed table fixtures from disk.
- Step 12 binary preview tools can serialize and decode the deterministic
  offline-only `GCFG` container.
- Step 12 invalid-corpus checks can reject malformed offline payloads.
- These tools do not open serial ports, do not write storage, and do not make
  firmware consume runtime-loaded config.

The source-backed firmware path remains the source-owned baseline:

- `src/modes/UltimateRuntimeConfigInterpreter.hpp` defines source-owned
  `RuntimeConfigView` metadata and fallback helpers.
- `src/modes/Ultimate.cpp` resolves `runtime_config` from
  `kSourceOwnedCurrentBaselineRuntimeConfig` or `kKnownGoodRuntimeConfig`.
- No inspected firmware source loads runtime table data from storage, serial,
  WebSerial, a file, or a runtime payload.

## Not Approved Or Unknown

- Firmware-consuming manual runtime config load is not implemented.
- Runtime-config storage is not implemented.
- Firmware binary/protobuf runtime-config parser integration is not implemented.
- Manual load from `config.bin` is not approved.
- Manual load from serial command payload is not approved.
- Manual load from WebSerial/device write is not approved.
- Compiled test fixture injection is not approved.
- Runtime-config migration behavior is unknown.
- Runtime-config recovery mutation is unknown.
- Runtime-config hardware validation is absent.

## Validation And Fallback Requirements

Any future Step 14 implementation must validate before use and fail closed to
the known-good source-owned baseline.

Minimum future requirements:

- approved byte source;
- approved payload format;
- explicit schema/version and mode-scope checks;
- exact table count and point count checks;
- complete and unique table ID order checks;
- checksum/CRC policy;
- coordinate validation before narrowing to `uint8_t`;
- rejection of macros, turbo, timing automation, scripts, one-shot behavior,
  toggles, hidden writes, firmware patches, transport payloads, and unproven
  hardware claims;
- whole-payload acceptance only, with no partial table use;
- deterministic fallback to `kKnownGoodRuntimeConfig` on any failure;
- hardware plan before firmware behavior changes;
- hardware result before validation claims.

## Hardware Test Trigger

Hardware testing is not required for this branch because no firmware source or
device-write code is changed.

Hardware testing becomes required before merge of any future branch that makes
firmware consume a runtime-config payload, adds a compiled fixture route,
changes storage/boot loading, or changes device-write behavior.

Minimum future rows include:

- boot;
- no runtime config baseline;
- valid manual-loaded config if implemented;
- invalid payload rejected;
- no hidden write;
- readback/round-trip if implemented;
- recovery/rollback;
- profile regression;
- nunchuk `NOT_TESTED` unless separately validated.

## Non-Claims

- Step 14 manual firmware load is not implemented.
- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware parser implementation is not implemented.
- WebSerial/device write is not implemented.
- Hidden device write is not implemented.
- Firmware flashing automation is not implemented.
- UF2 flashing automation is not implemented.
- Bootloader automation is not implemented.
- Official configurator compatibility is not claimed.
- Universal official configurator compatibility is not claimed.
- Nunchuk validation is not claimed.
- Senscope neutral profile schema is not changed.
- Super Smash Bros. Ultimate game semantics are not changed.

## Stop Conditions Hit

- Runtime-loaded config implementation source authority is missing.
- Firmware-consuming manual load byte source is unresolved.
- Runtime-config parser/storage authority is unresolved.
- Fallback, recovery, and migration policy remain unresolved for implementation.
- Hardware plan/result for firmware-consuming manual load is absent.
