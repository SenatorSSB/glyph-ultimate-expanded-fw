# G7 - Custom Mode Controller Logic Engine Design

Status: complete (design-only spike)  
Date: 2026-05-23  
Branch: `design/glyph-controller-logic-engine-g7`  
Scope: design only; not firmware implementation

## 1. Title and Status

This is the G7 custom mode / controller logic engine design for a future stateless Glyph/Senscope controller logic engine.

This document proposes a future design target. It does not implement firmware code, runtime adapters, evaluator code, export generation, push-to-device workflows, or changes to `platformio.ini`. It does not alter Senscope neutral profile schema or game-semantic source authority.

## 2. Scope

Reviewed:
- Standing repo contracts and boundaries: `AGENTS.md`, `docs/project/ACTIVE_AGENT_QUEUE.md`, `docs/project/AGENT_OPERATING_CONTRACT.md`, `docs/project/AGENT_STOP_CONDITIONS.md`, `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`, `docs/project/SENSCOPE_INTEGRATION_TARGET.md`, and `docs/project/GLYPH_CAPABILITY_MODEL_TARGET.md`.
- Prior milestone docs: `docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md`, `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`, `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`, `docs/project/G4_G1_G3_REVIEW_AND_NEXT_QUEUE.md`, `docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`, and `docs/project/G6_EVALUATOR_CONTRACT_TESTS_WITH_MOCK_CAPABILITIES.md`.
- Active source/reference files: `include/core/state.hpp`, `include/core/InputMode.hpp`, `src/core/InputMode.cpp`, `include/core/ControllerMode.hpp`, `src/core/ControllerMode.cpp`, `include/core/socd.hpp`, `src/core/socd.cpp`, `include/modes/Ultimate.hpp`, `src/modes/Ultimate.cpp`, `include/modes/CustomControllerMode.hpp`, `src/modes/CustomControllerMode.cpp`, `docs/sources/raw/ESAM1.hpp`, `docs/sources/raw/ESAM1.cpp`, and `docs/sources/raw/GlyphUserProfiles.json`.

This design proposes a future stateless custom controller logic engine that could support exact directional modifier tables, modifier-combination profiles, Force Up-B named override rules, table-defined flipper/off-direction behavior, multi-output button/chord rules, right-stick/C-stick exact output tables, and strict current-frame behavior.

This design intentionally does not decide:
- final protobuf/config schema;
- firmware storage representation;
- memory/flash budget;
- host-side export format;
- push-to-device workflow;
- runtime adapter behavior;
- evaluator implementation;
- gameplay semantic meaning of any coordinate.

No firmware/source/runtime implementation was performed.

## 3. Design Problem

G2, G3, and G5 show that current source has useful controller-backend primitives, but not a proven generic full 9-way modifier table system. `OutputState` has byte-level analog fields, `InputMode` has remap and SOCD handling, `Ultimate` has hardcoded mode-specific directional/modifier behavior, and `CustomControllerMode` has configurable mode-specific mappings and analog modifiers. Those facts are not enough to claim that current Glyph firmware already supports arbitrary Senscope-style exact 9-way modifier tables.

The design problem is therefore not "document existing generic support." It is to sketch a future custom logic engine that could become a clean backend target after review. Current source can inform the shape of the engine, but desired future behavior must remain separate from current firmware support.

## 4. Non-Negotiable Legality and Safety Constraints

The future engine must enforce:
- no macros;
- no timing automation;
- no toggles;
- no one-shot output;
- no stateful behavior except source-backed SOCD internals such as 2IP state in `include/core/socd.hpp` and `src/core/socd.cpp`;
- current-frame/snapshot-only evaluation for all non-SOCD behavior;
- no `uint8_t` overflow or wraparound as intended behavior;
- no game-semantic logic, gameplay thresholds, no-smash/no-strong-input rules, action labels, or semantic map authority.

When a button is released, non-SOCD behavior must be forgotten immediately. A later frame must be derived from the later physical snapshot, not from earlier button history.

## 5. Source-Backed Current-Firmware Facts Used as Design Inputs

