# Glyph Profile Config Adapter Policy Handoff

Date: 2026-05-26

## What This Branch Adds

- Documents safe pre-adapter policy decisions in `docs/calibration/glyph_profile_config_adapter_policy_decisions_2026-05-26.md`.
- Records unresolved gates that must stay blocked before any write-capable adapter exists.
- Keeps the distinction between omitted `activates` and explicit `BTN_UNSPECIFIED` visible and uncollapsed.

## Source-Grounded Facts Used

- `BTN_UNSPECIFIED` is a firmware no-op target in button helpers: `HAL/pico/include/util/state_util.hpp`.
- Runtime remap supports many-to-one aliases and suppresses later duplicate physical mappings: `src/core/InputMode.cpp`.
- Default config indices are one-based in source-confirmed paths: `HAL/pico/src/comms/backend_init.cpp`, `src/core/config_utils.cpp`.
- JSON fixtures are not canonical device storage authority; firmware storage/transport is protobuf-backed: `HAL/pico/src/core/Persistence.cpp`, `HAL/pico/src/comms/ConfiguratorBackend.cpp`.

## Open Decisions

- Outbound disabled-remap encoding remains unresolved.
- Whether an adapter may emit `defaultModeConfig = 0` remains unresolved.
- Configurator JSON import/export rules require source or corpus authority.
- Any write-capable adapter needs explicit user/domain approval and corpus-backed checks.

## Behavior Impact

- Runtime/source behavior changed: none.
- Configurator/profile schema behavior changed: none.
- Build artifacts or binaries committed: no.

## Recommended Next Branch

Proceed to read-only prewrite validation that reports decision surfaces without normalizing, rewriting, or reordering profile data.
