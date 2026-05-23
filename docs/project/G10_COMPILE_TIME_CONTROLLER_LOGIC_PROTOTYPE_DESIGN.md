# G10 - Compile-Time Controller Logic Prototype Design

Status: complete (design-only document)  
Date: 2026-05-23  
Branch: `design/glyph-compile-time-prototype-g10`  
Scope: design only; not firmware implementation

## 1. Title and status

This is the G10 compile-time prototype design for a minimal future prototype path for the G7 stateless controller logic engine.

This document is design-only. It does not implement firmware code, change protobuf/config schemas, add runtime adapters, add evaluator code, change `platformio.ini`, generate export files, add push-to-device workflows, or alter Senscope game-semantic source authority.

## 2. Scope

Reviewed:
- Standing repo contracts and boundaries: `AGENTS.md`, `docs/project/ACTIVE_AGENT_QUEUE.md`, `docs/project/AGENT_OPERATING_CONTRACT.md`, `docs/project/AGENT_STOP_CONDITIONS.md`, `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`, `docs/project/SENSCOPE_INTEGRATION_TARGET.md`, and `docs/project/GLYPH_CAPABILITY_MODEL_TARGET.md`.
- Prior milestone docs: G1 through G7 and G9.
- Active source/reference files: `include/core/state.hpp`, `include/core/InputMode.hpp`, `src/core/InputMode.cpp`, `include/core/ControllerMode.hpp`, `src/core/ControllerMode.cpp`, `include/core/socd.hpp`, `src/core/socd.cpp`, `include/modes/Ultimate.hpp`, `src/modes/Ultimate.cpp`, `include/modes/CustomControllerMode.hpp`, `src/modes/CustomControllerMode.cpp`, `docs/sources/raw/ESAM1.hpp`, and `docs/sources/raw/ESAM1.cpp`.

This design proposes a future compile-time prototype path for the G7 stateless current-frame controller logic model. The path uses compile-time data tables and validation before any protobuf/config storage, configurator, runtime adapter, evaluator, export, or push-to-device work.

This design intentionally does not implement or decide:
- final C++ headers or source files;
- protobuf/config schema;
- persistence/configurator support;
- runtime adapter behavior;
- evaluator implementation;
- export or push workflow;
- gameplay meaning for any coordinate.

Explicitly: no firmware/source/runtime implementation was performed.

## 3. Why compile-time first

G9 concludes that current config-backed structures do not directly fit the desired G7 table/profile model. Current source has useful primitives, including `CustomModeConfig` button mappings, stick direction mappings, analog modifiers, button combos, persistence, and configurator get/set paths. G9 also identifies gaps for exact 9-way left-stick tables, direction `5` entries, explicit profile fallback, table-defined flipper/off-direction behavior, Force Up-B override rules, exact right-stick tables, and deep validation.

Compile-time constants reduce risk because they let a future approved implementation validate the controller logic shape without committing to serialized storage. The prototype can keep tables explicit, bounded, and reviewable while avoiding early nanopb/protobuf capacity, migration, UI, export, and push assumptions.

This path also preserves source authority. A compile-time prototype can be labeled as a selected experimental mode, not as proof that current config-backed Glyph firmware already realizes every Senscope neutral profile.

## 4. Prototype objective

The smallest useful compile-time prototype target is a new future custom mode concept that exercises the G7 logic model while staying isolated from existing modes.

Target behavior:
- stateless current-frame evaluation outside the existing source-backed SOCD state machinery;
- exact 9-way left-stick tables for multiple modifier combinations;
- explicit direction `5` handling where a table defines direction `5`;
- table-defined flipper/off-direction profiles;
- Force Up-B fixed and horizontal-influenced forms;
- digital multi-output button/chord rules;
- one physical input emitting multiple direction roles before SOCD;
- exact right-stick/C-stick output table concept;
- strict validation rules before behavior can be considered safe to wire.

The prototype should prove data shape and resolver policy, not storage, configurability, exportability, or gameplay correctness.

## 5. Non-goals

- No firmware implementation in G10.
- No config/protobuf schema changes.
- No persistence/configurator support.
- No export or push workflow.
- No runtime adapter.
- No evaluator prototype.
- No gameplay semantics, thresholds, no-smash/no-strong-input behavior, action labels, or semantic maps.
- No tests in this batch.

## 6. Source basis

