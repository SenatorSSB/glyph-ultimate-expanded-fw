# Calibration Index

Status label: CURRENT.

This is a concise evidence map. It is not an exhaustive manifest. Use
`find docs/calibration -maxdepth 3 -type f` or the checker scripts in `tools/`
for full discovery.

## Current Merge-Gating Hardware PASS

- `gp_config_005_hardware_result_2026-09-17.md` - exact-snapshot
  `HARDWARE_PASS` for candidate
  `437f87e8086a50f0dfbd834176b80d245c1ed307` and UF2 SHA-256
  `650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44`
  under the bounded `GP_CONFIG_005_HW_V1` live-Config rejection protocol.
  The separate earlier persistence event remains inconclusive; no disk
  rollback, atomic persistence, power-loss, recovery, live-RAM readback,
  Nunchuk, unrelated-path, or root-cause claim is made.
- `fixtures/gp_config_005_hardware_evidence_2026-09-17.json` - Revision-2
  structured evidence for that exact candidate/artifact pair and fresh run.
- `x1_offset41_hardware_result_2026-09-02.md` - exact-snapshot manual
  HARDWARE_PASS for the X1-only offset-41 candidate at
  `74ae24364b84520d4e0e39240beb9867653cc7b9` and UF2 SHA-256
  `5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254`.
  The project owner confirmed all expected outputs and no disconnects, then
  confirmed the restored prior firmware worked. Nunchuk remains NOT_TESTED.
- `x1_offset41_hardware_test_protocol_2026-09-02.md` - exact sole/non-mode X1
  neutral, cardinal, diagonal, and connection-stability acceptance protocol.
- `fixtures/x1_offset41_hardware_evidence_2026-09-02.json` - Revision-2
  structured evidence for the same exact candidate/artifact pair.
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

- `gp_config_005_prior_inconclusive_persistence_event_2026-09-17.md` -
  separately preserved `INCONCLUSIVE_PERSISTENCE_EVENT` from the earlier
  GP-CONFIG-005 attempt. Its exact compiled-default post-drift identity does
  not prove a persistence-failure window and is not reused as PASS evidence.
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
