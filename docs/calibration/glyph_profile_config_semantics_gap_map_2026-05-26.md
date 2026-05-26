# Glyph Profile/Config Semantics Gap Map - 2026-05-26

## Issue 01 - Proto schema authority is external to tracked repo source

- Classification: `REQUIRES_EXTERNAL_CONFIGURATOR_SOURCE`
- Description: `Config`/`GameModeConfig`/`ButtonRemap` schema authority is dependency-provided and not tracked as first-party source.
- Evidence: nanopb proto path points at `.pio/libdeps/.../config.proto` and Glyph env pins dependency commit; no tracked `config.proto` found.
- Source files: `platformio.ini:18-24`, `config/glyph/env.ini:13-18`, `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto`
- Adapter implication: adapter contracts cannot be treated as stable from this repo alone.
- Recommended next action: capture and version-lock authoritative configurator/proto source snapshot for adapter work.
- Stop condition: stop before write-capable adapter implementation that claims schema certainty.

## Issue 02 - Generated protobuf code is local build artifact, not source contract

- Classification: `UNSAFE_TO_ASSUME`
- Description: `config.pb.h/.c` used by firmware are generated under `.pio/build/...` and not repo-tracked.
- Evidence: generated files exist locally only.
- Source files: `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.h`, `.pio/build/glyph_mk6/nanopb/generated-src/config.pb.c`
- Adapter implication: field layout/presence assumptions can drift with dependency/toolchain updates.
- Recommended next action: treat generated files as diagnostics only; derive contract from locked proto source.
- Stop condition: stop if adapter design depends on generated artifact details not tied to pinned external source.

## Issue 03 - Device persistence format is binary protobuf with header+CRC

- Classification: `SOURCE_CONFIRMED`
- Description: firmware persists config as raw protobuf bytes in `config.bin` with `config_size` and `config_crc` header.
- Evidence: persistence write/read implementation.
- Source files: `HAL/pico/include/core/Persistence.hpp:26-43`, `HAL/pico/src/core/Persistence.cpp:36-77`, `:154-178`
- Adapter implication: JSON fixtures are not device storage format authority.
- Recommended next action: keep adapter logic explicitly split between protobuf transport/storage and JSON fixture parsing.
- Stop condition: stop if work starts treating JSON fixture layout as firmware storage contract.

## Issue 04 - Configurator transport is command+COBS+protobuf; JSON behavior is unknown

- Classification: `REQUIRES_EXTERNAL_CONFIGURATOR_SOURCE`
- Description: firmware transport implements protobuf commands for get/set config and reboot; browser JSON import/export behavior is not defined in inspected firmware source.
- Evidence: command switch, pb encode/decode, raw config streaming.
- Source files: `HAL/pico/src/comms/ConfiguratorBackend.cpp:58-79`, `:127-167`, `:148-159`, `HAL/pico/include/comms/ConfiguratorBackend.hpp:21-23`
- Adapter implication: host-side JSON rules must not be inferred from device command handlers alone.
- Recommended next action: inspect/capture configurator host source and sample exports from matched version.
- Stop condition: stop before claiming JSON round-trip guarantees.

## Issue 05 - Remap runtime supports many-to-one and suppresses duplicate physical remaps

- Classification: `SOURCE_CONFIRMED`
- Description: remap is many-to-one capable and ignores later remaps from the same physical button.
- Evidence: physical button dedupe mask and OR-on-target behavior.
- Source files: `src/core/InputMode.cpp:63-81`
- Adapter implication: fixture/model validation must preserve these semantics when comparing expected runtime behavior.
- Recommended next action: retain many-to-one and first-physical-entry precedence checks in fixture checker outputs.
- Stop condition: stop if adapter transformation would reorder or collapse remaps in a way that changes precedence.

## Issue 06 - Explicit `BTN_UNSPECIFIED` is a runtime no-op target

- Classification: `SOURCE_CONFIRMED`
- Description: set/get button helpers return immediately for `BTN_UNSPECIFIED`.
- Evidence: utility helpers short-circuit on `BTN_UNSPECIFIED`.
- Source files: `HAL/pico/include/util/state_util.hpp:10-24`
- Adapter implication: explicit disabled target behavior is source-backed and distinct from absent JSON fields.
- Recommended next action: keep explicit `BTN_UNSPECIFIED` modeled as explicit disabled mapping.
- Stop condition: stop if implementation attempts to erase explicit unspecified entries as redundant.

## Issue 07 - Fixtures encode disabled/unmapped remaps mostly as omitted `activates`

- Classification: `FIXTURE_OBSERVED_ONLY`
- Description: inspected JSON fixtures have many omitted `activates` entries and zero explicit `"BTN_UNSPECIFIED"` remap targets.
- Evidence: read-only checker output across four fixture files.
- Source files: `docs/sources/raw/GlyphUserProfiles.json`, `docs/calibration/fixtures/*.json`, `tools/check_glyph_profile_config_semantics.py`
- Adapter implication: omission style is observed but not proven as canonical configurator contract.
- Recommended next action: preserve omission in fixture-path tooling; avoid normalization to explicit strings without authority.
- Stop condition: stop before policy decisions that collapse omission into explicit disable.

## Issue 08 - Omitted `activates` vs explicit `BTN_UNSPECIFIED` equivalence is unproven

- Classification: `UNSAFE_TO_ASSUME`
- Description: runtime explicit disable semantics are known, fixture omission semantics are observed, equivalence between them is not source-proven.
- Evidence: firmware uses explicit enum values; fixtures omit key; no host serializer source inspected here.
- Source files: `HAL/pico/include/util/state_util.hpp:10-24`, `config/glyph/common/include/glyph_overrides.hpp`, `docs/sources/raw/GlyphUserProfiles.json`
- Adapter implication: conflating them may create incorrect writes or lossy round trips.
- Recommended next action: require external configurator/proto source and export corpus to define canonical mapping.
- Stop condition: stop before write-capable adapter encodes omitted/explicit disabled interchangeably.

