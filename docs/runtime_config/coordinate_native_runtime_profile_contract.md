# Coordinate-Native Runtime Profile Contract

Status label: INACTIVE DESIGN / DOCS-CHECKER ONLY.

This packet is the inert contract scaffold for future coordinate-native runtime
profile support. It is documentation and checker scaffolding only. It does not
modify firmware source, does not change active firmware behavior, and does not
implement runtime interpretation.

## Contract Scope

The contract model names these durable concepts explicitly:

- physical input IDs
- direction resolver
- direction keys `1..9`
- neutral key `5`
- exact raw coordinates
- 9-way modifier tables
- sublayer and routing rules
- priorities
- digital side effects
- version and capability metadata

## Accepted Evidence

- The source-owned Y2 layout `HARDWARE_PASS` remains the current known-good
  firmware path.
- Active `RuntimeConfigView` selection remains unchanged.
- `GetActiveRuntimeConfigState()` still publishes the source-owned current
  baseline view.
- RuntimeConfigView replacement is not used.
- The generated active wrapper is not used.
- `candidate.view` is not active.
- RAM-backed active table publication is not used.
- Prior active-publication `HARDWARE_FAIL` evidence remains accepted.
- Nunchuk remains `NOT_TESTED`.
- The low-level root cause remains unproven.

## Contract Target

The future target is a coordinate-native runtime profile contract with the
primitive:

```text
active role/modifier state + resolved direction key 1..9 -> exact raw coordinate
```

The contract requires:

- Direction keys `1..9`.
- Neutral direction `5`.
- Full 9-way asymmetry.
- Exact raw coordinates as outputs.
- Explicit routing, sublayers, and priorities.

The canonical profile remains neutral, app-owned, and firmware-independent.
Senscope owns game semantics, datasets, and solver authority. Glyph firmware
should remain a deterministic coordinate-output backend and should not own game
semantics.

## Required Properties

- Active runtime config replacement is not allowed.
- RuntimeConfigView replacement is not allowed.
- Generated active wrapper publication is not allowed.
- `candidate.view` active publication is not allowed.
- RAM-backed active table publication is not allowed.
- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write path is not implemented.
- Backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Nunchuk validation is not claimed.
- Hardware test is not required before merge for this docs/checker-only
  scaffold because active behavior is unchanged.

## Future Implementation Gate

This contract scaffold is not approval to implement runtime interpretation,
runtime-loaded config, storage, device write, or active publication changes.
Future implementation must be hardware-gated if active source selection
behavior changes.

Any later runtime-active implementation must preserve the current source-owned
active path unless a separate source-backed and hardware-validated model proves
otherwise. It must still reject runtime-loaded config, persistent storage,
WebSerial/device write, backend/config.pb write paths, firmware flashing
automation, `candidate.view` active publication, and RAM-backed active table
publication unless later evidence changes those boundaries.

## Non-Claims

- This packet does not change active firmware behavior.
- This packet does not prove the low-level failure mechanism.
- This packet does not implement runtime interpretation.
- This packet does not implement runtime-loaded config, persistent storage,
  WebSerial/device write, backend/config.pb write, or flashing automation.
- This packet does not approve active `RuntimeConfigView` replacement.
- This packet does not approve `candidate.view` active publication.
- This packet does not approve RAM-backed active table publication.
- This packet does not claim nunchuk validation.
- This packet does not define or change Senscope game semantics.
