Complete controller-side ProfileStore profile selection for native Ultimate

## Outcome

Complete the missing end-user profile-selection path for the profile-native Ultimate firmware in:

`SenatorSSB/glyph-ultimate-expanded-fw`

The native execution backend, persistent ProfileStore, reboot-bound activation, converter, runtime identity, and resource architecture already exist.

The missing core requirement is:

> The controller's existing scrollable `.Profile` menu must expose the separately stored profiles that are eligible for the currently active controller/backend mode, using their individual stored profile names, and selecting one must safely persist the chosen profile/reference and activate it through the established reboot/reinitialization path.

This is **not** a UI redesign chapter.

Do not redesign the menu graphics, navigation model, icons, list presentation, or general controller UI.

The owner has already used this same scrollable list successfully with more than ten entries. Preserve that interaction. The problem is the data source and selection semantics, not the visual design.

---

# Exact implementation lineage

## Firmware implementation base

Branch from the exact retained profile-native candidate:

`334fbd06e4541c120b0db423e5be7e112eb1f6f6`

Tree:

`0483dbb0cc8f7eb5a1c93cb1d91044f4d3dcf999`

Branch lineage:

`codex/gp-native-001-profile-execution`

This is the exact firmware already installed and physically observed working with the owner's normal Ultimate setup.

Do **not** restart this work from plain `configurator`, because canonical does not yet contain the native implementation.

At startup:

1. verify the live `configurator` SHA and current governance state;
2. verify exact candidate `334fbd06...` still exists unchanged;
3. verify its source/tree/resource evidence;
4. create an isolated successor implementation branch from that exact candidate;
5. preserve canonical only as the control-plane/source-free publication target until later tested-source integration.

Do not silently merge unrelated canonical changes into the native source lineage. Reconcile only changes that are actually required and independently justified.

---

# Current established state

Treat these as starting facts to verify against source/evidence, not items to reinvent.

## Native execution

The exact candidate already contains:

- schema-5 native Ultimate profiles;
- encoding version 1 / engine ABI 1;
- native profile validation/preparation;
- profile-defined direction references;
- finite conditions;
- finite table selection;
- independent digital bindings;
- analogue effects;
- complete nine-way raw-coordinate tables;
- explicit original / remapped / post-SOCD observation domains;
- existing remapping and SOCD reused exactly once;
- legacy V1–V3 execution retained separately;
- fail-closed native-unavailable behavior rather than legacy physical-slot fallback.

Do not redesign this system.

## Storage

ProfileStore already provides:

- stable nonzero profile IDs;
- revisions;
- profile names;
- display ranks;
- payload/schema version metadata;
- checked transactions;
- recovery;
- directory enumeration through `Count()` / `EntryAt()`;
- up to 64 directory entries;
- native schema-5 payload admission;
- boot-bound activation;
- one active and bounded candidate representation rather than all stored profile bodies in RAM.

Do not redesign ProfileStore roots, records, IDs, transactions, recovery, reserve policy, or filesystem layout.

## Current controller menu

The existing `.Profile` menu currently builds its entries from:

`Config.game_mode_configs`

rather than ProfileStore.

On the owner's current controller this produces three entries, all effectively displayed as `Ultimate Runtime`.

The menu already:

- scrolls;
- renders only a bounded number of visible lines;
- supports more entries than are presently populated;
- reboots after profile/mode selection.

The owner does **not** request visual changes.

## Current physical state

The installed exact candidate has a permanent native Ultimate profile:

- ProfileStore ID 27
- revision 1
- schema 5
- name `Ultimate`

The owner's ordinary setup has been observed functioning through the GameCube adapter.

The existing native backend has also physically demonstrated Configurator-driven selection between stored profiles followed by reboot activation.

That proves the backend activation primitive exists.

It does **not** prove controller-menu selection.

---

# Owner product decision — profile visibility

This decision is authoritative for this chapter.

## Preserve backend eligibility

The Profile menu must preserve the established product behavior that profiles shown to the user are filtered according to the currently active communication/controller backend.

Do **not** turn `.Profile` into an unfiltered browser of every ProfileStore record.

The intended behavior is conceptually:

```text
Current backend
    ↓
existing backend/profile eligibility policy
    ↓
eligible selectable controller profiles
    ↓
.Profile scrollable list
```

