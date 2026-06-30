# Runtime Config Docs

Status label: CURRENT.

These packets describe Glyph runtime-config architecture, source authority,
offline fixtures, and future implementation gates. They are design/docs/tools
artifacts unless a specific packet says otherwise.

## Current Phase 6 Boundary

- `phase6_bounded_config_owned_data_architecture.md` - Phase 6 stable firmware
  and bounded config-owned modifier-data architecture; design complete, not
  implemented.
- `phase6_bounded_config_source_authority.md` - Phase 6 source-authority packet
  and inspected source/search record.
- `runtime_config_blockers_1_to_5_decision_packet.md` - proposed decisions for
  storage, parser format, boot/load, fallback/recovery/rollback, and
  WebSerial/device-write authority; all not implemented.
- `phase6_to_phase7_implementation_slice_plan.md` - future implementation
  slices and hardware gates; not an approval to implement.
- `fixtures/phase6_bounded_config_owned_modifier_data_schema_candidate.json` -
  schema/metadata candidate only; not runtime-loaded config.
- `fixtures/phase6_bounded_config_invalid_cases.json` - invalid corpus for
  forbidden config-owned semantics and malformed bounded data claims.

## Existing Runtime-Config Packets

- `phase7a_runtime_config_parser_offline_and_compiled_scaffold.md` - Phase 7A
  offline parser/generator/oracle/checker/storage-simulator foundation with a
  compiled but not runtime-active firmware parser scaffold.
- `phase7a_compiled_activation_failure_analysis_2026-06-08.md` - failure
  analysis only for the Phase 7A compiled/test payload activation hardware
  failure; no fix implemented and failed activation branch must not merge.
- `phase7a_runtime_config_activation_repair_minimal.md` - minimal source-level
  repair packet for Option A. This branch uses build-time/source validation only,
  records no runtime behavior changes, and marks the failed activation branch as
  abandoned.
- `phase7a_build_size_and_map_baseline_2026-06-08.md` - build-size/map/artifact
  baseline recorded from a known-good `configurator` lineage firmware build.
- `fixtures/phase7a_build_size_and_map_baseline_2026-06-08.json` - machine-readable
  artifact table for the build-size baseline.
- `tools/check_glyph_phase7a_build_size_and_map_baseline.py` - read-only checker
  for the Phase 7A build-size and map baseline packet/fixture.
- `phase7a_activation_failure_root_cause_analysis_2026-06-09.md` - root-cause
  analysis packet for the failed Phase 7A compiled-payload activation branch;
  analysis-only, no fix implemented, root cause not proven.
- `fixtures/phase7a_activation_failure_root_cause_analysis_2026-06-09.json` -
  machine-readable evidence fixture for the Phase 7A activation failure
  root-cause analysis.
- `phase7a_activation_failure_diagnostic_build_matrix.md` - diagnostic build
  matrix plan for isolating the activation failure cause; plan-only and not
  implemented.
- `tools/check_glyph_phase7a_activation_failure_root_cause_analysis.py` -
  read-only checker for the root-cause analysis packet, fixture, diagnostic
  matrix, and no-firmware-source-change guardrail.
- `phase7a_safer_activation_repair_plan.md` - plan-only next-branch strategy
  for a safer minimal activation repair attempt; not implemented.
- `hot_path_parse_status_guardrail.md` - accepted Phase 7A D5A/D5A-N1/D5A-N2
  guardrail: analog output hot-path code must not read or branch on parser
  result status; docs/tools only and no firmware behavior change.
- `fixtures/hot_path_parse_status_guardrail.json` - machine-readable guardrail
  fixture for the hot-path parse-status invariant.
- `active_runtime_config_state_contract.md` - accepted active runtime config
  state contract: activation/selection may use parser/materialization/load
  status before publication, while analog output generation may consume only
  `ActiveRuntimeConfigState.active_view`; docs/tools only and no firmware
  behavior change.
