# G8f7 - Transport Audit Rollup

Status: docs-only rollup
Date: 2026-05-24

## Created Docs

- `docs/project/G8F7_TRANSPORT_REPORT_SERIALIZATION_AUDIT.md`
- `docs/project/G8F7_GAMECUBE_REPORT_PATH_CAPABILITY_AUDIT.md`
- `docs/project/G8F7_NON_GC_TRANSPORT_TRANSFORM_BOUNDARIES.md`
- `docs/project/G8F7_TRANSPORT_STATUS_RECOMMENDATIONS.md`
- `docs/project/G8F7_TRANSPORT_AUDIT_ROLLUP.md`

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

## What Is Source-Backed For GC Transport

The GameCube backend report path is source-backed to carry selected-mode byte outputs:

- selected-mode `OutputState.leftStickX/Y` bytes are copied to GC `stick_x/stick_y`;
- selected-mode `OutputState.rightStickX/Y` bytes are copied to GC `cstick_x/cstick_y`;
- selected-mode `OutputState.triggerLAnalog/RAnalog` bytes are copied to GC analog trigger fields;
- selected-mode digital outputs are copied or mapped into GC digital report fields;
- no clamp, scale, or inversion is visible in `HAL/pico/src/comms/GamecubeBackend.cpp` before those analog byte assignments.

This supports a narrow `SOURCE_BACKED`, `TRANSPORT_SPECIFIC` claim for carrying bytes selected by the active mode.

It does not prove that the selected mode can produce every requested coordinate.

## What Is Transformed Or Non-Equivalent For Non-GC Transports

Nintendo Switch:
- scales stick bytes around 128 and inverts y axes.

DInput:
- inverts y axes, offsets trigger values by one, and the local `TUGamepad` setters expand byte values to 16-bit HID report fields.

XInput:
- scales stick bytes into XInput report fields and can promote digital trigger outputs to full analog trigger values.

N64:
- converts left-stick bytes to centered offset values and maps right-stick direction booleans to C-button report fields.

NES/SNES:
- reduce left-stick thresholds into digital D-pad report fields.

These transports are not equivalent to GC raw-coordinate output and should require separate output IDs, mapping datasets, and evaluator rules if modeled later.

## What Remains Unknown

Unknowns include:

- end-to-end exact coordinate realization for arbitrary Senscope neutral targets;
- selected-mode target-production rules for any future exact realization target;
- external GC report struct/library behavior beyond local backend assignments;
- electrical/protocol timing and hardware-observed behavior;
- whether external host/configurator tooling should participate in any approved future workflow;
- whether a future evaluator should model non-GC transformed transport spaces.

## Why This Supports GC-Adapter-First Scope

GC-adapter mode is the MVP-critical target because the inspected GameCube backend path is the strongest transport evidence for carrying selected-mode byte outputs without a visible transform in the local backend file.

Non-GC transports show transport-specific transforms or reductions. Treating them as equivalent to GC raw-coordinate output would erase source-visible differences and weaken evaluator diagnostics.

## Recommended Next Possible Batches

A. G8f8 ConfiguratorBackend/persistence deeper audit.

B. G8f9 external GC report struct/library audit if source-accessible.

C. G11 custom selected-mode realization implementation only after explicit approval.

D. Senscope-side evaluator package decision.
