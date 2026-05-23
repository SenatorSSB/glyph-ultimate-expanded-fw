# G8f7 - Transport Status Recommendations

Status: docs-only recommendation artifact
Date: 2026-05-24

## Scope

This document is docs-only and recommendation-only. It recommends transport/capability-model statuses based on source-audit evidence. It does not recommend firmware changes, runtime adapter implementation, export/push/upload/flashing workflows, hardware flashing, Senscope neutral profile schema changes, or game interpretation changes.

Statuses used:
- `SOURCE_BACKED`
- `INFERRED`
- `UNKNOWN`
- `UNSUPPORTED_BY_CURRENT_SOURCE`
- `OUT_OF_SCOPE`

## Recommended Statuses

| capability | recommended status | scope | source refs | caveats | evidence needed to upgrade |
| --- | --- | --- | --- | --- | --- |
| 1. GameCube transport carrying selected-mode left-stick bytes | `SOURCE_BACKED` | `TRANSPORT_SPECIFIC` | `HAL/pico/src/comms/GamecubeBackend.cpp:59-61`, `include/core/state.hpp:143-150` | Proves byte carrying from `OutputState` into GC report fields only; does not prove selected-mode arbitrary target production | Source-backed selected-mode realization rules for requested coordinates if exact realization status is needed |
| 2. GameCube transport carrying selected-mode C-stick bytes | `SOURCE_BACKED` | `TRANSPORT_SPECIFIC` | `HAL/pico/src/comms/GamecubeBackend.cpp:62-63`, `include/core/state.hpp:143-152` | Proves byte carrying from `OutputState` into GC C-stick fields only; does not enable or change right-stick/C-stick behavior | Source-backed selected-mode C-stick target production rules and explicit approval if this becomes a target |
| 3. GameCube transport carrying trigger bytes | `SOURCE_BACKED` | `TRANSPORT_SPECIFIC` | `HAL/pico/src/comms/GamecubeBackend.cpp:51-52`, `HAL/pico/src/comms/GamecubeBackend.cpp:64-65`, `include/core/state.hpp:118-119`, `include/core/state.hpp:143-154` | Digital trigger outputs map separately from analog trigger byte fields; source supports transport carrying/mapping only | Source-backed selected-mode trigger production rules if trigger realization is evaluated |
| 4. Nintendo Switch transport preserving GC raw coordinates | `UNSUPPORTED_BY_CURRENT_SOURCE` | `TRANSPORT_SPECIFIC` | `HAL/pico/src/comms/NintendoSwitchBackend.cpp:142-146` | Source shows scaling around 128 and y-axis inversion, not GC raw pass-through | A separate source-backed mapping dataset and evaluator rule for Switch report coordinates, not a GC-preservation upgrade |
| 5. DInput transport preserving GC raw coordinates | `UNSUPPORTED_BY_CURRENT_SOURCE` | `TRANSPORT_SPECIFIC` | `HAL/pico/src/comms/DInputBackend.cpp:52-58`, `lib/TUCompositeHID/src/TUGamepad.cpp:131-153` | Source shows y inversion, trigger offset, and expansion into local HID report fields | A separate source-backed DInput mapping dataset and evaluator rule, not a GC-preservation upgrade |
| 6. XInput transport preserving GC raw coordinates | `UNSUPPORTED_BY_CURRENT_SOURCE` | `TRANSPORT_SPECIFIC` | `HAL/pico/src/comms/XInputBackend.cpp:55-70` | Source shows stick scaling into XInput fields and digital trigger override behavior | A separate source-backed XInput mapping dataset and evaluator rule, not a GC-preservation upgrade |
| 7. transport-layer arbitrary coordinate realization | `UNSUPPORTED_BY_CURRENT_SOURCE` | `GENERIC_BACKEND` / `TRANSPORT_LAYER` | `src/core/CommunicationBackend.cpp:49-54`, `src/core/ControllerMode.cpp:8-15`, `HAL/pico/src/comms/GamecubeBackend.cpp:59-65`, `HAL/pico/src/comms/NintendoSwitchBackend.cpp:142-146`, `HAL/pico/src/comms/DInputBackend.cpp:52-58`, `HAL/pico/src/comms/XInputBackend.cpp:67-70` | Transports serialize, transform, or reduce selected-mode outputs; they do not accept target coordinate requests | A generic or selected-mode source path representing target coordinates, deterministic production rules, limits, and failure modes |
| 8. Senscope GC-adapter backend transport target | `SOURCE_BACKED` for narrow transport byte carrying; `UNKNOWN` for end-to-end exact realization | `TRANSPORT_SPECIFIC` plus future evaluator scope | `HAL/pico/src/comms/GamecubeBackend.cpp:59-65`, `docs/project/G8F4_OUTPUT_REPORT_PATH_AUDIT.md`, `docs/project/G8F7_GAMECUBE_REPORT_PATH_CAPABILITY_AUDIT.md` | GC transport is the best current transport target because it carries selected-mode bytes directly in inspected source; selected-mode arbitrary target production remains separate | Reviewed selected-mode realization design and explicit approval for implementation or evaluator package decisions |

## Guidance

- Use `SOURCE_BACKED` when the source refs and scope are exact.
- Use `UNSUPPORTED_BY_CURRENT_SOURCE` for non-GC transports preserving GC raw coordinates because inspected source shows transformations or reductions.
- Use `UNKNOWN` for end-to-end Senscope exact realization until selected-mode production and evaluator behavior are source-backed.
- Use `OUT_OF_SCOPE` for export product decisions, push-to-device workflows, hardware flashing, and game semantic interpretation.
- Keep transport/capability recommendations scoped to modeling and diagnostics, not firmware changes.

## Conservative Recommendation

For GC-adapter-first capability modeling, upgrade only the narrow transport claims:

- GC transport carrying selected-mode left-stick bytes: `SOURCE_BACKED`.
- GC transport carrying selected-mode C-stick bytes: `SOURCE_BACKED`.
- GC transport carrying selected-mode analog trigger bytes: `SOURCE_BACKED`.

Do not upgrade these from this audit:

- selected-mode exact target realization;
- generic backend arbitrary coordinate realization;
- non-GC transports preserving GC raw coordinates;
- export/push/upload/flashing workflows;
- game semantic equivalence.
