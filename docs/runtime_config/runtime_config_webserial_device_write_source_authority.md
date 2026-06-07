# Runtime Config WebSerial/Device-Write Source Authority

Status label: DESIGN_ONLY_BLOCKED_BY_SOURCE_AUTHORITY.

## Purpose

This packet records the Step 15 source-authority audit for future
WebSerial/device-write work in the runtime-config roadmap.

It does not implement WebSerial, serial/device write, runtime-loaded config,
firmware parser integration, protobuf binary write, firmware flashing
automation, official configurator compatibility, or hardware validation.

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
- `docs/calibration/glyph_runtime_config_firmware_binary_parser_hardware_plan_TEMPLATE.md`
- `docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md`
- `docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md`
- `docs/calibration/glyph_serial_active_config_writer_trace_2026-05-27.md`
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
- `tools/check_glyph_serial_config_writer.py`
- `tools/check_glyph_webserial_transport_blocker_packet.py`
- `tools/check_glyph_storage_transport_source_authority_registry.py`

The audit also ran the requested repository search:

```text
rg -n "WebSerial|serial|PacketIO|CMD_|CMD_GET_CONFIG|CMD_SET_CONFIG|config.bin|LittleFS|SaveConfig|LoadConfig|CheckSavedConfig|LoadConfigRaw|pb_decode|pb_encode|nanopb|CRC|crc|checksum|firmware|uf2|flash|bootloader|RPI-RP2|manual|upload|write|set config|get config" src include HAL config tools docs platformio.ini
find src include HAL config tools docs -maxdepth 6 -type f
```

## Implementation Decision

`DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`

Step 16 WebSerial/device-write implementation is blocked by missing WebSerial
source authority, missing official device-write workflow authority, unresolved
runtime-config storage/parser authority, unresolved safety/rollback policy, and
the repository approval stop line for write-capable workflows.

This branch may record source authority, safety requirements, non-claims, and
checker guardrails. It must not implement WebSerial, serial/device write,
runtime-loaded config writes, firmware flashing, UF2 copying, or hidden device
mutation.

## Current Source-Backed Transport Mechanisms

The repository has source-backed device-side transport for the existing
protobuf `Config` object only:

- `HAL/pico/src/comms/ConfiguratorBackend.cpp` dispatches configurator
  commands in `ConfiguratorBackend::SendReport`.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` handles `CMD_GET_CONFIG` by
  validating the saved current `Config`, then returning raw protobuf `Config`
  bytes as a `CMD_SET_CONFIG` response payload.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` handles `CMD_SET_CONFIG` by
  decoding the incoming protobuf `Config`, checking bounded references, saving
  the accepted `Config`, and returning `CMD_SUCCESS` or `CMD_ERROR`.
- `HAL/pico/include/comms/ConfiguratorBackend.hpp` wraps the stream with
  PacketIO COBS input/output helpers.
- `HAL/pico/src/comms/backend_init.cpp` initializes the configurator backend
  over `Serial.begin(115200)` when `COMMS_BACKEND_CONFIGURATOR` is selected.
- `HAL/pico/include/core/Persistence.hpp` names the current persisted file
  `config.bin` and exposes `SaveConfig`, `LoadConfig`, `CheckSavedConfig`, and
  `LoadConfigRaw`.
- `HAL/pico/src/core/Persistence.cpp` stores the existing protobuf `Config`
  body in LittleFS with a local size and CRC32 header.
- `config/glyph/common/src/config.cpp` loads the current `Config` at boot and
  saves defaults if current config loading fails.
- `platformio.ini` declares PacketIO, nanopb, HayBox-proto, LittleFS, and CRC32
  dependencies for relevant Pico builds.

These facts do not authorize a WebSerial browser workflow, a runtime-config
write command, a new runtime table payload, or a firmware-consuming
runtime-loaded config path.

## Current Command IDs And Payload Handling

Source-backed current `Config` command behavior:

| Command | Current source-backed behavior | Runtime-config authority |
| --- | --- | --- |
| `CMD_GET_CONFIG` | Request current saved protobuf `Config`; success response uses `CMD_SET_CONFIG` plus raw protobuf `Config` bytes. | None. It does not return runtime table payloads. |
| `CMD_SET_CONFIG` | Accept current protobuf `Config`, decode with nanopb, validate current config references, then save current `Config`. | None. It does not accept Step 12 binary preview or runtime table data. |
| `CMD_ERROR` | Error response with text payload. | Error response only. |
| `CMD_SUCCESS` | Empty success response for accepted current `Config` set. | Current `Config` success only. |

No inspected source defines:

- `CMD_GET_RUNTIME_CONFIG`;
- `CMD_SET_RUNTIME_CONFIG`;
- a WebSerial-specific command;
- a runtime-config storage slot;
- a browser-side WebSerial packet-framing implementation;
- official configurator write behavior source authority for runtime config.

## Current Config Get Set Behavior

Current get/set behavior is source-backed for the current protobuf `Config`
only.

