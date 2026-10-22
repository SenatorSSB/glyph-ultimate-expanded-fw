# CONTINUATION — Integrate exact tested GP-NATIVE-002 source and complete the chapter

Continue the GP-NATIVE-002 controller ProfileStore selector work you previously implemented, diagnosed after the GameCube hardware failure, repaired, rebuilt, reviewed, and handed off for integration.

Do **not** restart planning or implementation.

The repair has passed the applicable hardware acceptance scope. Your job now is to carry the exact tested source through canonical integration, independent integration review, and strict completion.

---

# Live state — verify before acting

Repository:

`SenatorSSB/glyph-ultimate-expanded-fw`

Primary branch:

`configurator`

Current live canonical at continuation start:

`3a7a8174f10dfc11563b4a6a6d2029a4e2acf29f`

Commit message:

`Record GP-NATIVE-002 GameCube hardware failure and stop`

Exact repaired and hardware-tested firmware candidate:

`8b2c75e35bb990aee06de3165e5780082c4f08ad`

Tree:

`cd5d280e3b04a3b4e9d9a1bc760917406175b988`

Branch:

`codex/gp-native-002-gc-liveness`

Exact tested UF2:

`ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760`

UF2 size:

`1046016`

Source-free acceptance/handoff branch:

`codex/gp-native-002-gc-liveness-handoff`

Current handoff tip:

`7ee104debde92c61390ff44fcc35afa14e9e5548`

The exact failed predecessor remains:

`4898951994bcabcaef2846145de2922a674656f8`

with failed UF2:

`7ab99a2f4461c5002c9f71b29f3b7bfe9c87f404970ecd3048e73f8ed885a81e`

Preserve that historical FAIL unchanged.

Before any publication or integration:

1. live-verify all refs above;
2. verify candidate F and its tree are unchanged;
3. verify exact UF2 custody/hash;
4. verify the source-free acceptance evidence still binds exactly F `8b2c75e3...`;
5. verify canonical has not moved unexpectedly;
6. if canonical has moved, reconcile governance/source correspondence explicitly rather than assuming this prompt's SHA is still current.

---

# Accepted hardware result

The repaired candidate has now passed the normal required selector workflows.

## XInput

Physical selector sequence:

`SEL01 → SEL20 → SEL01`

PASS.

Observed/recorded:

- individually named stored profiles remain visible;
- normal selection-driven reboot/reconnect;
- runtime identities matched IDs `28 → 47 → 28`;
- schema5/revision1 identity correspondence matched;
- expected distinct outputs matched;
- controller remained responsive.

## GameCube

Physical selector sequence:

`SEL01 → SEL20 → SEL01`

OWNER-REPORTED PASS on the normal Switch-through-GameCube-adapter setup.

Owner report:

> “everything worked without a hitch on the GC adapter.”

No Mac telemetry or raw GameCube runtime identity was captured or inferred.

Do not upgrade this to a stronger claim.

## Preservation

Post-test readback PASS:

- Config remained coherent and byte-exact against the approved Stage-A state;
- all **43 profiles** remained unchanged;
- wrappers unchanged;
- revisions unchanged;
- names/ranks/directory metadata unchanged;
- no profile body mutation occurred through selection;
- store status remained clear.

## Conditional no-poll row

Physical powered/no-poll testing remains:

`NOT_TESTED`

This is **not** a failure and is **not** a physical PASS.

The original owner objective made this test conditional on a safe, established setup being available.

No such setup is available.

The source-faithful old/new regression demonstrates the repaired bounded-progress property in software. Do not fabricate physical evidence or request an unsafe topology merely to fill this row.

The applicability correction is already documented.

## Historical root cause

The original GameCube freeze root cause remains:

`UNPROVEN`

Do not relabel the repaired liveness defect as proven physical causation.

The correct historical statement is:

- a concrete source-level selector liveness defect existed;
- it was capable of producing indefinite pending selection under absent GameCube traffic;
- it was repaired;
- exact old/new regression proves the property change;
- the normal previously failing physical workflow now passes;
- no captured PC/poll state established that this was definitely the cause of the historical freeze.

---

# Source-free acceptance material

Use and verify the existing handoff material under:

`docs/runtime_config/controller_profile_selector/liveness_candidate_8b2c75e3/`

Especially:

- `RESULT.md`
- `README.md`
- `OWNER_PACKET.md`
- `hardware_20261023/evidence.json`
- `hardware_20261023/SUMMARY.md`
- `hardware_20261023/CONDITIONAL_TEST_RECONCILIATION.md`
- `hardware_20261023/hep_conformance.json`
- `hardware_20261023/final_e_review.json`
- `hardware_20261023/validation.json`
- `hardware_20261023/INTEGRATION_HANDOFF.md`