- `fixtures/active_runtime_config_state_contract.json` - machine-readable
  fixture for the active runtime config state contract.
- `active_runtime_config_state_source_owned_preselection.md` - source-owned active
  state scaffold implemented in firmware source for stable preselection routing.
- `active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md` -
  build report for this scaffold branch.
- `fixtures/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.json` -
  machine-readable build report metadata for this branch.
- `parser_hotpath_postmortem_and_next_boundary.md` - accepted parser hot-path
  postmortem and next-boundary packet consolidating the diagnostic matrix,
  guardrail, source-owned preselection hardware pass, and next implementation
  boundary; docs/tools only and no firmware behavior change.
- `fixtures/parser_hotpath_postmortem_and_next_boundary.json` - machine-readable
  fixture for the parser hot-path postmortem and next-boundary state.
- `candidate_state_materialization_scaffold.md` - source-level candidate-state
  materialization scaffold; candidate state is not active and output generation
  remains limited to the already-selected `RuntimeConfigView`.
- `fixtures/candidate_state_materialization_scaffold.json` - machine-readable
  fixture for the candidate-state scaffold boundary.
- `candidate_state_materialization_scaffold_build_report_2026-06-10.md` - build
  report for the candidate-state scaffold branch.
- `fixtures/candidate_state_materialization_scaffold_build_report_2026-06-10.json` -
  machine-readable build report metadata for this branch.
- `diagnostic_parsed_candidate_present_source_owned_published.md` - hardware-test
  diagnostic branch packet: parsed candidate machinery is present/materialized,
  but active publication is forced to source-owned baseline.
- `fixtures/diagnostic_parsed_candidate_present_source_owned_published.json` -
  machine-readable diagnostic source-boundary fixture.
- `diagnostic_parsed_candidate_present_source_owned_published_build_report_2026-06-10.md` -
  build report packet for the parsed-candidate-present/source-owned-published
  diagnostic branch.
- `fixtures/diagnostic_parsed_candidate_present_source_owned_published_build_report_2026-06-10.json` -
  machine-readable build report metadata for the diagnostic branch.
- `diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.md` -
  `HARDWARE_PASS` result for the parsed-candidate-present/source-owned-published
  diagnostic branch; parsed candidate presence is safe only when source-owned
  baseline remains published active view.
- `fixtures/diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.json` -
  machine-readable hardware result metadata for the diagnostic branch.
- `active_storage_publication_model.md` - inactive scaffold for the next safe
  publication model: candidate buffer != active buffer; candidate values may be
  validated, but accepted values must be copied into dedicated active storage
  before any future active publication.
- `fixtures/active_storage_publication_model.json` - machine-readable evidence
  matrix and guardrail fixture for the active-storage publication model.
- `active_storage_publication_model_build_report_2026-06-10.md` - build report
  for the inactive active-storage publication model scaffold.
- `fixtures/active_storage_publication_model_build_report_2026-06-10.json` -
  machine-readable build report metadata for the inactive active-storage
  publication model scaffold.
- `diagnostic_active_storage_published.md` - hardware-gated diagnostic branch
  packet for publishing source-owned-equivalent dedicated active storage as the
  active runtime config view while keeping candidate storage non-active.
- `fixtures/diagnostic_active_storage_published.json` - machine-readable source
  boundary and diagnostic-state fixture for the dedicated active-storage
  publication branch.
- `diagnostic_active_storage_published_build_report_2026-06-10.md` - build
  report for the dedicated active-storage publication diagnostic branch.
- `fixtures/diagnostic_active_storage_published_build_report_2026-06-10.json` -
  machine-readable build report metadata for the dedicated active-storage
  publication diagnostic.
- `diagnostic_active_storage_published_hardware_failure_2026-06-28.md` -
  `HARDWARE_FAIL` result for the dedicated active-storage publication
  diagnostic; controller disconnect still happens during forced A + Up and
  forced A + Down, and the implementation branch must not merge.
