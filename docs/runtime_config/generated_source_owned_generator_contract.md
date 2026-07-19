# Generated Source-Owned Runtime Config Generator Contract

Status label: GENERATOR CONTRACT / DOCS-TOOLS ONLY.

This packet defines the first offline generator contract for generated
source-owned runtime table artifacts. It follows
`generated_source_owned_realization_design.md` and
`generated_source_owned_schema_scaffold.md`, and it now accepts the declarative
`generated_source_owned_layout_spec.md` mirror for the current baseline shape.
The generator input now requires `layout_spec`; spec-less JSON is rejected.
The 28-entry layout-spec mirror is strict and ordered: the generator rejects
reordered, truncated, or extra-key entries instead of normalizing them.

This branch adds a neutral JSON input contract, a Python stdlib-only offline
generator, an inert declarative layout spec, and docs fixtures for the
generated C++ text output. It also exposes an explicit `--emit-from-layout-spec`
packet-input mode so the declarative layout-spec packet can be consumed
deterministically. It does not write generated artifacts into active source
paths by default, does not wire generated tables active, and does not change
active firmware behavior.

The companion offline installer
`tools/install_generated_source_owned_runtime_config.py` can take either a
validated layout-spec packet or already-generated C++ output. It accepts
`--from-layout-spec`, `--from-generated-output`, and `--dry-run` so the inert
source-owned alias path can be previewed or written without activating runtime
selection.

## Accepted Evidence

- Source-owned active-state preselection has recorded `HARDWARE_PASS` evidence.
- Parsed/candidate machinery present while the source-owned active view remains
  published has recorded `HARDWARE_PASS` evidence.
- Dedicated active storage published active has recorded `HARDWARE_FAIL`
  evidence in
  `docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md`.
- RAM-backed active runtime table publication remains forbidden under current
  evidence.
- The low-level failure mechanism remains unproven.
- Nunchuk remains `NOT_TESTED`.

## Input Contract

The neutral JSON input must be a JSON object with duplicate keys rejected. The
required top-level keys are:

- `schema_version`
- `artifact_kind`
- `controller_family`
- `profile_name`
- `revision`
- `layout_spec`
- `table_shape`
- `tables`

`layout_spec` must be a declarative mirror of the current baseline layout. It
must match the generator input metadata and table shape, and it must describe
the current 28-table baseline order without changing the active runtime path.
The mirror is canonical and ordered; each slot must already match the declared
table id, name, and symbol, and the generator does not sort or repair the
array.

The explicit `--emit-from-layout-spec` mode consumes the declarative
`generated_source_owned_layout_spec.json` packet, validates that the embedded
layout spec remains inert, and emits the same deterministic source-owned C++
fixture as the standard generator input path.

`table_shape` must contain:

- `table_count: 28`
- `points_per_table: 9`
- `axes_per_point: 2`

Each table must include `table_id` or `table_name`. For the current scaffold
sample, `table_id` values are expected to cover the 28 current table slots.
Each table must contain exactly 9 points. Each point must contain integer byte
values `x` and `y` in the inclusive range `[0, 255]`.

The generator emits tables in deterministic order. The declarative
`layout_spec.tables` order is authoritative only when it already matches the
canonical baseline order. The generator rejects reordered or incomplete
layout-spec tables and does not silently normalize them.

`generated_source_owned_layout_spec.md` describes the inert spec packet and
its fixture pair in more detail. The spec is validation-only and does not alter
active runtime selection.

Production candidate generation must use one explicit policy:

- Full replacement: every active table is explicitly specified and validated.
- Overlay/preserve: only explicitly owned tables change; unspecified tables
  are copied from the current source-owned baseline.
- Reject: partial input without an explicit overlay/preserve policy fails.

Do not silently fill unspecified production tables with example/canonical
defaults. Example metadata such as `example_source_owned_runtime_config` is
diagnostic-only and must not produce a production candidate without explicit
approval. Generated candidates require a table-by-table change manifest, and
preserved tables must match the current source-owned baseline semantically.

## Output Contract

The generated C++ text must contain this explicit marker:

```text
generated source-owned runtime config artifact
```

Generated C++ output must use source-owned immutable style, such as
`static constexpr` table metadata and coordinate arrays. The sample output
fixture is written under
`docs/runtime_config/fixtures/generated_outputs/`, not under active firmware
include paths.

Generated output must not contain:

- `GetActiveRuntimeConfigState`
- `ResolveActiveRuntimeConfig`
- `UpdateAnalogOutputs`
- `active_view =`
- `candidate.view`
- `RuntimeConfigStorage`
- `WebSerial`
- `config.pb`
- `flash`
- `flashing`

## Generator Boundary

`tools/generate_source_owned_runtime_config.py` is stdlib-only. It validates the
contract shape, layout spec mirror, and byte ranges, rejects duplicate JSON
keys, emits deterministic C++ text, and rejects default writes into active
source, HAL, or backend paths. The explicit spec-input mode is
`--emit-from-layout-spec`, and the baseline/source-inspection mode remains
`--emit-current-source-owned-baseline`.

The generator may align with inert generated-source-owned schema names for
documentation consistency, but it does not depend on firmware build behavior.
The generated fixture is not selected active in this branch.

## Non-Claims

- This packet does not change active behavior.
- This packet does not prove the low-level failure mechanism.
- Root cause remains unproven.
- This packet does not wire generated tables into active runtime selection.
- This packet does not make `layout_spec` an active publication path.
- This packet does not implement a parser payload path.
- This packet does not implement runtime-loaded config.
- This packet does not implement persistent storage.
- This packet does not implement WebSerial/device write.
- This packet does not implement backend/config.pb write paths.
- This packet does not implement firmware flashing automation.
- This packet does not claim nunchuk validation.
- Nunchuk remains `NOT_TESTED`.
