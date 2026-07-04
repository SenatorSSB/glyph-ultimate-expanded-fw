# Source-Owned Table Replacement Generator Contract

Status label: GENERATOR CONTRACT / DOCS-TOOLS ONLY.

This packet follows `source_owned_table_replacement_design.md`. It defines a
stdlib-only generator/checker contract for replacing the numeric contents of
the existing source-owned `StickPoint` tables already consumed by
`kSourceOwnedCurrentBaselineRuntimeConfig`, without changing active
`RuntimeConfigView` selection and without writing patched tables into active
source paths on this branch.

## Accepted Evidence

- Source-owned active-state preselection has recorded `HARDWARE_PASS` evidence.
- Parsed/candidate machinery present while the source-owned active view remains
  published has recorded `HARDWARE_PASS` evidence.
- Parsed candidate.view published active has recorded `HARDWARE_FAIL` evidence.
- Source-owned-materialized candidate.view published active has recorded
  `HARDWARE_FAIL` evidence.
- Dedicated active storage has recorded `HARDWARE_FAIL` evidence.
- Generated source-owned baseline active `HARDWARE_FAIL` evidence shows that
  replacing the active `RuntimeConfigView` with a generated baseline-equivalent
  view is unsafe under current diagnostics.
- The low-level failure mechanism remains unproven.
- Nunchuk remains `NOT_TESTED`.

## Input Contract

The neutral replacement JSON input must reject duplicate keys and contain:

- `schema_version`
- `replacement_kind: source_owned_table_content_replacement`
- `target_file: src/modes/UltimateIdentityRuntimeTables.hpp`
- `table_shape`
- `tables`

`table_shape` must contain:

- `table_count: 27`
- `points_per_table: 9`
- `axes_per_point: 2`

Each table must include a `table_symbol` matching an existing source-owned
table symbol and exactly 9 points. Each point must contain integer byte values
`x` and `y` in the inclusive range `[0, 255]`. Duplicate `table_symbol` values
are rejected. The set of replacement symbols must exactly match the current
source table symbols.

Optional `metadata` may record `controller_family`, `profile_name`, `revision`,
and `notes`; metadata is descriptive only and does not affect emitted source
text.

## Output Contract

`tools/generate_source_owned_table_replacement.py` reads
`src/modes/UltimateIdentityRuntimeTables.hpp` and emits patched
`UltimateIdentityRuntimeTables.hpp` text to stdout or an explicit output path.
It must preserve table symbol names, table order, table count, table shape,
comments, includes, active-state text, and every non-table source region. It
must only modify `x`/`y` numeric table contents inside the existing
`constexpr StickPoint k...Table[9]` initializers.

The fixture output lives at
`docs/runtime_config/fixtures/generated_outputs/UltimateIdentityRuntimeTables.replacement.example.hpp`.
It is an output fixture only. It is not written into
`src/modes/UltimateIdentityRuntimeTables.hpp`, is not compiled by this branch,
and is not wired into active firmware behavior.

## Guardrails

- no RuntimeConfigView selection change
- `runtime_config_view_replacement_allowed: false`
- `active_view_selection_changed: false`
- `source_owned_table_content_replacement_wired: false`
- `active_source_file_modified: false`
- `output_fixture_only: true`
- runtime-loaded config remains not implemented
- persistent storage remains not implemented
- WebSerial/device write remains not implemented
- backend/config.pb write path remains not implemented
- flashing automation remains not implemented
- hardware test is not required before merge for this docs/tools contract
- Nunchuk remains `NOT_TESTED`

## Non-Claims

- This packet does not prove the low-level failure mechanism.
- This packet does not modify firmware source.
- This packet does not replace active table contents in source.
- This packet does not replace `RuntimeConfigView`.
- This packet does not change active view/state selection.
- This packet does not introduce a new active wrapper.
- This packet does not implement runtime-loaded config, persistent storage,
  WebSerial/device write, backend/config.pb write paths, or flashing
  automation.
- This packet does not claim nunchuk validation.
