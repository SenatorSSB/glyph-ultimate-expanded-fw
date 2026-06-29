# Generated Source-Owned Schema Scaffold

Status label: INERT SOURCE SCAFFOLD / DOCS-TOOLS ONLY.

This packet adds the first generated-source-owned schema/source scaffold for a
future generated immutable runtime-table realization path. It is intentionally
inert: the scaffold is not referenced by `src/modes/Ultimate.cpp`, is not wired
into runtime selection, and does not change active firmware behavior.

## Accepted Evidence

- `generated_source_owned_realization_design.md` is the governing design input
  for this scaffold.
- Source-owned active-state preselection has recorded `HARDWARE_PASS` evidence.
  The accepted baseline keeps the source-owned active view published.
- Parsed/candidate machinery present while the source-owned active view remains
  published has recorded `HARDWARE_PASS` evidence.
- Parsed `candidate.view` published active, source-owned-materialized
  `candidate.view` published active, and dedicated active storage published
  active are recorded `HARDWARE_FAIL` evidence. The active-storage
  `HARDWARE_FAIL` evidence is recorded in
  `docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md`.
- The low-level failure mechanism remains unproven.
- Nunchuk remains `NOT_TESTED`.

## Scaffold Boundary

The added source files under
`src/modes/runtime_config/generated_source_owned/` define only compile-time
schema/version metadata, generated artifact naming conventions, constexpr
metadata structs, and a fixture-like table-shape example. They are placeholders
for generated C++ immutable source-owned runtime table artifacts that may be
built into firmware in a future hardware-gated implementation.

The scaffold does not publish generated tables active. It does not introduce a
parser payload path, runtime-loaded config, persistent storage, WebSerial/device
write, backend/config.pb write path, firmware flashing automation,
`candidate.view` active publication, or RAM-backed active table publication.

## Future Hardware Gate

Future hardware gate required before generated source-owned tables are selected
active. This branch is not approval to select generated tables as an active
source, alter active source selection, or replace the current published source.

Any future branch that selects generated source-owned tables active must provide
source-backed generated artifacts, build evidence, and a hardware plan/result
before merge. It must preserve the current prohibitions on parser payload
activation, runtime-loaded config, persistent storage, WebSerial/device write,
backend/config.pb write paths, firmware flashing automation, `candidate.view`
active publication, RAM-backed active table publication, and nunchuk validation
claims unless later source-backed and hardware-validated evidence changes those
boundaries.

## Non-Claims

- This scaffold does not change active behavior.
- This scaffold does not prove the low-level failure mechanism.
- This scaffold does not implement a generator.
- This scaffold does not wire generated tables into active runtime selection.
- This scaffold does not implement runtime-loaded config, storage,
  WebSerial/device write, backend/config.pb write, or flashing automation.
- This scaffold does not claim nunchuk validation.
