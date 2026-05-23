# Active Agent Queue

This file is the current queue for Codex agents in the Glyph-side repository.

## Branch

Use the current checked-out branch unless instructed otherwise.

If branch/remote policy is unclear, stop and report.

## Current mode

```text
Tier 2 — autonomous with stop conditions
```

## Current objective

Prepare Glyph/HayBox-style controller-backend realization architecture without changing Senscope game semantic source authority.

## Current boundaries

Read:

- `AGENTS.md`
- `docs/project/AGENT_OPERATING_CONTRACT.md`
- `docs/project/AGENT_STOP_CONDITIONS.md`
- `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`

Do not add gameplay semantics.

Do not change Senscope no-smash/no-strong-input behavior.

Do not add export/push workflows.

Do not claim undocumented firmware behavior.

## Completed sequence

G1, G2, and G3 are complete and pushed.

### G1 - Glyph repo inventory and architecture map

Status: complete and pushed

Deliverable:

```text
docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md
```

### G2 - Controller capability surface extraction

Status: complete and pushed

Deliverable:

```text
docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md
```

### G3 - Neutral profile integration boundary design

Status: complete and pushed

Deliverable:

```text
docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md
```

## Current status

G5 non-runtime capability model schema draft is complete.

G6 evaluator contract tests with mock capabilities are now complete as a docs-only scaffold.

G7 custom mode / controller logic engine design is complete on `design/glyph-controller-logic-engine-g7`.

G9 config capacity / table storage inventory is complete on `docs/glyph-config-capacity-g9`.

After G9, stop for inspection. Do not proceed to G8/G10/G10b/G11 without explicit approval.

## Next candidate batches

### G4 - Review/normalize G1-G3 and active queue

Status: complete and pushed

Scope:

- review the completed G1/G2/G3 docs;
- normalize queue wording and stop conditions;
- keep the repo ready for human inspection before any runtime implementation.

### G5 - Non-runtime capability model schema draft

Status: complete

Scope:

- docs/design only unless explicitly approved;
- keep the model source-refed and conservative;
- do not introduce runtime code.

### G6 - Evaluator contract tests using mock capabilities

Status: complete (docs-only scaffold)

Scope:

- code/test scaffold only if explicitly approved after G5;
- use mock capabilities;
- keep behavior classification conservative.

### G7 - Firmware custom mode design spike

Status: complete

Scope:

- requires explicit approval;
- design only unless otherwise approved;
- do not change neutral profile schema.

### G8 - Realization evaluator prototype

Status: candidate

Scope:

- requires explicit approval;
- prototype only;
- no runtime adapter, no export/push workflow.

## Explicit stop condition

After G9, stop for inspection. Do not implement G8/G10/G10b/G11 unless the user explicitly asks.

## Verification

Docs/design only unless code is touched:

```bash
git status
git diff --stat
```

If code is touched or build output is relevant, inspect package files and verify wrappers before relying on them.

Use:

```bash
test -x ./scripts/pio-local.sh
test -x ./scripts/build-glyph-mk6-quiet.sh
./scripts/build-glyph-mk6-quiet.sh
```

Use `./scripts/pio-local.sh run -e glyph_mk6` only when debugging full build output.

Do not paste full successful PlatformIO logs into final reports. On failure, report only the final 80 lines unless the user asks for more.

## Final report

Use:

```text
docs/project/AGENT_FINAL_REPORT_TEMPLATE.md
```

Semantic changes must be:

```text
none
```
