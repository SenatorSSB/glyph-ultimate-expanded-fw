# Glyph Identity Runtime Table Source Sync - 2026-05-28

## Purpose and scope

This document records the source-parsed table extraction and table-sync guardrail
for the current Glyph Smash Box identity runtime behavior evaluator.

The guardrail keeps the evaluator's mirrored Python `TABLES` constants aligned
with the current `constexpr StickPoint` tables in `src/modes/Ultimate.cpp`. It is
tools/docs-only and does not change firmware runtime behavior.

## Source authority

Primary source authority:

- `src/modes/Ultimate.cpp`
- `tools/check_glyph_identity_runtime_behavior_evaluator.py`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`

The table values are sourced from `src/modes/Ultimate.cpp`. The evaluator mirror
remains a bounded regression harness, not a firmware simulator.

## Extracted table symbols

`tools/extract_glyph_identity_runtime_tables.py` extracts these required source
symbols and maps them to evaluator table names:

| Source symbol | Evaluator name |
| --- | --- |
| `kDefaultTable` | `Default` |
| `kModeDefaultTable` | `ModeDefault` |
| `kX1Table` | `X1` |
| `kX2Table` | `X2` |
| `kMX1Table` | `MX1` |
| `kMX2Table` | `MX2` |
| `kY1Table` | `Y1` |
| `kMY1Table` | `MY1` |
| `kLayerNormalXTable` | `LayerNormalX` |
| `kMLayerNormalXTable` | `MLayerNormalX` |
| `kLayerFlipperTable` | `LayerFlipper` |
| `kMLayerFlipperTable` | `MLayerFlipper` |
| `kY1Tilt1Table` | `Y1Tilt1` |
| `kMY1Tilt1Table` | `MY1Tilt1` |
| `kY1LayerFlipperTable` | `Y1LayerFlipper` |
| `kMY1LayerFlipperTable` | `MY1LayerFlipper` |
| `kY1LayerNormalXTable` | `Y1LayerNormalX` |
| `kMY1LayerNormalXTable` | `MY1LayerNormalX` |
| `kTilt1Table` | `Tilt1` |
| `kTilt2Table` | `Tilt2` |
| `kTilt3Table` | `Tilt3` |
| `kMTilt1Table` | `MTilt1` |
| `kMTilt2Table` | `MTilt2` |
| `kMTilt3Table` | `MTilt3` |
| `kLt1LowMagnitudeTable` | `Lt1LowMagnitude` |

## Extractor validation

`tools/extract_glyph_identity_runtime_tables.py` validates:

- every required source symbol is present;
- every required table uses the expected `StickPoint[9]` shape;
- every required table contains exactly nine `{x, y}` points;
- every coordinate is an integer in `[0, 255]`;
- malformed table bodies fail instead of being partially parsed.

The extractor supports a default text summary and deterministic JSON output via
`--json`. It does not write generated files by default.

## Table-sync checker validation

`tools/check_glyph_identity_runtime_table_source_sync.py` validates:

- the source tables can be parsed from `src/modes/Ultimate.cpp`;
- the evaluator exposes mirrored `TABLES`;
- required table names are present on both sides;
- no unexpected table names are present;
- table lengths match;
- every point matches exactly.

The checker prints `hardware_status=not_new_hardware_result` and exits nonzero
on any extraction or comparison failure.

## Runtime and hardware boundaries

This guardrail is not runtime behavior. It does not edit `src/modes/Ultimate.cpp`,
does not change table values, does not generate C++ config, and does not validate
hardware.

Passing this checker means only that the bounded Python evaluator's mirrored
tables still match the current source tables. It is not new hardware evidence and
does not validate nunchuk hardware behavior.

## Relation to behavior evaluator harness

`tools/check_glyph_identity_runtime_behavior_evaluator.py` now runs the
table-source sync checker after the behavior-case structural checker and before
evaluating cases. This prevents duplicated Python table constants from silently
drifting from `src/modes/Ultimate.cpp`.

The aggregate readiness runner also invokes the source-sync checker before the
behavior evaluator checker.

## Future migration path

1. Current source-parsed table sync.
2. Evaluator driven by extracted constants.
3. Generated C++ config prototype.
4. Generated regression fixtures.
5. Runtime-loaded config validation.

Each later step requires review before implementation and must preserve the
repository boundaries around firmware behavior, profile schema, hardware claims,
and Senscope game-semantic source authority.
