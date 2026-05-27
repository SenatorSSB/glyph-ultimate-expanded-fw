# Glyph/Senscope Workflow and Config Migration Plan - 2026-05-27

Purpose: control-plane plan for current firmware iteration and future Senscope-configurable Glyph firmware.

Scope: documentation/planning only. This file does not implement runtime behavior, change profile artifacts, change schema/proto/configurator structure, add migration logic, add firmware flashing automation, or add live serial write behavior.

## Current Development Workflow

During discovery, hardcoded runtime tables in native Ultimate are acceptable for the project owner's test device.

Changing modifier coordinates, priority behavior, or function behavior currently means:

1. edit runtime/profile docs
2. build firmware
3. flash firmware manually
4. apply active profile config if needed
5. hardware-test
6. record result

This rebuild/flash iteration loop is acceptable for the project owner during discovery because the user has full control of the test device and accepts firmware iteration while behavior is being proven.

This is not the intended long-term workflow for future users.

## Current Identity Physical/Logical Policy

During active development, prefer identity physical->logical mappings wherever practical.

User-facing button IDs denote physical-position IDs. Runtime code and docs should interpret same-named post-remap logical fields as physical positions for this discovery workflow.

Avoid semantic remapping such as physical LT5 -> arbitrary spare logical role unless explicitly needed and source-backed for the change being tested.

This reduces ambiguity and makes hardware/debug conversations easier because a user-facing ID, a board position, and the runtime field name can refer to the same physical location during iteration.

The profile/remap layer should be treated as layout assignment only after firmware behavior is stable. Until then, custom project-owner interpretation should live in runtime-side tables or docs rather than in semantic profile indirection.

## Why Not Parse Config During Gameplay

The gameplay frame loop must stay simple and predictable. It must not perform heavy control-plane work.

Explicit performance boundary:

- no protobuf/JSON parsing in gameplay frame loop
- no heap allocation
- no serial I/O
- no file I/O
- no CRC/storage work
- no string matching
- no large linear scans

Runtime gameplay should use booleans, simple priority checks, and fixed/small table lookup. The input path should not depend on parsing text formats, decoding schema payloads, scanning large config lists, or performing storage validation while frames are being processed.

## Future Migration Target

Future Senscope-enabled firmware should allow modifier-value changes without requiring firmware rebuilds.

The target architecture is:

1. read persistent config on boot/config update
2. validate modifier tables
3. convert config into compact runtime structs in RAM
4. use O(1) table lookup during gameplay

Conceptual runtime-side structs:

```c
typedef struct {
    int8_t x;
    int8_t y;
} StickCoord;

typedef struct {
    StickCoord directions[9];
} ModifierTable;

typedef struct {
    ModifierTable tilt;
    ModifierTable tilt2;
    ModifierTable tilt3;
    bool enable_tilt;
    bool enable_tilt2;
    bool enable_tilt3;
} UltimateModifierRuntimeConfig;
```

These names and shapes are conceptual architecture direction only. They are not implemented in this branch and do not claim existing Glyph/HayBox firmware behavior.

Heavy config work should happen at boot/config-write time. Gameplay should use compact cached representation with O(1) lookup over fixed/small RAM structs to avoid input-delay risk.

## Senscope Integration Levels

Level 0: current hardcoded runtime constants; firmware update for value changes.

Level 1: fixed firmware capabilities with remappable button placements.

Level 2: config-driven modifier tables; Senscope exports config; serial writer applies it; no firmware reinstall for value changes.

Level 3: richer dynamic table/role engine and possible custom/configurator app support.

## Configurator/Webapp Boundary

The Limit Labs webapp is closed-source from this repo perspective.

It was observed lossy for custom LT3 import, so it is not the reliable source-backed path for preserving custom LT3 configuration in the current workstream.

The current reliable path is a repo-local serial config writer for source-backed config writes. Any live write must remain explicitly user-triggered and must not be confused with firmware flashing automation.

Future options:

- Senscope profile visualizer/writer
- custom configurator if official source becomes available
- upstream collaboration if feasible

## Immediate Next Implementation Policy

Reset toward identity physical->logical Ultimate profile artifacts.

Use runtime-only custom interpretation for the project owner's profile during discovery, where practical and source-backed.

Later, when stable, decide whether to harden the behavior into:

- fixed role firmware + remappable profiles
- config-driven Senscope tables

This planning branch does not choose that architecture permanently and does not implement either migration path.

## Non-Goals

- no firmware flashing automation
- no macros/turbo/toggles/one-shot/timing automation
- no schema/proto changes in this branch
- no configurator structure changes in this branch
- no profile artifact changes in this branch
- no runtime source changes in this branch
- no live serial write behavior in this branch
- no claim that future config-driven runtime is implemented
