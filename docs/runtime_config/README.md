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

Activation-readiness finding for the current batch:
the blocker is that no new safe generated-source-owned activation path exists
beyond the existing source-owned baseline alias and active `RuntimeConfigView`
path. The generated source-owned artifact remains inert, and the forbidden
active publication paths remain forbidden.

The activation-alternatives note classifies A as currently hardware-passed, B
as plausible but requiring source design + build + hardware, C-E as explicitly
forbidden under current evidence, and F as future architecture only.

Current v0 production remains source-owned firmware generation as v0. Neutral
or profile intent may become generated source-owned tables/routing source, then
a firmware build uses the existing active `RuntimeConfigView` path.

Relevant current design packets:

- `runtime_config_activation_alternatives_a_f.md`
- `source_owned_table_replacement_design.md`
- `source_owned_table_replacement_generator_contract.md`
- `glyph_coordinate_native_runtime_plan.md`
- `coordinate_native_runtime_profile_contract.md`
- `IMPLEMENTATION_BOUNDARY.md`

The activation-alternatives note compares A-F activation ideas and hardens the
claim language around source-backed, inferred, and unknown statements before
any implementation discussion advances.

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
keeps current v0 production on source-owned firmware generation as v0. The
contract now includes deterministic selection semantics and annotated future
dry-run examples so a later offline resolver can be specified without inventing
behavior.

The contract bundle also includes:

- `docs/runtime_config/schemas/coordinate_native_runtime_profile.schema.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_9way_modifier_table.example.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_y2_inspired_sketch.example.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_merge.example.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_neutral_5.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_cardinal_2.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_diagonal_7.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_merge_5.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_neutral_5.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_cardinal_2.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_diagonal_7.json`
- `docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_y2_tilt3_8.json`
- `tools/dry_run_coordinate_native_runtime_profile.py`

This packet is design-only and inactive. It describes the future target as a
coordinate-native runtime profile where active role/modifier state plus
resolved direction key 1..9 maps to exact raw coordinates, including neutral
5, full 9-way asymmetry, and explicit routing/sublayers/priorities. The
contract also includes deterministic selection semantics for future offline
dry-runs: explicit `input_state` activation records, `selection_result`
trace/explanation metadata, deterministic tie behavior, missing-table behavior,
and `future_dry_run_examples` annotations that stay design-only.
Browser/protobuf/persistence as future infrastructure is likely solvable, but
the neutral app-owned profile remains canonical and firmware-independent.

The offline dry-run evaluator is tooling only. It produces deterministic JSON
for fixture-backed cases, but the generated result is not loaded by firmware,
runtime-loaded config remains not implemented, and there is no WebSerial/device
write, no persistence/storage, no flashing automation, and no active
RuntimeConfigView publication.

The coordinate-native bridge converter
`tools/convert_coordinate_native_profile_to_source_owned_spec.py` is also
offline tooling only. It validates a supported fixture-backed coordinate-native
profile and emits the canonical inert layout-spec packet consumed by
`--emit-from-layout-spec`. The emitted layout spec is not loaded by firmware,
runtime-loaded config remains not implemented, and there is no WebSerial/device
write, no persistence/storage, no flashing automation, and no active
RuntimeConfigView publication.

The bridge converter is exercised by the repo checker with the new bridge
fixtures
`docs/runtime_config/fixtures/coordinate_native_runtime_profile_source_owned_layout_spec_bridge.example.json`
and
`docs/runtime_config/fixtures/coordinate_native_runtime_profile_source_owned_layout_spec_bridge_invalid_extra_field.json`.
Validate the converter and the existing generator path together with:

```bash
python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py \
  --check-layout-spec-bridge
```

To inspect the bridge output directly:

```bash
python3 tools/convert_coordinate_native_profile_to_source_owned_spec.py \
  --profile docs/runtime_config/fixtures/coordinate_native_runtime_profile_source_owned_layout_spec_bridge.example.json
```

Offline provenance/index fixtures now cover the offline pipeline bundle and
export package layers too:

- `docs/runtime_config/fixtures/coordinate_native_offline_artifact_bundle_manifest.json`
- `docs/runtime_config/fixtures/coordinate_native_offline_export_package.json`

Validate them with:

```bash
python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py \
  --check-offline-pipeline
python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py \
  --check-offline-artifact-bundle-manifest
python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py \
  --check-offline-export-package
```

These fixtures are offline-only provenance records. They do not imply
runtime-loaded config, WebSerial/device write, persistent storage, or
flashing automation.

Offline tooling only: run `python3 tools/dry_run_coordinate_native_runtime_profile.py --profile`
with a fixture-backed case file to exercise the evaluator without any firmware
load path.

The Y2-inspired sketch now has fixture-backed positive dry-run cases for the
neutral, cardinal, diagonal, and Tilt3-aligned coordinate paths. Those cases
stay offline-only and are compared by the repo checker before any status docs
are updated.

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

Run the offline dry-run evaluator directly with:

```bash
python3 tools/dry_run_coordinate_native_runtime_profile.py \
  --profile docs/runtime_config/fixtures/coordinate_native_runtime_profile_minimal.example.json \
  --case docs/runtime_config/fixtures/coordinate_native_runtime_profile_dry_run_neutral_5.json
```

The checker also exercises the offline dry-run path in CI-style validation via
`python3 tools/check_glyph_coordinate_native_runtime_profile_contract.py --check-dry-run-fixtures`.

The invalid fixture corpus covers missing neutral `5`, out-of-range direction
keys, out-of-range raw coordinates, malformed 9-way tables, duplicate priority
ordering, missing capability metadata, missing modifier-table references, and
design-only fixtures that incorrectly claim runtime-loaded or device-write
behavior.

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
