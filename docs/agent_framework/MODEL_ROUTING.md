# Model Routing

Status label: CURRENT.

These are current recommended defaults, not permanent mandates. Review them
when provider docs, available tool surfaces, organization allowlists, or repo
evals change. Do not infer provider behavior beyond provider documentation.

For Claude Code, subagent model and effort availability depends on Claude Code
version and organization allowlists. For OpenAI/Codex, role routing is
currently an operator/runner responsibility unless a tool supports per-subagent
model selection.

## Role Matrix

| Role | OpenAI/Codex default | OpenAI effort | Claude default | Claude effort | Escalate when | De-escalate when | Output contract | Tool posture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| supervisor | GPT-5.4 mini | medium | Sonnet 5 | medium | gates conflict, branch risk changes, merge decision unclear | docs/checker-only scope is stable | cycle report and final merge recommendation | orchestrates, limited direct edits |
| planner | GPT-5.4 mini | medium | Sonnet 5 | medium | roadmap ambiguity or branch decomposition risk | task is single-file or checker-only | ready batch with dependencies and stop rules | read-oriented |
| architecture_specialist | GPT-5.5 | high | Opus 4.8 | high | active firmware, runtime model, or source authority is involved | docs-only pointer work | architecture note with evidence and unknowns | read-oriented unless explicitly assigned |
| implementer | GPT-5.4 mini | low or medium | Sonnet 5 | low/medium | edits cross ownership boundaries or firmware source | bounded docs/checker edit | patch summary and verification | bounded editing |
| validator_reviewer | GPT-5.5 | medium/high for firmware risk; GPT-5.4 mini medium for docs/checker-only | Sonnet 5 or Opus 4.8 depending firmware risk | medium/high | active behavior, generated artifacts, or merge gate is involved | docs/checker-only branch validates cleanly | findings first, commands run, classification | read/check oriented |
| docs_status_clerk | GPT-5.4 nano or GPT-5.4 mini | low | Haiku 4.5 or Sonnet 5 | low | status docs contradict current boundary | only navigation text changed | status doc delta and consistency checks | docs-only |
| judge_watchdog | GPT-5.4 mini or GPT-5.4 nano | low/medium | Haiku 4.5 or Sonnet 5 | low | loop, unsafe path, or hardware gate appears | branch is clearly done or blocked | one verdict plus evidence | read-only |

## Escalation Policy

Escalate model/effort when:

- A task touches active firmware source, `RuntimeConfigView` selection, or
  hardware merge gates.
- The branch classification is not obviously `DOCS_CHECKER_ONLY`.
- Source authority is ambiguous.
- The next step would create a new architecture commitment.

De-escalate model/effort when:

- Scope is docs/checker-only and current boundaries are unchanged.
- A subagent is filling a known template or updating status wording.
- The judge is only checking loop criteria and branch classification.

The routing source of truth is also mirrored as machine-readable defaults in
`model_routing.v0.json`, validated by
`tools/check_glyph_agent_framework_docs.py`.
