# Agent Operating Contract

This contract applies to every agent operating in this repo.

1. Treat Glyph as a firmware realization target, not the canonical game-semantics source.
2. Keep Senscope semantic-source work separate from this repository.
3. Preserve the no-smash / dataset semantic pipeline boundary.
4. Do not change firmware behavior unless the task explicitly asks for it.
5. Use repo-local PlatformIO through `./scripts/pio-local.sh` or `python -m platformio`.
6. Prefer small, reviewable docs and scaffolding changes.
7. Stop and report if a requested change would require destructive git operations.
8. End every completed batch by committing, pushing, and then stopping with a report.