Source-backed current-firmware facts used as grounding:
- `InputState` has a 64-bit physical button surface and nunchuk fields; `OutputState` has digital output bits and byte analog axes for left stick, right stick, and analog triggers. Source: `include/core/state.hpp`.
- `ControllerMode::UpdateOutputs` orders processing as remap, SOCD, digital outputs, then analog outputs. Source: `src/core/ControllerMode.cpp`.
- `InputMode::HandleRemap` supports many-to-one target activation and explicitly ignores duplicate remaps from the same physical button to prevent macro behavior. Source: `src/core/InputMode.cpp`.
- `InputMode::HandleSocd` dispatches configured SOCD pairs and uses a fixed `_socd_states[10]` state array. Sources: `include/core/InputMode.hpp`, `src/core/InputMode.cpp`.
- SOCD algorithms include neutral, second-input priority, second-input priority without reactivation, and direction-priority forms. Sources: `include/core/socd.hpp`, `src/core/socd.cpp`.
- `ControllerMode::UpdateDirections` centers sticks and then maps active direction booleans to min/max stick values. Source: `src/core/ControllerMode.cpp`.
- `Ultimate` has hardcoded mode-specific digital mappings, D-pad layer behavior, modifier/chord coordinate behavior, right-stick behavior, trigger analog values, C-stick shutoff in D-pad layer, and nunchuk left-stick override. Source: `src/modes/Ultimate.cpp`.
- `CustomControllerMode` consumes config-backed combo mappings, digital mappings, stick direction mappings, analog modifiers, analog trigger mappings, and nunchuk behavior. It does not expose a source-backed exact 9-way table field. Sources: `include/modes/CustomControllerMode.hpp`, `src/modes/CustomControllerMode.cpp`.
- `ESAM1` is copied reference-only behavior with alternate hardcoded coordinate logic and angle/math C-stick behavior; it is not treated as active current runtime authority. Sources: `docs/sources/raw/ESAM1.hpp`, `docs/sources/raw/ESAM1.cpp`, plus G1/G2/G7/G9 classifications.
- G7 defines the desired stateless controller logic engine target and its no-macro/no-timing/no-toggle/no-one-shot/no-overflow/no-game-semantics constraints. Source: `docs/project/G7_CUSTOM_MODE_CONTROLLER_LOGIC_ENGINE_DESIGN.md`.
- G9 recommends compile-time prototype first because existing config-backed structures do not cleanly model G7's table/profile needs. Source: `docs/project/G9_CONFIG_CAPACITY_AND_TABLE_STORAGE_INVENTORY.md`.

Current-source non-claims:
- Current stock firmware does not prove generic full 9-way modifier table support.
- Current stock firmware does not prove a generic first-class direction `5` table field.
- Current stock firmware does not prove generic flipper, Force Up-B, or exact right-stick table primitives.

## 7. Proposed compile-time data model

The following names are explicitly non-final. They are conceptual C++-like compile-time structs, not code to create in G10.

```cpp
struct RawCoord {
  uint8_t x;
  uint8_t y;
};

enum class DirectionKey {
  D1, D2, D3, D4, D5, D6, D7, D8, D9
};

using DigitalOutputMask = uint32_t;
using PhysicalButtonMask = uint64_t;
using LogicalRoleMask = uint64_t;
using DirectionRoleMask = uint8_t;

using ModifierId = uint8_t;
using ModifierCombinationMask = uint32_t;

struct ComboProfile {
  ModifierCombinationMask modifiers;
  uint8_t priority;
  uint8_t left_table_index;
  uint8_t right_table_index;
};

struct DirectionalStickTable9 {
  bool has_entry[9];
  RawCoord entry[9];
};

struct ForceStickOverrideRule {
  PhysicalButtonMask trigger;
  uint8_t form;
  RawCoord fixed_coord;
  bool use_post_socd_horizontal_x;
};

struct DigitalMultiOutputRule {
  PhysicalButtonMask condition;
  DigitalOutputMask outputs;
};

struct LayerRoleMap {
  PhysicalButtonMask held_condition;
  LogicalRoleMask role_outputs;
  DirectionRoleMask direction_outputs;
};

struct RightStickTable {
  bool has_entry[9];
  RawCoord entry[9];
};

struct PrototypeProfile {
  PhysicalButtonMask physical_buttons;
  LayerRoleMap layer_role_maps[MAX_LAYER_ROLE_MAPS];
  ComboProfile combo_profiles[MAX_COMBO_PROFILES];
  DirectionalStickTable9 left_tables[MAX_LEFT_TABLES];
  RightStickTable right_tables[MAX_RIGHT_TABLES];
  ForceStickOverrideRule force_rules[MAX_FORCE_RULES];
  DigitalMultiOutputRule digital_rules[MAX_DIGITAL_RULES];
};
```

