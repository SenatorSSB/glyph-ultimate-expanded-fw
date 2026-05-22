# Codex Workflow

This file is the legacy project-local workflow note.

Use [docs/project/CODEX_CLOUD_WORKFLOW.md](/Users/rasmus.pekkarinen/Library/Mobile%20Documents/com~apple~CloudDocs/Smash/glyph-ultimate-expanded-fw/docs/project/CODEX_CLOUD_WORKFLOW.md) as the current workflow reference.

## Legacy branch / scope cues

- Confirm work is on `docs/senscope-glyph-baseline` unless instructed otherwise.
- Inspect repo status before editing.
- Prefer docs/setup work unless the active queue expands scope.
- Verify `./scripts/pio-local.sh` and `./scripts/build-glyph-mk6-quiet.sh` are executable before relying on them.
- Use `./scripts/build-glyph-mk6-quiet.sh` for firmware/build-affecting tasks.
- Use `./scripts/pio-local.sh run -e glyph_mk6` only when debugging full build output.
- Record source provenance instead of inventing missing artifacts.
- Commit, push, stop, and report when the branch policy is clear.

## Compatibility note

If this file conflicts with the repository root [AGENTS.md](/Users/rasmus.pekkarinen/Library/Mobile%20Documents/com~apple~CloudDocs/Smash/glyph-ultimate-expanded-fw/AGENTS.md) or the current project docs under `docs/project/`, follow the newer repo-wide guidance.
