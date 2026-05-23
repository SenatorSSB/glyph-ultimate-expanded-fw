# G8 - Software Realization Evaluator Scope

Status: scaffold (docs-only, non-runtime)
Date: 2026-05-23

## Purpose

G8 defines a software-side realization evaluator scaffold for future Senscope integration planning.

This batch is non-runtime and docs-only. It does not implement firmware behavior, runtime adapter behavior, or host tooling behavior.

## Evaluator role

The evaluator role in G8 is contract-level only:

1. Compare Senscope neutral target intent against backend capability evidence.
2. Return realization statuses for representability, export readiness, and push readiness.
3. Produce diagnostics and evidence traces.
4. Avoid creating or modifying firmware behavior.

The evaluator reports what can be proven, what is unsupported, and what remains unknown. It is a decision/diagnostic layer, not an execution layer.

## Required layer separation

G8 keeps the following layers separate:

1. Senscope neutral profile concepts.
2. Backend capability claims (source-backed, inferred, unknown, unsupported-by-current-source).
3. Evaluator logic (comparison, status, diagnostics).
4. Firmware runtime behavior (mode/update/output logic in firmware source).
5. Gameplay semantics (game action meanings, semantic thresholds, semantic maps, no-smash/no-strong-input, source-authority promotion).

## Non-goals

G8 does not:

1. Change firmware source/header behavior.
2. Implement export or push workflows.
3. Change config/protobuf/default activation wiring.
4. Add or compute gameplay semantics.
5. Change Senscope neutral profile schema.

## Readiness level for this batch

Expected readiness remains conservative:

1. Level 0: evidence-only classification.
2. Level 1: static representability checks.

Levels requiring runtime behavior decisions or delivery workflows are out of scope for this batch.

## Why G8 stays in this repo

G8 remains in this repo at this stage because:

1. Glyph-side source authority for backend capability evidence is hosted here.
2. Backend-capability modeling boundaries are being documented here before app-side implementation.
3. Future Senscope adapter/evaluator handoff needs source-backed boundary artifacts first.
4. This is not a Senscope app implementation batch.
