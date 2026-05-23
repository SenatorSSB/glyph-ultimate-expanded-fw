# G8f6 - Custom Controller Audit Rollup

Status: docs-only rollup
Date: 2026-05-24

## Created Docs

- `docs/project/G8F6_CUSTOM_CONTROLLER_MODE_CAPABILITY_AUDIT.md`
- `docs/project/G8F6_CUSTOM_CONFIG_SCHEMA_SURFACE_AUDIT.md`
- `docs/project/G8F6_CUSTOM_ANALOG_MODIFIER_LIMITS.md`
- `docs/project/G8F6_CUSTOM_MODE_STATUS_RECOMMENDATIONS.md`
- `docs/project/G8F6_CUSTOM_CONTROLLER_AUDIT_ROLLUP.md`

## Boundary Statements

This batch is docs-only.

No source/header/config/protobuf files were changed.

No runtime/default reachability was changed.

No Force Up-B behavior was changed.

No digital output behavior was changed.

No right-stick/C-stick behavior was changed.

No export, push, upload, flashing, or hardware workflow was added.

No gameplay semantic claims were added.

No Senscope neutral profile schema was changed.

## What CustomControllerMode Is Source-Backed To Do

CustomControllerMode is source-backed as a selected-mode, config-driven controller mode.

Source-backed behavior includes:
- button combo mappings that can emit one digital output and suppress normal behavior for involved input buttons;
- ordered digital button mappings;
- ordered stick direction button mappings for left-stick and right-stick directions;
- a global `stick_range` used to compute min/center/max axis values around 128;
- per-axis analog modifiers gated by button masks;
- compound and override scalar modifier formulas;
- analog trigger mappings;
- digital-trigger-to-255 analog trigger promotion;
- nunchuk connected override of left-stick outputs;
- device-side protobuf config decode, validation, persistence, and raw config return paths.

## What Remains Unknown

Unknowns include:
- whether external host/configurator UX can author every CustomModeConfig field;
- whether external tooling applies additional validation or transformations;
- exact numeric edge behavior for unusual multipliers, ranges, overflow, or float-to-byte conversion without tests;
- whether incidental override-modifier no-direction outputs should ever be modeled as neutral-intent support, rather than scalar modifier behavior;
- whether limited Senscope neutral profiles can be proven representable through a future scalar/range evaluator;
- whether Senscope should target CustomControllerMode at all;
- whether any approved export/manual-entry/push workflow should exist.

## Unsupported By Current Source

Current source does not support these as audited CustomControllerMode capabilities:
- arbitrary exact raw left-stick `(x,y)` pair assignment;
- first-class non-center neutral raw pair configuration;
- neutral raw-pair support inferred from incidental scalar modifier effects;
- full 9-way raw direction table keyed by direction and modifier combination;
- pair-coordinate analog modifier entries;
- additive analog modifiers;
- generic backend exact raw realization promoted from selected-mode behavior;
- approved Senscope export/push/flashing workflows.

## Near-Term Viability For Exact Senscope Neutral Profiles

CustomControllerMode does not appear viable as a near-term exact realization backend for arbitrary Senscope neutral profiles if the target requires exact raw left-stick coordinate tables.

It may be viable as a limited evaluator target for profiles that can be represented by source-backed range/scalar primitives, but that requires a separately reviewed evaluator model and must report unsupported or unknown cases conservatively.

## Recommended Next Possible Batches

A. G8f7 transport-specific report serialization deeper audit.

B. G8f8 ConfiguratorBackend/persistence deeper audit.

C. G11 custom selected-mode realization implementation only after explicit approval.

D. Senscope-side evaluator package decision.
