# Example Supervisor Cycle Request

Branch: `docs-agent-framework-contracts`

Objective: add docs/checker-only supervisor and subagent framework contracts.

Classification target: `DOCS_CHECKER_ONLY`.

Allowed files:

- `AGENTS.md`
- `docs/agent_framework/**`
- `docs/AGENT_CONTEXT.md`
- `tools/check_glyph_agent_framework_docs.py`
- `tools/check_glyph_docs_navigation.py`

Forbidden files:

- `src/**`
- `include/**`
- `lib/**`
- `platformio.ini`
- protobuf schemas
- device-write paths
- flashing automation

Active behavior constraints:

- Active RuntimeConfigView selection remains unchanged.
- No active `candidate.view` publication.
- No active `active_storage.view` publication.
- No generated active RuntimeConfigView wrapper publication.
- No runtime-loaded config claim.
- Nunchuk remains NOT_TESTED.
- Root cause remains unproven.

Verification:

- `git diff --check`
- `python3 tools/check_glyph_docs_navigation.py`
- `python3 tools/check_glyph_docs_agent_surface.py`
- `python3 tools/check_glyph_agent_framework_docs.py`
- `python3 -m py_compile tools/check_glyph_agent_framework_docs.py`
