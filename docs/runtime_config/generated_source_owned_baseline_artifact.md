# Generated Source-Owned Baseline Artifact

Status label: CURRENT.

This packet records active compile-time generated source-owned runtime config
table content for the current source-owned baseline. The artifact lives at
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`.

This branch follows `generated_source_owned_artifact_install.md` and
`generated_source_owned_generator_contract.md`. It keeps the earlier generated
example artifact as a deterministic inert fixture only; the current baseline
header is active compile-time table content through
`UltimateIdentityRuntimeTables.hpp`.
The baseline header is included indirectly by
`src/modes/UltimateIdentityRuntimeTables.hpp`; active RuntimeConfigView
publication remains source-owned and unchanged. The generated example artifact
is not included by `src/modes/Ultimate.cpp` and is not wired into runtime
selection.

The source-inspection baseline CLI remains `--emit-current-source-owned-baseline`.
The explicit `--emit-from-layout-spec` packet mode remains inert and reproduces
the same baseline-shaped generated artifact when run against
`generated_source_owned_layout_spec.json`.

## Scope

- Add one generated source-owned runtime config artifact for the current
  baseline table data.
- Classify the artifact as active compile-time table-content source through
  `UltimateIdentityRuntimeTables.hpp`.
- Keep the existing active RuntimeConfigView publication path unchanged.
- Keep it included indirectly through `src/modes/UltimateIdentityRuntimeTables.hpp`;
  `Ultimate.cpp` retains only the existing wrapper include. The active table
  content is included by `src/modes/UltimateIdentityRuntimeTables.hpp`.
- Do not modify `src/modes/Ultimate.cpp`, `ResolveActiveRuntimeConfig`,
  `GetActiveRuntimeConfigState`, or `UpdateAnalogOutputs`.
- Do not add parser, runtime-loaded config, persistent storage, WebSerial/device
  write, backend/config.pb write path, or firmware flashing automation.

## Equivalence Proof

The checker `tools/check_glyph_generated_source_owned_baseline_artifact.py`
proves the generated baseline artifact is equivalent to the current
source-owned baseline by source inspection.

The comparison reads the current source-owned baseline table order from
`src/modes/UltimateRuntimeConfigInterpreter.hpp`, reads source table point
values from `src/modes/UltimateIdentityRuntimeTables.hpp`, reads generated
table values from
`src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`,
and compares:

- table count;
- table names and order;
- point count per table;
- every x/y point.

The checker does not use artifact hashes as gates. If any source table name,
table order, point count, or point value drifts, the equivalence check fails.
The fixture
`docs/runtime_config/fixtures/generated_source_owned_baseline_artifact.json`
sets
`generated_baseline_artifact_equivalent_to_current_source_owned_baseline: true`
only because this source/artifact comparison is required to pass.

## Evidence Boundary

The current accepted model remains unchanged:

- RAM-backed active table publication remains unsafe under current diagnostics.
- Active-storage `HARDWARE_FAIL` evidence is recorded in
  `diagnostic_active_storage_published_hardware_failure_2026-06-28.md`.
- Source-owned active-state `HARDWARE_PASS` evidence is recorded on the
  source-owned active-state preselection result branch.
- Generated source-owned artifacts remain the chosen path for future
  hardware-gated active-selection diagnostics when table behavior changes.

This artifact does not prove a low-level hardware failure mechanism. The
low-level failure mechanism remains unproven. Nunchuk remains `NOT_TESTED`.

## Activation Gate

This correction changes classification and host-side mutation safety only; it
does not change any table byte, routing decision, or active RuntimeConfigView
publication; it does not change active firmware behavior. No hardware test is
required.

Future behavior-changing activation work must happen on a separate
hardware-gated branch and must continue to avoid runtime-loaded config,
persistent storage, WebSerial/device write, backend/config.pb write path,
firmware flashing automation, and candidate-backed active publication unless
explicitly approved and source-backed.
