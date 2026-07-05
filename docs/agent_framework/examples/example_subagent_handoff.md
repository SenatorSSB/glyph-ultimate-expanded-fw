# Example Subagent Handoff

```yaml
role: validator_reviewer
branch_worktree: docs-agent-framework-contracts
objective: Review docs/checker-only framework branch and verify gates.
scope: Inspect diff, run required docs/checker commands, classify behavior.
excluded_scope: Firmware implementation, runner prompt, device write,
  runtime-loaded config, hardware claims.
allowed_files:
  - AGENTS.md
  - docs/agent_framework/**
  - docs/AGENT_CONTEXT.md
  - tools/check_glyph_agent_framework_docs.py
  - tools/check_glyph_docs_navigation.py
forbidden_files:
  - src/**
  - include/**
  - lib/**
  - platformio.ini
active_behavior_constraints:
  - Active RuntimeConfigView selection remains unchanged.
  - Runtime-loaded config remains not implemented.
  - Nunchuk remains NOT_TESTED.
  - Root cause remains unproven.
verification_required:
  - git diff --check
  - python3 tools/check_glyph_agent_framework_docs.py
stop_conditions:
  - Firmware source diff appears.
  - Any forbidden active-publication path is documented as supported.
return_format: Findings first, commands run, classification, residual risk.
tool_budget: Bounded read/check pass.
```