Examples:

- XInput shows profiles eligible for XInput.
- Nintendo Switch USB shows profiles eligible for that route.
- GameCube shows profiles eligible for GameCube.
- Existing Keyboard/DInput restrictions remain intact.
- A stored profile that is valid but not applicable to the active backend remains stored and untouched; it simply is not shown for that backend.

Audit the actual existing source-backed policy, including at minimum:

- `GameModeConfig.applicable_backends`;
- current `DefaultConfigMenu` behavior;
- backend/default-mode selection;
- Config validation;
- Keyboard/DInput restrictions;
- source-owned default configuration;
- GameCube and USB differences;
- any existing empty-list/default applicability semantics.

Reuse one authoritative eligibility helper/policy.

Do not independently implement slightly different eligibility logic in the menu.

If current source and the owner's established product behavior differ, preserve the owner's requirement above and document the exact source gap being repaired.

---

# Native profile versus GameModeConfig distinction

Do not recreate one `GameModeConfig` row per stored native profile.

That would undermine the multi-profile architecture by scaling fixed Config state with stored profile count.

The stored profile collection must remain ProfileStore-owned.

`GameModeConfig` should remain the bounded controller/preprocessing/backend configuration layer.

Conceptually:

```text
GameModeConfig / controller context
    ├─ controller mode = Ultimate
    ├─ remapping
    ├─ SOCD configuration
    ├─ backend applicability
    └─ native execution eligibility

ProfileStore record
    ├─ stable profile ID
    ├─ name / display rank
    ├─ native schema-5 body
    └─ modifier/function/table program
```

The selector connects these two layers.

Do not convert 20 stored profiles into 20 large Config rows merely to make the existing menu code convenient.

---

# Preprocessing compatibility

Native profiles already bind to their preprocessing context through the established context digest.

Preserve this.

Backend eligibility and preprocessing compatibility are separate concepts.

A profile may be:

- stored and healthy;
- native schema 5;
- generally eligible for the active backend;
- but incompatible with a particular candidate `GameModeConfig` preprocessing context.

Do not activate such a combination.

## Initial implementation rule

First determine from actual source and stored-profile generation whether the intended selectable native profiles share one or more existing bounded native Ultimate `GameModeConfig` template/context rows.

Prefer the smallest implementation that reuses those existing contexts.

For each visible/selectable native profile, the system must be able to resolve a valid pair:

```text
(profile_id, compatible_native_GameModeConfig)
```

where:

1. the GameModeConfig is eligible for the current backend;
2. it is an Ultimate native-capable row;
3. its preprocessing context matches the native profile's context digest;
4. Config validation accepts the resulting configuration.

Do not introduce a new preprocessing storage system unless the actual required profiles cannot be represented through the existing bounded GameModeConfig contexts.

If all intended profiles use the same preprocessing context, preserve that simple architecture.

If source evidence proves multiple distinct preprocessing contexts are genuinely required for ordinary stored profiles, implement the smallest explicit association mechanism that preserves bounded RAM and does not duplicate complete profile bodies in Config.

That expansion must be independently reviewed before implementation if it changes persisted schema or ProfileStore format.

Do not ask the owner to reconfirm this architecture unless a real source-backed incompatibility is found.

---

# Menu behavior

## No visual redesign

Preserve:

- the existing top-level `.Profile` item;
- existing list visuals;
- existing up/down scrolling;
- existing confirm/back interaction;
- existing six-ish visible-row rendering;
- existing fonts/icons/layout.

Do not spend this chapter redesigning the screen.

## Names

Use the actual ProfileStore entry name for stored native profile entries.

The owner's intended profiles have short distinct names.

Do not substitute a shared `GameModeConfig.name` such as `Ultimate Runtime`.

Do not append IDs or verbose debug metadata to the normal visible label unless absolutely necessary to resolve duplicate names.

Use bounded safe copying/truncation into the existing menu text buffer. Never read or render out of bounds.

If duplicate names actually exist, preserve deterministic identity internally and propose the smallest nonvisual disambiguation behavior. Do not invent elaborate UI.

## Ordering

Reuse ProfileStore's existing user-facing ordering / display-rank semantics.

