# GOAL — Complete Reuse-First Profile-Native Ultimate Execution

## Outcome

Implement and validate a complete profile-native Ultimate controller-function architecture in `SenatorSSB/glyph-ultimate-expanded-fw`.

The goal is to replace intrinsic Glyph-slot-to-controller-function semantics in the native Ultimate execution path with deterministic profile-defined behavior, **while reusing existing functioning firmware mechanisms wherever they meet the requirements**.

This is a full implementation chapter, not an X1-specific repair or planning-only request.

The owner has reviewed and approved the architecture direction. Complete ordinary governance/work-order authorization and evidence gates before implementation, but do not repeatedly request the same already-resolved design direction.

## Canonical repository

Repository:
`SenatorSSB/glyph-ultimate-expanded-fw`

Primary branch:
`configurator`

Last independently inspected canonical:
`976ba2195b72046b32f7ecdd41063e7bad791ded`

Verify live canonical and source state before acting.

The owner has not submitted any earlier Profile-Native Execution implementation prompts. This is the consolidated initial directive.

Read:

- `AGENTS.md`
- `docs/agent_framework/FUTURE_DAEMON_BOOTSTRAP.md`
- `docs/AGENT_CONTEXT.md`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md`
- `docs/agent_framework/AUTHORIZATION_AND_RUNWAY.md`
- `docs/agent_framework/VALIDATION_AND_GATES.md`
- `docs/agent_framework/HARDWARE_EVIDENCE.md`
- relevant profile, runtime-config, and ProfileStore design documents.

Distinguish current executable source and accepted evidence from older inactive design scaffolds and historical summaries.

Do not infer source authority from a roadmap alone.

## Fundamental owner design decisions

### D1 — Reuse before invention

For every proposed native component, first identify whether an equivalent working mechanism exists in the current firmware.

Classify each capability as:

- `REUSE_AS_IS`
- `REUSE_VIA_ADAPTER`
- `EXTEND_EXISTING`
- `NEW_REQUIRED`

Document:

- exact existing source paths/functions;
- relevant tests or accepted behavior;
- whether its semantics meet the native requirement;
- what integration, if any, is necessary;
- why a new implementation would be required.

Do not build a parallel system merely because the existing one was originally written for Custom Controller mode or for legacy Ultimate.

Do not copy an incompatible implementation merely because its name matches the desired capability.

Actual source behavior controls the decision.

### D2 — Preserve remapping and SOCD

The current physical-to-logical remapping and SOCD implementations are proven infrastructure.

Preserve the existing remapping algorithm, supported SOCD policies, state/history logic and direction-pair behavior wherever possible.

Do not implement a second SOCD resolver for native Ultimate profiles.

Preserve multiple physical sources mapping to one logical input.

The existing remapper's restriction against one physical input remapping to several logical IDs must not become a global restriction against one physical input activating several virtual outputs.

### D3 — Separate input observation stages

Explicitly distinguish:

1. original physical input snapshot;
2. remapped/pre-SOCD snapshot;
3. post-SOCD snapshot;
4. profile-defined activation signals;
5. resolved virtual controller outputs.

Audit the actual order in:

- `ControllerMode::UpdateOutputs`
- `InputMode::HandleRemap`
- `InputMode::HandleSocd`
- `InputState`
- Ultimate digital/analogue processing.

The current controller-mode interface passes the processed input downstream. The native evaluator may need minimal additional access to earlier snapshots.

Design the smallest safe extension that provides this access without changing behavior in other controller modes.

Stateful SOCD must execute once per input frame, not once per output function.

No input-domain aliasing or silent repeated routing.

### D4 — Reuse directional mapping

Reuse the proven direction-reference mapping concept from `CustomControllerMode::stick_direction_mappings` and `GetDirectionButton`, adapted to native Ultimate.

The native evaluator must not intrinsically interpret a particular Glyph slot as Left, Right, Up or Down.

Direction references select the appropriate logical inputs after preprocessing/SOCD. They do not implement SOCD.

Preserve `GameModeConfig` remapping/SOCD ownership initially.

The host-side native-profile package must explicitly describe and validate its associated preprocessing/GameModeConfig context.

Do not pretend a ProfileStore profile update independently changes GameModeConfig remapping.

If actual user requirements force profile-local changes to pre-SOCD direction mappings, first prove that the existing remapper plus associated configuration cannot represent the needed behavior. Propose only the smallest compatible adapter, with explicit validation and migration.

### D5 — Multi-output digital mappings

Reuse the existing per-output digital mapping principle demonstrated in `CustomControllerMode::UpdateDigitalOutputs`.

Support:

- one input activating one virtual digital output;
- one input activating multiple independent virtual digital outputs;
- multiple eligible inputs activating the same digital output;
- bounded conditions/gates;
- intentional composition with direction inputs and table modifiers.

Do not confuse this with the existing Custom Controller `ButtonComboMapping` mechanism, which maps multi-input combinations to one output and suppresses their ordinary functions.

Retain deterministic digital merge semantics.

Preserve the backend-facing `OutputState` contract.

For GameCube, ensure actual L/R serialization is based on `triggerLDigital` and `triggerRDigital`; `buttonR` provides Z. Distinguish these fields explicitly instead of equating generic button names with GameCube report bits.

Preserve existing backend mapping behavior. Do not invent backend equivalence.

### D6 — Normal directions versus forced coordinates

There are two distinct supported behaviors.

**Genuine SOCD-aware direction + digital output**

Example:

Physical P contributes logical Down through existing remapping/SOCD, while independently activating virtual A.

The A binding may observe the original physical input so that SOCD cancellation of Down does not unintentionally cancel A.

**Forced stick coordinate + digital output**

Example:

Physical P activates virtual A and a normal nine-way table modifier.

All nine coordinates in the modifier's table may contain the same raw Down coordinate, so the selected table forces Down irrespective of incoming resolved direction.

This modifier participates in the ordinary deterministic table-selection priority system.

Do not introduce a separate forced-direction resolver or a synthetic SOCD direction for this case.

If another table wins, the forced coordinates do not apply. The digital A binding remains independently active unless the profile explicitly specifies a bounded winner-dependent condition.

The selected raw Down coordinate is profile data, not a guessed magic value.

### D7 — Preserve nine-way modifier tables

Reuse the existing complete nine-way raw-coordinate table architecture, including:

- all direction keys 1–9;
- neutral 5 as an ordinary table entry;
- non-center neutral coordinates;
- full asymmetry;
- 0–255 absolute raw coordinates;
- existing table IDs and accepted values where applicable;
- deterministic selection and conflict rules.

Do not add a second coordinate-solving system.

Do not calculate effective Ultimate angles/radii inside firmware merely from raw coordinates.

### D8 — Reuse finite condition and output-effect machinery

Inspect and reuse the capabilities of:

- `UltimateProfileCondition`
- role evaluation
- `UltimateProfileTableRule`
- `UltimateProfileEvaluator`
- Stage-C output effects
- direction-source transformations
- fixed, inline, table and selected-table coordinate modes
- analogue trigger effects
- digital masks and D-pad routing.

Preserve their useful finite semantics.

Current Stage-C phases referencing hardcoded physical functions, such as RF6/RF7, must not remain intrinsic physical-slot behavior in the native evaluator.

Factor their behavior into generic profile-controlled operations only where necessary.

Do not reimplement already available fixed-coordinate or table-coordinate primitives.

A new generic output-effect type is justified only if the complete current behavior inventory demonstrates something that the existing available primitive types cannot represent safely.

### D9 — Preserve legacy paths

Legacy Ultimate profile versions V1–V3 retain their currently accepted behavior.

Preserve their interpretation, fallback, embedded/source-owned behavior, transport semantics, and data compatibility.

Do not silently reinterpret the historically failed experimental V4 format.

Choose a distinct, safely versioned native payload representation according to actual ProfileStore admission and migration constraints.

Native profiles use a complete native evaluator and do not run the old Glyph-slot semantic resolver before or after native output resolution.

Invalid native data must not silently fall back to legacy physical-slot meanings.

### D10 — No script or macro engine

This architecture is deterministic controller-function configuration.

Do not implement user-programmable scripts, loops, delays, input sequences, turbo, timing automation, or arbitrary code execution.

Bounded finite conditions and explicit compound simultaneous controller outputs are allowed.

Controller semantics are distinct from Smash/game semantics, which remain outside this firmware workstream.

## Required source inventory

Audit, at minimum:

- `src/core/InputMode.cpp`
- `src/core/ControllerMode.cpp`
- `include/core/state.hpp`
- `src/core/socd.cpp`
- `src/modes/CustomControllerMode.cpp`
- `src/modes/Ultimate.cpp`
- `include/modes/UltimateProfileEvaluator.hpp`
- `include/modes/UltimateProfileConfig.hpp`
- `src/core/config_validation.cpp`
- `schema/haybox/config.proto`
- `schema/haybox/config.options`
- current generated Nanopb descriptors
- relevant `ProfileStore` implementation and activation code
- `mode_selection.cpp`
- `HAL/pico/src/comms/GamecubeBackend.cpp`
- other directly affected backend implementations
- GP-BIND-003 runtime identity service
- accepted Stage A/B/C test harnesses and fixtures.

Inspect other firmware modes only to reuse proven mechanisms; do not migrate their unrelated gameplay behavior into Ultimate.

Produce a behavior coverage ledger containing every implemented Ultimate input/effect family, source path, corresponding native primitive, required compatibility behavior, and test evidence.

Include all ordinary modifiers and their interacting functions.

X1-only completion is not acceptable.

## Required architectural end state

The final execution boundary should conceptually resemble:

Physical Input
→ existing remapper
→ existing SOCD processor
→ explicit resolved input context
→ native profile function evaluation
→ deterministic digital and analogue output composition
→ existing backend serialization.

Original/pre-SOCD snapshots may also feed explicitly authorized native function activation.

Keep the existing algorithms that already satisfy the requirement.

New components must have narrow interfaces, explicit validation, and bounded resource use.

The final native evaluator must not contain hardcoded Glyph physical-slot identifiers as intrinsic controller-function assignments.

Physical IDs may appear in configuration, presets, input decoding, hardware interfaces, and tests. They must not be the semantic switch that defines which modifier or digital action is executed.

## Behavior families to support

Cover at minimum:

1. Ordinary left-stick cardinal direction inputs and SOCD.
2. Right-stick cardinal direction inputs.
3. Base/default nine-way stick output.
4. All current X1/X2/Y1/Y2 modifier behavior.
5. Tilt1/Tilt2/Tilt3, including source-supported combinations.
6. Mode and existing sublayers.
7. Current table-selection exclusions, priorities and fallback.
8. Virtual A/B/X/Y/Z digital outputs.
9. Digital L/R and correct analogue trigger relationships.
10. Normal multi-digital outputs, including L+R.
11. Genuine SOCD-aware Down+A.
12. Forced Down+A using normal table selection.
13. Existing historical LT6 Down+A compatibility behavior.
14. Other source-owned compound behaviors, including RF7 and relevant direction-plus-button actions.
15. C-stick diagonal/axis-specific effects.
16. D-pad and LS-to-D-pad behavior.
17. Null and other analogue output effects.
18. Non-center neutral and asymmetrical nine-way tables.

For every family, use existing functionality where adequate.

The legacy LT6 behavior must be characterized accurately. It is not necessarily equivalent to either new clean Down+A configuration in every conflict context.

## Input and composition invariants

One physical input may intentionally contribute to several independent output domains.

Do not impose global exclusive ownership of physical inputs.

Reject ambiguous assignments within a conflict domain when the semantics cannot be determined.

For mutually exclusive left-stick table candidates, use validated unique priorities or explicitly established deterministic conflict rules.

For independent digital outputs, merge contributions according to finite documented semantics.

An input used inside a condition does not automatically claim or consume that input.

A digital output must not disappear merely because an unrelated stick-table override loses.

A profile-data array's serialized ordering must not become hidden runtime precedence.

Use a coherent input snapshot and active-program generation for each output frame.

Preserve existing stateful SOCD history and avoid input-reprocessing side effects.

## Profile format and host tooling

Implement the smallest viable versioned native profile representation that covers the complete inventory.

Before adding fields, inspect which protobuf messages and arrays are embedded by value and how they affect Config, stack, and ProfileStore admission sizes.

Do not duplicate large native tables across Config copies or runtime buffers.

Build a non-destructive host converter that accepts:

- a source-supported legacy Ultimate profile;
- its relevant GameModeConfig preprocessing context;
- an explicit conversion policy.

It should produce:

- a native profile;
- its required or compatible preprocessing-context description;
- a complete correspondence report;
- source identity/provenance.

The converter must not modify original profile or Config bytes.

The converter must distinguish historical compatibility semantics from cleaner user-selected new behaviors.

Where exact parity requires a behavior not supported by existing primitives, document the smallest justified extension and prove it through tests.

## Storage and activation

Preserve:

- ProfileStore IDs/revisions/incarnations;
- checked transactions;
- directory/root/recovery behavior;
- reserve and capacity policy;
- corruption isolation;
- boot-bound activation;
- current Config reference semantics.

### Multi-profile persistence and RAM invariants

Preserve the existing architecture supporting multiple independently stored Ultimate profiles with boot-bound activation.

- Only one selected profile and bounded candidate/compiler workspace may be materialized in RAM. Inactive profiles remain in persistent flash storage.
- Switching profiles must preserve the established flow: update the persistent profile reference → checked commit → reboot/reinitialize → load and activate the selected profile.
- Do not implement hot swapping or cache all stored profiles in RAM.
- Each profile must independently contain its complete native modifier tables, bindings, conditions, and output-function configuration.
- Preserve stable profile IDs, revisions, atomic transactions, recovery behavior, and existing selection mechanisms.
- Maintain the existing 64-entry directory limit unless a separately justified change is authorized.
- Validate capacity for at least 20 fully populated representative native profiles, including storage overhead, retained revisions, transaction staging, and recovery reserve. Treat 20 as a capacity target requiring measurement, not an assumed guarantee.
- Ensure RAM usage is bounded independently of the number of stored profiles.
- Test switching between profiles with different modifiers, reboot persistence, and runtime attestation of the correct active profile.
- Avoid expanding large fixed-size protobuf structures embedded repeatedly in `Config`; measure actual RAM and encoded storage costs before finalizing the format.

**Completion requirement:** The controller must support tens of independently configured persistent profiles without loading all profile bodies into RAM simultaneously, subject to verified storage capacity.

Do not redesign the store.

Add only the smallest admission and activation integration necessary for the new native payload.

Validation and preparation happen outside the polling hot path.

Publish a complete, immutable active native program.

Never retain pointers into mutable decode or transaction scratch.

Stored record identity is not proof of the active runtime program.

Preserve and appropriately extend the GP-BIND-003 attestation relationship so actual runtime profile and engine identity are truthful.

Do not claim a Configurator read proves an earlier gameplay session or extend XInput runtime attestation claims to GameCube without source and physical proof.

## Resource constraints

Measure before full implementation:

- size of current legacy structs;
- size of proposed native schema structs;
- both supported enum ABI representations;
- encoded profile size;
- ProfileStore record admission capacity;
- active/candidate/compiler scratch;
- stack and static RAM;
- firmware flash usage;
- runtime polling cost;
- boot/activation cost.

Use the current exact Mk6 build as baseline.

The prior GP-BIND-003 build reported 187344 bytes static RAM out of 262144. Verify current measurement before committing to an expanded representation.

Do not quietly increase storage, reserve, stack, or memory limits.

No heap allocation, filesystem access, payload parsing, or persistent writes in the controller polling hot path.

If measured native requirements cannot fit within accepted budgets, perform a bounded memory-layout redesign that preserves storage semantics. If that requires crossing a protected resource/product boundary, stop for substantive owner authorization.

## Implementation milestones

### M0 — Baseline and reuse inventory

Verify live canonical, source authority, current queue, GP-BIND-003 completion, and previous GP-BIND-001/002 failures.

Freeze exact accepted legacy test oracles.

Produce the reuse-classification ledger and complete controller-behavior inventory.

### M1 — Design/resource freeze

Define:

- input snapshot/domain boundaries;
- direction references and existing SOCD integration;
- digital bindings;
- table-selection rules;
- output-effect composition;
- conflict-domain semantics;
- format/version and conversion;
- ProfileStore activation;
- attestation;
- resource layout;
- complete verification contract.

Require one strong independent adversarial architecture review focused on actual source gaps and overengineering.

Resolve review defects inside authorized scope.

Freeze the architecture before major source implementation.

### M2 — Native core

Implement the smallest new native evaluator and supporting data structures.

Reuse/adapt existing helpers rather than implementing parallel equivalent algorithms.

Preserve legacy dispatch unchanged.

Create source-faithful host tests against production data representations.

### M3 — Full behavior migration

Implement the complete accepted ordinary Ultimate profile as native profile data and converter output.

Cover all current modifiers and interacting behavior.

Complete generic rebinding, digital composition, direction mapping, roles and conflict handling.

Do not stop after X1.

### M4 — Storage and runtime integration

Add native payload admission, bounded compilation/preparation, boot-bound activation, and active-runtime identity correspondence.

Preserve ProfileStore and Config transaction/recovery behavior.

### M5 — Verification

Run full relevant source tests, including independent legacy/native differential comparisons.

Required cases include:

- every modifier singleton;
- modifier pairs and source-derived higher-order conflicts;
- all nine directions, including neutral;
- Mode and sublayers;
- genuine SOCD Down+A against Up under every supported SOCD policy;
- forced Down+A when its table wins and loses;
- one input activating digital L+R;
- one input activating a direction and digital A independently;
- two inputs activating the same digital output;
- duplicate physical directional sources;
- physical remap to logical direction;
- left/right/up/down SOCD history and release sequences;
- raw/pre-SOCD/post-SOCD activation distinctions;
- current LT6 legacy correspondence;
- X1/X2/Y1/Y2/Tilt rebinding across eligible physical controls;
- right-stick and trigger behavior;
- D-pad/null/compound effects;
- ProfileStore update, readback, reboot and active identity.

Add negative tests for ambiguous bindings, invalid roles/conditions, duplicate priority, missing tables, unsupported payload versions, malformed dimensions, invalid references, and resource exhaustion.

Add mutation tests that demonstrate detection of:

- legacy semantics leaking into native evaluation;
- incorrect physical/logical bit identity;
- double SOCD processing;
- digital A incorrectly depending on post-SOCD Down;
- an unselected table affecting output;
- array-order precedence;
- stale compiled active programs.

The independent legacy and native test oracles must not both call the same newly rewritten semantic resolver.

Preserve exact PASS/FAIL/incomplete states.

### M6 — Build and hardware preparation

Create one final reviewed firmware source candidate.

Run canonical:

`pio run -e glyph_mk6`

If this app environment cannot complete persistent PlatformIO dependency installation, delegate only the exact build/custody work to the owner's persistent terminal environment.

Do not treat environment failure as candidate-source failure.

Record exact:

- base SHA;
- candidate SHA/tree;
- source review;
- Mk6 RAM/flash;
- generated descriptors;
- UF2 bytes/SHA-256;
- durable content-addressed custody.

Create a complete hardware acceptance protocol, approved host scripts, expected-output fixtures and safe restoration procedure.

Use the actual source-supported Config/ProfileStore and Configurator interfaces.

### M7 — Physical acceptance and integration

Require owner approval of the concrete candidate-specific device packet before flashing or profile mutation.

Back up current ordinary Config/ProfileStore state and validate backup custody.

Hardware-test:

- basic ordinary behavior;
- representative every-modifier-family cases;
- important source-derived conflicts;
- genuine SOCD direction-plus-digital behavior;
- forced table behavior and priority;
- L+R digital output behavior;
- multiple modifier rebindings;
- ProfileStore switching/reboot;
- exact active-runtime attestation;
- final restoration.

Capture complete output observations, not only table selection.

Do not infer GameCube PASS from XInput observations or vice versa.

Preserve existing RT2 deferral and recovery restrictions.

Stop on uncertain writes or mismatched device/candidate/artifact identity.

After exact human evidence, process independent HEP.

Merge only the exact hardware-tested source after PASS, fresh source/integration correspondence and required governance.

Publish strict completion separately.

## Agent operating model

This is a substantial coherent architecture chapter.

Use one primary source writer. Parallelize bounded read-only inventory, resource research and oracle preparation only where they cannot produce conflicting implementation.

Use a strong-model architecture challenge at M1 and fresh independent source review before firmware handoff.

Do not create repeated reviewer-of-reviewer cycles or a standing team merely for status reporting.

The chapter daemon owns governance and coordination; stronger finite workers may own high-coupling design/implementation.

Do not silently invent unavailable model identifiers. Respect current capability and routing contracts.

Keep all useful evidence durable in repository files.

Do not modify unrelated firmware modes, UI systems, firmware transport protocols, keyboard behavior, Nunchuk behavior, or Senscope.

## Autonomous progression

Proceed mechanically through all authorized milestones without returning after every commit, checker result, or source review.

The owner has approved the architecture direction and its bounded implementation scope, including necessary native schema, evaluator, conversion, and activation integration.

However, respect the repository's actual complete READY work-order requirements and substantive Curator gates.

If source inventory reveals a genuine new product behavior choice, a budget conflict, or an incompatibility between the owner's requirements and accepted hardware behavior, stop for that decision rather than inventing semantics.

Do not stop merely because the current READY queue must be populated through its ordinary governance process.

Do not perform controller writes/flashing without concrete device-packet approval.

A hardware failure requires preserved exact evidence and source-grounded new repair authorization, not blind iteration.

## Completion contract

The chapter is DONE only when:

1. Every in-scope existing controller-function family is represented.
2. Existing direction remapping and SOCD are reused without unnecessary replacement.
3. Native evaluation has no inherited physical-slot controller-function semantics.
4. Independent digital outputs can be combined on the same physical input.
5. Forced directions are expressible through ordinary modifier tables.
6. Legacy V1–V3 behavior and stored data remain compatible.
7. Native ordinary-profile conversion passes complete relevant correspondence.
8. Native modifiers can be rebound without residual old-slot behavior.
9. ProfileStore and attestation identify the actual active runtime program correctly.
10. Memory, build, validation and review gates pass.
11. Fresh candidate-specific hardware acceptance passes.
12. Exact tested-source integration and strict DONE are verified live on canonical.

Do not declare success because X1 alone works, because a synthetic fixture passes, or because a source candidate builds.

The intended result is a complete, reusable, profile-native Ultimate controller-function architecture built from the working mechanisms we already have—not an unnecessary replacement for them.
