# Generated Source-Owned Artifact Install

Status label: INERT ARTIFACT INSTALL / DOCS-TOOLS ONLY.

This packet defines the controlled offline install workflow for a generated
source-owned runtime config artifact. It follows
`generated_source_owned_generator_contract.md` and
`generated_source_owned_schema_scaffold.md`.

The installed example artifact lives under
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp`.
It is a source-owned immutable table text artifact, but it is intentionally
inert: it is not included by `src/modes/Ultimate.cpp`, is not wired into
runtime selection, and does not change active firmware behavior.

## Accepted Evidence

- Source-owned active-state preselection has recorded `HARDWARE_PASS` evidence.
- Parsed/candidate machinery present while the source-owned active view remains
  published has recorded `HARDWARE_PASS` evidence.
- Active-storage `HARDWARE_FAIL` evidence is recorded in
  `docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md`.
- RAM-backed active runtime table publication remains forbidden under current
  evidence.
- The low-level failure mechanism remains unproven.
- Nunchuk remains `NOT_TESTED`.

## Install Workflow

The generator remains Python stdlib-only and rejects source-tree output by
default. The only approved source install path is the explicit inert install
mode:

```bash
python3 tools/generate_source_owned_runtime_config.py \
  --install-inert-source-artifact \
  docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json \
  src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp
```

The same generator also exposes an explicit `--emit-from-layout-spec` packet
mode for `docs/runtime_config/fixtures/generated_source_owned_layout_spec.json`.
That mode is still inert: it validates the declarative layout-spec packet and
produces the same deterministic source-owned C++ text without changing active
runtime selection.

The installed source artifact must contain these markers:

- `generated source-owned runtime config artifact`
- `inert generated-table placeholder`
- `not wired into runtime selection`

The checker regenerates the example output from
`docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json`
and compares it to the installed inert source artifact. The installed artifact
is deterministic from the example input.

## Active-Behavior Boundary

This branch does not modify `src/modes/Ultimate.cpp`, does not include the
generated artifact from `Ultimate.cpp`, does not modify
`ResolveActiveRuntimeConfig()`, `GetActiveRuntimeConfigState()`, or
`UpdateAnalogOutputs(...)`, and does not select generated tables active.

Future hardware gate required before generated source-owned tables are selected
active. This install workflow is not approval to alter active source selection,
replace the current active source-owned view, add a parser payload path,
implement runtime-loaded config, add persistent storage, add WebSerial/device
write, add backend/config.pb write paths, or add firmware flashing automation.

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