Do not sort by raw profile ID unless that is already the authoritative store ordering.

Reorder operations must continue to determine menu order according to existing ProfileStore semantics.

---

# Menu population architecture

Do not load all profile bodies into RAM merely to list them.

ProfileStore directory metadata already contains:

- stable ID;
- revision;
- payload version;
- name;
- display rank.

Use directory metadata for enumeration wherever possible.

Schema-5/native records can be identified from directory metadata without materializing every profile body.

A menu entry may internally map its small list index to a stable `uint32 profile_id`.

The existing `MenuItem.key` is 8-bit and can therefore safely represent a bounded directory/list index 0–63; do not truncate the actual ProfileStore ID into that field.

Maintain a bounded mapping from menu index to the actual stable profile ID and, when needed, compatible GameModeConfig index.

Example internal concept:

```cpp
struct ProfileMenuTarget {
    uint32_t profile_id;
    uint8_t mode_config_index;
};
```

This is an implementation example, not a required ABI.

Use the smallest representation supported by the source.

Do not create a second general profile cache.

---

# Compatibility checks and payload reads

Avoid ProfileStore body reads simply to redraw the menu.

Directory enumeration must remain metadata-oriented.

If preprocessing compatibility cannot be established from metadata alone, choose one of these source-grounded bounded approaches:

1. resolve compatibility during menu construction by reading one candidate profile at a time with no retained body cache; or
2. list backend-eligible native records from metadata and perform full context validation immediately on selection before any persistent mutation.

Prefer the second if it avoids unnecessary filesystem activity while preserving clear fail-closed behavior.

A context mismatch must:

- perform no Config/profile mutation;
- perform no reboot;
- preserve the current active profile;
- return safely to the menu or visibly refuse through existing menu behavior.

Do not silently substitute another preprocessing context.

Do not activate the profile under an incompatible context.

---

# Preserve existing non-native profiles

Do not accidentally delete existing profile/mode choices from the menu.

Audit all current `GameModeConfig` entries.

The final Profile list should preserve existing eligible non-native/legacy choices where they remain legitimate, while replacing or expanding the native Ultimate placeholder behavior into actual ProfileStore-backed native entries.

A likely model is:

```text
eligible ordinary/legacy GameModeConfig entries
+
eligible stored native Ultimate profiles expanded through native template rows
```

but derive the precise behavior from source.

Avoid duplicate menu entries where a native template GameModeConfig would otherwise appear both as a generic `Ultimate Runtime` row and through its ProfileStore records.

The user should not see a meaningless native template row if its purpose is solely to host stored native profiles.

---

# Selection transaction

This is the most important implementation boundary.

Selecting a stored native profile from the controller must be a checked persistent operation.

Do not rely on an unpersisted RAM pointer or merely change watchdog scratch.

Do not call the Configurator wire protocol from the menu.

Factor/reuse the underlying checked transaction semantics at the core/application layer.

## Required successful outcome

For a selected native profile:

1. resolve the stable ProfileStore ID;
2. resolve its compatible eligible native GameModeConfig row;
3. validate that the profile exists and is of the expected native schema;
4. validate preprocessing/context correspondence;
5. load the currently durable Config into the existing bounded candidate workspace;
6. update only the required fields;
7. set the chosen GameModeConfig's:
   - `ultimate_profile_id`;
   - `ultimate_profile_engine = 1`;
   - legacy `ultimate_profile_config = 0`;
8. preserve its required preprocessing/remap/SOCD state;
9. preserve unrelated Config fields;
10. persist the currently selected backend/default-mode destination as needed so the same active route remains selected after reboot;
11. validate the complete candidate;
12. perform one checked Config publication using existing generation/conflict rules;
13. only after confirmed successful persistence, set the established committed reboot destination;
14. reboot/reinitialize once;
15. activate the selected ProfileStore record through the existing boot path.

Do not perform ProfileStore UPDATE/CREATE merely to select a profile.

Selection changes a reference/context, not the stored profile body.

## Atomicity / failure

Prefer one checked Config publication for the coherent destination rather than two independently vulnerable writes.

If the exact existing APIs make one coherent save impossible, redesign the bounded core transaction helper rather than accepting an intermediate inconsistent state.

A failure, conflict, uncertain result, invalid profile, invalid context, or persistence error must:

