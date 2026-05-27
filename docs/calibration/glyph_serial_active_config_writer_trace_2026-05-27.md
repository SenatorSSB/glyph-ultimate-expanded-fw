# Glyph Serial Active Config Writer Trace - 2026-05-27

## Why Path B

- Path B is active because the Limit Labs configurator webapp is closed-source from this repo perspective and was observed lossy for standalone LT3 import/apply (`BTN_LT3 -> BTN_LT3` not taking effect on hardware post webapp path).
- This trace focuses on a repo-local, guarded host-side serial config writer over the firmware's existing configurator protocol.

## Source-Supported Verdict

- Host-side serial config write is source-supported at the firmware/protocol layer.
- Device-side path exists and is explicit:
  - command dispatch: `HAL/pico/src/comms/ConfiguratorBackend.cpp`
  - set handler: `ConfiguratorBackend::HandleSetConfig`
  - persistence write: `Persistence::SaveConfig`
- The JSON artifact is **not** the wire format. It must be transformed into protobuf `Config` bytes before `CMD_SET_CONFIG`.

## Protocol Trace

### Command IDs (source-confirmed)

From `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto` and generated `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`:

- `CMD_GET_CONFIG = 3`
- `CMD_SET_CONFIG = 4`
- `CMD_ERROR = 5`
- `CMD_SUCCESS = 6`

### Framing

- Backend wraps the serial stream with PacketIO COBS wrappers (`packetio::COBSStream`, `packetio::COBSPrint`) in `HAL/pico/include/comms/ConfiguratorBackend.hpp`.
- `COBSPrint::end()` writes a trailing `0x00` packet terminator (`.pio/libdeps/glyph_mk6/PacketIO/src/cobs/Print.h`).
- `COBSStream` treats `0x00` as end-of-packet (`EOP`) (`.pio/libdeps/glyph_mk6/PacketIO/src/cobs/Stream.h`).

### Length Encoding

- No separate protocol length field is used at command packet level.
- Packet boundaries come from COBS framing and the `0x00` terminator.

### Payload Encoding

- Command packet body starts with one command byte.
- Remaining bytes are command payload.
- For config transfer, payload is protobuf `Config` message bytes (`pb_decode` in set path, raw protobuf bytes in get path).

### ACK / Response Handling

- `CMD_GET_CONFIG` request:
  - success response command: `CMD_SET_CONFIG` with raw protobuf `Config` payload.
  - failure response command: `CMD_ERROR` with text message payload.
- `CMD_SET_CONFIG` request:
  - success response command: `CMD_SUCCESS` (empty payload).
  - failure response command: `CMD_ERROR` with text message payload.

### Checksum / CRC

- No transport-layer CRC/checksum is present in configurator command packets.
- Persistence layer uses CRC32 in `config.bin` header:
  - `config_size`
  - `config_crc`
  - Source: `HAL/pico/include/core/Persistence.hpp`, `HAL/pico/src/core/Persistence.cpp`.

## Firmware Handling Path

- Incoming command byte dispatch:
  - `ConfiguratorBackend::SendReport`
- Set-config path:
  - `ConfiguratorBackend::HandleSetConfig`
  - `pb_decode(..., Config_fields, &_config)`
  - validation gates
  - `persistence.SaveConfig(_config)`
  - `CMD_SUCCESS`/`CMD_ERROR` response
- Get-config path:
  - `ConfiguratorBackend::HandleGetConfig`
  - `persistence.CheckSavedConfig()`
  - `CMD_SET_CONFIG` + `persistence.LoadConfigRaw(_out, false)`

## Artifact Format Implication

- `docs/calibration/artifacts/glyph_ultimate_mvp_lt3_active_config_PROFILE.json` cannot be sent directly over serial.
- Required host steps for write:
  1. Parse/validate artifact JSON.
  2. Convert JSON to protobuf `Config` message bytes (schema: `config.proto`).
  3. Send `CMD_SET_CONFIG` packet with protobuf payload.
  4. Expect `CMD_SUCCESS`.
  5. Read back with `CMD_GET_CONFIG` and verify required bindings.

## Serial Port Expectations (macOS)

- Live access must use an explicit user-provided port path.
- Example only: `/dev/cu.usbmodem2101` (from observed paired Pico session).
- Do not treat that example as universal; require `--port` each run.

## Safety Model For Repo-Local Tool

- default mode is dry-run / read-only
- explicit `--write` required for live config write
- explicit `--read` required for live read
- explicit `--port` required for live device access
- explicit `--artifact` required for dry-run encode and write
- artifact validation required before write
- read current config before write when `GET_CONFIG` is available
- readback verify after write when `GET_CONFIG` is available
- never flash firmware
- never copy UF2
- never touch `RPI-RP2` mass-storage workflow

