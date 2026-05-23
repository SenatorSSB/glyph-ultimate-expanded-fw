# G8f8 - Persistence And Config Storage Audit

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It does not change storage behavior, default config, firmware update behavior, config/protobuf schema, export/push workflow, hardware flashing, or gameplay semantics.

Audit question:

> What does the Pico `Persistence` source prove about config storage, validation, fallback, and preservation expectations?

Short answer: active Pico source stores a protobuf-encoded `Config` body in LittleFS file `config.bin`, preceded by a local header containing byte length and CRC32. Loading and setting config reset to nanopb defaults before decode so messages replace rather than merge with previous/default state. Missing or invalid saved config causes load/check failures; fallback behavior depends on callers and startup paths, not this persistence file alone.

## Storage File And Filesystem

`Persistence` starts LittleFS in its constructor and ends it in its destructor. Source: `HAL/pico/src/core/Persistence.cpp:28-33`.

The private filename is `config.bin`, and the stored protobuf body begins at `config_offset = sizeof(ConfigHeader)`. Source: `HAL/pico/include/core/Persistence.hpp:39-42`.

## Header Fields

The persistence header contains:

- `size_t config_size`
- `uint32_t config_crc`

Source: `HAL/pico/include/core/Persistence.hpp:24-29`.

The header is local storage metadata. It is not part of the raw protobuf config body returned by `LoadConfigRaw`, because raw loading seeks to `config_offset` before writing bytes. Source: `HAL/pico/src/core/Persistence.cpp:138-147`.

## Save Encoding Path

`Persistence::SaveConfig` first verifies nanopb can compute an encoded size for `Config`. It opens `config.bin` with `"w+"`, writes an empty header, encodes the protobuf body directly into the file, computes CRC32 over the body, then seeks back to write the final header with encoded byte count and CRC.

Source: `HAL/pico/src/core/Persistence.cpp:36-77`.

Capability claim: persisted config is source-backed as protobuf body plus local header.

## Load Decode Path

`Persistence::LoadConfig` opens `config.bin`, validates it with `CheckSavedConfig`, seeks to `config_offset`, resets the target `Config` to `Config_init_default`, then decodes the protobuf stream into it.

Source: `HAL/pico/src/core/Persistence.cpp:80-110`.

The reset-to-default behavior before decode means loading is intended as a complete replacement over nanopb defaults, not an incremental merge with whatever was previously in the struct.

## CRC And Validation Behavior

`CheckSavedConfig(File&)`:

- reads `ConfigHeader`;
- fails if fewer header bytes are present;
- computes body size as `file_size - config_offset`;
- fails if body size differs from `header.config_size`;
- computes CRC32 over the body and fails if it differs from `header.config_crc`.

Source: `HAL/pico/src/core/Persistence.cpp:154-180`.

`CheckSavedConfig()` opens `config.bin`, calls the file-based check, and closes the file. Source: `HAL/pico/src/core/Persistence.cpp:113-122`.

## Invalid Or Missing Config Fallback

In `Persistence` itself:

- missing file causes `SaveConfig` open failure or `LoadConfig`/`CheckSavedConfig`/`LoadConfigRaw` return failure, depending on method;
- invalid header, size, or CRC causes validation failure;
- failed protobuf decode in `LoadConfig` returns false after closing the file.

Source: `HAL/pico/src/core/Persistence.cpp:36-151`.

In `ConfiguratorBackend::HandleGetConfig`, invalid saved config produces `CMD_ERROR` and does not return raw config bytes. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-158`.

In `ConfiguratorBackend::HandleSetConfig`, decode failure writes `CMD_ERROR` and then attempts `persistence.LoadConfig(_config)` to restore the previous persisted config. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-175`.

Startup fallback to compiled defaults or other call-site behavior must be cited from the startup/caller source when used. This document does not claim profile preservation without hardware/source evidence.

## Defaults, Saved Config, And Install Modes

Persisted user config:

- Source-backed as LittleFS `config.bin` containing header plus protobuf body.
- Device-side get/set uses this saved config path.
- Source: `HAL/pico/include/core/Persistence.hpp:24-42`, `HAL/pico/src/core/Persistence.cpp:36-151`, `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-272`.

Compiled defaults:

- Pico baseline default config exists in `HAL/pico/include/config_defaults.hpp`.
- Glyph overrides define a Glyph-specific `default_config` under `config/glyph/common/include/glyph_overrides.hpp`.
- These are runtime default config evidence, not host UX evidence.

Official Clean/Fresh Install high-flash wipe behavior:

- Not source-backed by the inspected persistence code alone.
- Any claim about a high-flash wipe, Clean/Fresh Install, or official updater behavior needs direct source/docs from that workflow.

Generated custom firmware Update-style preservation expectations:

- LittleFS storage and separate firmware image concepts make preservation plausible in some update styles, but this audit does not prove it for real hardware or tooling.
- Treat preservation across updates as `UNKNOWN` unless a source-backed updater/flashing path explicitly preserves LittleFS and is tested or documented.

## Source References

| file/path | symbol/function | observed behavior | capability claim | confidence |
| --- | --- | --- | --- | --- |
| `HAL/pico/include/core/Persistence.hpp:24-29` | `Persistence::ConfigHeader` | Header has `config_size` and `config_crc` | Local persisted config header fields are source-backed | High |
| `HAL/pico/include/core/Persistence.hpp:39-42` | `config_offset`, `config_filename` | Body offset is header size; file is `config.bin` | Config filename and body offset are source-backed | High |
| `HAL/pico/src/core/Persistence.cpp:28-33` | constructor/destructor | Calls `LittleFS.begin()` and `LittleFS.end()` | LittleFS usage is source-backed | High |
| `HAL/pico/src/core/Persistence.cpp:36-77` | `SaveConfig` | Encodes `Config` to file body, computes CRC, writes header | Save encoding path is source-backed | High |
| `HAL/pico/src/core/Persistence.cpp:80-110` | `LoadConfig` | Validates, seeks to body, resets to `Config_init_default`, decodes protobuf | Load/decode replacement behavior is source-backed | High |
| `HAL/pico/src/core/Persistence.cpp:113-122` | `CheckSavedConfig()` | Opens saved config and validates it | Saved config validity check is source-backed | High |
| `HAL/pico/src/core/Persistence.cpp:125-151` | `LoadConfigRaw` | Optionally validates, seeks to body, writes raw protobuf bytes | Raw saved config body export from device storage is source-backed | High |
| `HAL/pico/src/core/Persistence.cpp:154-180` | `CheckSavedConfig(File&)` | Checks header, body length, and CRC32 | CRC and size validation are source-backed | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-158` | `HandleGetConfig` | Fails get-config on invalid saved config | Device-side get fallback/error behavior is source-backed | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-175` | `HandleSetConfig` decode failure | Restores previous config from persistence after decode failure | Decode failure restore attempt is source-backed | High |

## Conclusion

Persistence support is source-backed for saved protobuf config storage in LittleFS with a local size/CRC header. The source does not prove cross-update preservation on hardware, official Clean/Fresh Install behavior, host configurator UX, export format support, or Senscope profile preservation. Any future claims about preservation across update styles must cite updater/flashing source or hardware-tested evidence.