- `fixtures/diagnostic_active_storage_published_hardware_failure_2026-06-28.json` -
  machine-readable hardware failure result fixture for the dedicated
  active-storage publication diagnostic.
- `generated_source_owned_realization_design.md` - docs/tools-only design for
  the next safe realization strategy after active-storage `HARDWARE_FAIL`:
  future generated C++ immutable source-owned runtime tables may be built into
  firmware, while active `RuntimeConfigView` remains source-owned and no
  parser/runtime-loaded/storage/write/flashing path is introduced.
- `fixtures/generated_source_owned_realization_design.json` - machine-readable
  fixture for the generated source-owned realization design; records
  source-owned active-state preselection `HARDWARE_PASS`, active-storage
  publication `HARDWARE_FAIL`, active behavior unchanged, hardware test not
  required for this docs/checker branch, and nunchuk `NOT_TESTED`.
- `generated_source_owned_schema_scaffold.md` - inert source/schema scaffold
  packet for generated-source-owned immutable table artifacts; follows
  `generated_source_owned_realization_design.md`, records source-owned
  active-state preselection `HARDWARE_PASS` and active-storage `HARDWARE_FAIL`
  evidence, and states that future hardware gate required before generated
  source-owned tables are selected active.
- `fixtures/generated_source_owned_schema_scaffold.json` - machine-readable
  fixture for the generated source-owned schema scaffold; active behavior
  unchanged, generated tables not wired active, runtime-loaded/storage/write/
  flashing paths not implemented, and nunchuk `NOT_TESTED`.
- `generated_source_owned_generator_contract.md` - docs/tools-only contract for
  the first offline generator that turns neutral JSON into generated
  source-owned runtime table C++ text fixtures; generated tables not wired
  active, no active firmware behavior change, and nunchuk `NOT_TESTED`.
- `fixtures/generated_source_owned_generator_contract.json` - machine-readable
  fixture for the generator contract and non-claims.
- `fixtures/generated_source_owned_generator_input.example.json` - neutral JSON
  input fixture with the current 27-table, 9-point, 2-axis shape.
- `fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp` -
  generated source-owned runtime table output fixture emitted under docs, not
  active source paths.
- `tools/generate_source_owned_runtime_config.py` - Python stdlib-only offline
  generator for the docs fixture contract; validates duplicate keys, required
  keys, byte ranges, exact table shape, and deterministic output.
- `generated_source_owned_artifact_install.md` - checker-guarded inert install
  workflow for a generated source-owned runtime table artifact under
  `src/modes/runtime_config/generated_source_owned/`; references
  `generated_source_owned_generator_contract.md`,
  `generated_source_owned_schema_scaffold.md`, active-storage `HARDWARE_FAIL`
  evidence, source-owned active-state preselection `HARDWARE_PASS` evidence,
  and states that future hardware gate required before generated source-owned
  tables are selected active.
- `fixtures/generated_source_owned_artifact_install.json` - machine-readable
  fixture for the inert artifact install workflow; active behavior unchanged,
  generated tables not wired active, runtime-loaded/storage/write/flashing
  paths not implemented, and nunchuk `NOT_TESTED`.
- `generated_source_owned_baseline_artifact.md` - inert generated source-owned
  current-baseline artifact packet for
  `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp`;
  follows `generated_source_owned_artifact_install.md` and
  `generated_source_owned_generator_contract.md`, references active-storage
  `HARDWARE_FAIL` evidence and source-owned active-state `HARDWARE_PASS`
  evidence, proves baseline equivalence by source/artifact table comparison,
  and states that future hardware gate required before generated source-owned
  baseline artifact is selected active.
- `fixtures/generated_source_owned_baseline_artifact.json` - machine-readable
  fixture for the inert generated source-owned baseline artifact; active
  behavior unchanged, generated tables not wired active, runtime-loaded/
  storage/write/flashing paths not implemented, and nunchuk `NOT_TESTED`.
