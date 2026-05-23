# G8f8 - ConfiguratorBackend Source Audit

Status: docs-only source audit
Date: 2026-05-24

## Scope

This document is docs-only and source-audit only. It does not implement firmware behavior, host tooling, Senscope export generation, push-to-device behavior, upload/flashing workflows, app-side TypeScript, or gameplay semantic claims.

Audit question:

> What does the device-side `ConfiguratorBackend` source prove, and what must remain separate from host UX, export, push, or flashing claims?

Short answer: the active Pico configurator backend source supports device-side command handling for device info, raw saved-config get, protobuf config set with validation, firmware reboot, and bootloader reboot. This is not by itself approval for Senscope export generation, push-to-device workflow, host configurator UX support, or firmware flashing/update support.

## Command Handling Summary

`ConfiguratorBackend::SendReport` reads one command byte from a COBS-wrapped stream and dispatches:

- `CMD_GET_DEVICE_INFO` to `HandleGetDeviceInfo`.
- `CMD_GET_CONFIG` to `HandleGetConfig`.
- `CMD_SET_CONFIG` to `HandleSetConfig`.
- `CMD_REBOOT_FIRMWARE` to `reboot_firmware`.
- `CMD_REBOOT_BOOTLOADER` to `reboot_bootloader`.
- unknown or unspecified commands to `HandleUnknownCommand`.

Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:49-81`.

The backend constructor wraps a single `Stream` in `packetio::COBSStream` for input and `packetio::COBSPrint` for output, stores a reference to the active `Config`, and sets a USB VID/PID through `TinyUSBDevice.setID`. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:29-42` and `HAL/pico/include/comms/ConfiguratorBackend.hpp:18-45`.

## Device Info Command

`HandleGetDeviceInfo` builds a `DeviceInfo` message from `FIRMWARE_NAME`, `FIRMWARE_VERSION`, and `DEVICE_NAME`, verifies that nanopb can compute an encoded size, writes `CMD_SET_DEVICE_INFO`, encodes the protobuf message to the output COBS stream, and ends the packet. On encoding-size failure it writes `CMD_ERROR`.

Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:127-145`.

Capability claim: device-side source supports a command response containing firmware/device identity fields. This does not prove any host UI presentation.

## Config Get Command

`HandleGetConfig` first calls `persistence.CheckSavedConfig()`. If validation fails, it emits `CMD_ERROR` with "Config file is invalid". If validation passes, it writes `CMD_SET_CONFIG`, then writes raw protobuf config bytes from `persistence.LoadConfigRaw(_out, false)` into the response packet.

Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-158`; raw loading behavior is in `HAL/pico/src/core/Persistence.cpp:125-151`.

Capability claim: device-side source supports returning the saved raw protobuf config body from LittleFS when the saved file is valid. This is not host export-format evidence.

## Config Set Command

`HandleSetConfig` resets the in-memory config to `Config_init_default`, decodes a protobuf `Config` from the input COBS stream, validates several cross-reference bounds, persists accepted config with `persistence.SaveConfig`, and replies with `CMD_SUCCESS`.

On protobuf decode failure it writes `CMD_ERROR`, then attempts to restore `_config` from persistence by calling `persistence.LoadConfig(_config)`. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-175`.

Validation gates visible in source:

- `default_backend_config` must not exceed `communication_backend_configs_count`.
- Each `communication_backend_configs[i].default_mode_config` must not exceed `game_mode_configs_count`.
- `keyboard_mode_config > 0` requires `mode_id == MODE_KEYBOARD`.
- `custom_mode_config > 0` requires `mode_id == MODE_CUSTOM`.
- `keyboard_mode_config` must not exceed `keyboard_modes_count`.
- `custom_mode_config` must not exceed `custom_modes_count`.

Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:177-263`.

Capability claim: device-side source supports protobuf config set, validation, and persistence. It does not prove complete semantic validity of every field, external host UX support, or Senscope profile realization.

## Reboot Commands

`CMD_REBOOT_FIRMWARE` dispatches directly to `reboot_firmware`, and `CMD_REBOOT_BOOTLOADER` dispatches directly to `reboot_bootloader`. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:69-73`.

Capability claim: device-side source exposes reboot command handlers. This does not prove a firmware update workflow, flashing workflow, recovery process, or safe host-side UX.

## Raw Config Byte Handling

The get path returns the stored protobuf body from LittleFS without the local persistence header. `Persistence::LoadConfigRaw` seeks past the header offset, then writes each file byte from the protobuf body to the provided `Print`. Source: `HAL/pico/src/core/Persistence.cpp:125-151`; `HAL/pico/include/core/Persistence.hpp:39-42`.

The set path decodes a protobuf `Config` from the stream rather than writing raw bytes directly to storage; persistence re-encodes the accepted in-memory `Config` to the file body. Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-175` and `HAL/pico/src/core/Persistence.cpp:36-77`.

