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

The full boundary lives in `IMPLEMENTATION_BOUNDARY.md`.

## Future Coordinate-Native Runtime Profile Plan

The Glyph coordinate-native runtime plan in
`docs/runtime_config/glyph_coordinate_native_runtime_plan.md` with
`docs/runtime_config/fixtures/glyph_coordinate_native_runtime_plan.json`
records the forward architecture after the source-owned Y2 layout HARDWARE_PASS.
It accepts prior active-publication HARDWARE_FAIL evidence and keeps current v0
production on source-owned firmware generation as v0.

The future target is a coordinate-native runtime profile where active
role/modifier state plus resolved direction key 1..9 maps to exact raw
coordinates, including neutral 5, full 9-way asymmetry, and explicit
routing/sublayers/priorities. Browser/protobuf/persistence as future
infrastructure is likely solvable, but the neutral app-owned profile remains
canonical and firmware-independent.

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
