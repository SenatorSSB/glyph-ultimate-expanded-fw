# Calibration Index

Status label: CURRENT.

This is a concise evidence map. It is not an exhaustive manifest. Use
`find docs/calibration -maxdepth 3 -type f` or the checker scripts in `tools/`
for full discovery.

## Current Merge-Gating Hardware PASS

- `latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md` - current
  merge-gating latest Y2 layout source-owned port HARDWARE_PASS. It records all
  usual tests passing including Up+A and Down+A, RF5 forced A + Up and LT6
  forced A + Down passing without disconnect, merge-approved status, root cause
  unproven, and Nunchuk remains NOT_TESTED.
- `alt_b_generated_table_alias_candidate_hardware_result_2026-07-09.md` -
  Alternative B generated-table alias candidate HARDWARE_PASS for commit
  `ee5fd35c4ce00e31d9a00905c771699ad17517b9`, preserving the existing active
  `RuntimeConfigView` publication path. It records the user report "Tested
  everything, everything worked.", root cause unproven, and Nunchuk remains
  NOT_TESTED.
- `fixtures/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.json`
  - machine-readable fixture for the current merge-gating hardware PASS.
- `latest_y2_layout_source_owned_port_hardware_plan_2026-06-29.md` - plan-only
  row set that preceded the current result.
- `fixtures/latest_y2_layout_source_owned_port_hardware_plan_2026-06-29.json` -
  machine-readable plan fixture.

## Current Baseline Evidence

- `glyph_gfw3_runtime_remap_hardware_result_2026-06-06.md` - preserved
  user-reported runtime remap hardware pass.
- `glyph_ultimate_preservation_hardware_result.md` - preserved applicable
  non-nunchuk preservation pass.
- `glyph_generated_constants_phase3_integration_hardware_result_2026-06-07.md`
  - preserved generated-like constants integration result.
- `glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md`
  - preserved manual workflow release-candidate result for its stated scope.

## Archived Failed Diagnostics

These packets remain important historical evidence. They are not current work
and must not be reintroduced as active publication paths.

- `generated_canonical_grid_candidate_hardware_result_2026-07-19.md` -
  generated canonical-grid candidate HARDWARE_FAIL for commit
  `e643017c1577c9ca2b94581fa6f18c0dfb1bac9b`. Forced Up + A, forced Down + A,
  Up + B, Y2 routing, and Tilt3 left-stick modification passed; most
  modifier-driven left-stick magnitude changes failed, including Z and Y2
  sublayer left-stick modification. Root cause remains unproven, runtime-loaded
  config and WebSerial/device write remain not implemented, and Nunchuk
  remains NOT_TESTED. The failed candidate and its evidence branch must not be
  merged into `configurator`.
- `glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure_2026-06-08.md`
  - archived runtime-active compiled payload activation failure.
- `docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md`
  - archived dedicated active-storage publication HARDWARE_FAIL.
- `docs/runtime_config/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md`
  - archived generated baseline active publication HARDWARE_FAIL.
- `docs/runtime_config/diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.md`
  - archived diagnostic HARDWARE_PASS where parsed candidate machinery is
  present but active publication remains source-owned.
- `docs/archive/README.md` - archive-oriented index for diagnostic evidence.

## Untested Nunchuk Scope

Nunchuk remains NOT_TESTED across the current known-good state and archived
diagnostics unless a future result packet explicitly records executed nunchuk
rows. No current doc claims nunchuk validation.

## Source And Corpus Notes

- `export_corpus/official_glyph_configurator_2026-06-06/manifest.json` -
  preserved official configurator corpus manifest for user-provided JSON
  fixtures.
- Historical external adapter/source-audit packets are quarantined evidence
  unless independently source-backed.