Capability claim: the configurator path is protobuf config transport, not arbitrary file transport.

## Packet And Stream Handling

Conceptually, the backend is a command stream layered over PacketIO COBS wrappers:

- input command bytes are read with `_in.read()` when the base stream has bytes;
- response packets begin with a command byte and are finished by `_out.end()`;
- `SkipToNextPacket` calls `_in.next()` after command handling;
- `ReadPacket` can read until COBS end-of-packet or a max buffer length, although the current command handlers primarily use protobuf stream decoding directly from `_in`.

Source: `HAL/pico/src/comms/ConfiguratorBackend.cpp:84-124`.

## Source Reference Table

| file/path | symbol/function | observed behavior | capability claim | scope | confidence |
| --- | --- | --- | --- | --- | --- |
| `HAL/pico/include/comms/ConfiguratorBackend.hpp:18-45` | `ConfiguratorBackend` members | Holds COBS input/output wrappers, base stream, and config reference | Configurator backend is a device-side command/packet transport | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:29-42` | constructor | Initializes COBS wrappers and sets TinyUSB ID | Device-side configurator has USB-facing stream setup | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:49-81` | `SendReport` | Dispatches command byte to get info, get config, set config, reboot firmware, reboot bootloader, or error | Device-side command dispatch is source-backed | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:84-124` | `ReadPacket`, `ReadByte`, `SkipToNextPacket`, `WritePacket` | Reads/writes packetized command stream with PacketIO COBS wrappers | Packet/stream handling exists at device side | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:127-145` | `HandleGetDeviceInfo` | Encodes `DeviceInfo` response from firmware/device macros | Device info command is source-backed | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-158` | `HandleGetConfig` | Validates saved config, writes `CMD_SET_CONFIG`, sends raw protobuf config body | Device-side config get is source-backed for saved valid configs | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:161-175` | `HandleSetConfig` decode path | Resets to nanopb defaults, decodes streamed `Config`, restores from persistence on decode error | Device-side set config decode path is source-backed | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:177-263` | `HandleSetConfig` validation gates | Checks backend/mode/custom/keyboard index consistency | Structural validation gates are source-backed | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:265-272` | `HandleSetConfig` save path | Persists accepted config and replies success | Device-side set plus persistence is source-backed | DEVICE_SIDE_CONFIG_TRANSPORT | High |
| `HAL/pico/src/comms/ConfiguratorBackend.cpp:69-73` | reboot dispatch | Calls firmware or bootloader reboot helpers | Reboot command dispatch is source-backed | DEVICE_SIDE_REBOOT_COMMAND | High |
| `HAL/pico/src/core/Persistence.cpp:125-151` | `Persistence::LoadConfigRaw` | Seeks past config header and writes protobuf body bytes | Raw saved config body return is source-backed | DEVICE_SIDE_CONFIG_TRANSPORT | High |

## Boundary Classification

| surface | status | source-backed statement | boundary |
| --- | --- | --- | --- |
| device-side config get | `SOURCE_BACKED` | Valid saved config can be returned as raw protobuf body | Does not prove host export UX |
| device-side config set | `SOURCE_BACKED` | Streamed protobuf `Config` can be decoded, validated, persisted | Does not approve Senscope export/push |
| host-side configurator UX | `UNKNOWN` | No host UI source was inspected in this repo batch | Do not claim UX support |
| Senscope export generation | `UNSUPPORTED_BY_CURRENT_SOURCE` | No Senscope export artifact generator exists in inspected source | Do not generate files |
| push-to-device workflow | `UNSUPPORTED_BY_CURRENT_SOURCE` as an approved workflow | Device-side set exists, but end-to-end host workflow is not established here | Stop before using commands on a device |
| firmware flashing/update | `UNSUPPORTED_BY_CURRENT_SOURCE` as an approved workflow | Reboot-to-bootloader command exists, but flashing workflow is not implemented or approved here | Stop before update/flashing |

## Conclusion

Device-side get/set support is source-backed. Device-side set-config support is not by itself approval for Senscope export, push, upload, host UX, or firmware flashing workflows. A future Senscope adapter may cite these device-side paths as transport evidence only after separately approved export/push scope, schema authority, safety checks, and host workflow evidence exist.
