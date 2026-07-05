# Runtime Config Implementation Boundary

Status label: CURRENT.

This document defines the current safe implementation boundary after the latest
Y2 layout source-owned HARDWARE_PASS and the coordinate-native runtime plan.

## Approved Current Active Path

- Active RuntimeConfigView selection remains unchanged.
- Source-owned table/routing source is the approved active Glyph realization
  path.
- `GetActiveRuntimeConfigState()` may continue to publish the source-owned
  current baseline view.
- `ResolveActiveRuntimeConfig()` may continue to dereference the selected active
  view.
- Source-owned realization generator work may produce source-owned
  tables/routing source for review, build, and hardware-gated firmware changes.

## Explicitly Forbidden Current Active Paths

- `candidate.view` active publication is forbidden.
- `active_storage.view` active publication is forbidden.
- Generated active RuntimeConfigView wrapper publication is forbidden.
- RuntimeConfigView replacement as the customization mechanism is forbidden.
- RAM-backed active table publication is forbidden.
- Runtime-loaded profile claims are forbidden without separate design, source
  authority, build proof, and hardware proof.

## Future Coordinate-Native Boundary

The future target is coordinate-native runtime profile support, but it remains a
separate design and hardware-proof phase. The runtime primitive should map
active role/modifier state plus resolved direction key 1..9 to exact raw
coordinates, including neutral 5, full 9-way asymmetry, and explicit
routing/sublayers/priorities.

Browser/protobuf/persistence work may be future infrastructure after the runtime
model exists. It is not approval for device write, persistent runtime-config
storage, backend config write paths, or flashing automation.

## Required Non-Claims

- Nunchuk remains NOT_TESTED.
- Root cause remains unproven.
- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write is not implemented.
- Protobuf binary write is not implemented.
- Firmware flashing automation is not implemented.