These sketches are meant to clarify table ownership and validation. They are not final names, not ABI, not schema, and not firmware implementation approval.

## 8. Button and role expansion design

The prototype should expand physical buttons into logical roles on each frame. A physical button may emit one role or many roles. Example role families include digital outputs, modifier roles, layer roles, left-stick direction roles, right-stick direction roles, and rule triggers.

Duplicate logical roles OR together. If two physical inputs both emit `B`, final `B` remains active while either input is held. If one physical input emits `DIR_UP` and `DIR_RIGHT`, both direction roles enter the pre-SOCD direction set on that frame.

Direction roles OR together before SOCD. Layer/Mode roles are held conditions, not toggles. Releasing a layer button removes that layer's role contributions immediately on that frame.

## 9. Direction/SOCD design

Normal table lookup uses the post-SOCD direction. The input path is:

```text
physical snapshot
  -> logical/direction role expansion
  -> pre-SOCD direction roles
  -> SOCD
  -> DirectionKey
  -> table/rule lookup
```

One physical input may create multiple direction roles before SOCD. Opposing direction behavior remains controller/backend behavior and must be resolved by source-backed SOCD policy, not gameplay semantics.

Force Up-B may ignore direction entirely, or it may use only the post-SOCD horizontal component if configured to do so. Direction `5` means no active direction after SOCD unless an explicit table/rule defines direction `5`.

## 10. Modifier-combination table design

The core table lookup is exact:

```text
modifier combination + DirectionKey -> RawCoord
```

Multiple explicit combo profiles may exist. A held active modifier set first seeks an exact matching combo profile. If no exact profile exists, it may fall back to the highest-priority defined subset. Equal-priority matching subsets are invalid. An undefined active combo with no valid fallback is invalid and should produce a hard diagnostic.

Direction `5` entries are optional but supported. A table may define direction `5` to produce a neutral or non-neutral coordinate, but no current-source claim is made that existing config-backed firmware already supports that as a generic field.

## 11. Flipper/off-direction design

Flipper is table-defined profile behavior. It is not arithmetic mirror behavior at runtime.

For the prototype, a flipper/off-direction profile is just another validated table. A table may map direction `6` to a leftward coordinate, direction `8` to a downward-biased coordinate, or any other authored raw value. Runtime truth is the table.

No overflow, wraparound, or implicit `uint8_t` arithmetic behavior is allowed. Future authoring shortcuts may generate mirrored/off-direction tables later, but generated authoring convenience must not become runtime truth unless the generated table is explicit and validated.

## 12. Force Up-B design

`ForceUpB` is a prototype rule label, not a gameplay-semantic claim.

Two compile-time rule forms are sufficient:

1. Fixed exact raw coordinate:
   - ignores direction;
   - writes a validated exact raw left-stick coordinate.

2. Forced upward Y family with optional post-SOCD horizontal X selection:
   - forces the selected upward Y coordinate family;
   - optionally selects X from the post-SOCD horizontal result;
   - ignores vertical input except for the rule's configured upward family.

Requirements:
- emits `B` only by default;
- does not emit `Y` unless a separate digital multi-output rule says so;
- left-stick priority category is force override;
- no gameplay labels or action-effect claims.

## 13. Digital multi-output / chord design

One digital rule can emit multiple digital outputs. The final digital output mask is OR-composed across direct logical roles, chord rules, layer roles, and force rules.

`B+Y` is separate from Force Up-B. A Force Up-B rule can emit `B`, and a separate digital multi-output rule can emit `B+Y` for a specific physical button or chord if approved.

Suppression/pass-through should be explicit if ever needed. The default prototype should use OR composition only because it is simpler to validate and avoids hidden macro-like behavior.

## 14. Right-stick / C-stick design

Right stick should be an exact raw output target independent from left stick.

A C-stick direction combination can be authoring shorthand, but the resolved prototype data should be an exact `RightStickTable` entry. ESAM1's angle/math behavior is reference-only and is not required implementation. The compile-time prototype should prefer table-defined right-stick raw outputs over runtime trigonometry.

Left-stick and right-stick analog targets are independent. A force override can own the left stick while a right-stick table owns the C-stick output for the same frame.

