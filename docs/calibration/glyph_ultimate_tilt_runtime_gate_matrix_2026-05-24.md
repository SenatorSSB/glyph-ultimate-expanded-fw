# Glyph Ultimate Tilt Runtime Gate Matrix (2026-05-24)

## Purpose

This matrix turns the prior Glyph/HayBox source traces into decision gates for a later custom Ultimate `TILT` / `Tilt2` firmware test branch.

This document is a design-gate packet only. It does not implement runtime firmware behavior, add modifiers, choose final Tilt1/Tilt2 values, add flashing, or change device behavior.

## Gate Matrix

| Gate | Current status | Source evidence | Remaining question | Required owner decision or source proof | Blocks runtime firmware patch? |
| --- | --- | --- | --- | --- | --- |
| Proto/source authority | PARTIAL | `platformio.ini` points nanopb proto generation at `.pio/libdeps/${PIOENV}/HayBox-proto/config.proto`; `config/glyph/env.ini` overrides Glyph env dependency to `https://github.com/GregTurbo/HayBox-proto#db4e2f6`; local cache observed in `docs/calibration/glyph_proto_source_authority_2026-05-24.md`. | Which tracked source or pinned dependency record is the reviewed authority for runtime/schema-sensitive work? | Approve exact proto source authority and full commit SHA, or add a reviewed source-authority record before schema-dependent runtime changes. | Yes, for schema/profile-dependent changes. |
| Native Ultimate implementation path | PARTIAL | `src/core/mode_selection.cpp` selects `ultimate_mode` for `MODE_ULTIMATE`; `src/modes/Ultimate.cpp::UpdateAnalogOutputs` contains hard-coded Ultimate analog values and comments such as Horizontal Tilts and MY Vertical Tilts; traced in `docs/calibration/glyph_modifier_value_trace_2026-05-24.md`. | Should custom Ultimate `TILT` / `Tilt2` be patched into native hard-coded Ultimate behavior? | User approval of native-mode patch scope, exact button/chord behavior, and value source. | Yes, if native Ultimate is chosen. |
| Custom mode implementation path | PARTIAL | `src/core/mode_selection.cpp` selects `CustomControllerMode` for `MODE_CUSTOM`; `src/modes/CustomControllerMode.cpp` consumes `CustomModeConfig.modifiers`; `HAL/pico/include/util/state_util.hpp::axis_pointer` maps `AnalogAxis` to `OutputState` byte fields; traced in `docs/calibration/glyph_modifier_value_trace_2026-05-24.md`. | Can current schema-backed `MODE_CUSTOM` represent the intended Ultimate-specific `TILT` / `Tilt2` behavior without losing native Ultimate behavior? | Source-backed profile examples or approved design showing custom-mode profile shape and parity requirements. | Yes, if custom mode is chosen. |
| Final Tilt1/Tilt2 value source | BLOCKED | Existing Ultimate source comments contain tilt-like constants, but `docs/calibration/glyph_tilt_modifier_firmware_test_readiness_2026-05-24.md` states final Tilt1/Tilt2 values are not selected. | What exact byte coordinates or scalar values should the later runtime branch test? | Explicit user/domain approval or source-backed fixture/design specifying values. | Yes. |
| Overflow/clamp behavior | BLOCKED | `include/core/state.hpp` stores analog axes as `uint8_t`; `src/modes/CustomControllerMode.cpp::UpdateAnalogOutputs` assigns multiplier formulas into `outputs.*axis`; no explicit clamp/saturate was found in prior trace docs. | Does current runtime intentionally clamp, wrap, or otherwise constrain out-of-range modifier math? | Source proof or host-side/unit evidence for conversion behavior before any overflow-dependent design. | Yes, for flipper/overflow-dependent behavior. |
| Flipper behavior | BLOCKED | `docs/calibration/glyph_modifier_value_trace_2026-05-24.md` found no `flipper` field, symbol, fixture, or runtime implementation in active proto/runtime paths. | Is flipper a real Glyph/HayBox feature, a planned Senscope authoring concept, or an out-of-scope shortcut? | Source proof or explicit owner design. Do not guess. | Yes, if requested behavior depends on flipper semantics. |
| SOCD/remap interaction | DEFERRED | `src/core/ControllerMode.cpp::UpdateOutputs` applies `HandleRemap`, then `HandleSocd`, then digital and analog updates; `config/glyph/common/include/glyph_overrides.hpp` and calibration fixtures contain Ultimate remaps and SOCD pairs; prior docs require preserving SOCD/remap semantics. | Should later `TILT` / `Tilt2` logic observe post-remap/post-SOCD input only, and are any exceptions needed? | Explicit design approval if any SOCD/remap semantics would change. | Yes, if runtime patch would alter SOCD/remap behavior; otherwise deferred. |
| Configurator/UI/profile serialization impact | PARTIAL | Current parser/patch tooling is read-only or JSON patch prototype only (`tools/glyph_config_model.py`, `tools/patch_glyph_ultimate_profile.py`); active proto source is dependency-provided; tracked JSON fixtures do not contain custom modifier/custom-mode arrays. | Does later work require new profile fields, UI controls, or only compiled firmware behavior? | Approval before schema/UI/profile serialization changes; source-backed profile examples if using `MODE_CUSTOM`. | Yes, if changing schema/UI/profile serialization. |
| Build verification | READY | Prior baseline reports `./scripts/build-glyph-mk6-quiet.sh` succeeded with `glyph_mk6 SUCCESS`; wrapper path is documented in `AGENTS.md` command policy. | Does this branch still build after docs/tooling additions? | Run quiet build if local setup remains healthy. | Yes before hardware test; docs-only branch should still compile. |
| Hardware smoke test | DEFERRED | Previous readiness docs require a human-controlled smoke-test protocol before flashing; no flashing or push-to-device tooling exists in this gate packet. | What exact manual observation checklist and rollback procedure should hardware owner use? | Add reviewed protocol draft, then require owner-present manual execution later. | Yes before any device flash; not required for this docs-only branch. |

## Runtime Patch Gate Summary

A later runtime branch must not proceed until these blockers are resolved:

- Final Tilt1/Tilt2 values are explicitly approved or source-backed.
- Overflow/clamp behavior is proven or avoided.
- Flipper behavior is source-proven or explicitly designed without relying on overflow.
- Implementation path is approved: native `MODE_ULTIMATE`, schema-backed `MODE_CUSTOM`, a new narrow profile mechanism, or deferral.
- Any schema/configurator/profile serialization impact is reviewed before implementation.
- Hardware smoke-test protocol and rollback plan are ready before flashing.

No runtime firmware or device behavior is changed by this matrix.
