# Work-Order Template

Status label: CURRENT.

Use this template for every executable or Preauthorized item in
`docs/project/ACTIVE_AGENT_QUEUE.md`. Do not omit fields merely because the
answer is unknown; an unresolved substantive field means the item is not
Ready.

```text
Work-order ID:
Title:
Status:
Branch:

Objective:
Why this matters:

Hardware risk:
H0 | H1 | H2 | H3

Behavioral claim:

Scope:
Explicit excluded scope:

Touched planes:
- configurator
- source-owned configuration
- generated tables/artifacts
- firmware runtime
- persistence
- USB/update
- build tooling
- docs/checkers

Source authority:

Dependencies / prerequisites:

Substantive authorization rationale:

Mechanical activation conditions:
[required for PREAUTHORIZED; objective checks only]

Invalidation conditions:
[required for PREAUTHORIZED]

Authorization snapshot / provenance:

Automated validation:

Canonical build:
pio run -e glyph_mk6

Expected artifact:
.pio/build/glyph_mk6/firmware.uf2 | NOT_APPLICABLE

Candidate Git SHA:
[full lowercase SHA when an H2/H3 candidate exists; otherwise null]

Candidate base configurator SHA:
[full lowercase SHA when an H2/H3 candidate exists; otherwise null]

Firmware artifact build path:
[exact build output path when an H2/H3 artifact exists; otherwise null]

Preserved firmware artifact locator:
[immutable candidate-SHA/artifact-SHA-addressed locator outside mutable .pio
output; otherwise null]

Firmware artifact SHA-256:
[full lowercase digest of preserved exact bytes; otherwise null]

Manual acceptance:
NOT_REQUIRED | REQUIRED

Manual acceptance protocol reference:

Hardware evidence record:
[canonical evidence path/ref after processing; otherwise null]

Hardware result:
PASS | FAIL | PARTIAL | INCONCLUSIVE | null

Hardware evidence gaps:
[exact missing/retest evidence; empty only when none]

Rollback / recovery:

Status/documentation updates:

Done evidence:

Stop conditions:
```

## Risk Classification

- `H0` — non-runtime docs, comments, inert fixtures, checker improvements, or
  non-behavioral generated artifacts. Automated validation and independent
  review normally suffice.
- `H1` — host/configurator-only behavior with no unproven firmware-runtime
  effect. Run host tests and any genuinely required UI/manual host acceptance;
  build when relevant.
- `H2` — firmware runtime behavior, runtime tables, source-owned active
  configuration, propagation, modifiers, or report/runtime values. Automated
  validation, canonical build, independent review, exact candidate artifact,
  and physical controller PASS are required before merge.
- `H3` — boot/update, USB identity, flash/update, persistence, migration,
  recovery-sensitive configuration, or critical dispatch/input paths. Strict
  validation, build, fresh safety review, explicit recovery plan, exact
  artifact, and physical controller PASS are required.

Risk follows behavioral effect, not file location. A configurator change that
changes generated firmware behavior is not automatically H1.

## Substantive Authority Invariant

The existing `Behavioral claim`, `Source authority`, `Substantive authorization
rationale`, `Authorization snapshot / provenance`, scope/exclusions,
dependencies, validation, and stop-condition fields jointly carry the
implementation authority decision; no redundant blanket human-approval field
is required. For a `READY` H2/H3 item they must durably establish that every
required behavior, product, domain, source-authority, architecture, scope, and
validation decision is resolved. Hardware risk alone does not require fresh
human approval before candidate implementation.

If any substantive decision is unknown, inferred without accepted authority,
or outside Curator's configured authority, the item is not `READY` and cannot
execute. Physical acceptance remains separate: H2/H3 candidate implementation
may proceed, but merge remains prohibited until exact-snapshot hardware PASS.

## Machine-Readable Queue Fields

Each future object in the queue's `items` list uses snake_case equivalents of
the template fields plus:

```text
activation_state:
NOT_APPLICABLE | WAITING | ACTIVATABLE | HARDWARE_PENDING | INVALIDATED

activation_requires_new_judgment:
true | false

hardware_evidence_dependency_satisfied:
true | false | null

candidate_git_sha:
full lowercase Git SHA | null

candidate_base_configurator_sha:
full lowercase Git SHA | null

firmware_artifact_build_path:
non-empty path | null

preserved_firmware_artifact_locator:
immutable candidate-SHA/artifact-SHA-addressed locator | null

firmware_artifact_sha256:
full lowercase SHA-256 | null

hardware_evidence_record:
non-empty path/ref | null

hardware_result:
PASS | FAIL | PARTIAL | INCONCLUSIVE | null

hardware_evidence_gaps:
list of non-blank strings
```

Only a `PREAUTHORIZED` item with non-empty mechanical and invalidation
conditions, `activation_state: ACTIVATABLE`,
`activation_requires_new_judgment: false`, and satisfied or inapplicable
hardware evidence may activate mechanically.

`HARDWARE_TEST_REQUIRED`, `LOCAL_ACCEPTANCE_PENDING`, `HARDWARE_VALIDATED`,
and `HARDWARE_FAILED` require the exact candidate/base Git SHAs, mutable build
path, immutable preserved-artifact locator, and artifact SHA-256.
`HARDWARE_VALIDATED` additionally requires `hardware_result: PASS`, a canonical
evidence record, and no evidence gaps. `HARDWARE_FAILED` requires
`hardware_result: FAIL` and a canonical evidence record. PARTIAL and
INCONCLUSIVE stay `LOCAL_ACCEPTANCE_PENDING` with exact evidence gaps unless
Curator separately authorizes repair work.
