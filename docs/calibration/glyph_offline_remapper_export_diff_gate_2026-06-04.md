# Glyph Offline Remapper Export Diff Gate - 2026-06-04

## Purpose and scope

This records a docs/tools-only gate over the no-device external remapper import/export result and the committed diff reports.

The gate interpretation is that import/export succeeded with warnings, the no-device boundary was preserved, the exported artifact was recorded, structural diff exists, Ultimate profile diff exists, and metadata diff exists.

This gate does not implement an adapter, does not generate or transform an external-remapper-compatible JSON candidate, and does not claim official configurator compatibility.

## Source artifacts

Gate fixture:

- `docs/calibration/fixtures/glyph_offline_remapper_export_diff_gate_2026-06-04.json`

Checker:

- `tools/check_glyph_offline_remapper_export_diff_gate.py`

Component evidence:

- `docs/calibration/glyph_offline_remapper_experiment_result_2026-06-04.md`
- `docs/calibration/glyph_offline_remapper_export_structural_diff_2026-06-04.md`
- `docs/calibration/glyph_offline_remapper_ultimate_diff_report_2026-06-04.md`
- `docs/calibration/glyph_offline_remapper_metadata_diff_report_2026-06-04.md`

Exported artifact:

- `docs/calibration/fixtures/glyph_offline_remapper_exported_GlyphUserProfiles_2026-06-04.json`

## Gate interpretation

- import/export succeeded with warnings
- no-device boundary preserved
- exported artifact recorded
- structural diff exists
- Ultimate profile diff exists
- metadata diff exists
- runtime-owned behavior not represented by external remapper profile-level JSON
- adapter remains blocked
- official configurator compatibility remains unclaimed
- device write/WebSerial remains blocked
- protobuf binary generation remains blocked
- runtime-loaded config remains blocked

## Boundaries

This is not official compatibility and does not claim official configurator compatibility.

This is not device write, not WebSerial, not protobuf binary generation, not runtime-loaded config, and not hardware validation.

Runtime-owned behavior not represented in the exported external remapper profile-level JSON remains blocked from adapter interpretation. Adapter implementation remains blocked, and the fixture keeps `adapter_implemented` false.

## Allowed next work

- docs/tools-only adapter candidate schema planning
- no-device adapter prototype planning, not implementation
- further structural diff improvements
- manual repeated experiment with browser/OS/version recorded

## Disallowed without approval

- adapter implementation
- external-remapper-compatible JSON generation
- device write/WebSerial
- protobuf binary generation
- runtime-loaded config
- official compatibility claim
- hardware validation claim

## Non-goals and caveats

- not official compatibility
- not device write
- not WebSerial
- not protobuf binary generation
- not hardware validation
- no adapter implementation
- no artifact transformation or generation
