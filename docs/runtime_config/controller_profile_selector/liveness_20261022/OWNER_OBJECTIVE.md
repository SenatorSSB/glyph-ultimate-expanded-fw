Repair GP-NATIVE-002 GameCube selector liveness without redesigning the selector or GameCube protocol

Repository:

`SenatorSSB/glyph-ultimate-expanded-fw`

Current live canonical failure publication:

`3a7a8174f10dfc11563b4a6a6d2029a4e2acf29f`

Failed selector implementation candidate:

`4898951994bcabcaef2846145de2922a674656f8`

Candidate tree:

`7b73fe086fcc6a0c4f5f8010751a64ec2dd07150`

Exact failed UF2:

`7ab99a2f4461c5002c9f71b29f3b7bfe9c87f404970ecd3048e73f8ed885a81e`

Implementation lineage base:

`334fbd06e4541c120b0db423e5be7e112eb1f6f6`

Do not restart the selector chapter from scratch.

The ProfileStore selector architecture is accepted as the basis for repair.

---

# Hardware failure to repair

GP-NATIVE-002 physically passed the intended selector workflow in XInput:

- individually named stored native profiles visible;
- 20 temporary profiles listed;
- controller-menu selection A → B → A;
- exact runtime identity matched each selected profile;
- distinct output values matched;
- selected profile persisted across ordinary reconnect.

GameCube then failed during:

`SEL01 → SEL20 → SEL01`

On the final transition:

- reported values had been correct;
- the display briefly returned to the intermediate parent menu;
- no boot screen followed;
- controller became unresponsive;
- owner reconnect restored operation.

Do not relabel this as a generic crash. No PC/fault capture proves exception, deadlock, or infinite loop.

Exact root cause remains:

`UNPROVEN`

The failed source must remain preserved.

---

# Source-supported liveness defect

The exact failed candidate introduces an asynchronous selection path:

```text
core1/menu:
SetStoredProfile()
→ profile_selection::Request(profile_id)
→ returns

core0:
service_profile_selection()
→ Persist(...)
→ checked Config save
→ committed reboot destination
→ reboot
```

The menu intentionally refuses further controls while:

`profile_selection::Pending() != 0`

This design is correct only if core0 has a bounded opportunity to service the request.

It currently does not on GameCube.

The exact source path is:

```text
core0 application loop
    ↓
service_profile_selection()
    ↓
backend SendReport()
```

A request arriving after the service call can therefore wait behind:

`GamecubeBackend::SendReport()`

That function repeatedly calls:

`GamecubeConsole::WaitForPollStart()`

The linked Joybus receive path can block indefinitely waiting for the first command byte when first-byte timeout is disabled.

Therefore:

> selector request progress currently depends on future GameCube host polling.

That dependency is unacceptable.

The repair must provide a **bounded safe opportunity for core0 to observe and execute a pending selector transaction even when GameCube polling is absent or stalled**.

---

# Do not redesign unrelated systems

This is a liveness repair.

Do not redesign:

- native schema 5;
- ProfileStore;
- menu graphics;
- ProfileStore enumeration;
- backend eligibility;
- stored profile names;
- preprocessing context matching;
- checked Config save semantics;
- GameCube report serialization;
- GameCube electrical protocol;
- SOCD;
- remapping;
- native evaluator;
- profile format;
- controller detection;
- USB backends.

Do not convert selection back into direct menu-core persistence.

Persistence remains core0-owned.

---

# Required invariants

Preserve all of these:

1. menu/core1 remains producer only;
2. core0 remains sole owner of Persistence/ProfileStore mutation;
3. profile selection still performs one checked Config publication;
4. no stored profile body is changed merely by selection;
5. reboot happens only after confirmed successful persistence;
6. failed/refused persistence does not reboot;
7. current backend remains selected after reboot;
8. native preprocessing/context validation remains exact;
9. selector remains blocked against competing reset/write actions while a transaction is pending;
10. GameCube report timing/serialization for ordinary active polling remains unchanged unless a source-proven minimal liveness hook is required.

---

# First milestone — exact liveness audit

Before editing, inspect exact candidate `48989519...`.

Audit:

- `include/core/ProfileSelection.hpp`
- `HAL/pico/src/display/DefaultConfigMenu.cpp`
- `HAL/pico/src/display/ConfigMenu.cpp`
- `config/glyph/common/src/config.cpp`
- `HAL/pico/src/comms/GamecubeBackend.cpp`
- exact pinned Joybus dependency used by the failed build;
- GamecubeConsole `WaitForPollStart` / `WaitForPollEnd`;
- `joybus_receive_bytes`;
- PIO wait paths;
- core0/core1 ownership;
- display/RGB scheduling;
- reboot path;
- flash/persistence critical sections;
- existing polling/timing assumptions.

