# G8e - Senscope Handoff Boundary Notes

Status: docs-only handoff boundary notes
Date: 2026-05-23

## Scope note

This document is docs-only and not app implementation.

It defines what should stay in this Glyph firmware repo versus what should be implemented later in the Senscope app repo.

## What belongs in this Glyph repo

The following artifacts belong in this repository at this stage:

1. Backend source authority notes.
2. Capability claim fixtures and drafts.
3. Source-reference expectations and references.
4. Firmware-side boundary findings.
5. Runtime/readiness constraints and gating notes.

These are source-authority and boundary inputs, not app-side implementation outputs.

## What belongs later in the Senscope app repo

The following belongs in the Senscope app repository:

1. TypeScript evaluator package.
2. Actual neutral profile schema integration in app code.
3. Dataset/equivalence lookup integration.
4. UI and solver integration.
5. App-side tests.

This separation keeps firmware-repo documentation and app implementation responsibilities distinct.

## Handoff artifacts

Recommended handoff artifact set from this repo to Senscope app work:

1. Capability fixture draft (synthetic examples and status handling).
2. Diagnostic taxonomy.
3. Source-ref trace requirements.
4. Known unknowns list.
5. Unsupported export/push status.
6. Selected-runtime caveats (mode-specific vs generic boundaries).

## Non-transferable items

The following must not be treated as transferable app implementation scope:

1. Firmware runtime code.
2. Hardware flashing workflow.
3. Gameplay semantic authority.
4. Private vendor format generation.

## Recommended Senscope-side future batches

A. Package target decision.

B. Mock evaluator implementation.

C. Fixture ingestion tests.

D. Same-effective dataset injection boundary.

## Implementation boundary rule

Any app-side implementation must still:

1. Respect raw-versus-effective separation.
2. Avoid inferring backend support where source-backed evidence is absent.
3. Preserve fail-closed unknown/unsupported behavior.
4. Keep gameplay semantic authority outside backend evaluator claims.
