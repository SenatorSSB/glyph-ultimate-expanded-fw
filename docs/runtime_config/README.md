# Runtime Config Docs

Status label: CURRENT.

This directory contains runtime-config design, evidence, fixtures, and checker
contracts. Read the current boundary first; use archived diagnostics only when
you need the supporting evidence.

The current declared-only build-input provenance boundary is documented in
`build_input_provenance_inventory.md`, with its deterministic fixture and
load-bearing static checker at
`fixtures/build_input_provenance_inventory.json` and
`tools/check_glyph_build_input_provenance_inventory.py`. It records declared
selectors and unresolved claims without fetching dependencies, executing build
tooling or the postprocessor, or claiming reproducibility.

The observed-only artifact-postprocessor provenance packet is documented in
`artifact_postprocessor_provenance.md`, with its synthetic fixture and
verifier at
`fixtures/artifact_postprocessor_provenance.json` and
`tools/check_glyph_artifact_postprocessor_provenance.py`. Its bounded
`build.yml` route verifies full checked-out Git identity and tracked
postprocessor identity, then emits and verifies a final-artifact sidecar before
upload. Postprocessor purpose and byte transformation remain `UNKNOWN`; the
sidecar does not claim immutable storage, artifact acceptance, reproducibility,
or hardware validation.

## Current Known-Good State

Overlay/preserve candidate-generation semantics are now checker-enforced in
`generated_source_owned_overlay_preserve_contract.md`. Full replacement,
overlay/preserve, and reject-partial are distinct modes; overlay/preserve
copies every unowned table from the current source-owned baseline and emits a
28-row manifest. Example provenance is refused by production preparation and
installation. A semantic no-op is not hardware-candidate material.

The complete offline generator-mode pipeline is now implemented in
`tools/source_owned_generator_modes.py` with the thin CLI
`tools/generate_source_owned_generator_modes.py`. It provides mandatory mode
selection, explicit provenance and ownership, source-extracted baseline
identity, deterministic semantic digests, complete artifacts/manifests,
classification, preparation, atomic inert installation, stable exit codes, and
fixture-backed positive/negative coverage via
`tools/check_glyph_source_owned_generator_modes.py`. The current example input
remains `SOURCE_AUTHORITY_BLOCKER`; no production profile or hardware
candidate is authorized by this cycle.
The 2026-07-19 proof report classifies the current example/layout-spec input as
`SOURCE_AUTHORITY_BLOCKER` because it declares no ownership.

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
- Alternative B generated-table aliasing is hardware-passed for candidate
  commit `ee5fd35c4ce00e31d9a00905c771699ad17517b9` when preserving the
  existing active `RuntimeConfigView` publication path through
  `&kSourceOwnedCurrentBaselineRuntimeConfig`,
  `GetActiveRuntimeConfigState()`, and `ResolveActiveRuntimeConfig()`.
- Hardware result:
  `docs/calibration/alt_b_generated_table_alias_candidate_hardware_result_2026-07-09.md`.
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
- `source_owned_candidate_generation_diff_diagnosis.md` and
  `fixtures/source_owned_candidate_generation_diff_diagnosis.json`
- `tools/install_generated_source_owned_runtime_config.py`
- `tools/check_glyph_source_owned_candidate_generation_diff.py`
- `source_owned_table_symbol_map.md` and
  `tools/check_glyph_source_owned_table_symbol_map.py`
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

The companion installer
`tools/install_generated_source_owned_runtime_config.py` can either dry-run or
write the inert example artifact. It refuses writes to the active baseline
header; its preferred path is a dry-run preview from `--from-layout-spec`.
It also accepts `--from-generated-output` for already-generated C++ text and
`--dry-run` for preview-only operation.

The candidate-prep wrapper
`tools/prepare_source_owned_candidate_branch.py` sits one layer above the
installer. It validates a coordinate-native profile or inert layout-spec
fixture, converts when needed, generates the source-owned artifact into a
temporary preview location, and emits a dry-run candidate plan for
`runtime-config-install-workflow-candidate-generation`. The wrapper stays
offline by default and keeps the approved inert Alternative B source path
explicit for future hardware-test candidate materialization, but active table
source writes are fail-closed until a separately authorized candidate workflow.

Quick smoke command:

```bash
python3 tools/generate_source_owned_runtime_config.py \
  --emit-from-layout-spec \
  docs/runtime_config/fixtures/generated_source_owned_layout_spec.json
```

This is the fastest offline check that the inert layout-spec packet still emits
the deterministic source-owned fixture. For the full generator-contract proof,
run `python3 tools/check_glyph_generated_source_owned_generator_contract.py`.

For a dry-run install preview of the inert source-owned alias path, run:

```bash
python3 tools/install_generated_source_owned_runtime_config.py \
  --from-layout-spec docs/runtime_config/fixtures/generated_source_owned_layout_spec.json \
  --dry-run
```

