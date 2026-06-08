# Phase 6 Bounded Config Source Authority

Status: PHASE6_SOURCE_AUTHORITY_COMPLETE_NOT_IMPLEMENTED.

## Purpose

This packet records the source boundary for Phase 6 Stable Firmware + Bounded
Config-Owned Modifier Data and the five runtime-loaded-config blockers. It is
docs/spec/tooling only.

No runtime-loaded config, runtime-config storage, firmware parser integration,
boot/load changes, WebSerial/device write, firmware flashing automation, or
production export is implemented here.

## Inspected Files

- `README.md`
- `AGENTS.md`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`
- `docs/calibration/README.md`
- `docs/calibration/INDEX.md`
- `docs/runtime_config/`
- `docs/export/`
- `docs/release/`
- `docs/calibration/export_corpus/`
- `src/modes/Ultimate.cpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- `HAL/pico/include/core/Persistence.hpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/include/comms/ConfiguratorBackend.hpp`
- `config/glyph/common/src/config.cpp`
- `platformio.ini`
- `tools/extract_glyph_identity_runtime_tables.py`
- `tools/glyph_runtime_config_binary_roundtrip.py`
- all present `tools/check_glyph_runtime_config*.py`
- `tools/run_glyph_next_runtime_change_readiness_checks.py`

## Inspected Searches

- `rg -n "RuntimeConfig|RuntimeConfigView|StickPoint|config.bin|LittleFS|Persistence|SaveConfig|LoadConfig|CheckSavedConfig|LoadConfigRaw|pb_decode|pb_encode|nanopb|Config_fields|CMD_SET_CONFIG|CMD_GET_CONFIG|CMD_SET_RUNTIME|CMD_GET_RUNTIME|WebSerial|device write|boot|fallback|rollback|recovery|migration|crc|checksum|runtime-loaded|runtime config|profile-scoped|global|MODE_ULTIMATE" README.md AGENTS.md docs src include HAL config tools platformio.ini`
- `find docs/runtime_config docs/export docs/release docs/calibration tools src/modes HAL/pico config/glyph -maxdepth 6 -type f`

## Precondition Files

All requested precondition files were present on the branch before Phase 6
edits.

## Source-Backed Facts

- Current canonical docs record runtime-loaded config, runtime-config storage,
  firmware binary/protobuf parser integration, WebSerial/device write, protobuf
  binary write, and firmware flashing automation as not implemented.
- Phase 6 is ready for engineering design only and requires user product
  approval before implementation.
- `src/modes/UltimateRuntimeConfigInterpreter.hpp`,
  `src/modes/UltimateIdentityRuntimeTables.hpp`, and `src/modes/Ultimate.cpp`
  provide the source-owned `MODE_ULTIMATE` runtime table baseline and
  `RuntimeConfigView` relationship.
- Step 12 offline `GCFG` binary tooling exists in
  `tools/glyph_runtime_config_binary_roundtrip.py` and is explicitly
  offline-only.
- Step 10 source-authority and architecture packets record current
  `Persistence` support for the existing protobuf `Config` object and keep
  runtime-config storage implementation blocked.
- Step 13 parser source-authority and integration-plan packets keep firmware
  binary/protobuf parser implementation blocked.
- Step 14 manual load path planning keeps firmware-consuming manual
  runtime-config load blocked.
- Step 15 and Step 16 packets keep WebSerial/device-write implementation
  blocked.
- Step 17 keeps flashing automation forbidden/not approved.
- Official-configurator export target work is offline/reference only and does
  not claim production export or official compatibility.

## Fixture-Observed Evidence

- `docs/runtime_config/fixtures/current_baseline_extracted_config_preview.json`
  and related baseline fixtures describe the current source-owned table
  preview.
- `docs/runtime_config/fixtures/current_baseline_runtime_config_binary_preview.json`
  and `.bin` are offline preview artifacts, not firmware inputs.
- `docs/runtime_config/fixtures/invalid_runtime_config_binary_cases.json` and
  `docs/runtime_config/fixtures/invalid_runtime_config_semantics_cases.json`
  show existing fail-closed offline invalid-corpus practice.

## Inferred Or Proposed Decisions

- PROPOSED_DECISION_NOT_IMPLEMENTED: first runtime-config scope should be
  `MODE_ULTIMATE` only.
- PROPOSED_DECISION_NOT_IMPLEMENTED: firmware should own evaluator semantics,
  validation, fallback, migration, storage policy, device-write policy, and
  parser acceptance rules.
- PROPOSED_DECISION_NOT_IMPLEMENTED: config may own only bounded table data and
  metadata/provenance/checksums.
- PROPOSED_DECISION_NOT_IMPLEMENTED: storage should prefer a separate
  mode-scoped runtime-config artifact rather than the current `config.bin`
  unless a future implementation proves extending current `Config` is safer.
- PROPOSED_DECISION_NOT_IMPLEMENTED: the first parser format should prefer a
  small deterministic firmware-owned binary format based on the existing
  offline `GCFG` preview shape; protobuf extension remains a later alternative.
- PROPOSED_DECISION_NOT_IMPLEMENTED: boot/load should keep existing config load
  behavior first, initialize source-owned known-good runtime config, then
  optionally validate a candidate and activate only if fully valid.
- PROPOSED_DECISION_NOT_IMPLEMENTED: invalid candidates should be ignored with
  no auto-delete, auto-rewrite, hidden recovery write, or partial activation.
- PROPOSED_DECISION_NOT_IMPLEMENTED: future device write must remain explicit,
  user-visible, validation-before-write, readback-capable if source-backed, and
  rollback/recovery-gated.

## Unknowns

- Exact future runtime-config storage path, filename, slot layout, and
  ownership implementation are unknown.
- Exact firmware parser ABI and memory-size limits are unknown.
- Exact boot/load hook and initialization ordering are unknown beyond the
  proposed design sequence.
- Runtime-config diagnostics and recovery mutation support are unknown.
- WebSerial/device-write authority for runtime-config payloads is not
  source-backed.
- Official configurator compatibility for any runtime-config payload is
  unknown and not claimed.
- Nunchuk behavior remains NOT_TESTED.

## Rejected Unsupported Claims

- Claim that runtime-loaded config exists in firmware.
- Claim that runtime-config storage exists.
- Claim that firmware parser integration exists.
- Claim that `config.bin` is approved as the runtime-config storage location.
- Claim that WebSerial/device write is approved or available.
- Claim that firmware flashing automation is approved or available.
- Claim that official configurator compatibility is proven.
- Claim that public release status exists.
- Claim that nunchuk validation exists.
- Claim that external-remapper evidence is primary authority.

## Explicit Implementation Boundary

Phase 6 stops before firmware/device behavior. The only allowed artifacts are
docs, fixtures, read-only checkers, index/navigation updates, and aggregate
readiness wiring.

No runtime-loaded config implementation claim is made.
