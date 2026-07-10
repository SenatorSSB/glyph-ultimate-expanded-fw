# Source-Owned Candidate Generation Diff Diagnosis

Status label: CURRENT.

This diagnostic records the candidate-generation output produced from
`docs/runtime_config/fixtures/generated_source_owned_layout_spec.json` and
compares it against the current checked-in source-owned baseline artifact at
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`.

## Classification

- `TABLE_CONTENT_EQUIVALENT`

## Summary

- The checked-in inert baseline artifact now matches the generated candidate
  on this branch.
- Table shape is unchanged: 28 tables, 9 points per table, 2 axes per point.
- Table order is unchanged.
- Metadata drift is absent.
- All 28 tables are source-aligned on this branch.

## Exact Equivalence

All source-owned tables are now source-aligned:

- `kDefaultTable`
- `kModeDefaultTable`
- `kX1Table`
- `kX2Table`
- `kMX1Table`
- `kMX2Table`
- `kY1Table`
- `kY2Table`
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
- `kTilt3Table`
- `kTilt1Minus41Table`
- `kRT1RF4CustomTable`
- `kMTilt1Table`
- `kMTilt2Table`
- `kMTilt3Table`
- `kLt1LowMagnitudeTable`

## Interpretation

This is a materialized source-owned candidate branch on the approved inert
alias path. The generated candidate output now matches the checked-in alias
file on this branch, while remaining offline-only and non-active.

The semantic comparison is implemented by
`tools/check_glyph_source_owned_candidate_generation_diff.py`.
