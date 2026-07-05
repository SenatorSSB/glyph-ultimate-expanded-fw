# Glyph Coordinate-Native Runtime Plan

Status label: DESIGN / DOCS-CHECKER ONLY.

This packet records the forward Glyph firmware architecture after the latest
Y2 layout source-owned port received a hardware pass. It is documentation and
checker scaffolding only. It does not modify firmware source, change active
firmware behavior, implement runtime-loaded config, or require a hardware test
before merge.

## Accepted Evidence

- The source-owned Y2 layout `HARDWARE_PASS` is the current known-good firmware
  path. The full latest Y2 layout source-owned port passes hardware testing.
- RF5 forced A + Up passes without disconnect.
- LT6 forced A + Down passes without disconnect.
- Y1 is simple.
- Y2 owns the migrated RF sublayers.
- Active `RuntimeConfigView` selection remains unchanged.
- `GetActiveRuntimeConfigState()` still publishes
  `&kSourceOwnedCurrentBaselineRuntimeConfig`.
- RuntimeConfigView replacement is not used.
- The generated active wrapper is not used.
- `candidate.view` is not active.
- RAM-backed active table publication is not used.
- Nunchuk remains `NOT_TESTED`.
- The low-level root cause remains unproven.

Prior active-publication `HARDWARE_FAIL` evidence remains accepted:

- `candidate.view` active publication: `HARDWARE_FAIL`.
- Source-owned-materialized `candidate.view` active publication:
  `HARDWARE_FAIL`.
- Dedicated / RAM-backed active storage publication: `HARDWARE_FAIL`.
- Generated source-owned baseline `RuntimeConfigView` active publication:
  `HARDWARE_FAIL`.

## Current V0 Production Path

The short-term safe backend is source-owned firmware realization:

```text
neutral/profile intent
-> generated source-owned tables and routing source
-> firmware build
-> existing active RuntimeConfigView path
```

Current v0 production work remains source-owned firmware generation as v0 until
coordinate-native runtime profile support is hardware-proven. The existing
active `RuntimeConfigView` path remains the accepted active boundary. Active
runtime config replacement, RuntimeConfigView replacement, generated active
wrappers, `candidate.view` active publication, and RAM-backed active table
publication are not allowed by this plan.

## Long-Term Target

The long-term target is one optimal coordinate-native firmware that users can
configure through browser profile files. That target requires a dedicated
coordinate-native runtime profile layer. It must not assume that the existing
generic scalar analog modifier / custom-mode abstraction can represent the
required behavior.

Browser-to-device transport, protobuf-style config exchange, and persistence
are likely solvable primitives. These primitives should be treated as future
backend infrastructure, not as the canonical Senscope profile model. In short:
browser/protobuf/persistence as future infrastructure, not source authority for
the neutral profile.

Senscope's canonical profile model remains neutral, app-owned, and
firmware-independent. Senscope, its datasets, and its solver own game
semantics. Glyph firmware should not know Super Smash Bros. Ultimate game
semantics. Glyph firmware should become a deterministic coordinate-output
backend.

The required runtime primitive is coordinate-native:

```text
active role/modifier state + resolved direction key 1..9 -> exact raw coordinate
```

Required properties:

- Direction keys `1..9` must be supported.
- Neutral direction 5 must be supported.
- Full 9-way asymmetry must be supported.
- Exact raw coordinates must be represented as output targets.
- Sublayers, routing, and priority must be represented explicitly.
- Y1/Y2/Tilt/Layer-style behavior requires profile-level routing primitives,
  not only scalar axis multipliers.

## Architecture Boundary

The canonical profile is not a protobuf payload, browser transport packet,
storage record, firmware table layout, or vendor-specific export. Those may
be backend infrastructure or derived artifacts. The neutral app-owned profile
remains canonical.

Firmware-side runtime work should target deterministic coordinate resolution:

```text
neutral app-owned profile
-> backend realization/generator
-> coordinate-native runtime profile or source-owned firmware tables
-> Glyph deterministic coordinate output
```

Short term, the backend realization/generator emits source-owned firmware source
and uses the existing active runtime path. Long term, the backend realization
may emit a hardware-proven coordinate-native runtime profile for firmware
loading, storage, and activation.

## Non-Claims

- This packet does not prove the low-level root cause.
- This packet does not modify firmware source.
- This packet does not implement runtime-loaded config, persistent storage,
  WebSerial/device write, backend/config.pb write, or flashing automation.
- This packet does not approve active `RuntimeConfigView` replacement.
- This packet does not approve `candidate.view` active publication.
- This packet does not approve RAM-backed active table publication.
- This packet does not claim nunchuk validation.
- This packet does not define or change Senscope game semantics.
- This packet does not change the Senscope neutral profile schema.
