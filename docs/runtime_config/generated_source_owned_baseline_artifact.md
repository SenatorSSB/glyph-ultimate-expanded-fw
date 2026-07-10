# Generated Source-Owned Baseline Artifact

Status label: CURRENT.

This packet records the inert generated source-owned runtime config artifact
materialized on the current candidate branch. The artifact lives at
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`,
and it matches the generated candidate output fixture on this branch.

This branch follows `generated_source_owned_artifact_install.md` and
`generated_source_owned_generator_contract.md`. It keeps the earlier generated
example artifact as a deterministic fixture only and does not select either
generated artifact active.

The source-inspection baseline CLI remains `--emit-current-source-owned-baseline`.
The explicit `--emit-from-layout-spec` packet mode remains inert and reproduces
the same baseline-shaped generated artifact when run against
`generated_source_owned_layout_spec.json`.

## Scope

- Add one generated source-owned runtime config artifact for the current
  baseline table data.
- Keep the artifact as an inert generated-table placeholder.
- Keep it not wired into runtime selection.
- Keep it not included by `src/modes/Ultimate.cpp`.
- Do not modify `src/modes/Ultimate.cpp`, `ResolveActiveRuntimeConfig`,
  `GetActiveRuntimeConfigState`, or `UpdateAnalogOutputs`.
- Do not add parser, runtime-loaded config, persistent storage, WebSerial/device
  write, backend/config.pb write path, or firmware flashing automation.

## Materialization Proof

The checker `tools/check_glyph_generated_source_owned_baseline_artifact.py`
proves the materialized artifact matches the generated candidate output
fixture on this branch. In short, the materialized artifact matches the
generated candidate output fixture, and the generator reproduces the same
output from `generated_source_owned_layout_spec.json`.

The comparison reads the generated candidate output fixture from
`docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp`,
reads the materialized artifact from
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`,
regenerates the same output from
`docs/runtime_config/fixtures/generated_source_owned_layout_spec.json`, and
compares:

- table count;
- table names and order;
- point count per table;
- every x/y point;
- deterministic generator output.

The checker does not use artifact hashes as gates. If the generated output
fixture, the materialized artifact, or the deterministic generator output
drifts, the materialization check fails.
The fixture
`docs/runtime_config/fixtures/generated_source_owned_baseline_artifact.json`
sets
`materialized_candidate_artifact_matches_generated_output: true` only because
this source-generated/artifact comparison is required to pass.

## Evidence Boundary

The current accepted model remains unchanged:

- RAM-backed active table publication remains unsafe under current diagnostics.
- Active-storage `HARDWARE_FAIL` evidence is recorded in
  `diagnostic_active_storage_published_hardware_failure_2026-06-28.md`.
- Source-owned active-state `HARDWARE_PASS` evidence is recorded on the
  source-owned active-state preselection result branch.
- Generated source-owned artifacts are the chosen next path for future
  hardware-gated active-selection diagnostics.

This artifact does not prove a low-level hardware failure mechanism. The
low-level failure mechanism remains unproven. Nunchuk remains `NOT_TESTED`.

## Activation Gate

This branch does not change active firmware behavior and does not require a
hardware test before merge. A future hardware gate required before generated
source-owned baseline artifact is selected active.

Future activation work must happen on a separate hardware-gated branch and must
continue to avoid runtime-loaded config, persistent storage, WebSerial/device
write, backend/config.pb write path, firmware flashing automation, and
candidate-backed active publication unless explicitly approved and
source-backed.