`CMD_SET_CONFIG` can mutate device state by saving the current `Config` through
`Persistence::SaveConfig`. The guarded repo-local host tool
`tools/glyph_serial_config_tool.py` records a POSIX serial dry-run/read/write
path for current active config artifacts, but that tool is not WebSerial, not
official configurator authority, not runtime-loaded config, and not approval
for Step 16.

Current `config.bin` is source authority for the existing persisted `Config`.
It is not source authority for runtime table data, Step 12 binary preview
payloads, rollback-safe runtime-config storage, or WebSerial/device-write.

## Classification

| Topic | Classification | Evidence |
| --- | --- | --- |
| Current protobuf `Config` get/set device-side command handling | source-backed | `HAL/pico/src/comms/ConfiguratorBackend.cpp` |
| Current COBS/PacketIO wrapping in firmware | source-backed | `HAL/pico/include/comms/ConfiguratorBackend.hpp`, `platformio.ini` |
| Current `Config` LittleFS persistence with size and CRC32 header | source-backed | `HAL/pico/include/core/Persistence.hpp`, `HAL/pico/src/core/Persistence.cpp` |
| Guarded POSIX serial dry-run/read/write host tool for current `Config` | repo-local docs/tool evidence | `tools/glyph_serial_config_tool.py`, `docs/calibration/glyph_serial_active_config_writer_trace_2026-05-27.md` |
| Official configurator corpus fixtures | user-provided fixture evidence | `docs/calibration/export_corpus/official_glyph_configurator_2026-06-06/manifest.json` |
| Browser WebSerial implementation source | unknown | no inspected source provides it |
| Official WebSerial packet framing authority | unknown | no inspected source provides it |
| Official runtime-config device-write workflow authority | unknown | no inspected source provides it |
| Runtime-config storage or parser write path | forbidden/not approved | current docs and Step 10/13 packets stop before implementation |
| Firmware flashing automation | forbidden/not approved | current docs and workflow prohibit it |

## Exact Allowed Implementation

No Step 16 implementation is allowed by this audit.

The only allowed work in this branch is docs/tools/checker work that preserves:

- `DEVICE_WRITE_IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`;
- WebSerial/device write not implemented;
- firmware flashing automation not implemented;
- runtime-loaded config not implemented;
- current `Config` transport facts scoped to current `Config` only;
- hardware validation not claimed.

## Missing Decisions

Step 16 remains blocked until all of these are resolved:

- official or repo-authoritative WebSerial/browser transport source;
- official or repo-authoritative packet-framing source;
- explicit product approval for a write-capable workflow;
- explicit decision whether Step 16 targets current protobuf `Config`, future
  runtime config, or another payload;
- selected runtime-config storage/parser format if runtime config is involved;
- validation contract before write;
- backup, rollback, and recovery policy;
- readback and round-trip verification policy;
- hardware test plan and later hardware result;
- nunchuk scope remains `NOT_TESTED` unless separately validated.

## Safety And Rollback Requirements

Any future write-capable proposal must require:

- explicit user action before any write;
- no hidden writes;
- no automatic background writes;
- no default write mode;
- explicit target/port/device selection;
- payload validation before write;
- backup/read current config before write when source-backed;
- readback/round-trip validation when source-backed;
- bounded payload size and schema/version checks;
- failure handling that preserves or restores known-good state;
- recovery path that does not depend on hidden writes or unsafe flashing;
- hardware plan before implementation claims;
- hardware result before validation claims;
- no firmware flashing, UF2 copying, bootloader automation, or `RPI-RP2`
  mass-storage automation.

## Hardware Test Trigger Points

Hardware testing becomes required before merge of any future branch that
implements write-capable transport or changes firmware/device-write behavior.

Trigger points include:

- first live write-capable implementation;
- first runtime-config payload accepted by firmware;
- first readback/round-trip verification path;
- first reboot or power-cycle persistence claim;
- first rollback/recovery claim.

No hardware result is recorded by this branch.

## Forbidden Claims

- WebSerial/device write is not implemented.
- Runtime-loaded config is not implemented.
- Firmware binary/protobuf runtime-config parser integration is not implemented.
- Firmware-consuming manual runtime config load is not implemented.
- Firmware flashing automation is not implemented.
- UF2 flashing automation is not implemented.
- Bootloader automation is not implemented.
- Hidden device write is not implemented.
- Official configurator compatibility is not claimed.
- Universal official configurator compatibility is not claimed.
- Nunchuk validation is not claimed.
- Senscope neutral profile schema is not changed.
- Super Smash Bros. Ultimate game semantics are not changed.

## Stop Conditions Hit

- WebSerial/device-write implementation source authority is missing.
- Official packet-framing authority is missing.
- Official device-write workflow authority is missing.
- Runtime-config storage/parser authority is missing.
- Safety, rollback, and recovery policy are not resolved for Step 16.
- Hardware plan/result for write-capable workflow is absent.
