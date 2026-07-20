# Source-authority intake workflow

Status: offline tooling only; no production table set is authorized.

## Purpose and boundary

This workflow records a human source-authority decision and converts a fully
reviewed record to existing generator-input v2. It does not create authority,
infer ownership, prepare a candidate, install source, change an alias, select
an active runtime view, build firmware, write a device, persist data, flash,
or establish hardware correctness.

The current source-owned baseline is the authority for identity and comparison
only. A different table, a complete table list, a profile name, or a prior
hardware result is not authority to change that table.

## Intake schema and review

Schema version 1 has identity fields, an explicit authority status, human
approval evidence, production intent, an exact source-extracted baseline
identity, explicit owned-table declarations, exact nine-point replacements,
and review acknowledgements. The baseline includes its source path, semantic
digest, table count, stable order digest, and per-table digests.

Authority status is one of `draft`, `submitted_for_review`, `approved`,
`rejected`, or `superseded`. Only `approved` can emit. It needs a non-empty
basis, approver, approval statement, and approval reference. Placeholders,
unresolved blocking questions, and missing acknowledgement that a build is not
hardware proof block emission.

`production_authorized` is required for a production changeset. Synthetic,
example, migrated-legacy, and unknown provenance never become production by
this tool. `source_baseline_derived` is accepted only for the narrowly scoped
empty overlay source-equivalence proof; a changed result stops.

The deterministic review report contains blockers, baseline match status,
ownership/replacement counts, and separate production and equivalence
eligibility. Its JSON semantic digest has no timestamp. Markdown rendering is
a human summary, not an authority record.

## Authoring modes

`overlay_preserve` requires every owned table to have exactly one replacement,
and every replacement to have explicit ownership. Unlisted tables are declared
unowned and are preserved only by the downstream generator.

`full_replacement` requires all 28 current source-owned tables to have an
explicit ownership declaration and replacement. Generator v2 represents this
as all 28 ordered tables and intentionally omits `owned_tables`; the intake
review record retains the explicit authorization evidence. `reject_partial` is
a review policy and cannot emit.

Canonical `0/128/255` defaults for unspecified tables are never filled or
treated as authority. This is a regression guard for the prior canonical-grid
failure class.

## CLI

```bash
python3 tools/manage_source_owned_source_authority_intake.py inspect-baseline
python3 tools/manage_source_owned_source_authority_intake.py create-template --output /absolute/path/intake.json
python3 tools/manage_source_owned_source_authority_intake.py validate /absolute/path/intake.json
python3 tools/manage_source_owned_source_authority_intake.py review /absolute/path/intake.json --output /absolute/path/review.json
python3 tools/manage_source_owned_source_authority_intake.py emit-generator-input /absolute/path/intake.json --output /absolute/path/generator-input.json
python3 tools/manage_source_owned_source_authority_intake.py prove-source-equivalence /absolute/path/intake.json --output /absolute/path/generator-input.json
```

Template creation is deterministic and safe: it is a `draft`, has unknown
provenance, no selected mode, no owned tables, no replacements, and fixed
human-required placeholders. It includes baseline inventory only as reference
data. All writes require an absolute offline output path and refuse `src/**`,
active publication names, and overwriting the input.

Exit codes are: 0 success; 2 structure; 3 authority/provenance; 4 baseline;
5 ownership/replacement; 6 ineligible/no-op; 7 I/O/integrity; 8 invariant.

## Downstream and hardware gates

Emission immediately calls the existing v2 input validator, generator,
manifest validator, and production gate. The emitted generator input is still
offline. Preparation/install and any later active-source candidate are separate
cycles. Firmware build and hardware testing only apply to that later active
candidate cycle, and active changes merge only after HARDWARE_PASS.

The required next production input is a human-approved version-1 intake with
an explicit owned-table set, exact replacement points, per-table authority
references, approval evidence, and the current matching baseline identity.
