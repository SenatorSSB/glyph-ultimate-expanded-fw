# Runtime Config Docs

Status label: CURRENT.

This directory contains runtime-config design, evidence, fixtures, and checker
contracts. Read the current boundary first; use archived diagnostics only when
you need the supporting evidence.

## Current Known-Good State

- Current active firmware state: latest Y2 layout source-owned port after
  HARDWARE_PASS.
- Primary packet:
  `docs/runtime_config/latest_y2_layout_source_owned_port.md`.
- Build packet:
  `docs/runtime_config/latest_y2_layout_source_owned_port_build_report_2026-06-29.md`.
- Hardware result:
  `docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md`.
- Checker:
  `tools/check_glyph_latest_y2_layout_source_owned_port.py`; it accepts the
  hardware-result branch and configurator after merge.
- Active RuntimeConfigView selection remains unchanged.
- Source-owned table/routing source path passed hardware for this layout.
- RuntimeConfigView replacement is not used.
- Generated active wrapper is not used.
- `candidate.view` is not active.
- RAM-backed active table publication is not used.
- Root cause remains unproven.
- Nunchuk remains NOT_TESTED.

## Generated Source-Owned Packets

The generated-source-owned realization lane is documented by these packets and
fixtures:

- `generated_source_owned_realization_design.md` and
  `fixtures/generated_source_owned_realization_design.json`
- `generated_source_owned_schema_scaffold.md` and
  `fixtures/generated_source_owned_schema_scaffold.json`
- `generated_source_owned_generator_contract.md` and
  `fixtures/generated_source_owned_generator_contract.json`
- `generated_source_owned_layout_spec.md` and
  `fixtures/generated_source_owned_layout_spec.json`
- `generated_source_owned_artifact_install.md` and
  `fixtures/generated_source_owned_artifact_install.json`
- `generated_source_owned_baseline_artifact.md` and
  `fixtures/generated_source_owned_baseline_artifact.json`
- `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`
- `fixtures/generated_source_owned_generator_input.example.json`
- `fixtures/generated_source_owned_layout_spec.example.json`
- `fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp`
- `tools/generate_source_owned_runtime_config.py`

The generator exposes an explicit `--emit-from-layout-spec` packet-input mode
for `fixtures/generated_source_owned_layout_spec.json`, while
`--emit-current-source-owned-baseline` preserves the source-inspection baseline
mode. The normal generator input now requires `layout_spec`, so spec-less JSON
is rejected.

Quick smoke command:

```bash
python3 tools/generate_source_owned_runtime_config.py \
  --emit-from-layout-spec \
  docs/runtime_config/fixtures/generated_source_owned_layout_spec.json
```

This is the fastest offline check that the inert layout-spec packet still emits
the deterministic source-owned fixture. For the full generator-contract proof,
run `python3 tools/check_glyph_generated_source_owned_generator_contract.py`.

These packets keep the generated tables not wired active, preserve the active
RuntimeConfigView selection boundary, and keep the source-owned active-state
preselection `HARDWARE_PASS` evidence and active-storage `HARDWARE_FAIL`
evidence separate. source-owned active-state `HARDWARE_PASS` evidence and
future hardware gate required before generated source-owned baseline artifact
is selected active remain part of this lane. The declarative
`generated_source_owned_layout_spec.md` mirror stays inert, and the explicit
spec-input mode only helps validate the baseline shape. Future implementation
must be hardware-gated if active source selection behavior changes. Future
hardware gate required before generated source-owned tables are selected
active. nunchuk `NOT_TESTED`.

## Safe Source-Owned Realization Path

The safe current path is source-owned realization: generate or patch
source-owned tables/routing source, review the source diff, build firmware, and
hardware-test any active behavior change before merge.

Current v0 production remains source-owned firmware generation as v0. Neutral
or profile intent may become generated source-owned tables/routing source, then
a firmware build uses the existing active `RuntimeConfigView` path.

Relevant current design packets:

- `source_owned_table_replacement_design.md`
- `source_owned_table_replacement_generator_contract.md`
- `glyph_coordinate_native_runtime_plan.md`
- `coordinate_native_runtime_profile_contract.md`
- `IMPLEMENTATION_BOUNDARY.md`

## Forbidden Active Publication Paths

Do not reintroduce these as current active publication mechanisms:

- `candidate.view` active publication.
- `active_storage.view` active publication.
- Generated active `RuntimeConfigView` wrappers.
- RuntimeConfigView replacement as the customization mechanism.
- RAM-backed active table publication.
- Runtime-loaded profile claims without separate design, source authority,
  build proof, and hardware proof.
- Generated source-owned tables selected active without a future hardware gate.

The full boundary lives in `IMPLEMENTATION_BOUNDARY.md`.

## Coordinate-Native Runtime Profile Contract

The coordinate-native runtime profile contract scaffold in
`docs/runtime_config/coordinate_native_runtime_profile_contract.md` with
`docs/runtime_config/fixtures/coordinate_native_runtime_profile_contract.json`
records the inert future profile contract after the source-owned Y2 layout
HARDWARE_PASS. It accepts prior active-publication HARDWARE_FAIL evidence and
keeps current v0 production on source-owned firmware generation as v0.

The contract bundle also includes:

- `docs/runtime_config/schemas/coordinate_native_runtime_profile.schema.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_9way_modifier_table.example.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json`

This packet is design-only and inactive. It describes the future target as a
coordinate-native runtime profile where active role/modifier state plus
resolved direction key 1..9 maps to exact raw coordinates, including neutral
5, full 9-way asymmetry, and explicit routing/sublayers/priorities.
Browser/protobuf/persistence as future infrastructure is likely solvable, but
the neutral app-owned profile remains canonical and firmware-independent.

The earlier coordinate-native runtime plan remains historical background for
this lane.

Validate the contract scaffold with:

```bash
python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py
```

Validate one profile JSON file with:

```bash
python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py \
  --validate-profile docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json
```

Assert the invalid fixture corpus still fails for the expected reasons with:

```bash
python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py \
  --check-negative-fixtures
```

The invalid fixture corpus covers missing neutral `5`, out-of-range direction
keys, out-of-range raw coordinates, malformed 9-way tables, duplicate priority
ordering, missing capability metadata, and design-only fixtures that
incorrectly claim runtime-loaded or device-write behavior.

## Archived Diagnostics

Older diagnostic packets are retained as evidence and de-emphasized from the
current path:

- `docs/archive/README.md` - concise archive index.
- `docs/calibration/INDEX.md` - calibration evidence index.
- `diagnostic_active_storage_published_hardware_failure_2026-06-28.md` -
  archived dedicated active-storage publication failure.
- `diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md`
  - archived generated baseline active publication failure.
- `diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.md`
  - archived diagnostic showing parsed candidate machinery present while
  source-owned active publication remains passing.

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware parser integration/runtime activation is not implemented.
- WebSerial/device write is not implemented.
- Firmware flashing automation is not implemented.
- Official configurator compatibility is not claimed.
- Nunchuk validation is not claimed.
