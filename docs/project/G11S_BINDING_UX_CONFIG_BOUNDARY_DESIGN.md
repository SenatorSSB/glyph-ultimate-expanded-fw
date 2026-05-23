# G11s Binding UX/Config Boundary Design (Design-Only)

Status: design-only (no implementation in this batch)

## Purpose

Document the boundary between current source-backed prototype/debug bindings and any future user-facing binding UX/config path, without implementing config/protobuf/default activation, export, or push workflows.

## Current source-backed prototype/debug bindings

In current selected `SenscopePrototype` runtime wiring (`src/modes/SenscopePrototype.cpp`):

- modifier bit 0 = `inputs.rf2`
- modifier bit 1 = `inputs.rf3`
- modifier bit 2 = `inputs.rf4`

These are prototype/debug runtime bindings derived from current source-backed fields and comments in the selected-mode implementation. They are not a product UX contract.

## Boundary model

Keep these layers separate:

1. Firmware source fields:
   - concrete runtime fields such as `InputState` and `OutputState` handling in checked-in source.
2. User-facing Senscope neutral profile concepts:
   - app-owned profile concepts that are not auto-promoted into firmware behavior.
3. Future adapter/export concepts:
   - serialization/export/push integrations, if later approved.
4. Selected-path runtime behavior:
   - what `SenscopePrototype` applies when explicitly selected in runtime.

## Why real binding UX/config is deferred

Real binding UX/config is not implemented yet because:

1. Current baseline is still default-unreachable (`kEnableSenscopePrototypeManualSelection = false`).
2. No `GameModeId`/protobuf/config/default-mode activation path exists for `SenscopePrototype`.
3. Current binding wiring is intentionally prototype/debug scoped.
4. Hardware safety, migration, and compatibility implications have not been approved for product-facing config paths.

## Requirements for any future real binding UX/config implementation

A future implementation must require all of:

1. Explicit source-backed mapping authority for binding fields and ownership.
2. A deliberate decision on config/protobuf/default activation strategy.
3. Explicit user approval for crossing from prototype/debug wiring to user-facing config behavior.
4. Hardware safety review before any flashing or push-to-device handling.
5. Migration/compatibility notes for existing users, configs, and mode-selection behavior.

## Forbidden actions for this design boundary

Do not do any of the following in this batch:

1. Protobuf/config/default activation changes.
2. `GameModeId`/`mode_id`/`activation_binding`/`default_mode_config` changes.
3. Export/push workflows.
4. Hardware flashing.
5. Gameplay semantic labels or threshold logic.

## Stop conditions for later implementation batches

Stop and ask before proceeding if any future work would require:

1. Claiming undocumented controller behavior as authoritative.
2. Choosing binding semantics not backed by inspected source authority.
3. Changing mode reachability/default activation behavior.
4. Introducing protobuf/config/default schema decisions without explicit approval.
5. Adding export/push workflows or flashing flows.
6. Coupling gameplay semantic claims into firmware runtime behavior.

## This batch decision

Current debug/source-backed modifier bindings remain `rf2`/`rf3`/`rf4` for selected runtime only. Real binding UX/config remains deferred.
