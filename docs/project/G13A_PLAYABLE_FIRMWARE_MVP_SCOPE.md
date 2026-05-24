# G13a Playable Firmware MVP Scope

Status: experimental build-path scope definition only.

## Purpose

Define the first playable firmware MVP step for `SenscopePrototype` as an opt-in, explicitly named experimental build path. This branch does not change default runtime reachability for normal `glyph_mk6`.

## Scope In

- Add a compile-time flag to control manual/debug `SenscopePrototype` selection.
- Keep the compile-time flag default-disabled for normal builds.
- Add a dedicated experimental PlatformIO environment for playtest-only local builds.
- Keep all activation opt-in through explicit build selection.

## Scope Out

- No `GameModeId` additions.
- No `mode_id` additions for `SenscopePrototype`.
- No `activation_binding` additions for `SenscopePrototype`.
- No `default_mode_config` additions for `SenscopePrototype`.
- No protobuf schema changes.
- No config/default activation changes.
- No export/push/upload/flashing workflow.
- No hardware flashing in this batch.
- No gameplay semantic labels, thresholds, or SSBU behavior claims.

## Default Safety Contract

- Normal `glyph_mk6` remains the default build target.
- Normal `glyph_mk6` keeps manual `SenscopePrototype` selection disabled by default.
- `SenscopePrototype` manual selection is enabled only when the explicit experimental build flag is defined by the dedicated playtest environment.

## Selected Runtime Behavior Contract (unchanged)

When `SenscopePrototype` is selected through the experimental manual/debug path, behavior remains constrained to:

- left-stick table resolver path only;
- modifier mask sourced from `rf2`/`rf3`/`rf4` bindings;
- digital outputs neutral;
- Force Up-B disabled;
- right-stick/C-stick centered;
- triggers at zero.

These constraints do not add config/protobuf/default activation.

## Build and Reachability Constraints

- This branch introduces an opt-in experimental build path only.
- It must not make normal `glyph_mk6` behavior default-reachable for `SenscopePrototype`.
- No runtime behavior change occurs unless the experimental build flag is explicitly enabled by environment selection.

## Hardware and Delivery Constraints

- This batch does not authorize flashing hardware.
- This batch does not run upload commands.
- This batch does not copy UF2 artifacts to mounted devices.