## Issue 09 - Parser helper preserves omission but does not validate backend/default index references

- Classification: `SOURCE_CONFIRMED`
- Description: parser keeps missing `activates` as `None` but does not parse/validate top-level backend default index semantics.
- Evidence: parser models remaps/socd/layout/applicableBackends only.
- Source files: `tools/glyph_config_model.py:13-33`, `:121-147`, `:186-202`
- Adapter implication: parser is useful for read-only inspection but insufficient as write preflight validator.
- Recommended next action: keep using dedicated semantics checker for structural/index checks.
- Stop condition: stop if write path relies on parser helper alone as safety gate.

## Issue 10 - Default mode/backend index handling is one-based in runtime code

- Classification: `SOURCE_CONFIRMED`
- Description: runtime converts config IDs to array offsets with `-1` and helper IDs are `i + 1`.
- Evidence: backend init and helper functions.
- Source files: `HAL/pico/src/comms/backend_init.cpp:138-143`, `:292-296`, `src/core/config_utils.cpp:59`, `:74`
- Adapter implication: zero-based assumptions would select wrong profiles.
- Recommended next action: enforce one-based index checks in pre-write validation.
- Stop condition: stop if adapter serialization chooses zero-based default indices.

## Issue 11 - `defaultModeConfig` is omitted for configurator backend in fixtures

- Classification: `FIXTURE_OBSERVED_ONLY`
- Description: all inspected fixtures omit `defaultModeConfig` for `COMMS_BACKEND_CONFIGURATOR`.
- Evidence: fixture checker output and direct fixture inspection.
- Source files: `docs/sources/raw/GlyphUserProfiles.json`, `docs/calibration/fixtures/*.json`, `tools/check_glyph_profile_config_semantics.py`
- Adapter implication: omission may be expected for configurator backend, but this is fixture-observed only.
- Recommended next action: verify against external configurator source/export corpus before enforcing as rule.
- Stop condition: stop before hard-coding omission/presence requirements for this field.

## Issue 12 - Profile count exceeds static mode activation mask capacity

- Classification: `UNSAFE_TO_ASSUME`
- Description: default Glyph config declares 13 game modes while mode activation masks are stored in fixed array of 10.
- Evidence: count in default config vs static array size and loop bound.
- Source files: `config/glyph/common/include/glyph_overrides.hpp:17`, `src/core/mode_selection.cpp:30`, `:187-193`
- Adapter implication: assumptions about unlimited mode-count handling are unsafe.
- Recommended next action: keep warning in checker and require runtime-side confirmation before adapter writes that increase/reshape mode sets.
- Stop condition: stop if adapter workflow would rely on mode activation behavior beyond confirmed safe capacity.

## Issue 13 - `applicable_backends` is used for UI filtering, not proven as hard runtime enforcement

- Classification: `SOURCE_CONFIRMED`
- Description: display menu filters profiles by `applicable_backends`; mode-setting switch path does not visibly enforce this list.
- Evidence: menu filter code and runtime mode switch path.
- Source files: `config/glyph/common/src/display/GlyphConfigMenu.cpp:32-47`, `src/core/mode_selection.cpp:90-147`
- Adapter implication: treating `applicable_backends` as strict runtime gate may be incorrect.
- Recommended next action: model as UI metadata unless external source proves stronger enforcement.
- Stop condition: stop before encoding hard backend eligibility constraints into adapter logic.

## Issue 14 - Write-time policy for omitted vs explicit disabled remaps is a domain decision

- Classification: `REQUIRES_USER_POLICY_DECISION`
- Description: repository evidence supports both explicit disable values (firmware defaults) and omission style (fixtures) but not a single required outbound style.
- Evidence: explicit defaults in source vs omitted fixture fields.
- Source files: `config/glyph/common/include/glyph_overrides.hpp`, `docs/sources/raw/GlyphUserProfiles.json`
- Adapter implication: adapter output policy must be explicitly chosen, not inferred.
- Recommended next action: obtain user/domain sign-off on outbound encoding policy before writes.
- Stop condition: stop before implementing adapter writes without agreed policy.

## Issue 15 - Captured export corpus is required for safe write/round-trip validation

- Classification: `REQUIRES_CAPTURED_EXPORT_CORPUS`
- Description: current fixture set is useful but not sufficient to prove canonical serializer behavior across omitted/default/enum-zero cases.
- Evidence: fixture variance and lack of inspected host serializer source.
- Source files: `docs/sources/raw/GlyphUserProfiles.json`, `docs/calibration/fixtures/*.json`
- Adapter implication: write path may regress import/export fidelity without corpus-backed tests.
- Recommended next action: capture multi-version export corpus from target configurator source revision and add round-trip assertions.
- Stop condition: stop before write-capable adapter rollout without corpus-backed regression checks.

## Issue 16 - Flash/push/export workflow decisions remain out of scope for this batch

- Classification: `OUT_OF_SCOPE`
- Description: this task is source-tracing/docs/check-script only and does not approve flashing, vendor export format claims, or push automation.
- Evidence: task constraints and repo operating contract.
- Source files: `AGENTS.md:49-60`, `AGENTS.md:163-177`
- Adapter implication: keep current batch read-only and preparatory.
- Recommended next action: defer operational workflow work to separate approved scope.
- Stop condition: stop immediately if task expands into flashing/push/export implementation claims.
