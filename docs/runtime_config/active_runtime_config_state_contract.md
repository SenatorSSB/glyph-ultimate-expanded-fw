---
status: DESIGN_ACCEPTED
title: Active Runtime Config State Contract
---

# Active Runtime Config State Contract

Status: DESIGN_ACCEPTED.

This branch is docs/tools-only and changes no firmware behavior.

This contract defines the production-safe active runtime config state boundary
that must exist before any further firmware behavior changes for runtime config
activation. It builds on the accepted Phase 7A hot-path parse-status guardrail:

Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver.

## Background Evidence

Phase 7A diagnostics established the accepted guardrail:

- D2B retained payload bytes only: PASS.
- D3 global/static parse result only: PASS.
- D4 resolver only: PASS.
- D5A parse-status-gated source-owned routing: FAIL.
- D5A-N1 direct canonical source-owned view after parse-status gate: FAIL.
- D5A-N2 resolver without parse-status hot-path read: PASS.

The failed activation branch remains abandoned and must not merge.

## Two-Phase Runtime Activation Contract

Future runtime config activation must be split into two phases.

### 1. Activation / selection phase

The activation / selection phase may:

- validate parser result state;
- inspect payload CRC, format, schema, and load status;
- inspect payload validation state;
- inspect source-owned baseline availability;
- inspect known-good fallback availability;
- choose which runtime config view is active.

The activation / selection phase must:

- run outside `UpdateAnalogOutputs(...)`;
- run outside any analog output hot-path resolver;
- produce a stable selected active state before output generation;
- publish parser, materialization, or load status only through the selected
  active state boundary, not through the hot path.

Parser/materialization/load status may be used only before active-state
publication.

### 2. Output generation phase

The output generation phase may consume only the stable selected
`RuntimeConfigView` through `ActiveRuntimeConfigState.active_view`.

The output generation phase must not:

- inspect parser result state;
- inspect payload validation state;
- inspect CRC state;
- inspect storage load state;
- inspect write status;
- inspect or branch on activation source;
- inspect or branch on activation status;
- branch on any activation decision state.

Output generation must preserve deterministic output behavior.

## Conceptual State Shape

The future conceptual contract is equivalent to:

```cpp
enum class RuntimeConfigSource {
    KnownGoodFallback,
    SourceOwnedBaseline,
    ParsedPayload,
};

enum class RuntimeConfigActivationStatus {
    Uninitialized,
    SourceOwnedSelected,
    ParsedPayloadSelected,
    FallbackSelected,
    InvalidPayloadRejected,
};

struct ActiveRuntimeConfigState {
    const RuntimeConfigView* active_view;
    RuntimeConfigSource source;
    RuntimeConfigActivationStatus status;
};
```

This document defines a design contract only. It does not add the types above
to firmware source.

## Invariants

- Analog output generation may consume only ActiveRuntimeConfigState.active_view.
- Analog output generation must not branch on ActiveRuntimeConfigState.source or ActiveRuntimeConfigState.status.
- `UpdateAnalogOutputs(...)` may use `*active_view`, but must not read
  `source`, `status`, parser result state, CRC state, storage load state, or any
  activation decision state.
- Any resolver used by the analog output hot path must obey the same
  parser-result and activation-status isolation rule.

## Future Implementation Rules

- ResolveActiveRuntimeConfig() may return a stable preselected view, but must not inspect parser result state.
- Parser/materialization/load status may be used only before active-state
  publication.
- Active-state selection may reject invalid payloads before publication.
- Active-state selection may choose source-owned baseline or known-good fallback
  before publication.
- Output generation must not re-evaluate why a view was selected.

## Deferred Work

- True parsed table materialization remains deferred.
- Runtime-loaded config remains deferred.
- Storage/write/WebSerial/flashing remain not implemented.
- Runtime-config storage remains not implemented.
- WebSerial/device write remains not implemented.
- Firmware flashing automation remains not implemented.
- Nunchuk remains not tested.

## Non-Goals

- No firmware source changes.
- No build required.
- No runtime-loaded config.
- No parsed table materialization.
- No storage.
- No WebSerial/device write.
- No flashing automation.
- No nunchuk validation claim.