- `diagnostic_generated_source_owned_baseline_active.md` - hardware-gated
  diagnostic branch packet for selecting the generated source-owned
  baseline-equivalent `RuntimeConfigView` as active without RAM-backed active
  table publication.
- `fixtures/diagnostic_generated_source_owned_baseline_active.json` -
  machine-readable diagnostic fixture; `active_behavior_changed: true`,
  `generated_source_owned_baseline_active: true`,
  `hardware_test_required_before_merge: true`, candidate view not active,
  runtime-loaded/storage/write/flashing paths not implemented, and Nunchuk
  remains NOT_TESTED.
- `diagnostic_generated_source_owned_baseline_active_build_report_2026-06-29.md` -
  local build report for the generated source-owned baseline active diagnostic;
  canonical command `pio run -e glyph_mk6`, fallback wrapper used locally, and
  artifact hashes recorded only as local observations.
- `fixtures/diagnostic_generated_source_owned_baseline_active_build_report_2026-06-29.json` -
  machine-readable build report metadata for the diagnostic branch.
- `diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md` -
  `HARDWARE_FAIL` result for the generated source-owned baseline active
  diagnostic; forced A + Up and forced A + Down still disconnect, initial two
  Up+A presses did not immediately disconnect before later reproduction,
  reconnect sometimes leaves left stick fully down or fully up across failed
  diagnostics, low-level mechanism remains unproven, source-owned active-state
  preselection remains the last known passing active-runtime boundary, and the
  implementation branch must not merge.
- `fixtures/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.json` -
  machine-readable hardware failure result fixture for the generated
  source-owned baseline active diagnostic.
- `source_owned_table_replacement_design.md` - docs/checker-only next
  realization strategy after generated source-owned baseline active
  `HARDWARE_FAIL`: a future generator may replace compile-time contents of the
  existing source-owned `StickPoint` tables used by the already-active
  `kSourceOwnedCurrentBaselineRuntimeConfig`, while source-owned table
  replacement does not change RuntimeConfigView selection. It records
  dedicated active storage `HARDWARE_FAIL`, source-owned active-state
  preselection `HARDWARE_PASS`, active behavior unchanged, no runtime-loaded
  config/storage/write/flashing paths implemented, and Nunchuk `NOT_TESTED`.
  Future implementation changing table contents must be hardware-gated before
  merge if active behavior changes.
- `fixtures/source_owned_table_replacement_design.json` - machine-readable
  fixture for the source-owned table replacement design; active view selection
  unchanged, `RuntimeConfigView` replacement not allowed, table-content
  replacement design-only, candidate/generated-baseline/RAM active publication
  not allowed, root cause not proven, and Nunchuk `NOT_TESTED`.
- `source_owned_table_replacement_generator_contract.md` - docs/tools-only
  generator contract following `source_owned_table_replacement_design.md`. It
  defines a stdlib-only replacement generator for
  `src/modes/UltimateIdentityRuntimeTables.hpp` that emits patched text under
  docs fixtures or stdout, preserves existing table symbols/order/shape and
  non-table source text, makes no RuntimeConfigView selection change, and does
  not modify active source files on this branch.
- `fixtures/source_owned_table_replacement_generator_contract.json` -
  machine-readable non-claim fixture for the generator contract; active
  behavior unchanged, hardware test not required before merge,
  source-owned active-state preselection `HARDWARE_PASS`, dedicated active
  storage `HARDWARE_FAIL`, generated source-owned baseline active
  `HARDWARE_FAIL`, root cause not proven, and Nunchuk `NOT_TESTED`.
- `fixtures/source_owned_table_replacement_input.example.json` - neutral
  replacement input fixture with `replacement_kind:
  source_owned_table_content_replacement`, target file
  `src/modes/UltimateIdentityRuntimeTables.hpp`, and the current 27-table,
  9-point, 2-axis shape.
- `fixtures/generated_outputs/UltimateIdentityRuntimeTables.replacement.example.hpp` -
  deterministic generated output fixture for replacing only numeric `x`/`y`
  table contents in existing source-owned `StickPoint` table initializers; it
  is an output fixture only, not active source.