The source-free acceptance preparation has already passed focused independent review.

Do not repeat the hardware campaign.

Do not rebuild and transfer acceptance to a new artifact.

---

# Critical integration fact

Canonical `configurator` does **not** contain only the missing GameCube liveness repair.

The tested F lineage includes:

1. the previously unmerged profile-native Ultimate implementation;
2. GP-NATIVE-002 controller-side ProfileStore selector implementation;
3. the subsequent GameCube liveness repair.

Therefore:

> Do not integrate only `lib/glyph-joybus-pio/src/GamecubeConsole.cpp` or only the final liveness patch.

The canonical integration must represent the **entire exact tested firmware-source state of F** for all source paths required by the accepted candidate.

Compute the exact canonical → F source delta mechanically.

Do not guess the integration path list from recent commits.

For every firmware-critical changed path:

- canonical integration bytes must equal tested F bytes exactly;
- no manual cleanup/refactoring;
- no formatting-only alterations;
- no regenerated-but-different equivalent source;
- no later “improvement” during merge.

Source-free governance/docs may necessarily differ from F, but firmware source correspondence must be exact.

---

# Goal

Produce a genuine tested-source integration `I` satisfying the repository's R → E → I governance model:

```text
reviewed tested F
        ↓
accepted source-free E
        ↓
exact source integration I
        ↓
independent integration review
        ↓
strict GP-NATIVE-002 DONE
```

Do not create another implementation candidate.

Do not perform controller operations.

Do not flash.

Do not modify profiles.

Do not perform another hardware test unless integration discovers an actual tested-source correspondence violation that invalidates the accepted tuple.

---

# Step 1 — Reconcile governance state

Read the current mandatory workflow/governance docs from live canonical, including:

- `AGENTS.md`
- `docs/AGENT_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md`
- applicable `docs/agent_framework/*`
- selector chapter records
- hardware evidence contract
- strict completion rules.

The current canonical state intentionally records GP-NATIVE-002 as hardware failed because the repaired acceptance remains on the handoff branch.

Do not treat that historical canonical failure record as invalid.

Instead, publish the normal successor acceptance transition preserving chronology:

```text
48989519 hardware FAIL
→ repair 8b2c75e3
→ exact acceptance PASS under applicable scope
→ integration
→ DONE
```

Never rewrite the failure as if it did not happen.

---

# Step 2 — Establish immutable accepted evidence E

The handoff already contains a reviewed source-free evidence record binding:

Candidate F:

`8b2c75e35bb990aee06de3165e5780082c4f08ad`

UF2:

`ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760`

Verify:

- hardware evidence schema;
- F SHA/tree;
- UF2 SHA/size;
- source review;
- exact build;
- ELF/BIN/UF2 correspondence;
- content-addressed custody;
- XInput PASS;
- normal GameCube PASS;
- preservation PASS;
- physical no-poll NOT_TESTED with correct conditional disposition;
- root cause UNPROVEN;
- Nunchuk NOT_TESTED;
- no unsupported GameCube runtime-identity claim.

Use ordinary canonical curation/publication to adopt the exact accepted E as required by current governance.

Do not manufacture a different E.

Do not change its factual claims to obtain cleaner status wording.

---

# Step 3 — Exact tested-source comparison

Before integrating, compute a complete path-level comparison between:

- current live canonical;
- exact tested F `8b2c75e3`.

Classify each differing path into:

1. firmware/product source required from F;
2. generated/build-affecting source required from F;
3. tests/fixtures required to preserve the accepted implementation;
4. source-free evidence/governance;
5. historical/private/build artifacts that must not be merged;
6. unrelated differences.

For categories 1–3:

- establish exact hashes;
- establish whether F bytes must become canonical bytes;
- document the resulting reviewed integration path set.

Do not assume the recent repair commit's file list is the complete integration set.

Remember that F descends from the unmerged native implementation and selector implementation.

---

# Step 4 — Integrate exact F source

Construct the canonical integration from the live canonical base.

For every accepted firmware source path:

> resulting canonical bytes must be byte-identical to exact tested F.

Preserve the source-free canonical failure/acceptance chronology around those source bytes.

Do not merge F's historical working docs wholesale if they conflict with canonical governance history.

Do not merge private absolute-path evidence.

Do not merge build outputs into source unless repository policy explicitly requires retained evidence.

