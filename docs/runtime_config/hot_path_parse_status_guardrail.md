# Runtime Hot-Path Parse-Status Guardrail

status: ACCEPTED_GUARDRAIL

## Summary

The Phase 7A D5A/D5A-N1/D5A-N2 diagnostic sequence establishes an accepted
production guardrail for future runtime-config activation work:

Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver.

Unsafe pattern:

```text
UpdateAnalogOutputs(...) -> ResolveActiveRuntimeConfig() -> kPhase7AD3GlobalParseResult.status
```

The analog output hot path may consume a stable already-selected
`RuntimeConfigView`. It must not inspect parser result status, parser result
fields, payload validation state, CRC state, storage load state, or any runtime
config activation decision state.

## Evidence Matrix

| Diagnostic | Finding | Result |
| --- | --- | --- |
| D2B | Retained payload bytes only | PASS |
| D3 | Global/static parse result only | PASS |
| D4 | Resolver only | PASS |
| D5A | Parse-status-gated source-owned routing | FAIL, RF5/RF6/LT6 disconnects |
| D5A-N1 | Direct canonical source-owned view after parse-status gate | FAIL, same disconnects |
| D5A-N2 | Resolver without parse-status hot-path read | PASS, no disconnects |

## Production Invariant

Do not read parser result state from UpdateAnalogOutputs or analog hot-path resolver.

The low-level mechanism is not proven. The actionable finding is narrower:
production repair must avoid parser-status reads in the analog hot path. The
failed activation branch remains abandoned and must not merge.

True parsed table materialization remains deferred. Runtime-loaded config,
storage, WebSerial/device write, and flashing remain not implemented.

## Required Runtime Split

Future runtime config activation must be split into two phases:

1. Activation / selection phase
   - may validate parser results;
   - may choose which runtime config view is active;
   - must run outside the analog output hot path;
   - must produce stable active state.

2. Output generation phase
   - may use only the stable selected `RuntimeConfigView`;
   - must not inspect parser result state;
   - must not branch on parser status or config-load status;
   - must preserve deterministic output behavior.

Future architecture recommendation: an activation phase computes stable active
runtime config state outside the hot path, and the analog output phase consumes
only the stable selected view.

## Non-Goals

- no storage
- no WebSerial/device write
- no flashing automation
- no parsed table materialization in this branch
- no firmware behavior change in this branch
- no public release claim
- no nunchuk validation claim