- `tools/generate_source_owned_table_replacement.py` - Python stdlib-only
  offline generator for the source-owned table replacement contract; rejects
  duplicate JSON keys, validates exact table shape and byte ranges, verifies
  every table symbol exists exactly once, and refuses to write active source
  paths.
- `runtime_config_semantics_evaluator_bridge.md`
- `runtime_loaded_config_schema_design.md`
- `firmware_interpreter_architecture_spec.md`
- `runtime_config_storage_fallback_source_authority.md`
- `runtime_config_storage_fallback_architecture.md`
- `runtime_config_binary_representation_design.md`
- `runtime_config_firmware_binary_parser_source_authority.md`
- `runtime_config_firmware_binary_parser_integration_plan.md`
- `runtime_config_manual_load_path_plan.md`
- `runtime_config_webserial_device_write_source_authority.md`
- `runtime_config_device_write_safety_plan.md`
- `runtime_config_flashing_automation_safety_boundary.md`

## Non-Claims

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- Firmware parser integration/runtime activation is not implemented; Phase 7A
  adds only a compiled inert parser scaffold.
- Phase 7A compiled/test payload activation failed hardware testing on its
  activation branch and is recorded as failure analysis only here.
- Phase 7A activation root cause is not proven; the failed activation branch
  must remain abandoned and future runtime activation requires hardware-gated
  diagnostic builds.
- The accepted hot-path parse-status guardrail forbids reading parser result
  state from `UpdateAnalogOutputs` or any analog hot-path resolver. Future
  activation must compute stable active runtime config state outside the analog
  output hot path.
- Source-owned active runtime config preselection scaffolding is implemented in
  `runtime-active-config-state-source-owned-preselection`; hot-path analog
  generation consumes `ResolveActiveRuntimeConfig()` output via
  `ActiveRuntimeConfigState.active_view`.
- The accepted active runtime config state contract requires future activation
  to publish a stable selected `RuntimeConfigView` before analog output
  generation. Analog output generation may consume only
  `ActiveRuntimeConfigState.active_view` and must not branch on activation
  source or activation status.
- The accepted parser hot-path postmortem and next boundary records
  source-owned active-state preselection as the repair architecture baseline.
  Parser/materialization/load may happen only before active-state publication;
  output generation may consume only the already-selected `RuntimeConfigView`.
- Candidate state materialization scaffolding is compile-present but not active.
  Candidate state is not consumed by `ResolveActiveRuntimeConfig()` or
  `UpdateAnalogOutputs(...)`; output generation remains limited to the stable
  selected `RuntimeConfigView`.
- The parsed-candidate-present/source-owned-published diagnostic branch keeps
  parsed candidate machinery present and materialized, but publishes only
  `kSourceOwnedCurrentBaselineRuntimeConfig` as the active view. It records no
  hardware result; Nunchuk remains NOT_TESTED.
- The active-storage publication model records the current safe rule:
  candidate buffer != active buffer. Dedicated active storage is scaffolded but
  not active; candidate.view is never active; active behavior remains
  source-owned baseline and no hardware test is required before merge for that
  scaffold-only branch.
- The diagnostic active-storage-published branch changes active behavior by
  publishing source-owned-equivalent dedicated active storage as the active view
  only after validation and equivalence succeed. It keeps candidate.view
  non-active and has a source-owned fallback. Its recorded hardware result is
  HARDWARE_FAIL: controller disconnect still happens during forced A + Up and
  forced A + Down. RAM-backed active runtime table storage appears unsafe as an
  active publication target under this diagnostic, the low-level mechanism
  remains unproven, and the implementation branch must not merge. Do not merge
  the failed implementation branch. Dedicated active storage published active is
  unsafe under this diagnostic. RAM-backed active table storage is unsafe as an
  active publication target under this test. Future strategy should pivot away
  from RAM-backed active table pointer publication.
