# Source-authority intake workflow

Status: offline tooling only; the exact baseline-equivalent `kX1Table`
`overlay_preserve` intake is production-authorized, but it is a semantic
no-op, creates no active-source change, and is not a hardware candidate.

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

Production authority and semantic change are separate facts. An approved
production-authority intake may deliberately reproduce an owned table's exact
baseline points to establish ownership without changing bytes. Such an intake
may emit deterministic offline generator input, but its review report records
`semantic_change_present: false` and
`future_hardware_candidate_after_downstream_gates: false`. A downstream
hardware-candidate gate continues to reject `NO_OP` output.

The deterministic JSON review report contains the complete blocker list,
baseline match status, ownership/replacement counts, and separate
`production_emission_allowed` and `source_equivalence_emission_allowed` flags.
Its semantic digest has no timestamp. Markdown rendering is a library helper
for human summaries and is not currently a CLI output format or authority
record.

## Authoring modes

`overlay_preserve` requires every owned table to have exactly one replacement,
and every replacement to have explicit ownership. Unlisted tables are declared
unowned and are preserved only by the downstream generator. Intake authoring
arrays may use any order, but emitted generator-input v2 canonicalizes both
`owned_tables` and `tables` to the authoritative current baseline table order.
This only reorders already explicit ownership; it never infers ownership.

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

`validate` is a script and CI gate. It always prints the deterministic review
report and may also write it with `--output`, but returns zero only when that
report has no blockers. `review` is observational: it also produces the
complete report and returns zero when report generation succeeds, including
when the report says that both emission flags are false.

When a blocked validation report has several categories, the reusable selector
uses this fixed precedence: baseline mismatch, authority/provenance,
ownership/unowned change, candidate ineligible, integrity, invalid input, then
internal invariant. The selected category determines only the process status;
the report still retains all blockers. Exit codes are: 0 success; 2 invalid
input/structure; 3 authority/provenance; 4 baseline mismatch; 5
ownership/unowned change; 6 candidate ineligible (including an attempted
hardware-candidate no-op); 7 I/O/integrity; 8 internal
invariant. An unexpected blocker category maps to 8 rather than incorrectly
returning success. Blocked emission uses the same selector, so `validate` and
the matching emit command agree on the category for a mixed-blocker packet.

The CLI translates expected downstream `GeneratorModesError` failures from
baseline inspection, template construction, review-time baseline inspection,
and emission into the same stable category and preserves the error message.
Unexpected programming exceptions are not relabeled as ordinary input errors.

Template creation is deterministic and safe: it is a `draft`, has unknown
provenance, no selected mode, no owned tables, no replacements, and fixed
human-required placeholders. It includes baseline inventory only as reference
data. All writes require an absolute offline output path, resolve symlinks
before classification, refuse protected repository components
case-insensitively (`src`, `include`, `lib`, `backend`, `HAL`, and `.git`),
refuse case-insensitive active-publication names (`candidate.view`,
`active_storage.view`, and `RuntimeConfigView`), and refuse overwriting the
input. In particular, every case variation of `src/**` remains forbidden.

## Downstream and hardware gates

Emission immediately calls the existing v2 input validator, generator,
manifest validator, and production gate. The emitted generator input is still
offline. This workflow performs no active-source change, preparation, install,
build, candidate creation, device write, persistence, flashing, or hardware
behavior. Preparation/install and any later active-source candidate are
separate cycles. Firmware build and hardware testing only apply to that later
active candidate cycle, and active changes merge only after HARDWARE_PASS.

The canonical first production-authority intake is
`intakes/x1_baseline_equivalent_overlay_v1.intake.json`. It owns only
`kX1Table`, copies that table's exact current nine-point baseline, and preserves
the other 27 tables as unowned. Its project-owner approval reference is
`docs/agent_framework/USER_DIRECTION.md#glyph-ud-008`. It validates the
incremental authority path only; it does not prove a future active X1 value
change safe or authorize any additional table.
