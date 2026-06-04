# Glyph Runtime Storage/Interpreter Blocker Packet - 2026-06-03

## Purpose and scope

This document records a docs/tools-only blocker packet for any future
runtime-loaded config storage or interpreter work.

It is not firmware source, not runtime-loaded config implementation, not
storage implementation, not interpreter implementation, not serial/device write
behavior, not WebSerial transport implementation, not official configurator
compatibility, and not hardware validation.

## Current blocker status

The current branch conclusion is:

- runtime-loaded config not implemented
- storage not implemented
- interpreter not implemented
- storage location undecided
- representation undecided
- boot-time validation undecided
- fallback policy undecided
- version migration undecided
- maximum config size undecided
- profile-bound vs global undecided
- latency/performance evidence missing
- hardware validation plan required
- nunchuk decision required
- firmware owns evaluator phase order
- firmware owns allowed role classes
- config must not own scripts/macros/turbo/timing/history
- config must not own phase-order mutation
- not hardware validation

This packet does not approve runtime-loaded config, persistent storage,
interpreter work, runtime storage location, runtime representation, boot-time
validation behavior, fallback behavior, version migration, transport behavior,
device writing, WebSerial, or hardware validation.

## Source-backed inputs

Repo-local evidence currently includes only bounded docs/tools inputs:

- `docs/calibration/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.md`
- `docs/calibration/fixtures/glyph_runtime_loaded_config_implementation_readiness_packet_2026-05-28.json`
- `docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md`
- `docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md`
- `tools/check_glyph_runtime_loaded_config_design.py`
- `docs/calibration/glyph_storage_transport_source_authority_registry_2026-06-03.md`
- `docs/calibration/glyph_protobuf_config_schema_research_packet_2026-06-03.md`
- `docs/calibration/glyph_webserial_transport_blocker_packet_2026-06-03.md`

Those inputs support a blocker record only. They do not establish a storage
location, runtime representation, boot-time validation path, fallback policy,
version migration policy, maximum config size, profile-bound/global policy,
latency/performance evidence, hardware validation result, or nunchuk hardware
validation result.

## Required unresolved design decisions

Future work remains blocked until design and source-authority review resolve:

- storage location
- representation
- boot-time validation
- fallback policy
- version migration
- maximum config size
- profile-bound vs global scope
- latency/performance evidence
- hardware validation plan
- nunchuk decision

## Required missing evidence

Any future implementation proposal must first provide:

- source-backed storage/interpreter authority
- latency/performance evidence
- hardware validation plan
- explicit user approval

These are prerequisites only. Recording them here does not approve
runtime-loaded config, storage, interpreter work, device writing, WebSerial, or
hardware validation claims.

## Firmware-owned semantics

Firmware must own:

- evaluator phase order
- allowed role classes
- priority/evaluator semantics
- rejection of unsupported role classes

Runtime-loaded config data must not take ownership of those semantics.

## Forbidden config capabilities

A future config must not own:

- scripts
- macros
- turbo
- timing
- history-dependent logic
- phase-order mutation

This packet does not authorize toggles, one-shots, macros, turbo, timing
automation, arbitrary scripting, or history-dependent behavior.

## Approval boundary

Required approval before future work:

- explicit user approval for any runtime-loaded config storage/interpreter
  implementation path
- source-authority review approval for storage, representation, validation,
  fallback, migration, and performance claims
- hardware-test-plan approval before any implementation branch can claim
  hardware results

## Checker ownership

`tools/check_glyph_runtime_storage_interpreter_blocker_packet.py` validates the
blocker fixture, hard false implementation flags, required unresolved design
decisions, required missing evidence, firmware-owned semantics, forbidden
config capabilities, approval requirements, and required document caveat
phrases.

Checker output lines:

- `glyph_runtime_storage_interpreter_blocker_packet`
- `status=PASS` or `status=FAIL`
- `runtime_loaded_config_implemented=false`
- `storage_implemented=false`
- `interpreter_implemented=false`
- `hardware_status=not_new_hardware_result`

Passing the checker confirms only that this packet preserves the intended
docs/tools-only blocker boundary. It is not runtime-loaded config
implementation, not storage implementation, not interpreter implementation, and
not hardware validation.
