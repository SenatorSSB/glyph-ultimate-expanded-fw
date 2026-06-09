# Active Runtime Config State Source-Owned Preselection

status: IMPLEMENTATION_SCaffold

branch: `runtime-active-config-state-source-owned-preselection`

baseline branch: `configurator`

Purpose:

- Add a stable source-owned active runtime config state scaffold in firmware source.
- Route runtime analog lookup through `ActiveRuntimeConfigState.active_view`.
- Keep lookup logic behavior-equivalent to configurator baseline for this branch.

Source constraints in this branch:

- No parser status checks in analog hot path.
- No parser calls added in firmware source.
- No parsed table materialization.
- No storage.
- No WebSerial/device write.
- No flashing automation.
- No HAL/backend/config.pb/write/flashing table or payload anchors added.
- RF5/RF6/LT6 expressions unchanged relative to `configurator`.
- `UpdateDigitalOutputs(...)` unchanged relative to `configurator`.

Implementation shape:

- `RuntimeConfigSource` and `RuntimeConfigActivationStatus` enums added.
- `ActiveRuntimeConfigState` struct added with fields:
  - `active_view`
  - `source`
  - `status`
- `GetActiveRuntimeConfigState()` now selects the active view with
  `ValidateRuntimeConfigView(kSourceOwnedCurrentBaselineRuntimeConfig)`.
- `ResolveActiveRuntimeConfig()` now returns
  `*GetActiveRuntimeConfigState().active_view`.
- `UpdateAnalogOutputs(...)` now binds
  `const RuntimeConfigView &runtime_config = ResolveActiveRuntimeConfig();`.

Constraint checks captured by checker:

- `UpdateAnalogOutputs(...)` does not read `RuntimeConfigSource` or
  `RuntimeConfigActivationStatus`.
- `ResolveActiveRuntimeConfig()` does not inspect parser result state.
- No `kPhase7AD3GlobalParseResult.status` in firmware source outside comments.
- No `ParseUltimateRuntimeConfigPayload` in firmware source.

Build command policy:

- User-facing canonical build command: `pio run -e glyph_mk6`
- Build artifacts for this branch are recorded in
  `docs/runtime_config/active_runtime_config_state_source_owned_preselection_build_report_2026-06-10.md`.

Hardware plan:

- `docs/calibration/glyph_active_runtime_config_state_source_owned_preselection_hardware_plan_2026-06-10.md`
- `docs/calibration/fixtures/glyph_active_runtime_config_state_source_owned_preselection_hardware_plan_2026-06-10.json`

Backend behavior claims in this branch:

- Source-backed and behavior-preserving from this branch baseline check list.
- No claimed runtime-loaded semantics extension.
- No changed output semantics from the accepted contract baseline.
