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
- `docs/project/ACTIVE_AGENT_QUEUE.md`: the only executable Ready queue,
  recorded Preauthorization, runway metrics, packet state, and liveness signal.
- `docs/agent_framework/USER_DIRECTION.md`: actual human directives, decisions,
  priorities, preferences, observations, and hypotheses only.
- `docs/agent_framework/HARDWARE_EVIDENCE.md`: H0-H3 and exact-snapshot result
  contract; concrete result records remain close to their evidence.
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
- Do not convert roadmap, Planner output, branch names, or chat suggestions into
  implementation authority. Only a complete queue work order may authorize.
- Curator owns new Ready/Preauthorized authorization. Implementation may update
  the selected item's execution/publication state but cannot create new work.
  The Hardware Evidence Processor may update only evidence identity, result,
  gaps, references, and hardware lifecycle status for an existing H2/H3 item.

## Future Run Ledger

A future `RUN_LEDGER` may record bounded cycle IDs, branch names, objectives,
classifications, verification, and verdicts. That guidance is docs-only and
future-facing. This framework does not create a runner prompt, runner daemon,
or scheduled automation.

Exact operator-facing task prompts exist in `SCHEDULED_TASKS.md`, but repository
documentation does not create or alter external schedules.
