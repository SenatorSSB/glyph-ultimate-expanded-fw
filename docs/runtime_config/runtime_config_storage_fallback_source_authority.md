# Runtime Config Storage/Fallback Source Authority

Status label: DESIGN_ONLY_BLOCKED_BY_SOURCE_AUTHORITY.

## Purpose

This packet records the Step 10 source-authority audit for future
runtime-config storage/fallback work.

It does not implement runtime-loaded config storage, runtime-loaded config
consumption, WebSerial/device write, protobuf/binary firmware parsing, firmware
flashing automation, migration, rollback, or a new firmware fallback behavior.

## Inspected Source And Docs

- `README.md`
- `AGENTS.md`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`
- `docs/runtime_config/runtime_config_semantics_evaluator_bridge.md`
- `docs/runtime_config/runtime_loaded_config_schema_design.md`
- `docs/runtime_config/firmware_interpreter_architecture_spec.md`
- `docs/runtime_config/fixtures/current_baseline_runtime_config_semantics_bridge.json`
- `docs/runtime_config/fixtures/current_baseline_extracted_config_preview.json`
- `docs/runtime_config/fixtures/invalid_runtime_config_semantics_cases.json`
- `src/modes/Ultimate.cpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `tools/extract_glyph_identity_runtime_tables.py`
- `tools/check_glyph_identity_runtime_table_source_sync.py`
- `tools/check_glyph_runtime_config_semantics_evaluator_bridge.py`
- `platformio.ini`
- `HAL/pico/include/core/Persistence.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `config/glyph/common/src/config.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md`
- `docs/calibration/fixtures/glyph_storage_transport_source_authority_registry_2026-06-03.json`
- `tools/check_glyph_storage_transport_source_authority_registry.py`

The audit also ran the required repository search:

```text
rg -n "flash|eeprom|storage|persist|filesystem|littlefs|save|load|config|profile|protobuf|pb_encode|pb_decode|nanopb|settings|boot|fallback|crc|checksum" src include lib tools docs platformio.ini
```

## Implementation Decision

`IMPLEMENTATION_ALLOWED_BY_SOURCE_AUDIT=false`

Step 10 firmware storage/fallback implementation is blocked by missing source
authority and unresolved implementation decisions.

The branch may document source authority, architecture constraints, future
gates, and offline-only representation tooling. It must not modify firmware to
consume runtime-loaded config from storage.

## Source-Backed Capabilities Found

Existing source-backed persistence exists for the current protobuf `Config`
object on Pico builds:

- `HAL/pico/include/core/Persistence.hpp` defines a `ConfigHeader` with
  `config_size` and `config_crc`.
- `HAL/pico/include/core/Persistence.hpp` names the current persisted file as
  `config.bin`.
- `HAL/pico/src/core/Persistence.cpp` uses LittleFS for current config
  persistence.
- `HAL/pico/src/core/Persistence.cpp` uses nanopb `pb_get_encoded_size` and
  `pb_encode` for current `Config_fields` writes.
- `HAL/pico/src/core/Persistence.cpp` computes CRC32 over the persisted
  protobuf body and stores the checksum in the local header.
- `HAL/pico/src/core/Persistence.cpp` checks saved config length and CRC before
  current config decode.
- `HAL/pico/src/core/Persistence.cpp` resets the in-memory `Config` to
  `Config_init_default` before protobuf decode.
- `config/glyph/common/src/config.cpp` initializes the global config from
  `glyph_default_config()`.
- `config/glyph/common/src/config.cpp` attempts to load the saved config during
  setup and saves the in-memory default if loading fails.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` validates saved config before
  returning raw `CMD_GET_CONFIG` payload bytes.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp` decodes `CMD_SET_CONFIG` with
  nanopb, performs bounded reference checks, and saves only after the accepted
  `Config` passes those checks.
- `platformio.ini` declares nanopb, HayBox-proto, LittleFS filesystem size,
  PacketIO, and CRC32 dependencies for relevant builds.

## Source-Backed Runtime-Config Boundary Found

`src/modes/UltimateRuntimeConfigInterpreter.hpp` is source-backed for the
current source-owned interpreter baseline only.

It provides:

- source-owned 27-table `StickPoint[9]` runtime table metadata;
- validation-before-use helpers for `RuntimeConfigView`;
- fallback-to-known-good source-owned baseline helpers;
- explicit caveats that the values are not runtime-loaded config and are not
  serial/device write behavior.

`src/modes/Ultimate.cpp` currently resolves `runtime_config` from
`kSourceOwnedCurrentBaselineRuntimeConfig` or `kKnownGoodRuntimeConfig`. It does
not load runtime config from storage.

## Fixture-Observed And User-Provided Evidence

Prior calibration packets and host-side tools record historical profile/config
experiments and a guarded serial config tool. Those are useful evidence for
offline review, but they are not source authority for a new runtime-loaded
Ultimate table storage path.

The official configurator corpus is primary for config/profile fixture evidence
when the correction packet and manifest are present. It is still not firmware
runtime-loaded storage authority.

## Unsupported Assumptions

The following assumptions are not supported by inspected source authority:

- a separate runtime-config storage slot exists;
- the current `config.bin` path may safely store future runtime table payloads;
- current config persistence is an atomic rollback architecture;
- current config persistence defines runtime-config fallback semantics;
- current config persistence defines runtime-config migration semantics;
- current device-side configurator command handling authorizes a new runtime
  config write or load path;
- protobuf/nanopb build dependencies authorize a runtime table protobuf format;
- external-remapper observations are official configurator or firmware source
  authority.

The existing LittleFS `config.bin` path is source authority for current
persisted `Config` behavior only. It is not source authority for a future
runtime-loaded config interpreter, separate runtime config storage slot, atomic
rollback design, migration policy, WebSerial/device-write workflow, or
protobuf/binary export implementation.

## Unknowns

- runtime-loaded config storage location;
- profile-scoped versus global runtime config ownership;
- maximum runtime config size;
- runtime config binary/protobuf schema authority;
- validation entry point in firmware;
- migration policy;
- atomic write, rollback, and recovery policy;
- hardware test trigger points for an implementation branch;
- latency/performance requirements;
- official configurator compatibility for a runtime table payload;
- whether a future runtime config may share the current `config.bin` file.

## Forbidden Or Not Approved

- WebSerial/device write is not implemented.
- Direct device mutation workflow is not implemented.
- Firmware flashing automation is not implemented.
- Firmware binary/protobuf runtime-config parser integration is not implemented.
- Firmware-consuming manual runtime config load path is not implemented.
- External adapter output generation is not implemented.
- Senscope neutral profile schema changes are not implemented.
- Super Smash Bros. Ultimate game-semantic changes are not implemented.

## Stop Conditions Hit

- Runtime-loaded storage implementation approval is missing.
- Runtime-loaded config storage source authority is missing.
- Runtime-loaded fallback policy remains ambiguous and unresolved.
- Runtime-loaded representation and migration policy are undecided.
- Runtime-loaded config hardware validation plan/result are absent.

## Allowed Future Use Of This Packet

This packet may be cited to justify design-only work and offline-only binary
representation experiments.

It must not be cited as approval to implement firmware storage, firmware
runtime-loaded config consumption, WebSerial/device write, firmware flashing
automation, or official protobuf compatibility.
