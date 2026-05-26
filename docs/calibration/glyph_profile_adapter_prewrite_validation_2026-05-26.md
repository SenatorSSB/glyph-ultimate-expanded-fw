# Glyph Profile Adapter Prewrite Validation - 2026-05-26

Scope: design and checker notes for a future read-only preflight gate that could inspect adapter candidate output before any write-capable Glyph profile/config adapter is approved.

## Status

- This is not a write-capable adapter.
- This is not a Glyph JSON canonical-format claim.
- This is not a firmware runtime change.
- This checker never normalizes, rewrites, or reorders profile data.

## Checker

`tools/check_glyph_profile_adapter_prewrite.py` accepts one or more explicit JSON fixture paths and reports structural errors separately from warning-level decision surfaces.

The checker reports:

- root JSON object shape;
- `gameModeConfigs` and `communicationBackendConfigs` list presence;
- omitted `activates` count;
- explicit `BTN_UNSPECIFIED` count;
- many-to-one logical aliases;
- duplicate physical remaps;
- one-based default-index checks where fields are present;
- warning when `gameModeConfigs` exceeds the known mode activation-mask capacity of 10;
- omitted `defaultModeConfig` by backend;
- omitted `socdType` count.

## Error Policy

- Structural errors fail the command.
- Warnings do not fail the command.
- Omitted `activates` and explicit `BTN_UNSPECIFIED` remain distinct reports.
- Many-to-one aliases and duplicate physical remaps are reported as runtime-relevant signals, not automatically rejected.

## Source Basis

- Runtime remap supports many-to-one aliases and first-physical-entry precedence: `src/core/InputMode.cpp`.
- Explicit `BTN_UNSPECIFIED` is a no-op target in button helpers: `HAL/pico/include/util/state_util.hpp`.
- Default indices are one-based in inspected runtime/default-selection paths: `HAL/pico/src/comms/backend_init.cpp`, `src/core/config_utils.cpp`.
- Mode activation-mask capacity is currently fixed at 10: `src/core/mode_selection.cpp`.
- JSON fixture omission behavior remains fixture-observed, not canonical serializer authority: `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md`.

## Decision Surfaces

Warnings are deliberate decision surfaces. They are not automatic adapter failures because source/corpus/user policy may later decide how to handle them.

- Omitted `activates` versus explicit `BTN_UNSPECIFIED` remains unresolved for outbound adapter encoding.
- `defaultModeConfig = 0` is source-confirmed as not rejected by current validation, but outbound adapter use still requires policy approval.
- Mode-count capacity warnings need runtime/source review before any adapter writes reshape mode lists.
