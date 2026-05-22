# Glyph Findings 2026-05-21

This local note preserves the conclusions from the nearby reference copy at:

- `/Users/rasmus.pekkarinen/Library/Mobile Documents/com~apple~CloudDocs/Smash/senscope/docs/research/GLYPH_FINDINGS_2026-05-21.md`

## Core conclusion

FW-Glyph is a firmware fork and realization workstream, not the canonical source of game semantics.

## What lives where

- Senscope owns neutral profile intent, SSBU datasets, raw/effective mappings, solver logic, and visualizer logic.
- Glyph firmware owns realization: whether exact coordinate outputs, flipper functions, button layers, chords, and overrides can be implemented.
- Glyph configurator JSON appears to be a HayBox-proto Config projection.
- ESAM1 is an older custom firmware mode and should be treated as behavior evidence, not a direct modern profile format.

## Current capability boundaries

- Current config covers game modes, SOCD, button remapping, backend configs, keyboard modes, RGB configs, and dashboard/menu metadata.
- The public config model does not appear sufficient for full exact 9-way modifier tables, flipper modifiers, pre-SOCD force-UpB overrides, or dynamic button-layer switching.
- Neutral output is first-class and may be non-center.
- Controller semantics and game semantics must stay separate.

## Safe modeling rule

Old overflow-style flipper behavior must be represented as explicit flipper transforms, not unsafe unsigned overflow behavior.