Do not rebuild the source and call that correspondence.

The integration claim is source identity, not rebuilt-artifact identity.

---

# Step 5 — Accepted-transition/catalog publication

Create the genuine accepted transition/catalog record required by the repository.

It must bind at minimum:

- work order: `GP-NATIVE-002`;
- implementation lineage base;
- failed predecessor `48989519...`;
- failed artifact identity;
- tested repaired F `8b2c75e3...`;
- exact F tree;
- accepted UF2 SHA/size;
- source review reference R;
- accepted source-free evidence E;
- integration commit I;
- exact reviewed changed/source paths;
- hardware result PASS for applicable scope;
- physical no-poll row NOT_TESTED;
- root cause UNPROVEN;
- preservation result;
- remaining Nunchuk limitation;
- exact tested-source correspondence status.

Do not claim a physical no-poll PASS.

Do not claim raw GameCube runtime identity.

Do not claim the old freeze cause was proven.

---

# Step 6 — Focused post-integration validation

Run the appropriate current focused validations.

At minimum verify:

## Exact source correspondence

For every firmware-critical reviewed path:

`I[path] == F[path]`

byte-for-byte.

No exceptions unless separately source-reviewed and hardware-revalidated.

## Selector behavior tests

Re-run host-level directly affected tests for:

- metadata enumeration;
- stored names;
- 0/1/11/20/64 entry cases;
- backend eligibility;
- legacy/native coexistence;
- stable profile-ID mapping;
- context matching;
- selection persistence;
- conflict/refusal;
- uncertain save;
- recovery;
- A → B → A;
- GameCube liveness no-poll old/new regression;
- active-command protection;
- ordinary report equivalence.

## Existing native system

Run directly affected existing:

- native schema/evaluator tests;
- ProfileStore tests;
- Persistence tests;
- both enum ABI tests;
- Config validation;
- mode selection;
- boot destination;
- relevant GameCube backend tests.

## Governance/framework

Run required:

- navigation;
- sequence;
- diff;
- agent-framework checks;
- accepted-transition validation;
- catalog validation;
- strict completion prerequisites.

Preserve known historical framework debt honestly.

Do not alter framework checkers merely to manufacture aggregate PASS.

If an existing known baseline checker still fails identically for unrelated historical reasons, record that exact comparison.

---

# Step 7 — Resource correspondence

The tested F resource facts are:

- static RAM: `198288 / 199632`;
- core0 conservative: `2048 / 2048`;
- core1 composition: `1060`, within retained `1152`;
- bounded layout: `506 / 510`, within the unchanged 512 envelope;
- all 140 old routes;
- 39 selector routes;
- 14 new GameCube routes;
- unchanged resource ceilings.

Because integration source is required to be exact F source, do not produce a new product/resource claim from different source.

Verify:

- critical source identity;
- compiler-relevant generated identities where required;
- no integration-only source changes;
- no linker/build configuration drift.

A fresh build may be used as an integration sanity check if governance requires it, but:

> it does not replace or supersede the exact hardware-tested UF2.

Do not transfer physical acceptance to newly built bytes.

The accepted hardware artifact remains the exact retained F UF2.

---

# Step 8 — Independent integration review

After integration candidate I is committed, obtain a fresh independent integration review.

The reviewer must verify:

1. correct canonical ancestry;
2. accepted E is genuine and immutable;
3. exact tested F source is integrated;
4. reviewed firmware path hashes match F;
5. no extra firmware behavior entered I;
6. failure chronology is preserved;
7. selector XInput/GameCube accepted scope is represented accurately;
8. physical no-poll remains NOT_TESTED;
9. root cause remains UNPROVEN;
10. source/artifact/custody tuple is not substituted;
11. no private evidence leaked;
12. catalog/transition record is genuine;
13. focused validation is sufficient;
14. no hardware PASS was transferred to changed source.

If review finds a firmware-source mismatch against F:

STOP.

Do not casually patch I.

Any behavior-affecting source change after hardware acceptance invalidates direct acceptance transfer and requires affected revalidation.

---

# Step 9 — Canonical publication

Only after independent integration review PASS:

publish/merge exact integration I into `configurator` according to repository governance.

Live-verify remote canonical afterward.

Verify again:

- integrated source bytes;
- expected parentage;
- accepted-transition/catalog record;
- current state;
- queue;
- evidence references.

Do not rely only on local branch state.

---

# Step 10 — Strict GP-NATIVE-002 completion

After live source integration is verified, run the repository's strict completion procedure as a separate publication.

