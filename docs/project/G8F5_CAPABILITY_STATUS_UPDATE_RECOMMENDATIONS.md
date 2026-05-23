# G8f5 - Capability Status Update Recommendations

Status: docs-only recommendation artifact
Date: 2026-05-23

## Scope

This document is docs-only and recommendation-only.

These are evaluator/capability-model recommendations, not firmware behavior changes.

The recommendations are based on:
- `docs/project/G8F2_EXACT_RAW_LEFT_STICK_SOURCE_AUDIT.md`
- `docs/project/G8F3_MODE_SPECIFIC_VS_GENERIC_CAPABILITY_AUDIT.md`
- `docs/project/G8F4_OUTPUT_REPORT_PATH_AUDIT.md`

## Recommended Statuses

| capability | recommended status | scope | source refs | caveats | evidence needed to upgrade |
| --- | --- | --- | --- | --- | --- |
| 1. generic exact raw left-stick output support | `INFERRED` | `GENERIC_BACKEND` | `include/core/state.hpp:143-154`, `src/core/ControllerMode.cpp:8-15`, `src/core/ControllerMode.cpp:30-70`, `HAL/pico/src/comms/GamecubeBackend.cpp:59-65` | Byte fields and GC forwarding exist, but arbitrary target realization is selected-mode dependent and not proven generically | A generic source path representing desired x/y targets, deterministic realization rules, limits, and failure modes outside one selected mode |
| 2. mode-specific exact left-stick assignment support | `SOURCE_BACKED` | `MODE_SPECIFIC` | `src/modes/Ultimate.cpp:61-265`, `src/modes/Melee20Button.cpp:79-125`, `src/modes/RivalsOfAether.cpp:69-115`, `src/modes/FgcMode.cpp:49-67`, `src/modes/64.cpp:52-70` | Source-backed only for specific selected modes and their own formulas | Per-mode exhaustive audit if evaluator needs exact coverage tables |
| 3. SenscopePrototype selected-path exact raw table support | `SOURCE_BACKED` | `SELECTED_PROTOTYPE_ONLY` | `src/modes/SenscopePrototype.cpp:94-130`, `src/modes/SenscopePrototype.cpp:156-190`, `include/prototypes/senscope/SenscopePrototypeTypes.hpp:23-32`, `src/prototypes/senscope/SenscopePrototypeResolver.cpp:187-204` | Prototype path is not generic and active manual selection is disabled by `src/core/mode_selection.cpp:35` and `src/core/mode_selection.cpp:170-174` | Explicit approval and source change making the path intentionally reachable, plus review of its profile authority |
| 4. full 9-way generic directional modifier table | `UNSUPPORTED_BY_CURRENT_SOURCE` | `GENERIC_BACKEND` | `src/modes/Ultimate.cpp:61-265`, `src/modes/CustomControllerMode.cpp:64-113`, `include/prototypes/senscope/SenscopePrototypeTypes.hpp:90-100` | Prototype has a 9-entry table type, but this is prototype-scoped and not generic backend capability | Generic active source representation and runtime path for all 9 directions with arbitrary x/y entries |
| 5. neutral direction 5 support | `SOURCE_BACKED` for prototype table concept; `UNSUPPORTED_BY_CURRENT_SOURCE` for generic backend first-class support | `SELECTED_PROTOTYPE_ONLY` / `GENERIC_BACKEND` | `include/prototypes/senscope/SenscopePrototypeTypes.hpp:10-32`, `src/prototypes/senscope/SenscopePrototypeResolver.cpp:187-204`, `src/core/ControllerMode.cpp:46-49` | Generic modes center neutral by default but do not expose first-class direction-5 table semantics | Generic backend rule or data model where neutral direction 5 is first-class and source-backed |
| 6. non-center neutral support | `UNKNOWN` | `GENERIC_BACKEND` | `src/core/ControllerMode.cpp:46-49`, `src/modes/Ultimate.cpp:61-265`, `src/modes/CustomControllerMode.cpp:64-113` | Current active helper centers neutral at 128; prototype data structures could hold coordinates, but generic/runtime authority is not proven | Source-backed active path allowing neutral-intent x/y values other than center under reviewed constraints |
| 7. export support | `UNSUPPORTED_BY_CURRENT_SOURCE` | `OUT_OF_SCOPE` for this firmware audit | `HAL/pico/src/comms/ConfiguratorBackend.cpp:44-226`, `HAL/pico/src/core/Persistence.cpp:24-143` | Config get/set exists, but no approved vendor export artifact workflow is shown | Explicit source-backed export format/workflow and approval to model it |
| 8. push-to-device support | `UNSUPPORTED_BY_CURRENT_SOURCE` | `OUT_OF_SCOPE` for this firmware audit | `HAL/pico/src/comms/ConfiguratorBackend.cpp:44-226`, `HAL/pico/src/core/Persistence.cpp:24-143` | Device-side set/persist command exists, but no approved host push workflow is established here | Explicit end-to-end host/device workflow, constraints, safety rules, and approval |
| 9. same-effective dataset dependency | `SOURCE_BACKED` as evaluator boundary rule | `OUT_OF_SCOPE` for firmware semantics | `docs/project/G8G_REALIZATION_EVALUATOR_DECISION_MATRIX.md`, `docs/project/G8F_CAPABILITY_KNOWN_UNKNOWNS_AND_AUDIT_BACKLOG.md` | Same-effective requires Senscope-supplied dataset proof; firmware source does not define gameplay equivalence | Senscope-side dataset contract and traceable provenance |

## Evaluator Guidance

- Use `SOURCE_BACKED` only when source refs and scope match.
- Use `INFERRED` for generic exact raw left-stick support until generic realization evidence exists.
- Use `UNKNOWN` when representability may exist but source evidence is incomplete.
- Use `UNSUPPORTED_BY_CURRENT_SOURCE` when the inspected source lacks the capability as stated.
- Use `OUT_OF_SCOPE` for gameplay equivalence, export product decisions, host push workflows, and schema ownership questions.

Recommended diagnostics:

- `MODE_SCOPE_MISMATCH` when selected-mode evidence is used for a generic requirement.
- `REPRESENTABILITY_UNKNOWN` when byte fields or transport pass-through exist but arbitrary target realization is not proven.
- `SOURCE_BACKED` only after source refs, scope, and caveats are preserved.

## Conservative Recommendation

Do not upgrade the generic exact raw left-stick capability to `SOURCE_BACKED` from this audit. Upgrade only the narrower claims:

- mode-specific byte-coordinate assignment is `SOURCE_BACKED`;
- SenscopePrototype selected example-table coordinate assignment is `SOURCE_BACKED` but `SELECTED_PROTOTYPE_ONLY`;
- GC transport forwarding of selected mode left-stick bytes is `SOURCE_BACKED` but `TRANSPORT_SPECIFIC`.
