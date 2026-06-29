# Generated Source-Owned Runtime Config Generator Contract

Status label: GENERATOR CONTRACT / DOCS-TOOLS ONLY.

This packet defines the first offline generator contract for generated
source-owned runtime table artifacts. It follows
`generated_source_owned_realization_design.md` and
`generated_source_owned_schema_scaffold.md`.

This branch adds a neutral JSON input contract, a Python stdlib-only offline
generator, and docs fixtures for the generated C++ text output. It does not
write generated artifacts into active source paths by default, does not wire
generated tables active, and does not change active firmware behavior.

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
- `table_shape`
- `tables`

`table_shape` must contain:

- `table_count: 27`
- `points_per_table: 9`
- `axes_per_point: 2`

Each table must include `table_id` or `table_name`. For the current scaffold
sample, `table_id` values are expected to cover the 27 current table slots.
Each table must contain exactly 9 points. Each point must contain integer byte
values `x` and `y` in the inclusive range `[0, 255]`.

The generator emits tables in deterministic order. Integer `table_id` ordering
is preferred when present; table-name ordering is the fallback for name-only
inputs.

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
contract shape and byte ranges, rejects duplicate JSON keys, emits deterministic
C++ text, and rejects default writes into active source, HAL, or backend paths.

The generator may align with inert generated-source-owned schema names for
documentation consistency, but it does not depend on firmware build behavior.
The generated fixture is not selected active in this branch.

## Non-Claims

- This packet does not change active behavior.
- This packet does not prove the low-level failure mechanism.
- This packet does not wire generated tables into active runtime selection.
- This packet does not implement a parser payload path.
- This packet does not implement runtime-loaded config.
- This packet does not implement persistent storage.
- This packet does not implement WebSerial/device write.
- This packet does not implement backend/config.pb write paths.
- This packet does not implement firmware flashing automation.
- This packet does not claim nunchuk validation.
