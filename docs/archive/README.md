# Archive Index

Status label: CURRENT.

This archive index points to historical diagnostics and evidence that should be
preserved but not treated as current work. Prefer linking here instead of moving
or deleting old packets, so existing checkers and references remain stable.

## Current Evidence To Read First

- `docs/AGENT_CONTEXT.md` - concise agent entrypoint.
- `docs/CURRENT_STATE.md` - short current state.
- `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md` - safe implementation
  boundary.
- `docs/runtime_config/README.md` - runtime-config docs surface.
- `docs/calibration/INDEX.md` - calibration evidence index.

## Historical Diagnostics

- `docs/runtime_config/diagnostic_active_storage_published_hardware_failure_2026-06-28.md`
  - archived dedicated active-storage publication failure.
- `docs/runtime_config/diagnostic_generated_source_owned_baseline_active_hardware_failure_2026-06-29.md`
  - archived generated baseline active publication failure.
- `docs/calibration/glyph_phase7a_runtime_config_compiled_payload_activation_hardware_failure_2026-06-08.md`
  - archived runtime-active compiled payload activation failure.
- `docs/runtime_config/diagnostic_parsed_candidate_present_source_owned_published_hardware_result_2026-06-10.md`
  - archived diagnostic showing parsed candidate machinery present while active
  publication remains source-owned.

## Current Merge-Gating Result

- `docs/calibration/latest_y2_layout_source_owned_port_hardware_result_2026-06-29.md`
  - latest Y2 layout source-owned HARDWARE_PASS and current merge-gating result.

## Archive Rules

- Do not delete historical failure evidence unless all references and checkers
  are updated.
- Do not present archived failed implementation branches as current work.
- Do not claim the root cause is proven.
- Do not claim nunchuk was tested.
