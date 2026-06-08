# Phase 7A Runtime Config Activation Repair (Minimal, Build-Time Only)

Status: `PHASE7A_REPAIR_MINIMAL_BUILD_ONLY_NO_RUNTIME_BEHAVIOR_CHANGE`.

This packet is for branch
`phase7a-runtime-config-activation-repair-minimal` and records a build-time/source-level
repair strategy that does **not** alter firmware outputs.

## Selected Strategy

- Option A: build-time/source-level validation only.
- Scope: source/doc/tooling checks and compile-only diagnostics.
- Out of scope: runtime behavior, storage, parser execution on hot input paths, or device write/flash flow.

## Why failed branch is abandoned

- The prior compiled-payload activation branch
  (`phase7a-runtime-config-compiled-payload-activation`) is abandoned because it
  produced a user-reported RF5/RF6 disconnect regression and was reverted to
  `configurator` baseline after the report.
- `phase7a-runtime-config-compiled-payload-activation` is treated as a failed
  activation branch and must not merge.
- The failure packet is recorded as source- and docs-level analysis only and is
  not used as a basis for any runtime path change.

## Failed-Risk Patterns Avoided by Construction

- no global non-`constexpr` parse result used in firmware output logic.
- no parser call from hot runtime/output path (`UpdateAnalogOutputs` or equivalent
  per-frame hot loops).
- no storage read/write dependency.
- no WebSerial input/output path.
- no device write/flash command path.
- no flashing automation.

## Exact Firmware Changes in this branch

- None.

There are no file-level firmware edits in this packet. It does not modify
`src/modes/Ultimate.cpp`, parser headers, storage helpers, transport code, or
build-flash scripts.

## Runtime Behavior Classification

- `runtime behavior unchanged`.
- `configurator` baseline source-owned behavior retained.
- no runtime-loaded config activation.
- no output-path selection changes.
- no persistence, transport, or boot/load behavior changes.

## Hardware Gate Status

- Hardware gate: not executed in this branch because this strategy is source-level
  only.
- No map/build artifacts were produced for a build-size comparison in this step.
- Therefore no hardware-result claim is made in this packet.

## Size Report Reference

- Build-size artifact: unavailable in this branch.
- `map_size_artifact_unavailable: true`.
- If a build-only validation pass is performed later, add a companion artifact to
  record compiler/linker size impact before any runtime-active attempt.

## Next Branch Recommendation

- Next step: chat inspection against `configurator` before merge consideration.
- Any continued source-level validation can remain on
  `phase7a-runtime-config-activation-repair-minimal` if build-size and parser
  equivalence validation is the only active work.
- Any later branch that activates runtime behavior must satisfy the existing
  hardware plan template and hardware gate sequence before merge, and must not
  repeat the failed activation branch pattern.