GP-NATIVE-002 may be marked DONE only if the strict completion record establishes:

- exact implementation base;
- exact reviewed F;
- accepted E;
- exact integrated I;
- exact reviewed source path correspondence;
- integration review;
- focused validation;
- exact hardware-tested artifact;
- applicable hardware PASS;
- no unresolved required evidence gap.

Preserve these limitations in DONE:

- historical first selector candidate hardware FAIL;
- old freeze root cause UNPROVEN;
- physical no-poll NOT_TESTED because safe conditional setup unavailable;
- Nunchuk NOT_TESTED;
- no raw GameCube runtime identity claim;
- target electrical timing/high-water claims remain only where actually measured.

Those limitations do not prevent selector completion if current governance agrees they are outside the required accepted scope.

---

# Product behavior being integrated

The final integrated selector behavior must remain exactly the tested behavior:

## `.Profile` menu

- existing visual layout unchanged;
- existing scroll behavior unchanged;
- stored native profiles shown using their own stored short names;
- backend-ineligible profiles hidden rather than deleted;
- eligible ordinary/legacy rows retained;
- no meaningless duplicate native template labels where expansion applies.

## Profile IDs

Menu index is never treated as stable ProfileStore ID.

Stable stored IDs remain full-width internally.

## Selection

Controller menu selection:

```text
choose stored native profile
→ core1 posts bounded request
→ core0 receives request
→ selected body/context validated
→ one checked Config publication
→ committed destination set
→ reboot
→ selected native record activated
```

Profile bodies/revisions are not modified by selection.

## GameCube liveness

The repaired behavior must remain:

- pending selection gains a bounded core0 service opportunity when no GameCube command has begun;
- real active Joybus commands are not interrupted unsafely;
- absent first byte is never dispatched as a command;
- normal report serialization remains unchanged;
- no second persistence writer;
- no watchdog workaround;
- no fake traffic.

---

# Things you must NOT do

Do not:

- redesign the selector;
- redesign schema 5;
- modify profile semantics;
- change menu visuals;
- change SOCD;
- change remapping;
- redesign ProfileStore;
- increase stack/RAM/storage limits;
- add a new backend;
- perform another flash;
- delete fixtures;
- clean up the controller;
- repeat hardware acceptance;
- demand a physical no-poll topology;
- claim old root cause proven;
- merge only the final one-file repair while omitting the tested native/selector source lineage;
- rebuild and substitute a different artifact;
- mark DONE before tested-source integration is live and independently reviewed.

---

# Existing retained fixture state

The controller currently retains the twenty owned selector fixtures:

IDs `28–47`

alongside the original stored profiles.

Do not perform device cleanup in this continuation.

Fixture cleanup, if ever desired, is a separate owner/device operation and is unnecessary for source integration.

---

# Stop rules

Continue autonomously through governance, integration, review, publication and strict completion.

Stop for the owner only if:

1. live canonical has changed in a way that creates a substantive source conflict;
2. exact tested F bytes cannot be integrated without modifying behavior;
3. accepted evidence/custody tuple cannot be verified;
4. independent integration review finds a behavior-affecting discrepancy;
5. governance unexpectedly requires new device action;
6. any proposed source change would invalidate exact hardware acceptance.

Do not stop for ordinary documentation, queue, catalog or publication mechanics.

Resolve those autonomously.

---

# Expected final report

At completion, report:

## Canonical

- pre-integration canonical SHA;
- integration I SHA;
- final strict-DONE canonical SHA.

## Exact accepted implementation

- F SHA/tree;
- exact accepted UF2 SHA/size;
- evidence E reference.

## Integration

- exact firmware paths integrated;
- byte-for-byte F correspondence result;
- catalog/accepted-transition identity;
- independent integration review result.

## Validation

- focused selector/native/GameCube tests;
- governance/framework results;
- known retained framework debt;
- no unsupported aggregate PASS.

## Final status

Explicitly state whether:

`GP-NATIVE-002 = DONE`

and separately state preserved limitations:

- historical freeze root cause UNPROVEN;
- physical no-poll NOT_TESTED;
- Nunchuk NOT_TESTED;
- no hidden GameCube runtime-identity inference.

No further implementation or hardware work should be performed unless a real integration contradiction is discovered.

## Commit-message guidance

Use clear commit messages separating the stages, for example:

- integration:
  `Integrate hardware-accepted native profile selector`
- strict completion:
  `Complete GP-NATIVE-002 after tested-source integration`

Do not squash away the historical hardware FAIL or acceptance chronology.