Source-backed facts:
- `OutputState` has digital fields and byte analog fields for left stick, right stick, and analog triggers. Source: `include/core/state.hpp`.
- `ControllerMode::UpdateOutputs` runs remap, then SOCD, then digital output update, then analog output update. Source: `src/core/ControllerMode.cpp`.
- `InputMode::HandleRemap` supports many-to-one remap behavior in an OR-like way: a target remains pressed when either the current physical input is pressed or an earlier remap already activated that target. The same function also ignores duplicate remaps from the same physical button to avoid macro behavior. Source: `src/core/InputMode.cpp`.
- `InputMode::HandleSocd` dispatches configured SOCD pairs and supports `SOCD_NEUTRAL`, `SOCD_2IP`, `SOCD_2IP_NO_REAC`, `SOCD_DIR1_PRIORITY`, and `SOCD_DIR2_PRIORITY`. Sources: `src/core/InputMode.cpp`, `include/core/socd.hpp`, `src/core/socd.cpp`.
- `ControllerMode::UpdateDirections` centers both sticks first, then sets min/max values from direction booleans. Source: `src/core/ControllerMode.cpp`.
- `Ultimate` has hardcoded mode-specific digital outputs, D-pad layer behavior, coordinate constants, modifier/chord contexts, right-stick behavior, trigger values, and nunchuk override behavior. Source: `src/modes/Ultimate.cpp`.
- `CustomControllerMode` has configurable mode-specific button combo mappings to single digital outputs, direct digital output mappings, stick direction mappings, analog modifiers with override/compound paths, analog trigger mappings, and nunchuk override behavior. Source: `src/modes/CustomControllerMode.cpp`.
- `ESAM1` is copied reference material with alternate hardcoded behavior, non-center neutral-like values in a mode path, and angle-based C-stick behavior, but G1/G2/G5 treat it as reference-only rather than active current runtime authority. Sources: `docs/sources/raw/ESAM1.cpp`, `docs/sources/raw/ESAM1.hpp`.
- `GlyphUserProfiles.json` is staged config-like reference material. It is useful for source inventory, but it does not by itself prove stable config capacity or generic exact 9-way table support. Source: `docs/sources/raw/GlyphUserProfiles.json`.

Non-claims:
- Current stock firmware does not prove generic full 9-way modifier table support.
- Current stock firmware does not prove first-class direction `5` as a generic backend field.
- Current stock firmware does not prove a generic flipper primitive or generic Force Up-B primitive.

## 6. Desired Future Architecture Overview

Desired current-frame pipeline:

```text
Physical input snapshot
  -> logical role expansion
  -> current-frame layer/role map
  -> pre-SOCD direction role set
  -> SOCD
  -> resolved DirectionKey 1..9
  -> active rule/profile selection
  -> high-priority override resolution
  -> exact left-stick output resolution
  -> exact right-stick/C-stick output resolution
  -> digital output OR composition
  -> analog output priority composition
  -> final OutputState
```

The pipeline is intentionally stateless outside SOCD internals. The engine should be understandable as a pure function from a physical input snapshot plus a validated configuration to a final `OutputState`, with SOCD state treated as the explicit and narrow exception.

## 7. Core Concepts

Conceptual pseudotypes only:

