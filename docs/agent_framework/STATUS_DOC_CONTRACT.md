# Status Doc Contract

Status label: CURRENT.

Status docs are source-of-truth surfaces, not scratchpads.

## Current Documents

- `docs/CURRENT_STATE.md`: factual current state, readiness categories,
  approval gates, and non-claims.
- `docs/ROADMAP.md`: milestone and intent state.
- `docs/AGENT_CONTEXT.md`: first-read agent state and current operating
  snapshot.
- `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`: hard boundary for
  runtime-config implementation and forbidden active-publication paths.
- `docs/archive/README.md`: evidence and archive index for historical
  diagnostics.

## Update Rules

- Update status docs only when validated facts change.
- Do not promote archived failures into current work.
- Do not claim Nunchuk validation without explicit user test evidence.
- Do not claim root cause is proven without direct evidence.
- Do not claim runtime-loaded config, device write, protobuf binary write,
  persistence, or flashing automation as implemented.
- Keep Senscope game semantics outside this repo.

## Future Run Ledger

A future `RUN_LEDGER` may record bounded cycle IDs, branch names, objectives,
classifications, verification, and verdicts. That guidance is docs-only and
future-facing. This framework does not create a runner prompt, runner daemon,
or scheduled automation.
