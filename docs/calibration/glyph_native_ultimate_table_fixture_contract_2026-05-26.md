# Glyph Native Ultimate Table Fixture Contract - 2026-05-26

Scope: fixture contract for any future native Ultimate runtime table patch. This is pre-runtime design/checker work only and does not require or implement a production table.

## Contract Goals

A future table fixture must support:

- `table_contract_version`;
- named modifier states;
- explicit 9-way direction tables;
- direction keys `1..9`;
- neutral direction `5` as an explicit entry;
- absolute raw coordinates in `[0,255]`;
- center-relative display offsets that match `raw - 128` when both are present;
- optional source/evidence notes per coordinate;
- expected runtime branch exclusivity metadata;
- conflict/chord policy as explicit metadata;
- no game-semantic labels as required behavior.

## Template

The template fixture is `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`.

It contains example coordinates only. These coordinates are not production behavior, not hardware evidence, and not gameplay semantics.

## Checker

`tools/check_glyph_native_ultimate_table_fixture.py` validates the template and future fixtures without mutating files.

The checker validates:

- JSON root object shape;
- duplicate JSON object keys;
- contract version presence;
- required metadata objects;
- non-empty named modifier state list;
- exact direction key set `1..9` for each state;
- explicit neutral direction `5`;
- raw coordinate integer range `[0,255]`;
- center-relative offsets matching raw coordinates.

## Non-Goals

- No runtime table implementation.
- No production coordinate table requirement yet.
- No profile schema/proto/configurator changes.
- No macro, turbo, timing automation, or push-to-device automation.
- No Smash/game-semantic source changes.
