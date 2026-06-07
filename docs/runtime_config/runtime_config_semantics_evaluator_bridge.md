# Runtime-Config Semantics Evaluator Bridge

## Purpose

This is a docs/tools bridge package for `MODE_ULTIMATE` that binds the current
source-backed table/role/evaluator baseline to a deterministic offline checker set.
It is not firmware source, not runtime-loaded configuration, and not a device
I/O implementation.

The bridge is the current baseline oracle for semantics parity review.
Its role is to keep evaluator behavior checks anchored to a source-backed
contract while avoiding any runtime-loaded implementation.

For a future runtime-loaded config path, this bridge is the future runtime-config
semantic validator candidate and the safety rail for proving equivalence before any
implementation work exists.

## Layer Separation

- Neutral profile layer: intent model and profile-level expressions.
- Controller/backend layer: firmware-owned evaluator semantics and priority model.
- Runtime-config boundary: bounded data packaging only.
- Transport/storage layer: intentionally deferred.

This bridge keeps evaluator logic and table-shape validation in the controller
backend layer and keeps runtime-loaded claims out of the profile and transport
layers.

## Baseline Extraction

Current baseline evidence is sourced from:

- `src/modes/Ultimate.cpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp` (included via source include)
- `tools/extract_glyph_identity_runtime_tables.py`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`

`table_family=StickPoint` and the baseline contains `27` tables with `9` points
per table in the source-backed extractor output.

## Baseline Equivalence Invariant

The bridge requires the following invariants before any future validator can be
considered:

- The extracted source table set and names must remain stable for the current
  baseline.
- Point count per baseline table remains exactly `9`.
- Table metadata used for downstream checks must match source-extracted
  `StickPoint[9]` shape and source symbols.
- The evaluator parity fixture must compare runtime-candidate semantics only
  against the baseline contract/evaluator outputs.

Breaking these invariants invalidates the bridge baseline.

## Evaluator Role

The evaluator bridge role is:

- compare source-backed table metadata against candidate artifacts,
- compare candidate evaluator outputs against known-baseline outputs,
- reject forbidden semantics classes before candidate proposals move out of
  docs/tools scope.

It does **not** provide firmware semantics, transport, or persistence behavior.

## Runtime-Loaded Config Boundary

This package marks runtime-loaded config as explicit non-goal:

- `runtime_loaded_config_implemented = false`
- `consumed_by_firmware = false`
- no storage/runtime bootstrap,
- no protobuf write protocol,
- no WebSerial transport,
- no firmware flashing automation,
- no direct game play semantics claims.

## Migration Path

1. Keep current source-owned behavior as the baseline.
2. Keep the evaluator bridge as docs/tools parity checker only.
3. Require a future runtime-config semantic validator to consume only bounded,
   schema-approved candidate data.
4. Delay runtime-loaded storage and transport implementation until explicit gates
   are passed.
5. Introduce a versioned runtime config format only after equivalent offline
   checker proof and manual review.

## Gates

The bridge defines the following required gates for future expansion:

- source/backward-compatible extractor agreement,
- rejected forbidden capabilities gate,
- fallback policy gate,
- version migration gate,
- storage/transport authority gate,
- hardware-test gate before implementation.

## Manual Hardware-Test Trigger Points

The bridge only triggers hardware evidence when an implementation path reaches:

- proposed runtime-loaded config evaluator changes that alter output behavior,
- proposed runtime-loaded config storage/interpreter changes,
- any proposal that would assert firmware behavior parity against hardware.

For this branch and package, no new hardware tests are executed because this is
docs/tools-only.

## Non-Claims

The following are explicitly outside this package and not claimed:

- runtime-loaded config implementation,
- storage/transport/protobuf transport,
- device write path,
- firmware flashing automation,
- nunchuk hardware-validated claim,
- any Super Smash Bros. Ultimate game-semantic interpretation.

Any stale source references or prior packets that conflict with this package are
treated as scope boundaries, not approvals.
