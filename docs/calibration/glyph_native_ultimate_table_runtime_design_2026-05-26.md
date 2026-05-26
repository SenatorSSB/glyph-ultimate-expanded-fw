# Glyph Native Ultimate Table Runtime Design - 2026-05-26

Scope: design-only notes for future native Ultimate arbitrary table support. This document does not implement runtime behavior, does not change firmware, and does not approve flashing or push-to-device workflows.

## Current Hard-Coded Ultimate Branch Model

Native Ultimate behavior is implemented in `src/modes/Ultimate.cpp` as ordered source branches over post-remap logical `InputState` fields.

Source-confirmed current shape:

- `UpdateDigitalOutputs` maps logical inputs directly to output button fields.
- `UpdateAnalogOutputs` first calls `UpdateDirections(...)` with logical left-stick and right-stick direction inputs.
- Later ordered branches conditionally overwrite left-stick, right-stick, trigger analog, and D-pad-layer outputs.
- Branch order is behavior-relevant because later assignments can override earlier assignments.
- C-stick/right-stick and trigger behavior are implemented in the same function and must be preserved by any future patch.

Primary source: `src/modes/Ultimate.cpp`.

## Current Tilt/Tilt2 Formula Implementation

The current native Ultimate Tilt/Tilt2 behavior is source-confirmed in the marked patch block in `src/modes/Ultimate.cpp`:

- Tilt1 uses post-remap logical `inputs.lt1` and only runs when `inputs.lt1 && !inputs.lt2`.
- Tilt2 uses post-remap logical `inputs.lt2` and only runs when `inputs.lt2 && !inputs.lt1`.
- Tilt1 formula: `leftStickX = 128 - directions.x * 59`, `leftStickY = 128 + directions.y * 41`.
- Tilt2 formula: `leftStickX = 128 + directions.x * 40`, `leftStickY = 128 + directions.y * 49`.
- Existing source checker confirms the patch is left-stick-only and does not assign right stick or triggers inside the patch markers.

Primary sources: `src/modes/Ultimate.cpp`, `tools/check_glyph_ultimate_tilt_runtime_source.py`, `tools/check_glyph_ultimate_tilt_tables.py`.

## Why Arbitrary Table Support Is Not Currently Present In Native Ultimate

Native Ultimate currently uses hard-coded branches and formulas. It does not read a profile-configured arbitrary 9-way table for modifier states in `MODE_ULTIMATE`.

Source-backed absence:

- No native Ultimate table data structure is consumed by `Ultimate::UpdateAnalogOutputs`.
- The current Tilt/Tilt2 patch computes values from fixed constants rather than fixture/config data.
- Existing profile/config JSON fixtures define remaps, SOCD pairs, backend defaults, and related profile fields, not a source-confirmed native Ultimate arbitrary table contract.

## Existing `MODE_CUSTOM` Capabilities

`MODE_CUSTOM` supports a separate configurable controller mode implemented in `src/modes/CustomControllerMode.cpp`.

Source-confirmed capabilities include:

- digital button mappings;
- button-combo mappings;
- stick direction mappings;
- analog modifiers over axes;
- analog trigger mappings;
- modifier combination modes such as override and compound;
- nunchuk left-stick overwrite handling.

Why this is not automatically equivalent to native Ultimate arbitrary tables:

- `MODE_CUSTOM` is a different mode, not `MODE_ULTIMATE`.
- It uses generic direction ranges and modifier multipliers rather than native Ultimate's ordered hard-coded branch semantics.
- Moving required behavior into `MODE_CUSTOM` would risk losing native Ultimate-specific digital, trigger, C-stick, D-pad-layer, and branch-order behavior unless separately modeled and tested.
- Using `MODE_CUSTOM` for production would be an architecture decision, not a safe inference from the source.

Primary sources: `src/modes/CustomControllerMode.cpp`, `include/modes/CustomControllerMode.hpp`.

## Existing `SenscopePrototype` Scaffold

A `SenscopePrototype` mode and prototype helper files exist under `include/modes/SenscopePrototype.hpp`, `src/modes/SenscopePrototype.cpp`, and `include/prototypes/senscope/` plus `src/prototypes/senscope/` paths.

Source-confirmed scaffold properties:

- The header comments describe it as an experimental shell with no runtime effect unless explicitly instantiated and activated.
- The prototype runtime path is left-stick-focused and uses example/prototype resolver data.
- Build flags and self-test helpers exist for prototype work, not production native Ultimate realization.
- It is not currently a reviewed production runtime table layer for `MODE_ULTIMATE`.

Why this is not production runtime yet:

- It is intentionally separated from normal mode selection unless future work wires it in.
- It uses prototype example profiles and compile-time helpers, not a reviewed production fixture/config contract.
- It does not prove complete preservation of native Ultimate right-stick, triggers, SOCD, remap, default profile, or hardware behavior.

