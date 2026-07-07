# Generated Source-Owned Layout Spec

Status label: INERT LAYOUT SPEC / DOCS-TOOLS ONLY.

This packet records the declarative layout spec mirror for the source-owned
generator lane. It follows `generated_source_owned_generator_contract.md` and
describes the current baseline table shape without changing active runtime
selection.

## Accepted Evidence

- Source-owned active-state preselection has recorded `HARDWARE_PASS` evidence.
- Parsed/candidate machinery present while the source-owned active view remains
  published has recorded `HARDWARE_PASS` evidence.
- Candidate-backed active publication remains `HARDWARE_FAIL` evidence.
- Dedicated active storage published active remains `HARDWARE_FAIL` evidence.
- The low-level failure mechanism remains unproven.
- Nunchuk remains `NOT_TESTED`.

## Layout Spec Contract

The declarative spec is a JSON object that mirrors the current source-owned
baseline generator input. It must describe:

- `schema_version: 1`
- `layout_spec_kind: generated_source_owned_layout_spec`
- `layout_name: current_source_owned_baseline_layout`
- `controller_family: glyph_mk6`
- `profile_name: example_source_owned_runtime_config`
- `revision: 1`
- `table_shape.table_count: 27`
- `table_shape.points_per_table: 9`
- `table_shape.axes_per_point: 2`

The `tables` array is an ordered declarative mirror of the 27 current source
tables. Each entry names the source table slot with:

- `table_id`
- `table_name`
- `table_symbol`

The generator may use the spec as a validation and ordering mirror, but it does
not use the spec to activate runtime behavior, replace `RuntimeConfigView`, or
publish any active source path. It is not wired into runtime selection and
does not change active firmware behavior. The layout spec is inert and
docs-tools only. The normal generator input path now requires `layout_spec`,
and the explicit `--emit-from-layout-spec` generator mode consumes the packet
deterministically and still emits the same source-owned fixture.
Future hardware gate required before generated source-owned tables are
selected active.

## Non-Claims

- This packet does not change active firmware behavior.
- This packet does not wire generated tables into active runtime selection.
- This packet does not implement runtime-loaded config, persistent storage,
  WebSerial/device write, backend/config.pb write, or flashing automation.
- This packet does not claim nunchuk validation.
