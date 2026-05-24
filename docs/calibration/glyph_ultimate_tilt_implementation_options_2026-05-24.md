# Glyph Ultimate Tilt Implementation Options (2026-05-24)

## Scope

This document compares implementation paths for a later custom Ultimate `TILT` / `Tilt2` firmware test branch.

No option is implemented or selected here. The recommendation below is advisory only and requires user approval before any runtime branch.

## Option A: Patch Native `MODE_ULTIMATE` Hard-Coded Analog Behavior

### Source Files Involved

- `src/core/mode_selection.cpp`
  - Selects `ultimate_mode` for `MODE_ULTIMATE`.
- `src/modes/Ultimate.cpp`
  - `Ultimate::UpdateDigitalOutputs` maps physical inputs to output buttons.
  - `Ultimate::UpdateAnalogOutputs` computes left-stick, C-stick, trigger, D-pad-layer, modifier, and nunchuk behavior.
- `include/core/state.hpp`
  - `OutputState` stores analog byte fields.
- `src/core/ControllerMode.cpp`
  - Applies remap and SOCD before mode-specific output updates.

### Expected Config/Profile Impact

Likely none if implemented as compiled native Ultimate behavior only. Existing `MODE_ULTIMATE` profile identity and serialization could remain unchanged.

### Benefits

- Preserves current native Ultimate profile path.
- Avoids schema/profile changes if values and button conditions are hard-coded.
- Closest source location to existing Ultimate tilt-like comments and constants.

### Risks

- Changes live runtime behavior for every profile using this native Ultimate mode unless gated narrowly.
- Requires exact source-approved Tilt1/Tilt2 values and button/chord definitions.
- Risks accidental interaction with existing Ultimate shield, C-stick, D-pad layer, nunchuk, SOCD, or remap behavior.
- Does not create a general schema-backed export/profile mechanism.

### Blocker Status

BLOCKED for implementation until values, activation conditions, overflow/clamp handling, flipper status, and smoke-test plan are approved.

### Must Be Proven Before Implementation

- Exact Tilt1/Tilt2 byte outputs or formulas.
- Whether behavior uses left stick, right stick/C-stick, triggers, or multiple axes.
- That no SOCD/remap semantics change is intended.
- That no overflow/flipper trick is required, or that explicit safe behavior is designed.

### Fit For Custom Ultimate `TILT` / `Tilt2`

Good fit if the user goal is a narrowly scoped firmware experiment in native Ultimate mode with compiled constants and no profile/schema work. It is not a fit if the goal is configurable/exportable user profiles without further schema/design approval.

## Option B: Use Schema-Backed `MODE_CUSTOM` / `CustomControllerMode` Modifiers

### Source Files Involved

- `src/core/mode_selection.cpp`
  - Selects `CustomControllerMode` for `MODE_CUSTOM` when `custom_mode_config` indexes an existing custom mode.
- `src/modes/CustomControllerMode.cpp`
  - Reads `CustomModeConfig.stick_direction_mappings`, `stick_range`, `modifiers`, `analog_trigger_mappings`, and button combo mappings.
- `HAL/pico/include/util/state_util.hpp`
  - `axis_pointer` maps `AnalogAxis` values to `OutputState` fields.