- Generated source-owned realization design is docs/tools only. It pivots the
  next strategy toward generated C++ immutable source-owned runtime tables built
  into firmware, keeps active `RuntimeConfigView` source-owned, and introduces
  no runtime-loaded config, persistent storage, WebSerial/device write,
  backend/config.pb write path, flashing automation, candidate.view active
  publication, RAM-backed active table publication, or nunchuk validation
  claim. Future implementation must be hardware-gated if active source
  selection behavior changes.
- Generated source-owned schema scaffold is inert source/docs/tools only. It
  follows `generated_source_owned_realization_design.md`, adds isolated
  generated-source-owned schema metadata headers, records source-owned
  active-state preselection `HARDWARE_PASS` and active-storage `HARDWARE_FAIL`
  evidence, and keeps generated tables unwired active. A future hardware gate
  required before generated source-owned tables are selected active.
- Generated source-owned generator contract is docs/tools only. It defines a
  neutral JSON input contract and an offline C++ text output contract for
  generated source-owned immutable runtime table artifacts. Generated tables
  remain not wired active, generated fixture output lives under docs fixture
  paths by default, runtime-loaded config/storage/write/flashing paths are not
  implemented, and nunchuk `NOT_TESTED` remains unchanged.
- Generated source-owned artifact install is inert source/docs/tools only. It
  installs a deterministic generated source-owned runtime table artifact under
  `src/modes/runtime_config/generated_source_owned/`, but the artifact is not
  included by `src/modes/Ultimate.cpp`, is not wired into runtime selection,
  and active behavior remains unchanged. Future hardware gate required before
  generated source-owned tables are selected active.
- The diagnostic generated source-owned baseline active branch
  `runtime-config-diagnostic-generated-source-owned-baseline-active` changes
  active behavior by selecting the generated source-owned baseline-equivalent
  `RuntimeConfigView` as active. It uses source-owned immutable generated table
  data, does not use RAM-backed active table publication, does not publish
  `candidate.view`, does not implement a parser payload path, runtime-loaded
  config, storage, WebSerial/device write, backend/config.pb write path, or
  flashing automation, and has `hardware_test_required_before_merge: true`.
  Nunchuk remains NOT_TESTED.
- The generated source-owned baseline active diagnostic has a recorded
  `HARDWARE_FAIL` result on
  `runtime-config-diagnostic-generated-source-owned-baseline-active-hardware-failure`.
  Generated/source-owned/baseline-equivalent table data was not sufficient for
  safe active publication. Failure is no longer isolated to RAM-backed active
  table storage; changing the active `RuntimeConfigView`/table publication path
  remains unsafe under this diagnostic. The implementation branch must not
  merge, root cause is not proven, and Nunchuk remains NOT_TESTED.
- Source-owned table replacement design is docs/checker only. Generated
  source-owned baseline active HARDWARE_FAIL, dedicated active storage
  HARDWARE_FAIL, and source-owned active-state preselection HARDWARE_PASS are
  the accepted evidence. The future strategy is to replace only the
  compile-time contents of the existing source-owned `StickPoint` tables used
  by the already-active `kSourceOwnedCurrentBaselineRuntimeConfig`; source-owned
  table replacement does not change RuntimeConfigView selection. Future
  implementation changing table contents must be hardware-gated before merge if
  active behavior changes.
- Source-owned table replacement generator contract is docs/tools only. It
  follows `source_owned_table_replacement_design.md`, adds a stdlib-only
  generator, contract fixture, replacement input fixture, and deterministic
  generated output fixture under docs. It preserves the existing source-owned
  table symbols/order/shape and non-table source text, makes no
  RuntimeConfigView selection change, does not modify active source files, and
  requires no hardware test before merge for this contract-only branch.
- WebSerial/device write is not implemented.
- Firmware flashing automation is not implemented.
- Official configurator compatibility is not claimed.
- Nunchuk validation is not claimed.
