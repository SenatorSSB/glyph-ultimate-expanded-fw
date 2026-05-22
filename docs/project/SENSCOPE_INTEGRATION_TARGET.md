# Senscope Integration Target

This document defines the intended integration boundary between this Glyph-side repo and the Senscope app.

## Purpose

This repo may eventually provide source-backed controller/backend knowledge for Senscope.

The integration target is not game semantics. The integration target is backend realization.

## Senscope concepts expected by integration

Senscope uses a neutral app-owned profile format with:

- controller family metadata;
- dataset ID;
- modifier directional maps;
- raw coordinate outputs by FGC/numpad direction;
- first-class neutral direction `5`.

Integration should consume or reason about those concepts without requiring Senscope to adopt vendor-private configuration as canonical truth.

## Valid integration outputs

This repo may eventually support producing:

- backend capability metadata;
- realization evaluator;
- manual-entry guidance;
- diagnostics for unsupported outputs;
- exact match / mismatch reports;
- possible export artifacts if source format support is explicit.

## Invalid integration outputs without approval

Do not produce:

- Super Smash Bros. Ultimate semantic predicates;
- no-smash/no-strong-input changes;
- game threshold logic;
- push-to-device workflow;
- vendor import/export files without source authority;
- neutral Profile schema changes.

## Desired adapter boundary

A future adapter should answer:

```text
Given a Senscope neutral profile and a backend capability model,
which desired raw outputs are:
- exactly realizable;
- realizable with caveats;
- mismatched;
- unsupported;
- unknown due to missing source evidence?
```

## Desired diagnostic categories

Suggested diagnostic classes:

- `EXACT_RAW_MATCH`
- `SAME_EFFECTIVE_OUTPUT`
- `RAW_MISMATCH`
- `UNSUPPORTED_FIELD`
- `BACKEND_LIMITATION`
- `UNKNOWN_BEHAVIOR`
- `SOURCE_EVIDENCE_MISSING`
- `EXPORT_UNSUPPORTED`
- `PUSH_UNSUPPORTED`

These are design targets, not final API names.

## Non-goals

- game semantic solving;
- global profile optimization;
- macros/turbo/timing automation;
- reverse engineering private encrypted formats;
- assuming universal backend behavior.
