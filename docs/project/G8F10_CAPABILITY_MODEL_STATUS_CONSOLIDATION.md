# G8f10 - Capability Model Status Consolidation

Status: docs-only recommendation artifact
Date: 2026-05-24

## Scope

This document is docs-only and recommendation-only. It consolidates source-backed audit outcomes for future evaluator/capability-model work. It does not implement firmware behavior, app-side TypeScript, export/push workflows, hardware flashing, schema changes, or gameplay semantic claims.

Inputs consolidated:

- `docs/project/G8F2_EXACT_RAW_LEFT_STICK_SOURCE_AUDIT.md`
- `docs/project/G8F3_MODE_SPECIFIC_VS_GENERIC_CAPABILITY_AUDIT.md`
- `docs/project/G8F4_OUTPUT_REPORT_PATH_AUDIT.md`
- `docs/project/G8F5_CAPABILITY_STATUS_UPDATE_RECOMMENDATIONS.md`
- `docs/project/G8F6_CUSTOM_CONTROLLER_AUDIT_ROLLUP.md`
- `docs/project/G8F7_TRANSPORT_AUDIT_ROLLUP.md`
- `docs/project/G8F8_CONFIGURATOR_BACKEND_SOURCE_AUDIT.md`
- `docs/project/G8F8_PERSISTENCE_AND_CONFIG_STORAGE_AUDIT.md`
- `docs/project/G8F8_EXPORT_PUSH_BOUNDARY_ASSESSMENT.md`
- `docs/project/G8F9_EXTERNAL_GC_REPORT_LIBRARY_AUDIT.md`

## Consolidated Capability Table

