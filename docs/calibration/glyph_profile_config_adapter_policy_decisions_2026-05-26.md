# Glyph Profile Config Adapter Policy Decisions - 2026-05-26

Scope: source-grounded adapter policy notes for future Glyph profile/config adapter work. This document is preparatory only. It does not implement a write-capable adapter, does not change firmware runtime behavior, and does not claim that Senscope neutral Profile JSON maps directly to Glyph JSON.

## Current Adapter Status

- Status: `NO_WRITE_CAPABLE_ADAPTER`
- Decision: no adapter in this repo may emit Glyph profile/config output until the unresolved policy gates below are reviewed.
- Boundary: JSON fixtures are examples and corpus candidates, not canonical firmware storage or wire format authority.
- Source basis: `HAL/pico/src/core/Persistence.cpp`, `HAL/pico/src/comms/ConfiguratorBackend.cpp`, `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md`.

## Policy Decisions

| Topic | Current policy | Status | Source or evidence | Caveats |
| --- | --- | --- | --- | --- |
| Outbound disabled-remap encoding | Remains unresolved. Do not choose omitted `activates` or explicit `BTN_UNSPECIFIED` as canonical outbound style without source, corpus, or user policy. | `USER_POLICY_REQUIRED` | `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md` issues 07, 08, 14, 15 | Runtime explicit disabled behavior is known; JSON omission equivalence is not proven. |
| Omitted vs explicit disabled distinction | Preserve the distinction in all read-only adapter models and diagnostics. | `POLICY_DECIDED` | `tools/glyph_config_model.py`, `tools/check_glyph_profile_config_semantics.py`, `HAL/pico/include/util/state_util.hpp` | Preservation is a safety rule, not a claim that omission has runtime meaning by itself. |
| Omitted `activates` normalization | Do not normalize omitted `activates` to `BTN_UNSPECIFIED`. | `POLICY_DECIDED` | `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md` issues 07, 08 | Any future write path needs explicit approval before choosing an encoding. |
| Remap entry order | Preserve remap entry order unless source or corpus proves reordering is safe. | `POLICY_DECIDED` | `src/core/InputMode.cpp` | Duplicate physical entries are order-sensitive because runtime suppresses later mappings for the same physical button. |
| Many-to-one logical aliases | Treat many physical buttons activating the same logical target as valid runtime behavior. | `SOURCE_CONFIRMED` | `src/core/InputMode.cpp` | This is not macro behavior; it ORs button state into one logical button bit. |
| Duplicate physical remaps | Treat duplicate physical remap entries as first-entry-wins for runtime semantics. | `SOURCE_CONFIRMED` | `src/core/InputMode.cpp` | Adapter checks should report duplicates; they should not silently reorder or collapse them. |
| Default indices | Treat default profile/backend indices as one-based where source-confirmed. | `SOURCE_CONFIRMED` | `HAL/pico/src/comms/backend_init.cpp`, `src/core/config_utils.cpp`, `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md` issue 10 | Do not infer one-based behavior for unrelated external JSON fields without source. |
| `defaultModeConfig = 0` | Firmware validation currently does not reject zero; outbound use still requires policy decision. | `SOURCE_CONFIRMED_VALIDATION_GAP` | `tools/check_glyph_profile_config_semantics.py`, `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md` | A validator accepting zero is not approval to emit zero from an adapter. |
| `applicableBackends` | Treat as UI/filter metadata unless stronger source appears. | `SOURCE_CONFIRMED_CURRENT_SCOPE` | `config/glyph/common/src/display/GlyphConfigMenu.cpp`, `src/core/mode_selection.cpp`, `docs/calibration/glyph_profile_config_semantics_gap_map_2026-05-26.md` issue 13 | Do not encode it as a hard runtime eligibility gate in adapter policy yet. |
| JSON fixtures | Treat as examples and corpus candidates, not canonical wire format. | `POLICY_DECIDED` | `docs/sources/raw/GlyphUserProfiles.json`, `docs/calibration/fixtures/*.json`, `HAL/pico/src/comms/ConfiguratorBackend.cpp` | The source-confirmed device path is protobuf transport/storage, not JSON storage. |

## Unresolved Policy Gates

- Choose outbound disabled-remap encoding only after source/corpus/user policy proves the desired representation.
- Decide whether any adapter may emit `defaultModeConfig = 0`; current firmware-side validation acceptance is not sufficient policy.
- Capture or inspect authoritative configurator/proto source before claiming JSON round-trip behavior.
- Build a corpus-backed fixture set before enabling any write-capable adapter output.
- Keep `applicableBackends` as metadata until source proves stronger runtime enforcement.

## Non-Goals

- No write-capable adapter implementation.
- No firmware runtime behavior changes.
- No SOCD or remap semantic changes.
- No profile schema/proto/configurator behavior changes.
- No flashing or push-to-device automation.
- No macro, turbo, toggle, one-shot, or timing automation.
- No Smash or game-semantic claims.
