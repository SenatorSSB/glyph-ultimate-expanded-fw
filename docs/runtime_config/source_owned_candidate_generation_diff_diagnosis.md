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

The semantic comparison is implemented by
`tools/check_glyph_source_owned_candidate_generation_diff.py`.

