# Source-Owned Table Symbol Map

Status label: DOCS / TOOLS ONLY.

This note records the current source-owned table alias/replacement boundary
for Alternative B. It is documentation and checker material only. It does not
change active firmware behavior, active publication, or the runtime-config
implementation boundary.

## Current Source-Owned Map

| Boundary | File | Symbols | Role |
| --- | --- | --- | --- |
| Active publication | `src/modes/Ultimate.cpp` | `GetActiveRuntimeConfigState()`, `ResolveActiveRuntimeConfig()` | Publishes the stable active pointer and dereferences `active_view`. |
| Baseline alias | `src/modes/UltimateRuntimeConfigInterpreter.hpp` | `kSourceOwnedCurrentBaselineRuntimeTables`, `kKnownGoodRuntimeConfig`, `kSourceOwnedCurrentBaselineRuntimeConfig` | Defines the current source-owned baseline table array and its alias. |
| Table content source | `src/modes/UltimateIdentityRuntimeTables.hpp` -> `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigBaseline.current.hpp` | `kDefaultTable` through `kLt1LowMagnitudeTable` | Holds the active source-owned compile-time table contents consumed by the baseline alias. |

The current active pointer still comes from
`&kSourceOwnedCurrentBaselineRuntimeConfig`, and
`ResolveActiveRuntimeConfig()` still dereferences
`GetActiveRuntimeConfigState().active_view`.
`src/modes/UltimateIdentityRuntimeTables.hpp` includes the generated
source-owned baseline header as active compile-time table content while
keeping the active publication symbols unchanged.

The Alternative B generated-table alias candidate at
`ee5fd35c4ce00e31d9a00905c771699ad17517b9` is hardware-passed only in this
source-owned alias shape while preserving the existing active publication path.

## Alternative B Touchpoints

Alternative B remains the source-owned table-content replacement or aliasing
path. The hardware-passed generated-table alias candidate touched:

- `src/modes/UltimateIdentityRuntimeTables.hpp` for compile-time table content
  replacement or generated aliasing.
- `src/modes/UltimateRuntimeConfigInterpreter.hpp` to keep
  `kSourceOwnedCurrentBaselineRuntimeTables`, `kKnownGoodRuntimeConfig`, and
  `kSourceOwnedCurrentBaselineRuntimeConfig` stable.
- `src/modes/Ultimate.cpp` only to confirm the active pointer publication path
  stays on the stable source-owned baseline view.

## Inert Generated-Source-Owned Artifacts

The source-inspection lane tracks these inert artifacts (the active baseline
header is intentionally excluded):

- `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigArtifact.example.hpp`
- `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigExample.hpp`
- `src/modes/runtime_config/generated_source_owned/GeneratedRuntimeConfigSchema.hpp`
- `docs/runtime_config/fixtures/generated_outputs/generated_source_owned_runtime_config.example.hpp`
- `docs/runtime_config/fixtures/generated_source_owned_realization_design.json`
- `docs/runtime_config/fixtures/generated_source_owned_schema_scaffold.json`
- `docs/runtime_config/fixtures/generated_source_owned_generator_contract.json`
- `docs/runtime_config/fixtures/generated_source_owned_layout_spec.json`
- `docs/runtime_config/fixtures/generated_source_owned_layout_spec.example.json`
- `docs/runtime_config/fixtures/generated_source_owned_generator_input.example.json`
- `docs/runtime_config/fixtures/generated_source_owned_artifact_install.json`
- `docs/runtime_config/fixtures/generated_source_owned_baseline_artifact.json`

These files are inert evidence or offline generator fixtures. The baseline
header above is active table content, but it is not the active publication
mechanism. None of these paths introduce runtime-loaded config,
persistent storage, WebSerial/device write, backend/config.pb write paths, or
flashing automation.

## Checker Contract

The repo checker
`tools/check_glyph_source_owned_table_symbol_map.py` reports the exact source
symbol locations, active table-source path, inert artifact paths, and Alternative B touchpoints listed
above. It also fails if the checked docs drift into positive claims about
runtime-loaded config, storage, device write, flashing automation, candidate
publication, or active-storage publication.

## Non-Claims

- This note does not change active firmware behavior.
- This note does not implement runtime-loaded config.
- This note does not implement persistent storage.
- This note does not implement WebSerial/device write.
- This note does not implement backend/config.pb write paths.
- This note does not implement firmware flashing automation.
- This note does not approve `candidate.view` active publication.
- This note does not approve `active_storage.view` active publication.
- This note does not approve `RuntimeConfigView` replacement as the
  customization mechanism.
