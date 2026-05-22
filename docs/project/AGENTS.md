# Project AGENTS

This file is the legacy project-local companion to the repository root [AGENTS.md](/Users/rasmus.pekkarinen/Library/Mobile%20Documents/com~apple~CloudDocs/Smash/glyph-ultimate-expanded-fw/AGENTS.md).

Use the root file as the primary operating contract.

## What this file is for

This directory historically held docs/setup guidance for the Glyph workstream. The active, broader rules now live in the repository root and in:

- [docs/project/AGENT_OPERATING_CONTRACT.md](/Users/rasmus.pekkarinen/Library/Mobile%20Documents/com~apple~CloudDocs/Smash/glyph-ultimate-expanded-fw/docs/project/AGENT_OPERATING_CONTRACT.md)
- [docs/project/AGENT_STOP_CONDITIONS.md](/Users/rasmus.pekkarinen/Library/Mobile%20Documents/com~apple~CloudDocs/Smash/glyph-ultimate-expanded-fw/docs/project/AGENT_STOP_CONDITIONS.md)
- [docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md](/Users/rasmus.pekkarinen/Library/Mobile%20Documents/com~apple~CloudDocs/Smash/glyph-ultimate-expanded-fw/docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md)

## Legacy guidance

- Stay within docs/setup unless the active queue explicitly expands scope.
- Use `./scripts/build-glyph-mk6-quiet.sh` for firmware/build-affecting tasks.
- Use `./scripts/pio-local.sh run -e glyph_mk6` only when debugging full build output.
- Keep Senscope semantic authority separate from Glyph backend realization work.
- Do not use destructive Git operations.

## Compatibility note

If this file and the root AGENTS file differ, follow the root file unless a task explicitly says otherwise.