Reconstruct exact ordering:

```text
menu confirm
→ Request(id)
→ menu returns
→ display redraw
→ core0 service opportunity
→ GC wait
→ persistence
→ reboot
```

Enumerate every point where a pending request can become stranded.

Do not stop after writing this audit unless it reveals an actual architectural contradiction.

Proceed into repair.

---

# Preferred repair direction

The selector transaction itself should remain outside active controller report generation.

The preferred design is:

> Make the GameCube poll-start wait periodically yield a bounded “no command yet” result to the outer backend loop, so core0 can return to its application loop and service pending control-plane work.

This must be done without treating absence of traffic as a valid GameCube command and without changing ordinary report bytes.

Conceptually:

```text
while waiting for GC poll:
    wait for a bounded interval

    if real command arrived:
        continue ordinary GC protocol

    if no command:
        return/yield to core0 application loop
```

Then:

```text
application loop
→ service_profile_selection()
→ if none, re-enter GC poll wait
```

This is preferred over:

- executing persistence inside the Joybus library;
- performing persistence from core1;
- adding a second mutation owner;
- rebooting directly from the menu;
- polling ProfileStore from interrupt/PID code;
- forcing fake GameCube traffic;
- watchdog-resetting around the defect.

The exact API shape is implementation-owned.

---

# Important protocol constraint

A bounded poll-start yield is allowed only if source analysis proves it preserves normal GameCube protocol behavior.

Do not confuse:

- “no command arrived during this bounded host-service interval”

with:

- Joybus protocol timeout/error after a command has begun.

If the linked Joybus implementation already exposes a safe first-byte timeout mechanism, prefer reusing it rather than creating another timer subsystem.

If enabling its existing first-byte timeout changes observable protocol behavior or assumptions, isolate a wrapper behavior that returns to the application loop without treating the condition as a GameCube packet error.

Do not silently modify report timing or wire semantics.

---

# Pending selector priority

When a selector request is pending, bounded progress should be prompt.

Do not require repeated long GameCube idle windows before servicing it.

A reasonable behavior is:

```text
GC wait returns to application loop
→ pending selector detected immediately
→ checked selection transaction executes
→ reboot on confirmed success
```

Do not continue generating ordinary gameplay reports after selection persistence has begun.

---

# Menu behavior

Do not fix the intermediate parent-menu redraw as the primary repair.

That view is explained by current asynchronous behavior and is not itself the liveness defect.

A visual improvement may only be made if it is tiny and incidental after the liveness repair is proven.

No UI redesign.

The existing profile list functionality must remain:

- individually named native records;
- scrollable list;
- backend filtering;
- ordinary/legacy rows retained where eligible.

---

# Postfailure recovery state

Before any new physical testing, treat the controller state after the failed GameCube transition as unknown.

Known retained state from the failure report:

- temporary owned profiles IDs 28–47 remain on device;
- current active identity after reconnect is not yet independently verified;
- postfailure Config integrity is not yet independently verified;
- original profile-record preservation after failure is not yet independently verified.

The repair chapter must prepare a bounded read-only recovery/preflight packet before flashing a repaired candidate.

Do not delete fixtures or restore anything automatically.

---

# Host regression tests

Add a source-faithful regression that reproduces the new dependency:

## Required no-poll test

Simulate:

1. GameCube backend enters poll-start wait;
2. no Joybus command arrives;
3. core1/menu posts a selector request;
4. core0 regains a service opportunity within a finite bound;
5. selector transaction executes;
6. checked save succeeds;
7. reboot request is reached.

Old failed source must fail this regression or demonstrably lack the required bounded progress property.

Repaired source must pass.

## Required normal-poll test

Prove ordinary GameCube polling remains unchanged:

- valid command received;
- output update occurs;
- exact report serialization unchanged;
- ordinary poll-end/send behavior unchanged.

## Interleaving cases

Test at minimum:

- request before entering GameCube wait;
- request immediately after core0 service point;
- request while idle waiting for first byte;
- request while a real GameCube command is already in progress;
- request immediately after report transmission;
- repeated idle yields with no request;
- refused selection;
- checked-save conflict;
- uncertain persistence;
- successful selection.

A request must never interrupt an already-active Joybus command at an unsafe point.

It may wait until the current command completes, but it must not wait indefinitely for a command that never begins.

---

# Existing selector regressions

Re-run all GP-NATIVE-002 selector tests:

- profile-name listing;
- >20 profiles;
- backend eligibility;
- stable ID mapping;
- preprocessing/context validation;
- A → B → A persistence;
- legacy/ordinary rows;
- profile revisions unchanged by selection;
- inactive records unchanged;
- failure/refusal behavior.

Re-run directly affected:

- ProfileStore;
- Persistence;
- ModeSelection;
- GameCube backend;
- boot destination;
- native activation;
- Config validation;
- both enum representations.

---

# Resource proof

The failed candidate had:

- static RAM: 197,936 bytes;
- ceiling: 199,632 bytes;
- core0 conservative bound: 2,048 bytes;
- core1 composition: 1,060 bytes within retained 1,152 bound;
- exact resource proof passing before hardware.

The repaired candidate must fit all unchanged limits.

Do not increase:

- core0 stack;
- core1 stack;
- static RAM ceiling;
- ProfileStore filesystem;
- reserve;
- partition sizes;
- native owner budgets.

Any new timer/service/yield state must be explicitly charged.

Because core0 has zero conservative stack margin, perform a fresh linked-ELF stack/resource proof for all affected paths.

Do not assume the previous 2,048 proof transfers.

---

# Independent review

After implementation:

1. commit exact repair candidate;
2. obtain fresh independent source/safety review;
3. reviewer must specifically inspect:
   - bounded selector progress;
   - GC first-byte wait semantics;
   - active-command safety;
   - report timing/serialization preservation;
   - persistence ownership;
   - reboot ordering;
   - no second writer;
   - resource/stack impact;
4. repair concrete findings;
5. re-review exact final source as required.

---

# Exact build and custody

Build:

`pio run -e glyph_mk6`

or established fallback if required.

Record:

- implementation base;
- failed candidate ancestry;
- repaired candidate SHA/tree;
- exact dependencies;
- linked Joybus dependency identity;
- build flags;
- static RAM;
- flash;
- stack/resource results;
- ELF/BIN/UF2;
- SHA-256;
- content-addressed custody.

No rebuilt/substituted artifact may inherit physical evidence.

---

# Hardware continuation gates

Do not flash automatically.

Prepare a separate owner approval packet.

## Pre-flash readback

Before installing repair candidate:

- identify current unit;
- read current Config;
- read active runtime identity where supported;
- verify IDs 28–47 still exist as expected;
- verify original records;
- verify no unexpected postfailure Config mutation;
- preserve exact backups.

Any unexpected state stops for adjudication.

## Repair hardware test

After explicit owner approval, repeat the smallest decisive sequence.

### XInput regression

Verify quickly:

- list still shows named fixtures;
- A → B → A still works;
- identity/output still correct.

Do not repeat the whole earlier campaign unnecessarily.

### GameCube decisive test

Use the existing fixture profiles.

Perform:

`SEL01 → SEL20 → SEL01`

through the controller Profile menu.

For each transition verify:

- profile list usable;
- selection accepted;
- reboot occurs;
- controller reconnects;
- expected profile behavior is observed;
- controller remains responsive.

Then repeat at least once from a genuinely idle/no-poll or disconnected-host condition if the approved test setup can safely create that condition, because the repaired property specifically concerns progress without incoming GameCube poll traffic.

Do not invent unsafe adapter unplug/replug steps without explicit packet approval.

---

# Acceptance criteria

The repair is not accepted merely because the original freeze fails to reproduce once.

Required acceptance:

1. source-level bounded progress guarantee exists;
2. regression reproduces the old dependency and proves repaired bounded progress;
3. normal GameCube report path remains source/fixture-equivalent;
4. all selector host tests pass;
5. exact resource proof passes unchanged limits;
6. fresh independent review passes;
7. XInput selector regression passes physically;
8. GameCube A → B → A passes physically;
9. repaired exact candidate remains responsive;
10. post-test Config/ProfileStore preservation is verified;
11. exact tested artifact/source correspondence is preserved.

Only then prepare source-free HEP/integration evidence.

Do not merge before exact hardware acceptance.

---

# Stop conditions

Stop and return for owner/domain input only if:

- safe bounded core0 progress cannot be achieved without changing GameCube protocol semantics;
- repair requires a second persistence owner;
- resource limits cannot be met;
- physical recovery/readback shows unexpected stored-state damage;
- repaired candidate fails hardware again;
- any new device mutation requires owner approval.

Do not ask the owner to re-decide selector behavior, profile naming, backend filtering, or reboot-bound activation. Those requirements are already settled.

---

# Commit recommendation

Use a commit message along the lines of:

`Guarantee selector progress across idle GameCube polling`

Preserve failed candidate `48989519...` and its evidence unchanged.