```text
type PhysicalSnapshot = {
  physical_buttons: Set<PhysicalButtonId>;
  analog_inputs?: InputAnalogValues;
};

type LogicalRole =
  | { kind: "DIGITAL_OUTPUT"; target: DigitalOutputTarget }
  | { kind: "DIRECTION"; target: DirectionRole }
  | { kind: "MODIFIER"; id: ModifierId }
  | { kind: "LAYER"; id: LayerId }
  | { kind: "RULE_TRIGGER"; id: RuleId };

type LogicalRoleSet = Set<LogicalRole>;
type DirectionRoleSet = Set<"LEFT" | "RIGHT" | "DOWN" | "UP">;
type DirectionKey = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;

type ButtonCondition = {
  required_roles?: LogicalRole[];
  forbidden_roles?: LogicalRole[];
};

type LayerCondition = {
  layer_id: LayerId;
  while_held: true;
};

type ModifierCombination = {
  modifiers: Set<ModifierId>;
};

type ComboProfile = {
  id: ComboProfileId;
  combination: ModifierCombination;
  priority: number;
  outputs: OutputContribution[];
};

type OutputContribution =
  | { target: AnalogOutputTarget; priority_category: OutputPriorityCategory; coordinate: RawCoordinate }
  | { target: DigitalOutputTarget; active: true };

type AnalogOutputTarget = "LEFT_STICK" | "RIGHT_STICK" | "TRIGGER_L" | "TRIGGER_R";
type DigitalOutputTarget = "A" | "B" | "X" | "Y" | "L" | "R" | "ZL" | "ZR" | "START" | "DPAD_UP" | "DPAD_DOWN" | "DPAD_LEFT" | "DPAD_RIGHT" | string;

type OutputPriorityCategory =
  | "FORCE_OVERRIDE"
  | "EXPLICIT_CHORD_PROFILE"
  | "MODIFIER_COMBINATION_TABLE"
  | "NORMAL_DIRECTION_OUTPUT"
  | "NEUTRAL_DEFAULT";

type RawCoordinate = {
  x: number; // validated 0..255
  y: number; // validated 0..255
};
```

These names are not final API names and do not imply a schema change.

## 8. Stateless Input Snapshot Model

Each frame begins with the physical buttons currently held. Logical roles are expanded from that snapshot only.

Layer buttons are held conditions, not toggles. If a held layer button changes another held button's role, that role changes on the same frame. If the layer is released, the alternate role is gone on that frame. If a button is released, it no longer contributes roles or outputs.

This model allows expressive current-frame mappings without becoming macro/timing automation.

## 9. OR-Composed Digital and Logical Roles

Duplicate physical buttons are OR-composed. If multiple physical buttons activate `B`, the final `B` digital output remains active while at least one source remains active.

One physical input may emit multiple logical roles in the same frame. For example, one physical input may emit a digital output role and a modifier role, or may emit `DIR_UP` plus `DIR_RIGHT` before SOCD.

Final digital outputs are OR-composed across direct buttons, chord outputs, layer outputs, and override outputs. Direction roles are also OR-composed before SOCD.

## 10. Direction and SOCD Model

Direction roles are accumulated before SOCD. Then SOCD resolves opposing directions. Normal exact modifier tables use the post-SOCD direction.

Direction `5` means no active direction buttons after direction resolution unless an explicit table/rule defines a direction-5 output. Ordinary no-direction output should remain neutral, usually raw `(128,128)`.

A physical button may activate multiple direction roles before SOCD, such as `DIR_UP + DIR_RIGHT`. Override rules may ignore direction entirely or use the post-SOCD direction/horizontal component if configured.

SOCD behavior must be recorded as controller/backend behavior only. This design attaches no gameplay meaning to SOCD.

## 11. Modifier-Combination Profile Model

Exact 9-way tables for multiple modifiers are a core desired future capability. A held modifier combination plus a resolved direction key selects a predefined raw coordinate.

Each explicit `ComboProfile` names:
- a modifier set;
- an output target;
- a 9-way table or partial table;
- a priority;
- source/design refs once implemented.

If active modifiers are `{A,B,C}` and exact combo `{A,B,C}` is undefined, selection should use the highest-priority defined subset. Equal-priority matching subsets are invalid. An undefined active combo with no matching fallback is a validation error or hard diagnostic.

This full 9-way support is a desired design target, not a current firmware support claim.

## 12. Exact Left-Stick Output Model

Left-stick output should resolve as:

```text
active profile + DirectionKey -> raw left-stick coordinate
```

Coordinates are predefined and validated. Direction `5` may have a table entry where explicitly defined, but ordinary neutral does not require a non-center direction-5 entry.

Normal neutral remains `(128,128)` unless an explicit table/rule overrides it. Each coordinate component must validate to `[0,255]`.

## 13. Flipper / Off-Direction Model

