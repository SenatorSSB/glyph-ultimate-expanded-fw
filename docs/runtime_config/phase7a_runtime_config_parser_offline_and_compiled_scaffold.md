# Phase 7A Runtime-Config Parser Offline And Compiled Scaffold

Status: `PHASE7A_COMPILED_SCAFFOLD_NOT_RUNTIME_ACTIVE`.

This packet records the first autonomous Phase 7A build sequence for the
source-owned Ultimate runtime-config baseline. It is grounded in the existing
offline `GCFG` preview format in
`tools/glyph_runtime_config_binary_roundtrip.py`, the source-owned 27-table
baseline in `src/modes/UltimateIdentityRuntimeTables.hpp`, and the interpreter
boundary in `src/modes/UltimateRuntimeConfigInterpreter.hpp`.

## Implemented

- Offline deterministic candidate generator:
  `tools/glyph_runtime_config_candidate_generator.py`.
- Valid baseline payload fixtures:
  `fixtures/phase7a_valid_baseline_runtime_config_payload.bin`,
  `fixtures/phase7a_valid_baseline_runtime_config_payload.json`, and
  `fixtures/phase7a_valid_baseline_runtime_config_payload_report.json`.
- Parser vector corpus:
  `fixtures/phase7a_runtime_config_parser_test_vectors.json`.
- Host-side parser oracle:
  `tools/glyph_runtime_config_parser_oracle.py`.
- Static equivalence checker:
  `tools/check_glyph_runtime_config_parser_equivalence.py`.
- Design-time storage simulator:
  `tools/glyph_runtime_config_storage_simulator.py`.
- Storage simulator checker:
  `tools/check_glyph_runtime_config_storage_simulator.py`.
- Firmware parser scaffold:
  `src/modes/UltimateRuntimeConfigParser.hpp`.
- Firmware parser scaffold checker:
  `tools/check_glyph_runtime_config_firmware_parser_scaffold.py`.

## Format Scope

The Phase 7A offline payload uses the existing `GCFG` preview container:

- magic: `GCFG`;
- format version: `1`;
- mode scope: `MODE_ULTIMATE`;
- table count: `27`;
- point count per table: `9`;
- table order: `RuntimeTableId` order;
- coordinate bytes: bounded unsigned byte coordinates;
- checksum: CRC32 over the payload before the checksum.

The valid baseline fixture decodes back to the source-owned 27-table
`StickPoint[9]` corpus. The static checker compares the generated payload,
decoded payload, current runtime table metadata, and source-owned baseline.

## Firmware Scaffold Boundary

`src/modes/UltimateRuntimeConfigParser.hpp` is a compiled scaffold only. It is
included by `src/modes/Ultimate.cpp` so the firmware build compiles the parser
symbols, but `Ultimate.cpp` does not call `ParseUltimateRuntimeConfigPayload`.

The scaffold:

- does not read storage;
- does not write storage;
- does not mutate `RuntimeConfigView`;
- does not change controller outputs;
- does not add boot/load hooks;
- does not add WebSerial or serial device-write commands;
- does not use `config.bin`;
- does not add firmware flashing automation.

## Storage Simulator Boundary

`tools/glyph_runtime_config_storage_simulator.py` is design-time simulation
only. It covers missing storage, valid storage, corrupt storage, wrong version,
wrong checksum, and invalid payload cases. It does not use firmware
`Persistence`, does not read or write actual device storage, and does not claim
runtime-loaded firmware behavior.

## Not Implemented

- Runtime-loaded config activation.
- Runtime-config storage reads or writes.
- Boot/load source changes.
- `config.bin` reuse for runtime config.
- WebSerial or serial runtime-config write commands.
- Device write.
- Firmware flashing automation.
- Production export.
- Official configurator compatibility.
- Nunchuk validation.

## Hardware-Test Status

Hardware testing is not required for this slice because the parser is compiled
but not runtime-active and no controller output behavior is intended to change.

## Next Slice

Runtime activation of a compiled/test payload requires explicit product
approval, source-backed storage and fallback decisions, a hardware test plan,
and a hardware result before merge.
