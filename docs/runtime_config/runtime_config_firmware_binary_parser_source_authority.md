# Runtime Config Firmware Binary Parser Source Authority

Status label: DESIGN_ONLY_BLOCKED_BY_SOURCE_AUTHORITY.

## Purpose

This packet records the Step 13 source-authority audit for future firmware
binary/protobuf runtime-config parser integration.

It does not implement firmware parser integration, runtime-loaded config
consumption, runtime-config storage, WebSerial/device write, protobuf binary
write, firmware flashing automation, rollback mutation, or profile
import/export.

## Inspected Files And Tools

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
- `docs/runtime_config/fixtures/current_baseline_runtime_config_binary_preview.json`
- `docs/runtime_config/fixtures/invalid_runtime_config_binary_cases.json`
- `src/modes/Ultimate.cpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `tools/glyph_runtime_config_binary_roundtrip.py`
- `tools/check_glyph_runtime_config_binary_offline_roundtrip.py`
- `tools/check_glyph_runtime_config_storage_fallback.py`
- `HAL/pico/include/core/Persistence.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/include/comms/ConfiguratorBackend.hpp`
- `HAL/pico/src/comms/backend_init.cpp`
- `config/glyph/common/src/config.cpp`
- `platformio.ini`

The audit also inspected the requested repository searches:

```text
rg -n "pb_decode|pb_encode|nanopb|Config_fields|config.bin|LittleFS|crc|checksum|Persistence|LoadConfig|SaveConfig|CMD_SET_CONFIG|CMD_GET_CONFIG|serial|PacketIO" src include lib HAL config tools docs platformio.ini
find src include HAL config tools docs -maxdepth 5 -type f
```

## Implementation Decision

`IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`

Step 13 firmware binary/protobuf parser integration remains blocked by missing
source authority, unresolved product decisions, and absent hardware validation
for a firmware-consuming runtime-loaded config path.

This branch may define the future implementation boundary, validation sequence,
approval gates, and hardware-test template. It must not make firmware consume
the Step 12 offline binary preview or any runtime-loaded config payload.

## Source-Backed Parser And Persistence Mechanisms

Existing source-backed mechanisms are limited to the current firmware `Config`
object and the source-owned Ultimate runtime table baseline:

- `HAL/pico/include/core/Persistence.hpp` defines `Persistence::ConfigHeader`
  with `config_size` and `config_crc`, names `config.bin`, and exposes
  `SaveConfig`, `LoadConfig`, `CheckSavedConfig`, and `LoadConfigRaw`.
- `HAL/pico/src/core/Persistence.cpp` uses LittleFS for `config.bin`.
- `HAL/pico/src/core/Persistence.cpp` uses nanopb `pb_get_encoded_size` and
  `pb_encode` for current `Config_fields` writes.
- `HAL/pico/src/core/Persistence.cpp` validates the stored config body length
  and CRC32 before current `Config` decode.
- `HAL/pico/src/core/Persistence.cpp` resets the in-memory `Config` to
  `Config_init_default` before `pb_decode`.
- `config/glyph/common/src/config.cpp` initializes global `Config` from
  `glyph_default_config()`, attempts `persistence.LoadConfig(config)` during
  setup, and saves defaults when loading fails.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` handles `CMD_GET_CONFIG` and
  `CMD_SET_CONFIG` for the existing protobuf `Config`.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` decodes `CMD_SET_CONFIG` with
  nanopb, applies bounded reference checks, saves accepted `Config`, and
  restores persisted config after decode failure.
- `HAL/pico/src/comms/backend_init.cpp` can persist the current `Config` after
  watchdog override/default selection updates.
- `platformio.ini` declares nanopb, HayBox-proto, LittleFS filesystem size,
  PacketIO, and CRC32 dependencies for relevant Pico builds.
- `src/modes/UltimateRuntimeConfigInterpreter.hpp` defines the source-owned
  `RuntimeConfigView`, 27 `StickPoint[9]` table metadata, validation helpers,
  and fallback-to-known-good helpers.
- `src/modes/Ultimate.cpp` uses
  `kSourceOwnedCurrentBaselineRuntimeConfig` or `kKnownGoodRuntimeConfig` for
  Ultimate analog outputs.

These mechanisms are source-backed facts about current behavior. They are not
approval to add a new runtime table parser or storage path.

## Fixture-Observed Offline Binary Evidence

`docs/runtime_config/fixtures/current_baseline_runtime_config_binary_preview.json`
and `tools/glyph_runtime_config_binary_roundtrip.py` define and verify an
offline-only deterministic binary preview container:

- magic `GCFG`;
- binary format version `1`;
- mode-scope hash for `MODE_ULTIMATE`;
- `27` tables with `9` points each;
- canonical table-id order;
- raw `uint8` x/y payload bytes;
- CRC32 over header, order, and payload;
- fixture size `530` bytes.

`docs/runtime_config/fixtures/invalid_runtime_config_binary_cases.json` is an
offline negative corpus for this preview. It is fixture-observed docs/tools
evidence only. It is not firmware input, not a protobuf format, not a storage
format, not a transport format, and not official configurator compatibility
evidence.

## What Current Config Persistence Supports

Current `Config` persistence supports:

- file-backed Pico persistence for the current protobuf `Config` object;
- `config.bin` with a local header containing body size and CRC32;
- nanopb encode/decode of `Config_fields`;
- validation of saved `Config` body length and CRC before decode;
- returning the saved raw protobuf `Config` body from `CMD_GET_CONFIG`;
- receiving and validating a new protobuf `Config` from `CMD_SET_CONFIG`;
- falling back at boot by saving `glyph_default_config()` when
  `persistence.LoadConfig(config)` fails.

These claims are source-backed by the inspected Pico persistence, setup, and
ConfiguratorBackend files.

## What Current Config Persistence Does Not Support

Current source does not support or approve:

- a separate runtime-config binary or protobuf parser;
- firmware consumption of the Step 12 offline binary preview;
- firmware consumption of runtime-loaded Ultimate table data;
- a runtime-config storage slot, filename, flash address, or boot-time read;
- storing runtime table data inside current `config.bin`;
- profile-scoped versus global runtime-config ownership;
- runtime-config maximum size or memory budget;
- migration between runtime-config schema versions;
- atomic two-slot rollback for runtime-config payloads;
- recovery mutation, deletion, or replacement policy for invalid payloads;
- WebSerial/device write for runtime config;
- firmware flashing automation;
- official protobuf or universal official configurator compatibility.

## Classification

| Topic | Classification | Evidence |
| --- | --- | --- |
| Current `Config` protobuf persistence in `config.bin` | source-backed | `HAL/pico/include/core/Persistence.hpp`, `HAL/pico/src/core/Persistence.cpp` |
| Current `CMD_GET_CONFIG` / `CMD_SET_CONFIG` handling | source-backed | `HAL/pico/src/comms/ConfiguratorBackend.cpp` |
| Boot fallback to default `Config` after failed load | source-backed | `config/glyph/common/src/config.cpp` |
| Source-owned Ultimate runtime table boundary | source-backed | `src/modes/Ultimate.cpp`, `src/modes/UltimateRuntimeConfigInterpreter.hpp` |
| Step 12 raw binary preview layout and invalid cases | fixture-observed | `tools/glyph_runtime_config_binary_roundtrip.py`, binary preview fixtures |
| Reusing `config.bin` for runtime table payloads | unknown | no inspected source defines this |
| Firmware parser entry point for runtime table payloads | unknown | no inspected source defines this |
| Runtime-loaded config implementation | forbidden/not approved | current docs require product approval and source authority |
| WebSerial/device write, flashing automation | forbidden/not approved | current docs and workflow prohibit implementation in this branch |

## Missing Decisions

- whether Step 13 should target the Step 12 raw preview, a protobuf schema, or a
  different firmware-owned format;
- parser entry point and ownership;
- storage filename, flash region, or current `config.bin` reuse decision;
- boot-time read timing and mode-scope activation decision;
- profile-scoped versus global runtime-config ownership;
- maximum payload size and memory budget;
- error reporting and diagnostics surface;
- version support and migration policy;
- rollback and recovery mutation policy;
- hardware validation artifact and result process;
- explicit user product approval for firmware behavior implementation.

## Future Approval Gates

A future implementation branch must pass all of these gates before firmware can
consume a runtime-config binary/protobuf payload:

- explicit user product approval for firmware behavior implementation;
- selected firmware-owned parser format and schema/version policy;
- source-backed storage/boot entry point decision;
- source-backed fallback and recovery policy;
- source-backed checksum/CRC policy;
- memory and maximum-size review;
- build gate for the selected firmware target;
- hardware test plan and recorded hardware result;
- rollback/recovery evidence when recovery is testable;
- confirmation that nunchuk remains `NOT_TESTED` unless separately validated.

## Non-Claims

- Firmware parser implementation is not implemented.
- Runtime-loaded config consumption is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- Firmware flashing automation is not implemented.
- Nunchuk validation is not claimed.
- Official protobuf compatibility is not claimed.
- Universal official configurator compatibility is not claimed.
- Senscope neutral profile schema is not changed.
- Super Smash Bros. Ultimate game semantics are not changed.

## Stop Conditions Hit

- Runtime-loaded config implementation approval is missing.
- Firmware parser format authority is missing.
- Storage and boot-time read authority are missing.
- Migration, rollback, and recovery policies are unresolved.
- Hardware test plan exists only as a future template; no hardware result exists
  for firmware binary/protobuf parser integration.
