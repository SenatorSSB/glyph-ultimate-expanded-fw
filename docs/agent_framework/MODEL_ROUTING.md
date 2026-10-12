# Model Routing

Status label: CURRENT.

Route by the current task/lane, not the importance of a role. Capability families
are durable preferences; resolve actual available model identifiers at dispatch.
Explicitly select or verify model and effort on every dispatch AND resume, and
record requested versus observed execution separately. Unknown remains unknown.
Never resume a chat merely for a convenient model setting.

| Task lane | Preferred family / effort | Escalation |
| --- | --- | --- |
| Chapter daemon | Terra / low | Terra / medium for coupled chapter-state reconciliation |
| Mechanical / frequent | Luna / low | Medium for guarded multi-step mechanical work |
| Established bounded implementation | Terra / medium where available/appropriate; Luna / medium for well-known patterns | Sol / medium for technical coupling |
| Coupled technical / diagnosis | Sol / medium | Sol / high for difficult finite architecture or conflicting evidence |
| Ambiguous / high-leverage | Sol / high first | Exceptional Astra only with written reason |
| Exceptional finite question | Astra / medium; high needs a reason | Cheaper attempt inadequate OR genuinely novel risk justifies direct use |

Astra must have a finite high-leverage question, written reason and expected
benefit. Return a decision/counterexample and end the expensive session; never
use Astra as the persistent control-loop default. De-escalate after resolution.

The local catalog inspected on 2026-10-10 lists Terra as `gpt-5.6-terra`, with
low and medium supported. This is a dated availability observation, not a
permanent framework model pin. Re-resolve at each dispatch/resume. If Terra is
unavailable, preserve the preference and require an explicit owner-approved
available fallback; no silent substitute or fabricated ID. Machine-readable
policy remains capability-family based.

Independent investigation normally gets a fresh context; resume a clean context
only for the same bounded chain when prior context is useful and independence
survives. A reviewer may be independent while using Luna/Terra. One independent
review layer is normally sufficient; a role is not a quota. Planner/Curator/HEP
and specialists exist only when required by the current transition.

`model_routing.v0.json` mirrors task lanes and dispatch rules. Its `roles` retain
permission/output contracts and compatibility defaults; each default references
a lane and is overridden by the actual task's uncertainty, not role prestige.
The schema and `tools/check_glyph_agent_framework_docs.py` validate the mirror.
Use runtime-emitted telemetry passively; missing usage does not block work and
placeholder zeros are not measurements. No calls or polls solely for metrics.

## Model provenance and worker choice

**Requested model is not proof of observed model.** Keep three concepts distinct:

- `requested`: family/resolved identifier and effort sent or intended at dispatch.
- `owner_selected`: owner-selected UI/model configuration, with `OWNER_SELECTED`
  provenance and its source. This is owner configuration, not independent runtime
  telemetry and not a guarantee of fixed execution identity.
- `runtime_observed`: actual model/effort exposed by runtime telemetry, with its
  exact source labeled `RUNTIME_OBSERVED:` in roster records. Without that evidence record `observed_model = UNKNOWN` and
  `observed_effort = UNKNOWN`; partial telemetry may prove only one field.

Worker or daemon prose, preference configuration, requested dispatch parameters
and capability-family assumptions cannot prove actual execution identity.
Matching requested and observed values are legal only with independent runtime
telemetry; requested != observed means separate evidence concepts, not mandatory
unequal strings. Missing telemetry does not block mechanically verifiable work.
Owner-selected chats still require honest UNKNOWN runtime fields when unproved.

Model spend follows **epistemic difficulty**, not worker title. A SHA/checker
runner needs no Sol merely because it is called reviewer; a finite difficult
architecture counterexample may justify Sol/high. Mechanical proof must remain
mechanically verified regardless of model. Use native disposable workers for
such mechanical tasks; owner-selected roster chats serve difficult judgment.
See [bootstrap roster authority](FUTURE_DAEMON_BOOTSTRAP.md#optional-chapter-worker-roster)
and [templates](PROMPT_TEMPLATES.md#optional-chapter-worker-roster).
