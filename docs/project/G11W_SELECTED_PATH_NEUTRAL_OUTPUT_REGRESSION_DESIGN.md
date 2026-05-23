# G11w Selected-Path Neutral Output Regression Design (Design-Only, Docs-Only)

Status: design-only and docs-only.  
Scope: define a future hardening path against neutral-output regressions in selected `SenscopePrototype` runtime, without expanding behavior in this batch.

## Purpose

Design a conservative future batch that reduces selected-runtime neutral-output regression risk while preserving current runtime behavior boundaries.

## Target invariant

Selected runtime should start from or preserve a neutral packet baseline for:

1. digital outputs;
2. right-stick/C-stick outputs;
3. analog triggers;

unless a separate, explicit, source-backed feature approval changes those fields.

## Current expected selected-runtime neutral outputs (source-backed baseline)

From inspected source:

1. `outputs.buttons = 0`.
2. right-stick/C-stick is set to neutral centered state through `UpdateDirections(...)`.
3. `outputs.triggerLAnalog = 0` and `outputs.triggerRAnalog = 0`.
4. Force Up-B remains disabled in selected runtime baseline (no Force helper call-site).
5. On helper/resolver failure, runtime keeps fallback neutral left-stick coordinate (returns before overriding neutral defaults).

## Future regression-hardening options

### Option A: Helper-level output packet invariant tests only

Additive self-test expansion focused on helper/output composition invariants:

- preserve neutral packet defaults for unresolved/no-left-stick paths;
- preserve fail-closed digital invalid-bit diagnostics;
- preserve Force no-match disabled behavior.

Pros:

- lowest runtime risk;
- strongest source-backed guardrails;
- no mode-selection/config/reachability touch.

### Option B: Selected-runtime comments or assert-like compile-visible helpers (safe-only)

Introduce narrowly scoped compile-visible runtime guard comments/helpers that document neutral-output expectations without enabling new behavior.

Pros:

- improves runtime readability at call-site.

Risk:

- touches selected runtime source and can increase churn around a safety-sensitive path.

### Option C: Docs-only manual checklist

If runtime changes are too invasive, expand docs/checklists only and require explicit review steps for neutral-output invariants.

Pros:

- zero runtime risk.

Limitation:

- no executable invariant guard.

## Recommended implementation option

Recommended first step: **Option A**.

Rationale:

1. Prefer helper-level/self-test expansion first.
2. Do not modify mode-selection or config/protobuf/default activation.
3. Avoid selected-runtime edits unless a concrete, source-backed regression gap is proven.

## Mandatory stop-before conditions for any future G11w implementation

Stop before:

1. changing runtime outputs;
2. enabling any non-neutral digital output;
3. enabling Force Up-B;
4. enabling right-stick/C-stick behavior changes;
5. making config/protobuf/default reachability changes;
6. hardware flashing.

## Design conclusion

A low-risk, source-backed path exists to harden selected-runtime neutral-output regressions by prioritizing additive helper/self-test coverage and deferring runtime/config reachability changes unless separately approved.

