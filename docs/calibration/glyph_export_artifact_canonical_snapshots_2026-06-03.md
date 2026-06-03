# Glyph Export Artifact Canonical Snapshots - 2026-06-03

## Purpose and status

- These snapshots are offline guardrails for committed export-related docs/tools artifacts.
- They canonicalize committed artifact text into deterministic hashes plus a few bounded summary counts.
- They are not firmware.
- They are not runtime-loaded config.
- They are not serial/device write behavior.
- They are not hardware validation.

## Covered artifacts

- Generated-config prototype fixture
- Runtime config candidate sample fixture
- Senscope export package sample fixture
- Runtime config validation report fixture
- Generated C++ table review artifact
- Behavior cases fixture

## Snapshot shape

- `schema_name=glyph_export_artifact_snapshots`
- `snapshot_version=1`
- `status=docs_tools_canonical_snapshots`
- `hardware_status=not_new_hardware_result`
- Each artifact stores only repo path, canonical-text SHA-256, status/hardware caveats, and selected summary counts.

## Summary counts

- Generated-config prototype table count must stay `25`.
- Runtime config candidate table count must stay `25`.
- Generated C++ table declaration count must stay `25`.
- Behavior case count is sourced from the committed behavior-cases fixture.
- Invalid corpus counts are sourced from the committed generated-config and runtime-candidate invalid-corpus fixtures.

## Non-goals

- No firmware runtime behavior change
- No generated C++ integration into firmware
- No runtime-loaded config implementation
- No serial/device write behavior
- No hardware or nunchuk validation claim