The generated baseline header is active compile-time table-content source
through `UltimateIdentityRuntimeTables.hpp`; the example packets remain inert
and are not wired active. These packets preserve the active
RuntimeConfigView selection boundary, and keep the source-owned active-state
preselection `HARDWARE_PASS` evidence and active-storage `HARDWARE_FAIL`
evidence separate. source-owned active-state `HARDWARE_PASS` evidence and
the active baseline header is already compile-time source, not a future
selection. The declarative
`generated_source_owned_layout_spec.md` mirror stays inert, and the explicit
spec-input mode only helps validate the baseline shape. Future implementation
must be hardware-gated if active source selection behavior changes. Future
active table bytes remain hardware-gated for any behavior change; future
hardware gate required before generated source-owned tables are selected active
for a behavior-changing candidate. The source-owned table symbol-map note and checker document the
current Alternative B alias/replacement boundary without changing the active
path. nunchuk `NOT_TESTED`.
	The future hardware gate required before generated source-owned tables are
	selected active for a behavior-changing candidate applies to any replacement
	with changed table bytes; the current included baseline remains the approved
	source-owned path.
The example packets retain the bounded non-claim that generated tables not
wired active are not selected through the inert fixture lane.

The candidate-generation diff diagnosis currently classifies the inert
layout-spec candidate as `TABLE_CONTENT_DIFFERENT` against the current
source-owned baseline. Use
`python3 tools/check_glyph_source_owned_candidate_generation_diff.py` to
reproduce the semantic comparison. The generated canonical-grid candidate at
`e643017c1577c9ca2b94581fa6f18c0dfb1bac9b` is now recorded as HARDWARE_FAIL
in
`docs/calibration/generated_canonical_grid_candidate_hardware_result_2026-07-19.md`.
The failure concerns generated table content: 26 non-Y2/Tilt3 tables were
canonical `0/128/255` grids, while `kY2Table` and `kTilt3Table` remained
source-aligned. It does not invalidate the already hardware-passed Alternative
B alias mechanism when source-aligned table content preserves the existing
active `RuntimeConfigView` publication path.

Future candidate generation must use explicit full-replacement,
overlay/preserve, or reject semantics. Partial/example input must not silently
fill unspecified production tables with canonical defaults, and generated
candidates must include a table-by-table change manifest before hardware.

See `generated_source_owned_generator_modes.md` for the mode, provenance,
versioning, digest, manifest, CLI, preparation/install, and migration contract.

The separate `source_authority_intake_workflow.md` records a human-approved
source-authority intake and deterministically emits generator-input v2 only
after explicit ownership, replacement, baseline, and approval gates pass. It
is offline-only and cannot infer authority. The canonical
`intakes/x1_baseline_equivalent_overlay_v1.intake.json` owns only `kX1Table`
with its exact matching baseline bytes. That authorized no-op exercises the
authority flow without creating an active-source delta or hardware candidate;
future X1 values or additional ownership remain separately gated.

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
as hardware-passed only for the source-owned generated-table alias candidate
that preserves the active publication path, C-E as explicitly forbidden under
current evidence, and F as future architecture only.

Current v0 production remains source-owned firmware generation as v0. Neutral
or profile intent may become generated source-owned tables/routing source, then
a firmware build uses the existing active `RuntimeConfigView` path.

Relevant current design packets:

- `runtime_config_activation_alternatives_a_f.md`
- `source_owned_table_replacement_design.md`
- `source_owned_table_replacement_generator_contract.md` (SUPERSEDED historical
  27-table literal-body contract; current authority is generator modes and
  source-authority intake)
- `glyph_coordinate_native_runtime_plan.md`
- `coordinate_native_runtime_profile_contract.md`
- `IMPLEMENTATION_BOUNDARY.md`

The activation-alternatives note compares A-F activation ideas and hardens the
claim language around source-backed, inferred, and unknown statements before
any implementation discussion advances.

The generated table alias path is hardware-passed when preserving the existing
active `RuntimeConfigView` publication path. That result does not validate
runtime-loaded profiles, device-write flows, or C/D/E forbidden
active-publication paths.

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
# Offline validation

Run `python3 tools/run_glyph_runtime_config_validation.py` for the current,
read-only runtime-config validation lane. `python3 tools/check_glyph_runtime_config_source_sync.py`
checks the canonical 28-table source baseline (digest
`9ea314bd17680d8353198ac174e59faf84c419fcd95a4ef3db24b3bd7e0f2970`).
`python3 tools/check_glyph_checker_census.py` verifies the deterministic,
repository-wide static checker census. The census count is derived from the
discovered `tools/check_glyph_*.py` set; it does not behaviorally audit every
checker. The aggregate manifest reconciles every checker with a strong static
runtime-config signal to either the curated scope or an explicit exclusion.
Historical and hardware-evidence checkers are explicitly excluded from current
aggregate PASS; this does not create production authority or a candidate.
