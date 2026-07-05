# Model Routing

Status label: CURRENT.

This framework is Codex/OpenAI-only for current repository operations. These
are current recommended defaults, not permanent model mandates. Provider/model
availability may change and should be reviewed separately before changing this
routing table.

Role routing is currently an operator/runner responsibility unless a tool
supports per-subagent model selection. Runner prompt and runner implementation
remain deferred.

Non-Codex agent surfaces are intentionally out of scope for the current repo
workflow and require a separate approved docs branch before use.

## Role Matrix

| Role | Default model | Default reasoning effort | Escalation model | Escalation effort | Escalation triggers | De-escalation triggers | Output contract | Tool posture |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| supervisor | GPT-5.4 mini | medium | GPT-5.5 | high | ambiguous architecture, unsafe merge risk, tricky firmware source review, conflicting evidence | docs/checker-only scope is stable | cycle report and final merge recommendation | orchestrates, limited direct edits |
| planner | GPT-5.4 mini | medium | GPT-5.5 | medium/high | complex branch decomposition or source-authority ambiguity | task is single-file or checker-only | ready batch with dependencies and stop rules | read-oriented |
| architecture_specialist | GPT-5.5 | high | GPT-5.5 | high | active firmware, runtime model, or source authority is involved | GPT-5.4 mini medium for simple docs/checker architecture | architecture note with evidence and unknowns | read-oriented unless explicitly assigned |
| implementer | GPT-5.4 mini | low or medium | GPT-5.5 | medium/high | firmware behavior risk or difficult compiler/generator logic is involved | bounded docs/checker edit | patch summary and verification | bounded editing |
| validator_reviewer | GPT-5.4 mini for docs/checker-only; GPT-5.5 for firmware source risk | medium for docs/checker-only; medium/high for firmware source risk | GPT-5.5 | medium/high | active behavior, generated artifacts, or merge gate is involved | docs/checker-only branch validates cleanly | PASS / FAIL / NEEDS_HARDWARE / UNSAFE / BLOCKED | read/check oriented |
| docs_status_clerk | GPT-5.4 nano or GPT-5.4 mini | low | GPT-5.4 mini | medium | status docs contradict current boundary | only navigation text changed | status doc delta and consistency checks | docs-only |
| judge_watchdog | GPT-5.4 nano or GPT-5.4 mini | low/medium | GPT-5.4 mini | medium | loop, unsafe path, or hardware gate appears | branch is clearly done or blocked | DONE / CONTINUE / BLOCKED / NEEDS_HARDWARE / UNSAFE / LOOPING | read-only |

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