- not reboot into an uncommitted destination;
- not alter the stored profile body;
- not silently activate another profile;
- not fall back to old native-slot semantics;
- preserve current known-good behavior.

Reuse the existing transaction/fence/generation machinery.

---

# Backend behavior

Selecting a profile should not unexpectedly change the communication backend.

Examples:

```text
XInput + select Profile B
→ reboot
→ XInput + Profile B

GameCube + select Profile B
→ reboot
→ GameCube + Profile B

USB Switch + select Profile B
→ reboot
→ USB Switch + Profile B
```

unless the existing explicit profile/backend eligibility policy requires otherwise.

Do not merge `.USB Mode` and `.Profile` behavior.

Do not introduce automatic host-protocol selection in this chapter.

Do not change GameCube serialization, Switch serialization, XInput serialization, or controller detection.

---

# Scope boundaries

## In scope

- ProfileStore-backed Profile menu enumeration.
- Existing backend eligibility filtering.
- Short individual stored names.
- Stable menu-index → profile-ID mapping.
- Native preprocessing compatibility validation.
- Checked profile-reference/default-mode transaction.
- Reboot-bound activation.
- Preservation of existing ordinary/legacy menu entries.
- Host tests.
- resource proof.
- exact firmware build/review.
- preparation of a small physical acceptance packet for selector behavior.

## Explicitly out of scope

- Native evaluator redesign.
- New SOCD algorithm.
- New remapper.
- New coordinate engine.
- Modifier semantic changes.
- New profile body format unless proven unavoidable.
- ProfileStore root/directory redesign.
- Increasing directory capacity beyond 64.
- Loading all profile bodies into RAM.
- Hot profile switching without reboot.
- scripts/macros/turbo/sequences.
- visual menu redesign.
- new fonts/icons/layout.
- automatic USB/backend detection redesign.
- Configurator protocol redesign.
- cloud/profile sharing.
- Senscope changes.
- Nunchuk changes.
- Keyboard redesign.
- RT2/factory recovery work.
- resource-limit increases.

---

# Resource constraints

The implementation base is resource-tight.

The exact retained candidate has:

- static RAM: 197,872 bytes;
- accepted whole-firmware static ceiling: 199,632 bytes;
- only 1,760 bytes below that ceiling;
- per-core stack reservation: 2,048 bytes;
- conservative core0 bound: exactly 2,048 bytes;
- core1 bound: 1,152 bytes;
- native active + candidate owners: exactly 7,800-byte engineering cap;
- PreparedView: exactly 560-byte engineering cap;
- native frame + context: exactly 144-byte engineering cap;
- bounded layout charge: 499 / 512 bytes.

Do not casually add static state.

Do not increase:

- stack sizes;
- RAM ceiling;
- ProfileStore filesystem size;
- recovery reserve;
- partition limits;
- native owner caps.

Prefer metadata reuse and short-lived/bounded menu state.

The existing menu already performs dynamic menu allocation. Audit actual heap/startup implications before increasing its maximum allocation to dozens of entries.

If 64 full `MenuItem` objects are unnecessarily expensive, use a bounded virtual/windowed internal representation while leaving the visual interaction identical.

Do not redesign the screen merely to solve internal memory ownership.

Any changed persistence/selection call chain must receive fresh stack/call/interrupt analysis. Do not inherit the exact old 2,048-byte proof blindly after modifying those paths.

---

# Required first milestone — source audit, then continue

Do not stop merely to produce a research memo.

Begin with a bounded source audit and immediately use it to implement unless it uncovers a substantive contradiction.

Audit at minimum:

- `HAL/pico/src/display/DefaultConfigMenu.cpp`
- `HAL/pico/include/display/DefaultConfigMenu.hpp`
- `HAL/pico/src/display/ConfigMenu.cpp`
- `HAL/pico/include/display/ConfigMenu.hpp`
- `include/core/ProfileStore.hpp`
- `HAL/pico/src/core/ProfileStore.cpp`
- `include/core/ModeSelectionTransaction.hpp`
- `src/core/mode_selection.cpp`
- `HAL/pico/src/comms/backend_init.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/include/core/Persistence.hpp`
- `src/core/config_validation.cpp`
- `schema/haybox/config.proto`
- source-owned default GameModeConfig/backend definitions;
- native profile context digest code;
- current selector tests/fixtures;
- exact candidate resource proof.

