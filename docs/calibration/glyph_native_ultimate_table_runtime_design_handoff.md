# Glyph Native Ultimate Table Runtime Design Handoff

Date: 2026-05-26

## What This Branch Adds

- `docs/calibration/glyph_native_ultimate_table_runtime_design_2026-05-26.md`, a design-only comparison of future native Ultimate table implementation options.
- No code changes.

## Recommended Path

Option D, a new reviewed native table layer consumed by `MODE_ULTIMATE`, is recommended only after fixture contracts, source checkers, requirements docs, and preservation hardware gates are reviewed.

## Key Boundaries

- Current native Ultimate arbitrary table support is absent.
- `MODE_CUSTOM` is not automatically equivalent to native Ultimate.
- `SenscopePrototype` is scaffold/prototype material, not production runtime.
- No runtime behavior was changed.
- No flashing/push automation was added.

## Behavior Impact

- Runtime/source behavior changed: none.
- Configurator/profile schema behavior changed: none.
- Build artifacts or binaries committed: no.