## 15. Analog output priority

Use the G7 order per analog target:

1. force override
2. explicit chord profile
3. modifier-combination table
4. normal direction output
5. neutral/default

Priorities are per analog target. Equal-priority same-target conflicts are invalid. Different analog targets are independent, so a left-stick force override does not inherently suppress a right-stick table output.

## 16. Validation plan

Validation should happen at compile time where feasible, or at startup before the selected prototype mode can run.

Hard validation requirements:
- every raw coordinate component is in `[0,255]`;
- no equal-priority matching combo ambiguity;
- no equal-priority same-target analog conflict;
- no undefined active combo with no fallback;
- no use of reference-only ESAM behavior as an active source-backed claim;
- no macro, timing, toggle, or one-shot behavior;
- no overflow or wraparound-intended behavior;
- table sizes stay within explicit compile-time constants.

Diagnostics should keep source facts and future design separate. If a future implementation uses source-backed facts, those facts need source refs. If it uses prototype behavior, it should say that behavior belongs to the selected prototype mode only.

## 17. Prototype profile sizing

Rough conceptual sizing dimensions:
- physical buttons: bounded by the current `InputState` 64-bit rectangle button surface plus separately modeled nunchuk inputs if chosen;
- logical roles: enough for digital outputs, direction roles, modifier roles, layer roles, and rule triggers;
- modifier roles: a small explicit count for the first prototype, chosen before implementation;
- explicit combo profiles: fixed compile-time maximum;
- directional tables: 9 entries per table, with optional validity bits for direction `5` and other sparse entries;
- right-stick tables: fixed compile-time maximum;
- force override rules: fixed compile-time maximum;
- digital multi-output rules: fixed compile-time maximum.

This document does not claim actual RAM or flash usage. Measurement is future work for an approved implementation batch.

## 18. Integration boundary

Relationship to other batches:
- G5 capability model: a future prototype can become source evidence only for its own selected prototype mode, not generic backend capability.
- G6 evaluator contracts: mock evaluator cases can later include prototype-mode capabilities without treating them as current stock support.
- G8 software evaluator prototype: remains software-side and separate; it should consume capability facts rather than firmware-internal assumptions.
- G9 config-backed storage: remains future work because current config structures do not cleanly fit the desired G7 table/profile model.
- Future G11 firmware implementation: requires explicit approval and should begin with isolated scaffolding, validation, and no behavior changes outside the selected mode.

All future work remains separated from Senscope game semantics, export/push workflows, and neutral profile schema changes.

## 19. Open questions before firmware implementation

- What is the first concrete custom mode name/target?
- What exact physical buttons and logical roles belong in the first prototype?
- How many modifier combinations are needed for the first useful prototype?
- Is startup validation feasible, or should the first implementation rely on compile-time static assertions only?
- How will verification prove no behavior changed outside the selected prototype mode?
- How should the prototype be tested without hardware?
- Should the right-stick table be included in the first firmware prototype or deferred?

## 20. Recommended next batches

- G10R: human review of compile-time prototype design.
- G11a: minimal compile-time data-structure scaffold, no behavior wiring, only after approval.
- G11b: isolated custom mode shell, only after approval.
- G11c: exact left-stick table resolver prototype, only after approval.
- G8: evaluator prototype remains software-side and separate.
- G10b: config schema design remains deferred.

Do not proceed to G8, G10b, or G11 without explicit approval.

## 21. Verification

Commands run:
- `git checkout configurator`: succeeded; branch was already `configurator`.
- `git pull origin configurator`: succeeded; already up to date.
- `git status`: clean on `configurator` before branch creation.
- `git branch --show-current`: reported `configurator` before branch creation.
- `git checkout -b design/glyph-compile-time-prototype-g10`: succeeded.
- `sed -n '1,260p' ...` and targeted continuations for required project docs.
- `sed -n '1,260p' ...` and targeted continuations for required source/reference files.

Docs-only verification after edits:
- `git status`: branch `design/glyph-compile-time-prototype-g10`; `docs/project/ACTIVE_AGENT_QUEUE.md` modified; this G10 document untracked before staging.
- `git diff --stat`: tracked unstaged diff showed `docs/project/ACTIVE_AGENT_QUEUE.md | 16 ++++++++++++++--`; the new G10 document was reviewed with `sed` because untracked files do not appear in unstaged `git diff --stat`.

Build was not run because this is a docs-only design task and must not be build-affecting.
