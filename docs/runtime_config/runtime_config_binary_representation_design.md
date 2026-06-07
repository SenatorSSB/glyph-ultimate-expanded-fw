# Runtime Config Binary Representation Design (Offline Preview Only)

## Purpose

This design defines an offline-only deterministic binary preview container for the current
MODE_ULTIMATE source-backed runtime table baseline.

It is an experiment artifact for docs/tools only and does **not** define a firmware parser,
device-write path, WebSerial transport, flashing automation, or official protobuf
compatibility.

## Scope

- source baseline input: current source-owned `MODE_ULTIMATE` `StickPoint[9]` tables
- deterministic binary preview serialization
- offline roundtrip verification from source to binary and back
- fixture generation and invalid-corpus checks

The design intentionally avoids firmware/HAL/config writes and does not consume the binary in runtime.

## Non-Goals

- do not modify firmware source
- no firmware runtime-config consumption
- no firmware/runtime bridge claim
- no device write path
- no WebSerial transport path
- no flashing automation
- no protobuf/nanopb format claim for this container

## Explicit stop line

This artifact stops before Step 13 firmware binary/protobuf parser integration.

## Binary Container

All fields are deterministic and ordered.

- magic: `0x47434647` (`GCFG`)
- version: `1` (`u8`)
- mode scope identity hash: `crc32("MODE_ULTIMATE")` (`u32`, little-endian)
- table count: `27` (`u8`)
- point count per table: `9` (`u8`)
- reserved byte: `0` (`u8`)
- table_id_order_count: `27` (`u8`)
- table id order: `27` bytes of canonical ids (`u8`), index order `0..26`
- table payload: `27 * 9 * 2` raw uint8 values as sequential `x,y` pairs in table order
- crc32: `u32` little-endian over header + order + payload

The container has no nested varints, tags, or protobuf descriptors.

## Canonical Table Order

Table order in the header is explicitly encoded and must be deterministic.
The source baseline canonical order is:

- `Default`, `ModeDefault`, `X1`, `X2`, `MX1`, `MX2`,
- `Y1`, `MY1`, `LayerNormalX`, `MLayerNormalX`,
- `LayerFlipper`, `MLayerFlipper`, `Y1Tilt1`, `MY1Tilt1`,
- `Y1LayerFlipper`, `MY1LayerFlipper`, `Y1LayerNormalX`,
- `MY1LayerNormalX`, `Tilt1`, `Tilt2`, `Tilt3`, `Tilt1Minus41`,
- `RT1RF4Custom`, `MTilt1`, `MTilt2`, `MTilt3`, `Lt1LowMagnitude`.

Each table stores exactly 9 points in `u8` `(x, y)` order.

## Validation Rules

`magic`, `version`, `mode scope hash`, table count, point count, CRC, order bytes, and payload
length are all required to match expected values to decode successfully.
Any violation is a decode failure and must remain offline-only.

## Integrity

CRC32 is computed over all bytes from the start of the header through the end of the payload.
The CRC field at the end must match. This is intentionally simple and explicit for offline QA.

## Source References

No runtime serialization behavior is inferred from protobuf/nanopb runtime loading.
All values come from the source-backed extractor and are provenance-tracked in preview JSON.

- `src/modes/Ultimate.cpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `tools/extract_glyph_identity_runtime_tables.py`

## Prohibited Claims

- no official protobuf compatibility claim
- no firmware runtime-loaded config claim
- no transport authority claim
- no profile schema change claim
- no gameplay semantics claim
