# CLAUDE.md

This file is guidance/context for Claude Code. It is not an enforcement layer.
Hard safety gates are checked by repo checkers plus human merge and hardware
rules.

Read first:

- `docs/AGENT_CONTEXT.md`
- `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`
- `docs/agent_framework/README.md`

Custom subagents should use:

- `docs/agent_framework/SUBAGENT_CONTRACTS.md`
- `docs/agent_framework/MODEL_ROUTING.md`
- `docs/agent_framework/VALIDATION_AND_GATES.md`

Do not duplicate large policy blocks in Claude-specific files. Keep any local
subagent definitions thin and point back to `docs/agent_framework`.
