# Glyph Native Ultimate Table Fixture Contract - 2026-05-26

Scope: fixture contract for any future native Ultimate runtime table patch. This is pre-runtime design/checker work only and does not require or implement a production table.

## Contract Goals

A future table fixture must support:

- `table_contract_version`;
- `source_status`;
- `mode_scope`;
- named modifier states;
- named table entries;
- explicit 9-way direction tables;
- direction keys `1..9`;
- neutral direction `5` as an explicit entry;
- absolute `raw_x`/`raw_y` coordinates in `[0,255]`;
- center-relative `offset_x`/`offset_y` display offsets that match raw coordinates minus 128;
- optional source/evidence notes per coordinate;
- expected branch exclusivity metadata;
- chord/both-held policy as explicit metadata;
- preservation requirements metadata;
- no game-semantic labels as required behavior.

## Template

The template fixture is `docs/calibration/fixtures/glyph_native_ultimate_table_contract_TEMPLATE.json`.

It contains example coordinates only. These coordinates are not production behavior, not hardware evidence, and not gameplay semantics.

The template separates controller output contract shape from Smash/game semantics. Direction names are numeric keypad-style fixture keys only; they are not action labels or gameplay requirements.

## Checker

`tools/check_glyph_native_ultimate_table_fixture.py` validates the template and future fixtures without mutating files.

The checker validates:

- JSON root object shape;
- duplicate JSON object keys;
- contract version presence;
- required metadata objects;
- source status and mode scope presence;
- named table entry references;
- non-empty named modifier state list;
- exact direction key set `1..9` for each state;
- explicit neutral direction `5`;
- `raw_x`/`raw_y` coordinate integer range `[0,255]`;
- `offset_x`/`offset_y` values matching raw coordinates minus 128.

## Why This Comes First

The fixture contract gives future runtime work a reviewable target before any firmware logic changes. It allows source-shape and preservation checkers to validate table structure and boundary assumptions without claiming that any table is production-ready or hardware-accepted.

Future hardware evidence is still required before accepting a runtime implementation.

## Non-Goals

- No runtime table implementation.
- No production coordinate table requirement yet.
- No profile schema/proto/configurator changes.
- No macro, turbo, timing automation, or push-to-device automation.
- No Smash/game-semantic source changes.