Flipper is table-defined modifier/rule behavior. It is not arithmetic mirroring at runtime.

A flipper profile may map direction `6` to a leftward coordinate, direction `8` to another off-direction coordinate, or any other predefined output table. Runtime truth is the validated table output.

No arithmetic mirror is required. No `uint8_t` overflow or wraparound is allowed as intended behavior. Future authoring tools may generate mirrored tables as a convenience, but runtime should consume explicit validated coordinates.

## 14. Force Up-B / Force-Stick Override Model

`ForceUpB` is a product/design rule name in this document, not a gameplay-semantic claim. It can take two forms:

```text
fixed exact output:
  ignores all directions and sets a fixed left-stick coordinate

forced upward family:
  forces the upward Y coordinate family
  optionally derives X from the post-SOCD horizontal result
```

Requirements:
- standard Force Up-B emits `B` only by default;
- it does not emit `Y` unless a separate digital chord/multi-output rule configures `Y`;
- Force Up-B left-stick output uses `FORCE_OVERRIDE` priority;
- if horizontal influence is enabled, the X component uses post-SOCD horizontal result;
- pressing the Force Up-B trigger always forces the upward Y vector regardless of held down/up direction roles;
- no coordinate is labeled by move result or gameplay effect.

## 15. Digital Multi-Output and Chord Model

A button or chord may emit multiple digital outputs, for example `B` and `Y`. Digital outputs OR with all other digital sources. Individual `B` and `Y` buttons remain read normally; if one output is already active through a chord, OR composition keeps it active.

Digital multi-output chords are separate from Force Up-B. A Force Up-B rule should not implicitly become `B+Y`; `B+Y` must be its own configured digital output rule.

Suppression/pass-through should be explicit if future source-backed behavior requires it. The default future design can rely on OR composition unless a source-backed suppression need is defined.

No chord rule may encode macro or timing behavior.

## 16. Layer / Mode Button Model

A Mode/Layer button may remap other roles while held. It may also emit outputs itself or contribute modifier roles.

It is not a toggle. It is current-frame conditional mapping:

```text
if layer role is held in this snapshot:
  use layer-specific role map
else:
  use normal role map
```

Releasing the layer button immediately returns evaluation to the non-layer map on that frame.

## 17. Right-Stick / C-Stick Exact Output Model

Right stick should be modeled as an exact raw output target parallel to left stick.

C-stick direction combinations can exist as authoring shorthand, such as "C-left plus C-up", but runtime should resolve to an exact right-stick coordinate or another validated right-stick output contribution.

ESAM1's `atan`/`cos`/`sin` angle behavior is reference evidence only. A future implementation does not need to use angle math. The preferred design target is exact right-stick raw coordinate tables, with authoring shortcuts added later only if reviewed.

## 18. Analog Output Priority and Composition

Analog targets are independent: left stick, right stick, and triggers can be resolved separately.

For each analog output target, same-target conflicts use global priority categories:

1. `FORCE_OVERRIDE`
2. `EXPLICIT_CHORD_PROFILE`
3. `MODIFIER_COMBINATION_TABLE`
4. `NORMAL_DIRECTION_OUTPUT`
5. `NEUTRAL_DEFAULT`

Equal-priority same-target conflicts are invalid. Different analog targets can be set by different active rules in the same frame. Example: ForceUpB may control left stick while a C-stick modifier controls right stick.

## 19. Transport-Neutral Output Vocabulary

The logic engine should speak logical gamepad outputs where possible: digital output names and raw analog target values.

The first concrete realization target should remain compatible with GC-style output / GC adapter routing because the existing `OutputState` and backend paths already include GC-style byte stick fields. ProCon/Switch mapping should remain future transport adapter work.

This document does not create transport-specific export design or push-to-device design.

## 20. Config Migration Strategy

Two-stage migration:

1. Prototype design may use compile-time constants after explicit approval. This would reduce early storage uncertainty while proving the logic model.
2. Long-term design should become config-backed only if actual source/config constraints prove adequate capacity, validation, and transport semantics.

