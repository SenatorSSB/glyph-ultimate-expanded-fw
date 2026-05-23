# G11v Runtime Expansion Readiness Gate

Status: design/readiness documentation only (no runtime implementation in this batch)

## Purpose

Define required readiness gates that must be passed before any future `SenscopePrototype` runtime expansion work for Force Up-B, digital outputs, or binding UX/config path decisions.

This document is a gate and planning artifact, not an implementation change.

## Global minimum gate criteria

Before any runtime expansion implementation, all of the following must be satisfied:

1. Source authority identified:
   - implementation behavior must be tied to inspected source/docs/tests (or explicit user-provided domain authority).
2. Selected-path-only implementation plan:
   - behavior scope must be constrained to selected `SenscopePrototype` runtime path.
3. Fail-closed behavior specified:
   - unsupported, invalid, or ambiguous states must fall back to conservative neutral/disabled behavior.
4. Self-test coverage plan:
   - additive tests defined for both valid and fail-closed paths.
5. Build verification plan:
   - wrapper checks plus `./scripts/build-glyph-mk6-quiet.sh` verification defined.
6. Reachability/config/protobuf/default boundaries held:
   - no reachability, config, protobuf, or default activation changes unless separately approved.
7. No hardware flashing by agent:
   - flashing remains explicit human action outside agent runs.
8. No gameplay semantics in firmware:
   - no gameplay meaning, threshold, or semantic source promotion into firmware runtime behavior.

## Separate readiness gates by expansion area

### Force Up-B runtime gate

Must pass all of:

1. Source-backed rule authority for force behavior is identified.
2. Selected-path-only call-site plan is documented.
3. Fail-closed force behavior is explicit (`disabled`/no force on invalid or ambiguous states).
4. Self-tests cover no-match, resolved, ambiguity, and invalid-rule diagnostics.
5. Build + grep verification plan is documented.

### Digital output behavior gate

Must pass all of:

1. Source-backed output-bit authority is identified.
2. Selected-path-only output-composition plan is documented.
3. Fail-closed digital behavior is explicit (neutral output on invalid/unknown states).
4. Self-tests cover neutral default, triggered composition, and invalid-bit failure paths.
5. Build + grep verification plan is documented.

### Binding UX/config path gate

Must pass all of:

1. Prototype/debug bindings are explicitly separated from product UX/config contract.
2. Ownership/source authority for any UX/config mapping is identified.
3. Config/protobuf/default activation decisions are deferred unless separately approved.
4. Migration/safety implications are documented before any schema/default wiring work.
5. Build + grep verification plan is documented.

## Stop conditions (mandatory)

Stop before proceeding if work would:

1. Enable Force Up-B runtime behavior.
2. Enable digital output runtime behavior.
3. Change right-stick/C-stick behavior.
4. Change mode reachability.
5. Require config/protobuf/default schema decisions.
6. Introduce export/push workflows.
7. Trigger hardware flashing.

## Recommended next possible batches

A. `G11p-impl-readiness` audit only, no implementation.
B. `G11q-impl-readiness` audit only, no implementation.
C. `G11w` selected-path neutral output regression hardening.
D. `G8` software-side realization evaluator prototype.
