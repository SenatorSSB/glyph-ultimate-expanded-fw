# Model Routing

Status label: CURRENT.

Use capability tiers rather than permanent model names. Catalogs and product
surfaces change; review current availability before configuring tasks. Role
separation and independent judgment remain required even when every role uses
the same available model.

| Role | Default capability | Reasoning | Escalate when |
| --- | --- | --- | --- |
| Implementation Supervisor | strong coding model | moderate | recovery, cross-cutting source authority, or H2/H3 safety is difficult |
| Portfolio Planner | strong broad-synthesis model | high | broad portfolio scarcity or conflicting evidence is hard to establish |
| Work-Order Curator | strong skeptical synthesis/review model | high | Preauthorization invalidation, source authority, or global evidence wait is ambiguous |
| Architecture Specialist | strong architecture/coding model | high for bounded question | active runtime or critical-path design is involved |
| Implementer | competent coding model | low/moderate | compiler/generator logic or firmware risk is difficult |
| Validator Reviewer | strong review model | moderate/high proportional to risk | H2/H3, generated artifacts, or publication safety is involved |
| Hardware Evidence Processor | strong verification/review model | moderate/high | H3 or evidence identity/scope is ambiguous |
| Docs Status Clerk | fast competent model | low | canonical docs contradict source or evidence |
| Judge Watchdog | fast competent model | low/moderate | loop, unsafe path, or hardware gate is ambiguous |

Use the strongest reasoning only on bounded uncertainty. Do not make maximum
reasoning the routine long-lived root default. Mechanical scans and template
updates should use a faster competent tier when available. Any fresh reviewer
must remain independent of the implementation reasoning, regardless of model
name.

Machine-readable role defaults are mirrored in `model_routing.v0.json` and
validated by `tools/check_glyph_agent_framework_docs.py`.
