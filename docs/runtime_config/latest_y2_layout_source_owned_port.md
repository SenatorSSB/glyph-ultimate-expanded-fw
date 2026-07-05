# Latest Y2 Layout Source-Owned Port

Status: FIRMWARE_BEHAVIOR / WAITING_FOR_HARDWARE_TEST.

Branch:
`runtime-config-latest-y2-layout-source-owned-port`

Base branch: `configurator`.

Reference branch: `codex/update-custom-modifier-tables-y2`.

This branch restores the full required latest Y2 layout onto current
`configurator` while preserving the source-owned active runtime config
publication boundary. It does not split Tilt3-only for hardware testing. The
next hardware run is for the full restored layout.

## Active Publication Boundary

- `GetActiveRuntimeConfigState()` still publishes
  `&kSourceOwnedCurrentBaselineRuntimeConfig`.
- `ResolveActiveRuntimeConfig()` still dereferences
  `GetActiveRuntimeConfigState().active_view`.
- `UpdateAnalogOutputs(...)` still consumes the active runtime config through
  `ResolveActiveRuntimeConfig()`.
- Active view selection unchanged: `false`.
- RuntimeConfigView replacement is not used.
- Generated active wrapper used: `false`.
- `candidate.view` is not active.
- RAM-backed active table publication is not used.
- Runtime-loaded config, persistent storage, WebSerial/device write,
  backend/config.pb write path, and flashing automation are not implemented.
- The low-level root cause for failed active-publication diagnostics remains
  unproven.
- Nunchuk remains NOT_TESTED.

## Source Changes

Changed firmware source files:

- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `src/modes/Ultimate.cpp`

`src/modes/UltimateIdentityRuntimeTables.hpp` now contains source-owned
`kY2Table` and the latest `kTilt3Table` values.

`src/modes/UltimateRuntimeConfigInterpreter.hpp` integrates Y2 into the
source-owned runtime table identity/order/count path by increasing the table
count to 28 and adding `RuntimeTableId::Y2`, `kY2Table`, and the corresponding
symbol lookup.

`src/modes/Ultimate.cpp` moves the RF sublayer-bearing role from Y1/LT2 to
Y2/LT3, removes LT3 L/R digital output behavior, and keeps Y2 priority below
RT/RF modifiers.

## Required Table Values

Tilt3:

| Direction | x | y |
| --- | ---: | ---: |
| 1 | 69 | 82 |
| 2 | 128 | 83 |
| 3 | 187 | 82 |
| 4 | 69 | 128 |
| 5 | 128 | 128 |
| 6 | 187 | 128 |
| 7 | 76 | 169 |
| 8 | 128 | 179 |
| 9 | 180 | 169 |

Y2:

| Direction | x | y |
| --- | ---: | ---: |
| 1 | 69 | 78 |
| 2 | 128 | 78 |
| 3 | 187 | 78 |
| 4 | 61 | 128 |
| 5 | 128 | 128 |
| 6 | 195 | 128 |
| 7 | 61 | 164 |
| 8 | 128 | 174 |
| 9 | 195 | 164 |

## Routing And Role Facts

- LT3 selects Y2 and emits no L/R digital.
- Y2+RF1 alone keeps base A.
- Y2+RF1+RF4 emits X.
- Y1+RF1 no longer emits X sublayer.
- Y2+RF2 alone keeps base B.
- Y2+RF2 alone does not force up.
- Y2+RF2+RF4 forces up without base B.
- Y1+RF2 no longer forces up.
- Y2+RF3 emits B and uses LayerNormalX where applicable.
- Y1+RF3 no longer emits B sublayer.
- Y2+RF4 uses LayerFlipper where applicable.
- Y1+RF4 no longer flipper sublayer.
- Y2+RT1 selects Tilt2.
- Y2+RT1+RF4 selects Tilt3.
- Y2 priority remains below RT/RF modifiers.
- Y1 is a simple modifier only.
- Y1 no longer owns RF1/RF2/RF3/RF4 sublayer behavior.
- The former Y1 RF sublayer behaviors are migrated to Y2.

## Evidence Basis

- RuntimeConfigView replacement and active publication replacement paths failed
  hardware diagnostics.
- Source-owned table-content replacement passed the RF5 forced A+Up and LT6
  forced A+Down hardware boundary.
- This branch keeps the accepted source-owned publication boundary and replaces
  table content and routing in source-owned firmware code.
- This branch changes active behavior and therefore has hardware test required
  before merge.

## Explicit Non-Claims

- This is not a hardware result.
- Nunchuk remains NOT_TESTED.
- Root cause remains unproven.
- Runtime-loaded config is not implemented.
- Persistent storage is not implemented.
- WebSerial/device write is not implemented.
- backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