Produce a concise implementation ledger answering:

1. what currently determines profile visibility;
2. what `applicable_backends` actually means in executable source;
3. how Keyboard/DInput is handled;
4. how a stored native record maps to a native Ultimate GameModeConfig context;
5. how context compatibility is checked;
6. how current menu selection persists backend/mode choice;
7. which existing checked transaction pieces can be reused;
8. what new helper, if any, is actually necessary.

Then proceed.

---

# Tests

## Menu population

Create host/source-faithful tests containing at least:

- zero stored native profiles;
- one stored native profile;
- more than ten profiles;
- at least 20 independently named stored native profiles;
- maximum 64 directory entries;
- mixed legacy and native records;
- mixed backend eligibility;
- duplicate/ineligible records;
- reordered display ranks.

Prove:

- scrolling remains safe;
- index arithmetic remains bounded;
- no item-count underflow/overflow;
- no profile ID truncation;
- names remain NUL-terminated;
- long names truncate safely rather than overrun;
- display rank/order is deterministic;
- hidden profiles remain stored unchanged.

## Backend filtering

Test at minimum:

- XInput;
- Nintendo Switch USB;
- DInput where applicable;
- GameCube;
- Keyboard/DInput special handling;
- empty/default `applicable_backends` semantics from actual source;
- explicitly incompatible profiles.

The same stored profile set should produce the correct backend-specific visible subset.

Do not create selector-specific eligibility semantics that disagree with the rest of firmware.

## Preprocessing/context

Test:

- native profile matching the selected native context;
- profile with different preprocessing digest;
- multiple native template rows if actually supported;
- legacy profile;
- corrupt/missing profile;
- recovered-previous record where existing store semantics allow it.

A context mismatch must not mutate Config or reboot.

## Selection

Use actual persistence/storage fixtures.

Prove:

- selecting native ID A saves A;
- reboot activates A;
- selecting B saves B;
- reboot activates B;
- switching back to A removes B behavior;
- current backend remains unchanged;
- unrelated Config bytes/fields remain unchanged;
- selection performs no ProfileStore body mutation;
- inactive records stay untouched;
- revision does not change merely because a profile is selected;
- transaction conflict refuses;
- uncertain persistence refuses reboot;
- validation failure refuses;
- missing record refuses;
- recovery/read-only states refuse safely.

## Legacy preservation

Existing legacy V1–V3 paths and built-in Ultimate must continue to behave as before.

Do not require every existing legacy profile to become schema 5.

## Resource tests

Measure:

- static RAM delta;
- heap/menu allocation;
- stack frames;
- new persistent Config candidate path;
- changed boot/reboot path;
- ProfileStore metadata use.

Re-run all directly affected old tests plus current native/ProfileStore/Persistence/selector tests.

Because the existing core0 proof has zero conservative margin, rerun the complete affected linked-ELF resource analysis and prove that all formerly accepted resource routes remain valid.

If the selection transaction creates a new core0 route, add it explicitly to the proof set.

No resource limit may be raised to make the implementation pass.

---

# Independent review

After implementation and host/resource tests:

1. commit the complete source candidate;
2. obtain a fresh independent source/safety review;
3. review specifically for:
   - incorrect backend filtering;
   - profile-ID truncation;
   - stale directory pointers;
   - context mismatch;
   - partial Config persistence;
   - reboot before commit;
   - accidental profile mutation;
   - hidden legacy fallback;
   - list allocation/resource regression;
   - changed stack/resource paths;
4. repair only concrete findings;
5. re-review the repaired exact source as required.

Do not create reviewer-of-reviewer loops without a concrete defect.

---

# Firmware build

After source review:

Run the canonical Mk6 build:

`pio run -e glyph_mk6`

Use the established fallback only if required by the environment.

Record:

- exact base SHA;
- candidate SHA/tree;
- generated schema/descriptors;
- build flags;
- static RAM;
- flash;
- stack/resource proof;
- ELF;
- BIN;
- UF2;
- exact byte sizes and SHA-256s;
- content-addressed artifact custody.

Do not rebuild after review and claim the prior review applies.

