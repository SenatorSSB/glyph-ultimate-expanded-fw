# Source-Owned Candidate Generation Diff Diagnosis

Status label: CURRENT.

This diagnostic records the candidate-generation output produced from
`docs/runtime_config/fixtures/generated_source_owned_layout_spec.json` and
compares it against the current checked-in source-owned baseline artifact at
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`.

## Classification

- `TABLE_CONTENT_DIFFERENT`

## Summary

- The candidate output is not byte-for-byte equivalent to the current
  source-owned baseline.
- Table shape is unchanged: 28 tables, 9 points per table, 2 axes per point.
- Table order is unchanged.
- Metadata drift is present: `profile_name` changes from
  `current_source_owned_baseline_runtime_config` to
  `example_source_owned_runtime_config`.
- Table-content drift is the real mismatch: 26 tables collapse to the same
  canonical `0/128/255` grid pattern.
- Two tables remain source-aligned: `kY2Table` and `kTilt3Table`.
- The checker emits a table-by-table change manifest for all 28 source-owned
  table slots: 26 `replace_candidate_points` rows and 2
  `preserve_source_owned_baseline` rows.
- The changed values are structurally valid byte coordinates with the expected
  shape, but they are semantically unsuitable for the current source-owned
  profile.
- The candidate tested as HARDWARE_FAIL on
  `runtime-config-generated-canonical-grid-candidate` commit
  `e643017c1577c9ca2b94581fa6f18c0dfb1bac9b`.

## Exact Non-Equivalence

The following source-owned tables changed content in the candidate output:

- `kDefaultTable`
- `kModeDefaultTable`
- `kX1Table`
- `kX2Table`
- `kMX1Table`
- `kMX2Table`
- `kY1Table`
- `kMY1Table`
- `kLayerNormalXTable`
- `kMLayerNormalXTable`
- `kLayerFlipperTable`
- `kMLayerFlipperTable`
- `kY1Tilt1Table`
- `kMY1Tilt1Table`
- `kY1LayerFlipperTable`
- `kMY1LayerFlipperTable`
- `kY1LayerNormalXTable`
- `kMY1LayerNormalXTable`
- `kTilt1Table`
- `kTilt2Table`
- `kTilt1Minus41Table`
- `kRT1RF4CustomTable`
- `kMTilt1Table`
- `kMTilt2Table`
- `kMTilt3Table`
- `kLt1LowMagnitudeTable`

The source-aligned tables were:

- `kY2Table`
- `kTilt3Table`

## Interpretation

This is not a formatting-only diff and not a pure canonicalization-only diff.
It is hardware-candidate material because table contents changed while the
shape stayed stable.

The immediate mechanism supported by source/checker evidence is that the
example/canonical layout-spec candidate generation produced a complete
28-table artifact whose 26 non-Y2/Tilt3 tables are canonical `0/128/255`
grids instead of current source-owned table contents. This is not a proven
low-level firmware root cause.

The user-reported HARDWARE_FAIL is consistent with this table-content
diagnosis: Y2 routing and Tilt3 left-stick modification still worked, while
most modifier-driven left-stick magnitude changes, including Z and the Y2
sublayer left-stick modification, failed. Routing/digital side effects appear
functional in the reported Y2 scope. Nunchuk remains NOT_TESTED.

## Candidate-Generation Policy

Future candidate generation must select one explicit mode:

- Full replacement: every active table is explicitly specified and validated.
- Overlay/preserve: only explicitly owned tables change; all unspecified
  tables are copied from the current source-owned baseline.
- Reject: partial input without an explicit overlay/preserve policy fails.

Production candidate generation must not silently fill unspecified active
tables with example/canonical defaults. Example profile metadata must not
create a production candidate without explicit approval. Every generated
candidate must provide a table-by-table change manifest, and preserved tables
must match the current source-owned baseline semantically.

The semantic comparison is implemented by
`tools/check_glyph_source_owned_candidate_generation_diff.py`.
