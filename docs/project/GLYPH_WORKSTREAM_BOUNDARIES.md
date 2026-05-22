# Glyph Workstream Boundaries

This document defines the boundaries for Glyph / HayBox-style controller-backend work.

## Purpose

The Glyph workstream investigates and implements controller-backend realization support without changing game-semantic source authority.

It is separate from Senscope's no-smash / dataset semantic-source pipeline.

## Allowed work

Glyph-side agents may work on:

- backend capability modeling;
- neutral profile realization checks;
- adapter interfaces;
- controller-specific diagnostics;
- manual-entry/export planning;
- evaluation of documented Glyph/HayBox behavior;
- comparison of desired neutral profile outputs against realizable backend outputs;
- docs and tests for backend constraints.

## Forbidden work without explicit user approval

Do not:

- add Super Smash Bros. Ultimate gameplay semantic sources;
- change no-smash scope;
- modify no-smash/no-strong-input behavior;
- promote manual gameplay evidence;
- treat controller realization constraints as game semantics;
- assume Glyph/HayBox behavior without source evidence;
- add push-to-device workflows;
- generate vendor-specific files unless format/source support is explicit;
- change neutral Profile schema unless separately approved.

## Required separation

Keep these layers separate:

1. Neutral Senscope profile
   - app-owned canonical profile format
   - raw coordinates by modifier/direction

2. Controller backend capability model
   - what a backend can represent
   - backend-specific fields, buttons, modes, layers, or chords

3. Realization/evaluation
   - compare desired profile outputs to backend-realized outputs
   - classify exact match / mismatch / unsupported / unknown

4. Export/manual-entry adapter
   - user-facing artifacts
   - manual-entry guide
   - generated export only if source support is explicit

5. Solver/search
   - future inverse backend realization
   - must distinguish infeasible from unknown-not-searched

## Source authority

A backend behavior claim must cite or reference a source file, implementation file, documentation file, or inspected code path.

If behavior is inferred, mark it as inferred and do not build irreversible product behavior on it.

## Stop conditions

Stop and ask the user before:

- claiming undocumented firmware behavior;
- deciding a backend capability is universal;
- adding push-to-device;
- adding a vendor export format;
- changing neutral Profile schema;
- modeling priority/fusion/SOCD behavior without source evidence;
- coupling backend constraints into the game semantic solver;
- selecting or promoting game semantic sources.

## Branch policy

Use the shared branch policy from `AGENTS.md`.

## Command policy

Use the shared command policy from `AGENTS.md`.