Do not reuse the existing `334fbd06` hardware/resource PASS for changed source.

---

# Physical acceptance preparation

Do **not** flash automatically.

Prepare a separate candidate-specific packet and return for explicit owner approval before any device mutation.

Keep the physical selector test small and decisive.

The later hardware packet should include at minimum:

## XInput / USB-route selector

1. install exact reviewed candidate;
2. enter existing Profile menu normally;
3. verify multiple separately named eligible profiles appear;
4. verify scrolling through >10 entries;
5. verify backend-ineligible entries do not appear;
6. select native Profile A;
7. observe reboot/reconnect;
8. verify active runtime identity = A;
9. verify one distinctive A behavior;
10. select native Profile B from the controller menu;
11. observe reboot/reconnect;
12. verify identity = B;
13. verify one distinctive B behavior and absence of A-only behavior.

## GameCube selector

If the existing menu is available in the current GameCube route:

1. verify the eligible ProfileStore-backed list;
2. select an eligible native profile;
3. reboot;
4. confirm GameCube remains the backend;
5. confirm selected profile's distinctive behavior in the available observer/game;
6. confirm an XInput-only/ineligible profile is not exposed if such a distinction exists.

Do not infer GameCube acceptance from XInput.

## Persistence

After ordinary power/reconnect:

- selected profile remains the intended one;
- original unrelated stored profiles remain unchanged;
- no profile revision changed solely due to selection;
- Config reference/default destination reflects the selected profile/context.

Use disposable or already-approved test profiles; do not risk original records unnecessarily.

---

# Governance

Treat this as a new bounded continuation chapter correcting the missing controller-side selector requirement.

The owner's direction in this prompt resolves:

- the product requirement;
- no UI redesign;
- ProfileStore-backed selection;
- backend eligibility filtering;
- individual stored names;
- reboot-bound activation;
- preservation of the native architecture.

Follow repository governance mechanically:

- establish the chapter;
- prepare/adopt the required READY work order;
- use one primary source writer;
- use fresh independent source review;
- preserve one canonical source-free publisher;
- preserve hardware/device approval gates.

Do not stop just because ordinary Planner/Curator paperwork is required.

Complete that control-plane work and continue.

Stop for the owner only if:

1. source proves the intended profiles genuinely require a new persisted preprocessing architecture not representable through the existing bounded contexts;
2. implementing the selector cannot fit existing resource limits;
3. existing backend eligibility semantics materially conflict with the owner's stated requirement;
4. a hardware/device mutation packet is ready for approval;
5. a genuine hardware failure occurs.

---

# Completion criteria

This selector chapter is not DONE until all of the following are true:

1. `.Profile` is no longer limited to the three current `GameModeConfig` labels for native Ultimate selection.
2. Stored native ProfileStore records are represented by their own stored names.
3. The existing scrollable UI handles at least 20 stored profiles safely.
4. Visibility preserves existing current-backend eligibility semantics.
5. Ineligible profiles remain stored but hidden for that backend.
6. Existing legitimate non-native/legacy profile choices remain available.
7. Selecting a native entry uses its stable ProfileStore ID, not an 8-bit-truncated ID.
8. The chosen profile is validated against an appropriate native preprocessing context.
9. Selection persists through a checked transaction before reboot.
10. The current backend remains the intended backend after reboot.
11. The selected native profile becomes the actual active runtime profile.
12. Switching A → B → A from the controller itself works without Configurator.
13. No inactive profile bodies are all loaded into RAM.
14. Profile bodies/revisions are not modified merely by selecting them.
15. Existing ProfileStore/recovery/legacy/native behavior remains intact.
16. Fresh exact build and resource proofs pass under unchanged limits.
17. Fresh independent source review passes.
18. Exact physical menu-based selection passes on the approved routes.
19. Source-free hardware evidence is accepted.
20. Only the exact tested source is later integrated.

The key user-visible test is simple:

> The owner opens the existing Profile list, sees the separately named profiles appropriate to the current backend, scrolls through them, chooses one, the controller reboots, and that exact stored profile becomes active.

Do not declare completion merely because Configurator can change `ultimate_profile_id`.

That backend primitive already works.

This chapter exists to make the same stored-profile selection work correctly from the controller itself.