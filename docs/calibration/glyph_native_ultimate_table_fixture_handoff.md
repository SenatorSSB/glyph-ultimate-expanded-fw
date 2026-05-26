# Glyph Native Ultimate Table Fixture Handoff

Date: 2026-05-26

## What This Branch Adds

- `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`.
- `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`.
- `tools/check_glyph_native_ultimate_table_fixture.py`.

The template includes explicit `source_status`, `mode_scope`, named table entries, direction keys `1..9`, neutral direction `5`, flat `raw_x`/`raw_y` and `offset_x`/`offset_y` coordinate fields, branch exclusivity metadata, chord/both-held policy metadata, preservation requirements metadata, and source evidence fields.

## Important Boundaries

- The template is not a production table.
- The checker does not require production table data.
- Direction `5` is explicitly neutral by contract shape, not a gameplay claim.
- Controller output fixture shape remains separate from Smash/game semantics.
- Future hardware evidence is still required before runtime acceptance.
- No runtime/source/configurator behavior changed.
- No build artifacts or binaries were committed.

## Next Gate

A future runtime patch should not proceed until this contract is reviewed and paired with source-shape checks plus hardware preservation testing.
