# Phase 7A Runtime Config Compiled Payload Activation

Status: `PHASE7A_COMPILED_PAYLOAD_RUNTIME_ACTIVE_PENDING_HARDWARE_RESULT`

This branch activates a source-owned, compiled-in Phase 7A valid baseline
runtime-config payload for `MODE_ULTIMATE`.

This is a validation-gated source-equivalent activation.

## What Changed

- Added `src/modes/UltimateRuntimeConfigCompiledPayload.hpp` with bytes copied
  from
  `docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin`.
- `Ultimate.cpp` validates the compiled payload through
  `ParseUltimateRuntimeConfigPayload` before selecting the active runtime config.
- When the compiled payload validates, the runtime keeps using the
  source-owned current baseline `RuntimeConfigView`.
- If compiled payload validation fails, the runtime falls back to
  `kKnownGoodRuntimeConfig`.

## Behavior-Preserving Intent

The committed Phase 7A baseline payload is generated from the same
source-owned 27-table baseline used by `UltimateRuntimeConfigInterpreter.hpp`.
This branch intentionally preserves current output behavior for the valid
baseline payload.

Payload-backed table lookup is deferred. The activation implemented here is a
behavior-preserving parser validation gate, not arbitrary payload data
ownership. A later branch must implement bounded payload-backed lookup before
any storage read or externally supplied runtime config is considered.

## Fallback Policy

Activation is all-or-nothing:

- valid compiled/test payload plus valid source-owned runtime view: use the
  source-owned current baseline runtime view;
- invalid compiled/test payload, invalid source-owned view, or any parser
  rejection: fall back to `kKnownGoodRuntimeConfig`;
- no partial activation is allowed.

## Explicit Non-Implementations

- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- `config.bin` runtime-config use is not implemented.
- Boot-time external payload loading is not implemented.
- Device write / WebSerial is not implemented.
- Runtime-config command IDs are not implemented.
- Firmware flashing automation is not implemented.
- UF2 copy automation is not implemented.
- Official configurator compatibility is not claimed.
- Nunchuk remains NOT_TESTED.

## Hardware Gate

Hardware validation is required before merge because the firmware runtime path
changed. The plan is recorded at
`docs/calibration/glyph_phase7a_runtime_config_compiled_payload_activation_hardware_plan_2026-06-08.md`.

No hardware result is recorded on this branch.

## Source Authority

- Payload bytes: `docs/runtime_config/fixtures/phase7a_valid_baseline_runtime_config_payload.bin`
- Parser scaffold: `src/modes/UltimateRuntimeConfigParser.hpp`
- Runtime interpreter baseline: `src/modes/UltimateRuntimeConfigInterpreter.hpp`
- Active firmware path: `src/modes/Ultimate.cpp`
- Fixture generator/checker:
  `tools/glyph_runtime_config_candidate_generator.py` and
  `tools/check_glyph_runtime_config_parser_equivalence.py`