Primary sources: `include/modes/SenscopePrototype.hpp`, `src/modes/SenscopePrototype.cpp`, `include/prototypes/senscope/*`, `src/prototypes/senscope/*`.

## Design Options

### Option A: Extend Native Ultimate Hard-Coded Tables

Description: add more hard-coded branches/constants to `src/modes/Ultimate.cpp` for required native Ultimate behavior.

Pros:

- Minimal architecture shift from current Tilt/Tilt2 patch style.
- Preserves native Ultimate mode identity.
- Easier to reason about local diff scope if requirements remain small.

Cons:

- Does not scale well to arbitrary user/domain table data.
- Branch order can become fragile.
- Every new modifier state requires source edits and hardware preservation tests.

### Option B: Use `MODE_CUSTOM`

Description: express future behavior through the existing generic custom controller mode.

Pros:

- Reuses source-confirmed generic mapping/modifier machinery.
- Avoids adding table machinery to native Ultimate.

Cons:

- Not equivalent to native Ultimate semantics.
- Risks C-stick/right-stick, trigger, D-pad-layer, and default Ultimate behavior preservation.
- Would require a separate reviewed adapter and hardware test matrix.

### Option C: Use Existing `SenscopePrototype` Scaffold

Description: mature the existing prototype resolver/table scaffold into a production path.

Pros:

- Already contains table/resolver concepts and self-test scaffolding.
- Keeps experimental table logic outside the current Ultimate file while design evolves.

Cons:

- Prototype is explicitly not production runtime.
- Current scaffold does not itself prove native Ultimate preservation.
- Requires reviewed fixture contracts, source checkers, mode-selection decisions, and hardware evidence before production use.

### Option D: Introduce A New Reviewed Native Table Layer

Description: create a small reviewed table layer consumed from native Ultimate, with explicit fixture contracts and source checkers before implementation.

Pros:

- Preserves `MODE_ULTIMATE` as the runtime mode.
- Keeps arbitrary table data separate from hard-coded formula branches.
- Can be guarded by fixture contract, source-shape checker, and preservation hardware matrix.
- Allows explicit branch exclusivity and chord/conflict policy to be documented before runtime changes.

Cons:

- Requires new runtime code after explicit approval.
- Needs careful integration to avoid changing SOCD, remap, right-stick, trigger, and existing native Ultimate branch behavior.
- Needs hardware testing before any claim of preservation.

## Recommendation

Recommendation: pursue Option D only after fixture/checker prerequisites are reviewed, and do not implement it in this branch.

Rationale:

- Option D best matches the objective of future arbitrary native Ultimate table support while keeping native Ultimate identity and preservation requirements explicit.
- Option A is acceptable for small fixed patches, as with current Tilt/Tilt2, but it is a poor long-term fit for arbitrary table realization.
- Option B is not source-equivalent to native Ultimate.
- Option C is useful as prior art/scaffold, but it is not production runtime yet.

## Risks And Stop Conditions

Stop before implementation if any of the following occur:

- required behavior depends on inferred rather than source-backed controller behavior;
- user/domain requirements are missing for modifier states, both-held/chord policy, or conflict policy;
- fixture contract is not reviewed;
- source checker cannot guard native Ultimate patch scope;
- preservation hardware matrix is incomplete or blocked;
- implementation would change SOCD or remap semantics;
- implementation would add flashing/push automation;
- implementation would require Smash/game-semantic claims.

## Source Files That Would Be Affected If Later Implemented

Potential source touch points for a future approved implementation:

- `src/modes/Ultimate.cpp` for native Ultimate integration.
- `include/modes/Ultimate.hpp` if table declarations or helper interfaces are needed.
- A new focused helper under `include/modes/` and `src/modes/` if Option D is selected.
- Existing prototype files only if a later branch explicitly chooses to promote/refactor scaffold logic.
- Tooling under `tools/` for source-shape and fixture validation.
- Calibration docs/fixtures under `docs/calibration/`.

Not approved here:

- profile schema/proto changes;
- configurator behavior changes;
- flashing or push-to-device automation;
- runtime implementation.

## Fixture/Checker Prerequisites Before Implementation

Before any runtime patch, add and review:

- explicit native Ultimate table fixture contract;
- checker for raw-coordinate ranges and 9-way table completeness;
- source-shape checker for native Ultimate table runtime scope;
- preservation hardware checklist/result workflow;
- adapter prewrite policy gates for omitted/disabled remaps and default indices;
- requirements spec with user/domain inputs clearly marked.

## Explicit Non-Goals

- No macros.
- No timing automation.
- No push automation.
- No game-semantic source changes.
- No SOCD semantic changes.
- No remap semantic changes.
- No firmware runtime patch in this branch.