- `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
  - Defines `AnalogModifier`, `AnalogAxis`, `ModifierCombinationMode`, and `CustomModeConfig`.

### Expected Config/Profile Impact

Requires valid `MODE_CUSTOM` game mode configuration and `CustomModeConfig` data. Existing tracked JSON fixtures do not currently provide custom modifier/custom-mode arrays to regression-check.

### Benefits

- Uses existing schema-backed modifier concepts.
- Keeps generic custom-controller behavior separate from native Ultimate source.
- Could be more profile-driven if profile/source authority is later pinned.

### Risks

- Current source backs one-axis scalar modifiers, not arbitrary two-axis raw coordinate tables.
- Current `stick_range` is global and symmetric around neutral.
- No explicit clamp/saturate was found around modifier math into `uint8_t` output fields.
- May not preserve native Ultimate behavior without rebuilding it in custom mode.
- Requires schema/profile source authority and fixture coverage before safe tooling changes.

### Blocker Status

PARTIAL for analysis, BLOCKED for implementation until profile shape, value realization, and overflow/clamp behavior are proven.

### Must Be Proven Before Implementation

- That the intended `TILT` / `Tilt2` outputs can be represented by `stick_range` plus per-axis `multiplier`.
- How custom mode should map all required Ultimate buttons and directions.
- That profile serialization and configurator behavior are safe and reviewed.
- That modifier math has safe numeric behavior or explicit tests.

### Fit For Custom Ultimate `TILT` / `Tilt2`

Potential fit if the user wants schema/profile-driven exploration and accepts the current custom-mode constraints. It is not yet a proven fit for native Ultimate parity or arbitrary exact raw coordinates.

## Option C: Add A New Narrowly Scoped Config/Profile Mechanism Later

### Source Files Involved

Unknown until design is approved. Likely areas would include:

- Proto/config source authority and generated nanopb output.
- Config persistence and parser/model tooling.
- Mode runtime code that consumes the new field.
- Configurator/UI code if user-editable.

### Expected Config/Profile Impact

High. This would likely require schema or serialization changes and reviewed migration/compatibility behavior.

### Benefits

- Could model the exact intended concept instead of forcing it into existing native hard-coding or generic custom-mode scalar modifiers.
- Could avoid relying on overflow/flipper behavior by storing explicit safe values or tables.

### Risks

- Violates the current branch scope.
- Requires explicit approval before neutral/profile schema changes.
- Requires proto/source authority to be pinned.
- Larger blast radius across firmware, configurator, persistence, and docs.

### Blocker Status

DEFERRED. Not suitable for this branch and not approved for immediate runtime work.

### Must Be Proven Before Implementation

- Exact schema/source authority.
- Backward compatibility and persistence behavior.
- UI/configurator impact.
- Tests and fixtures for profile serialization.
- Explicit no-macro/no-timing/no-SOCD-change boundaries.

### Fit For Custom Ultimate `TILT` / `Tilt2`

Could be the best long-term fit if exact configurable behavior is required, but it does not fit the immediate goal unless the user explicitly approves schema/configurator work.

## Option D: Defer Firmware Runtime Changes And Keep JSON/Profile Patch Tooling Only

### Source Files Involved

- `tools/glyph_config_model.py`
- `tools/patch_glyph_ultimate_profile.py`
- `tools/check_glyph_calibration_fixtures.py`
- `tools/check_glyph_patch_script.py`
- Calibration fixtures under `docs/calibration/fixtures/`

### Expected Config/Profile Impact

None beyond read-only inspection and explicit JSON patch prototype outputs. No firmware runtime or device behavior changes.

### Benefits

- Safest path while value, overflow, flipper, and implementation-path blockers remain unresolved.
- Supports continued source inventory and profile patch experiments.
- Keeps Senscope game-semantic authority untouched.

### Risks

- Does not produce testable runtime `TILT` / `Tilt2` behavior.
- May delay hardware learning until blockers are resolved.

### Blocker Status

READY for docs/tooling-only continuation. It is not a runtime implementation path.

### Must Be Proven Before Implementation

Nothing for docs/read-only tooling. Runtime work still needs the blockers listed in the gate matrix.

### Fit For Custom Ultimate `TILT` / `Tilt2`

Good fit for the current design-gate branch. Not sufficient for the later firmware test branch by itself.

## Recommendation Requiring Approval

The likely safest next runtime experiment is Option A, a narrowly scoped native `MODE_ULTIMATE` patch, only if the user approves exact activation conditions and Tilt1/Tilt2 values and the patch avoids overflow/flipper-dependent behavior.

That recommendation is not an implementation decision. Option B remains viable only if a source-backed custom-mode profile can represent the target behavior without rebuilding or weakening native Ultimate behavior. Option C should wait for explicit schema/configurator approval. Option D remains the default while blockers are unresolved.