| capability | status | scope | source refs | caveats | evaluator behavior |
| --- | --- | --- | --- | --- | --- |
| 1. OutputState byte-shaped left-stick fields | `SOURCE_BACKED` | `GENERIC_OUTPUT_STATE` | `include/core/state.hpp:143-154`, G8f2 | Field shape exists; field existence does not prove target realization | May model output byte fields as evidence only |
| 2. selected-mode byte assignment | `SOURCE_BACKED` | `MODE_SPECIFIC` | `src/core/ControllerMode.cpp:8-15`, `src/modes/Ultimate.cpp:61-265`, `src/modes/CustomControllerMode.cpp:64-113`, G8f2/G8f3 | Each mode has its own rules; do not promote to generic backend support | Require mode scope match; otherwise fail closed with scope diagnostic |
| 3. SenscopePrototype selected exact table path | `SOURCE_BACKED` | `SELECTED_PROTOTYPE_ONLY` | `src/modes/SenscopePrototype.cpp:94-130`, `src/modes/SenscopePrototype.cpp:156-190`, `src/core/mode_selection.cpp:35,170-174`, G8f2/G8f5 | Manual selection gate is disabled; prototype is not generic or default reachable | Can cite as likely implementation lineage, not active support |
| 4. CustomControllerMode scalar/range representability | `SOURCE_BACKED` for scalar/range primitives | `MODE_SPECIFIC_CONFIG_DRIVEN` | `src/modes/CustomControllerMode.cpp:64-113`, G8f6 | Needs separate evaluator math for limited profiles; unusual numeric edge behavior remains untested | May model limited representability only with exact source formulas and conservative diagnostics |
| 5. CustomControllerMode arbitrary raw pair representability | `UNSUPPORTED_BY_CURRENT_SOURCE` | `MODE_SPECIFIC` | G8f6, `src/modes/CustomControllerMode.cpp:64-113`, `.pio/libdeps/glyph_mk6/HayBox-proto/config.proto:440-467` | No first-class arbitrary x/y table for every direction/modifier pair | Return unsupported for arbitrary exact raw neutral profile target |
| 6. GameCube transport byte carrying | `SOURCE_BACKED` | `TRANSPORT_SPECIFIC_GC` | `HAL/pico/src/comms/GamecubeBackend.cpp:59-69`, `.pio/libdeps/glyph_mk6/joybus-pio/include/gamecube_definitions.h:14-38`, `.pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp:127-134`, G8f7/G8f9 | Transport carries selected-mode bytes; selected mode must still produce them | May mark GC byte carrying as source-backed once selected output exists |
| 7. non-GC transport GC-equivalence | `UNSUPPORTED_BY_CURRENT_SOURCE` | `TRANSPORT_SPECIFIC_NON_GC` | G8f4/G8f7; Nintendo Switch/DInput/XInput/N64/NES/SNES backend audits | Non-GC transports transform, scale, invert, or reduce values | Do not treat non-GC as GC-equivalent; require separate output IDs |
| 8. config get/set device-side support | `SOURCE_BACKED` | `DEVICE_SIDE_CONFIG_TRANSPORT` | `HAL/pico/src/comms/ConfiguratorBackend.cpp:148-272`, G8f8 Configurator audit | Device-side only; not host UX/export approval | May cite as device capability, not as approved workflow |
| 9. persistence support | `SOURCE_BACKED` | `DEVICE_SIDE_STORAGE` | `HAL/pico/src/core/Persistence.cpp:36-180`, `HAL/pico/include/core/Persistence.hpp:24-42`, G8f8 Persistence audit | Cross-update preservation remains unknown without updater/hardware evidence | May cite saved config support; preserve update unknown |
| 10. host export format | `UNKNOWN` or `UNSUPPORTED_BY_CURRENT_SOURCE` | `HOST_WORKFLOW` | G8f8 Export/Push boundary | No approved host export artifact source in this repo batch | Return export unsupported/out-of-scope |
| 11. push-to-device workflow | `UNSUPPORTED_BY_CURRENT_SOURCE` as approved workflow | `HOST_DEVICE_WORKFLOW` | G8f8 Export/Push boundary | Device set command exists, but end-to-end host workflow is absent/unapproved | Return push unsupported/out-of-scope |
| 12. bootloader/update path | `SOURCE_BACKED` for reboot command dispatch; `UNSUPPORTED_BY_CURRENT_SOURCE` for approved update workflow | `DEVICE_REBOOT_COMMAND` / `FLASH_WORKFLOW` | `HAL/pico/src/comms/ConfiguratorBackend.cpp:69-73`, G8f8 Configurator audit | Reboot helper calls do not prove flashing/update workflow | Stop before firmware update/flashing |
| 13. same-effective dependency | `SOURCE_BACKED` as evaluator boundary requirement; `OUT_OF_SCOPE` for firmware | `SENSCOPE_DATASET_DEPENDENCY` | G8f5, `docs/project/G8J_GLYPH_TO_SENSCOPE_HANDOFF_PACKET.md` | Requires Senscope-supplied equivalence dataset; firmware source does not define it | Fail closed unless dataset evidence is injected |
| 14. gameplay semantic authority | `OUT_OF_SCOPE` | `GAME_SEMANTICS` | `AGENTS.md`, G3, G8j | No SSBU labels, thresholds, or semantic maps may be invented here | Do not evaluate or add gameplay semantic claims |

## Final Capability-Model Recommendation

GC transport byte-carrying is source-backed for selected-mode byte outputs. The strongest source chain is:

```text
selected mode writes OutputState.leftStickX/Y
  -> GamecubeBackend copies bytes to gc_report_t.stick_x/stick_y
  -> local joybus-pio sends sizeof(gc_report_t) bytes
```

Exact arbitrary profile realization should not be modeled as generic backend support. Existing source proves selected-mode behavior, not a generic target-coordinate resolver.

CustomControllerMode is not suitable as the generic exact arbitrary raw neutral profile target. Its source-backed range/scalar primitives may support a limited evaluator later, but arbitrary pair-table support is unsupported by current source.

A selected custom `SenscopePrototype`-style mode is the likely exact-realization path if firmware implementation is explicitly approved. The current prototype lineage already shows selected exact table lookup and byte output assignment, but current reachability remains disabled and no runtime implementation approval is implied.

The app-side evaluator should remain fail-closed:

- source-backed only when status, scope, and source refs match;
- unsupported for arbitrary exact raw pair realization through CustomControllerMode;
- unknown for profile preservation across update flows;
- out-of-scope for export/push/flashing and gameplay semantics unless separately approved.

## Conclusion

The source-backed transport story is now strong enough for GC byte-carrying once selected-mode outputs exist. The source-backed realization story is not generic. Implementation planning should either proceed app-side with fail-closed evaluator logic, or ask explicit approval for a Glyph-side selected custom exact-table mode lineage.