G7 does not decide protobuf fields, config schema, serialized format, UI affordances, or export format. Future config-backed work must inspect actual config constraints before claiming support.

## 21. Validation and Diagnostics

Hard validation errors:
- coordinates outside `[0,255]`;
- same-priority matching combo profiles;
- same-priority same-target analog output contributions;
- undefined active combo with no matching fallback;
- missing source refs for claimed source-backed behavior;
- reference-only ESAM behavior used as active runtime support;
- macro/timing/toggle behavior;
- one-shot output behavior;
- intended `uint8_t` overflow/wraparound behavior.

Warning diagnostics:
- mode-specific behavior used as generic design evidence;
- config-backed support unknown;
- export/push unsupported;
- first-class direction `5` not proven in current source;
- full generic 9-way table support not proven in current stock firmware;
- source facts mixed with desired future behavior.

## 22. Example Scenarios

Gameplay-neutral examples:
- Duplicate `B` buttons: `P1` and `P2` both emit `B`; final `B` is active while either is held.
- One physical button emits `DIR_UP + DIR_RIGHT` before SOCD; SOCD then resolves any opposing direction roles from the full direction role set.
- Modifier `A` plus direction `6` selects the direction-6 coordinate from modifier `A`'s exact left-stick table.
- Active modifiers `{A,B,C}` fall back to the highest-priority defined subset, such as `{A,C}`, if `{A,B,C}` is undefined.
- A flipper profile maps direction `6` to a predefined leftward coordinate; no arithmetic mirror occurs at runtime.
- ForceUpB fixed exact coordinate ignores held direction roles and emits `B` plus the fixed left-stick coordinate.
- ForceUpB upward-Y/horizontal-X form forces upward Y and derives X from post-SOCD horizontal result.
- C-left with a profile outputs an exact right-stick up-left coordinate.
- A digital chord emits `B+Y` as a separate multi-output rule; this is not implied by ForceUpB.

## 23. Current Source Gaps Before Implementation

Open gaps:
- exact current config capacity for combo/profile tables is unknown;
- memory/flash implications are unknown;
- best storage representation is unknown;
- first concrete mode target is undecided;
- no test framework has been chosen;
- no source-backed export/push path is approved;
- current stock firmware does not prove generic full 9-way table support;
- first-class direction `5` support as a generic backend concept is not proven;
- generic flipper and generic Force Up-B primitives are not proven in current source.

These gaps must be resolved before implementation claims can be made.

## 24. Recommended Next Steps After G7

Options after human inspection:
- G7R: human review of design decisions and priority categories.
- G9: config capacity/source inventory for custom mode table storage.
- G10: compile-time prototype design, still no code.
- G11: minimal firmware prototype only after explicit approval.
- G8: software-side evaluator prototype remains separate and should wait until backend target shape is stable.

Do not proceed to G8, G9, G10, or G11 automatically.

## 25. Verification

Commands run:
- `git checkout configurator`: succeeded; branch was already `configurator`.
- `git pull origin configurator`: succeeded; already up to date.
- `git status`: clean on `configurator` before branch creation.
- `git branch --show-current`: reported `configurator` before branch creation.
- `git checkout -b design/glyph-controller-logic-engine-g7`: succeeded.
- `sed -n '1,260p' ...` and continuation reads for required project docs.
- `sed -n '1,260p' ...` and targeted continuations for required source/reference files.
- `find docs/project docs/architecture docs/research docs/firmware docs/sources include src -maxdepth 4 -type f`: inspected repository document/source surface.
- Targeted `rg` checks across project docs, active source, and staged reference material.

Docs-only verification after edits:
- `git status`: on `design/glyph-controller-logic-engine-g7`; `docs/project/ACTIVE_AGENT_QUEUE.md` modified and this G7 document untracked before staging.
- `git diff --stat`: tracked pre-staging diff showed `docs/project/ACTIVE_AGENT_QUEUE.md | 8 +++++---`; the new G7 document was reviewed with `sed` because untracked files do not appear in unstaged `git diff --stat`.

Build was not run because this is a docs-only design task and must not be build-affecting.
