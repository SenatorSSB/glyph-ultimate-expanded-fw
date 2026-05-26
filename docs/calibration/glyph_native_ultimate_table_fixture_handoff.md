# Glyph Native Ultimate Table Fixture Handoff

Date: 2026-05-26

## What This Branch Adds

- `docs/calibration/glyph_native_ultimate_table_fixture_contract_2026-05-26.md`.
- `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`.
- `tools/check_glyph_native_ultimate_table_fixture.py`.

## Important Boundaries

- The template is not a production table.
- The checker does not require production table data.
- Direction `5` is explicitly neutral by contract shape, not a gameplay claim.
- No runtime/source/configurator behavior changed.
- No build artifacts or binaries were committed.

## Next Gate

A future runtime patch should not proceed until this contract is reviewed and paired with source-shape checks plus hardware preservation testing.
