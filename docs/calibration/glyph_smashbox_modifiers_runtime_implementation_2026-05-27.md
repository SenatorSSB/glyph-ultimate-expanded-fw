# Glyph Smash Box Modifiers Runtime Implementation - 2026-05-27

## Scope

- Native `MODE_ULTIMATE` only.
- Left-stick output tables plus LS->DPad function only if source-backed role bindings are resolved.
- No schema/proto/configurator structural change.
- No flashing or push-to-device automation.

## Checker Semantics

- This branch is a source-trace/planning stop, not a runtime implementation branch.
- Missing Smash Box runtime markers in `src/modes/Ultimate.cpp` are expected in this branch.
- Runtime implementation requires explicit user decisions for:
  - physical/logical role bindings
  - modifier priority/composition
  - LS->DPad left-stick neutral/active policy

## Source-Traced Role Bindings

Resolved from current repository sources and active artifact evidence:

- `Tilt1`: physical `BTN_RF3` -> logical `BTN_LT1` -> runtime `inputs.lt1`.
- `Tilt2`: physical `BTN_RF4` -> logical `BTN_LT2` -> runtime `inputs.lt2`.
- `Tilt3`: physical `BTN_LT3` -> logical `BTN_LT3` -> runtime `inputs.lt3`.

Unresolved for this branch's requested Smash Box profile set:

- `Mode`
- `X1`
- `X2`
- `Y1`
- `Y2`
- `LS->DPad` function button

Status: `MODIFIER_ROLE_BINDING_SOURCE_GAP`.

## Output Table Source

- Required table source document: `docs/calibration/glyph_smash_box_profile_output_tables_2026-05-27.md`.
- This branch records that table source but does not apply runtime table behavior due unresolved bindings.

## Ordinary vs Mode Behavior

Requested behavior was source-traced as a requirement packet for implementation:

- ordinary default and modifier tables
- Mode default center/table and M-prefixed modifier tables

Implementation status: blocked before runtime edit because Mode/X/Y role bindings are unresolved in active Ultimate mapping evidence.

## LS->DPad Behavior

Source findings:

- Current native Ultimate runtime (`src/modes/Ultimate.cpp`) has a nunchuk C D-pad path and direct D-pad remap inputs.
- Current native Ultimate runtime does not define an LS->DPad function button allocation for this profile.
- Reference file `docs/sources/raw/ESAM1.cpp` contains historical D-pad-layer behavior, but uses legacy logical fields (`lightshield`, `midshield`, `mod_x1`, etc.) that are not present in the active `InputState` contract.

Implementation status: blocked.

Stop code:

- `LS_DPAD_LEFT_STICK_NEUTRAL_POLICY_UNRESOLVED`

## Priority / Composition Policy

Source-backed preserved behavior currently available:

- `Tilt3` priority in active Ultimate runtime: `inputs.lt3 || (inputs.lt1 && inputs.lt2)`.

Unresolved for requested new modifier families:

- documented precedence/composition among `X1`, `X2`, `Y1`, `Y2`, and Mode-prefixed states in active Ultimate mapping.

Stop code:

- `MODIFIER_COMPOSITION_POLICY_UNRESOLVED`

## Preservation Boundaries

Preserved by stopping before runtime edits:

- Current Ultimate runtime behavior in `src/modes/Ultimate.cpp` unchanged.
- Current LT3/Tilt3 behavior unchanged.
- Current D-pad repaired mapping artifacts unchanged.
- Current nunchuk behavior unchanged.
- No schema/proto/configurator structure changes.

## Hardware Test Requirements

Hardware testing is still required for any later runtime branch once role bindings and policies are resolved. See:

- `docs/calibration/glyph_smashbox_modifiers_hardware_test_plan_2026-05-27.md`

## Unresolved Caveats

- Runtime implementation intentionally not performed due unresolved binding and policy gates.
- Role allocation authority for Mode/X1/X2/Y1/Y2/LS->DPad must be provided as source-backed profile mapping before runtime changes.
