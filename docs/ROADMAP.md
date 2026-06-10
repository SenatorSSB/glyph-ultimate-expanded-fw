# Glyph Roadmap

Status label: CURRENT.

This is the clean long-term Glyph-side roadmap. Dated calibration packets remain
evidence, but current direction should be read here first.

## Status Taxonomy

Current roadmap status and requirement fields are separate. `BLOCKED` is a
legacy calibration label only; older packets may use it for user input, source
research, product approval, hardware, safety policy, or not-yet-started work.
Current docs use these labels instead:

- `COMPLETE`
- `CURRENT_BASELINE`
- `READY_FOR_ENGINEERING_DESIGN`
- `READY_FOR_SOURCE_RESEARCH`
- `READY_FOR_PROTOTYPE`
- `READY_FOR_USER_PRODUCT_DECISION`
- `WAITING_FOR_USER_ARTIFACT`
- `WAITING_FOR_HARDWARE_TEST`
- `FUTURE_PHASE`
- `NOT_STARTED`
- `FORBIDDEN_BY_POLICY`
- `OUT_OF_SCOPE`

Each phase lists requirement fields separately:

- `requires_user_domain_input`
- `requires_user_product_approval`
- `requires_source_research`
- `requires_hardware_test`
- `requires_user_artifact`
- `requires_firmware_change`
- `requires_safety_review`
- `requires_schema_decision`
- `requires_transport_authority`

## Phase 0 - Current Hardcoded Firmware Baseline

Goal: Preserve the current hardcoded Glyph/HayBox firmware behavior and its
recorded hardware scope.

Status: `CURRENT_BASELINE` / `COMPLETE` for the current non-nunchuk scope.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=false`; `requires_source_research=false`;
`requires_hardware_test=false` for already recorded scope.

Engineering/source research can proceed: yes, for preservation, inventory, and
checker maintenance only.

Next concrete action: preserve the current baseline and use it as the comparison
target for future generated artifacts.

Required evidence: source files, hardware result packets, current checker output,
and recorded artifact/hash data where available.

Stop conditions: unexpected firmware behavior, unclear hardware scope, missing
result provenance, or any attempt to expand nunchuk claims.

Explicit non-goals: no runtime-loaded config, no device write, no external
adapter output, no Senscope game-semantic changes.

## Phase 1 - Senscope Neutral Profile Format

Goal: Keep a neutral Senscope-owned profile concept separate from Glyph firmware
and game semantics.

Status: `READY_FOR_ENGINEERING_DESIGN`, but in the Senscope workstream.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=false` unless schema product choices are being
requested; `requires_schema_decision=true` before schema changes.

Engineering/source research can proceed: yes, in the Senscope workflow when that
workstream is explicitly active.

Next concrete action: Senscope-side profile/save/load work outside this repo.

Required evidence: explicit user approval for schema changes and Senscope-side
source authority when that workstream is active.

Stop conditions: task requires changing neutral profile schema or coupling
controller constraints into game-semantic solving.

Explicit non-goals: no Glyph firmware edits, no game-semantic source promotion,
and no schema changes from this repo alone.

## Phase 2 - Generated-Config/Evaluator Bridge

Goal: Use source-backed generated config artifacts to drive offline evaluator
checks and compare expected controller/backend behavior.

Status: `READY_FOR_ENGINEERING_DESIGN` / `READY_FOR_PROTOTYPE`.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=false`; `requires_source_research=false` for
source-backed generated-config/evaluator artifacts.

Engineering/source research can proceed: yes, when scoped to docs/tools,
fixtures, validators, and source-backed evaluator inputs.

Next concrete action: connect Senscope neutral profile outputs to
generated-config/evaluator artifacts without changing firmware source or
Senscope game semantics.

Required evidence: source-parsed tables, role maps, behavior-case fixtures,
deterministic checker output, and explicit non-claims.

Stop conditions: generated data depends on inferred behavior, unsupported roles,
or undocumented backend behavior.

Explicit non-goals: not firmware input, not runtime-loaded config, not hardware
validation, and not device transport.

## Phase 3 - Generated C++ Constants / Firmware Build Path

Goal: Keep the current source-owned generated-like constants firmware path
stable for the merged 27-table `StickPoint[9]` baseline and keep future deltas
source-backed.

Status: `CURRENT_BASELINE` / `COMPLETE` for the current baseline behavior-preserving firmware path.

Note: before the approved merge, this work sat at `READY_FOR_ENGINEERING_DESIGN`.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=false` for the merged baseline itself.

Future generated constants changes remain allowed only through source-backed
review, build, hardware plan/result, explicit product approval when behavior/
build-path risk exists, and no runtime-loaded config/device-write expansion.

Engineering/source research can proceed: yes, for source-sync checker
maintenance, source-backed diff review, and docs/tools validation of the current
baseline.

Next concrete action: maintain the source-sync checker and keep future
generated constants deltas behind source-backed review, build, hardware
plan/result, and approval gates.

Required evidence: exact source diff, build output, artifact inspection,
behavior-preserving checker coverage, and hardware plan/result for any future
delta.

Stop conditions: generated constants drift from source, build fails, or a
future delta would alter behavior without approval and test plan.

Explicit non-goals: no broad refactor, no runtime-loaded config interpreter, no
device write, no profile artifact change, no firmware flashing automation, no
nunchuk validation claim, and no intentional controller behavior change.

The source-owned active runtime config preselection scaffold has a recorded
`HARDWARE_PASS` on
`runtime-active-config-state-source-owned-preselection-hardware-result`; it is
behavior-preserving, keeps RF5/RF6/LT6 expressions unchanged, and is safe to
use as the repair-architecture basis without expanding runtime-loaded config
or device-write scope.

The candidate-state materialization scaffold is the next safe source-level
architecture step after that baseline. Candidate state remains pre-publication
scaffolding only; `ResolveActiveRuntimeConfig()` and `UpdateAnalogOutputs(...)`
continue to consume only the stable selected `RuntimeConfigView`.

The parsed-candidate-present/source-owned-published diagnostic is a hardware
test branch (`diagnostic_parsed_candidate_present_source_owned_published`), not
an activation repair. It keeps parser bridge, candidate
materialization, and equivalence validation present while forcing active
publication to `kSourceOwnedCurrentBaselineRuntimeConfig`. Candidate active
publication remains unsafe after the
`runtime-config-parsed-candidate-opt-in-diagnostic-batch` hardware failure and
must not merge without a separate source-backed, hardware-gated repair.

## Phase 4 - Offline Official Configurator Export Target Contract

Goal: Define the offline target-contract boundary for official-configurator-
oriented comparison after the profile format exists.

Status: `READY_FOR_ENGINEERING_DESIGN` after the official corpus correction.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=true` before exporter implementation;
`requires_user_artifact=false` for the initial corpus, though exact configurator
metadata may still be provided if available; `requires_schema_decision=true`
because the Senscope neutral profile is a prerequisite.

Engineering/source research can proceed: yes, for export target contract,
source-authority packet, preview fixture, and candidate validator design.

Next concrete action: define the export target contract and offline preview /
checker; do not generate vendor-specific output until source support and
approval exist.

Required evidence: official corpus manifest, fixture hashes, source-authority
classification, and offline preview validation report or blocker.

Stop conditions: vendor format is undecided, official source authority is
insufficient, or compatibility would be claimed from incomplete evidence.

Explicit non-goals: no production export, no WebSerial/device write, no
protobuf binary write, no firmware flashing automation, and no universal
official compatibility claim.

## Phase 5 - Manual Import/Export And Hardware Validation Loop

Goal: Compare offline candidates through manual official configurator
import/export and separately record any hardware validation.

Status: `FUTURE_PHASE`; becomes `WAITING_FOR_USER_ARTIFACT` or
`WAITING_FOR_HARDWARE_TEST` only after a candidate or firmware artifact exists.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=false` for result recording;
`requires_hardware_test=false` until a test artifact exists.

Engineering/source research can proceed: not applicable until a candidate
exists, except for maintaining templates/checkers.

Next concrete action: none until an offline candidate or firmware artifact
exists.

Required evidence: exact app/version/source reference when available, input and
output hashes, no-device/write caveats, hardware artifact provenance, and result
packet.

Stop conditions: test route requires push-to-device behavior, WebSerial write,
firmware flashing automation, or undocumented compatibility claims.

Explicit non-goals: no automated flashing, no direct device write, no nunchuk
validation unless executed and recorded.

## Phase 6 - Stable Firmware + Bounded Config-Owned Modifier Data

Goal: Define a stable firmware boundary where future config may own bounded
modifier data while firmware owns evaluator semantics.

Status: `PHASE6_DESIGN_COMPLETE_NOT_IMPLEMENTED` for docs/spec/tooling;
runtime-loaded config implementation remains `FUTURE_PHASE`.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=true` before implementation;
`requires_firmware_change=true` only for the implementation branch;
`requires_safety_review=true`.

Engineering/source research can proceed: yes, for checker maintenance and
future implementation-slice design if scoped to docs/tools.

Next concrete action: inspect the Phase 6 design artifacts and keep future
implementation slices behind product approval, source authority, build, and
hardware gates.

Required evidence: source-backed ownership split, bounded schema, validator
contract, fallback policy, and hardware validation plan.

Stop conditions: config attempts to own evaluator phase order, scripts, macros,
turbo, timing automation, or history-dependent logic.

Explicit non-goals: no arbitrary scripting, no hidden transport behavior, no
runtime interpreter implementation without explicit approval.

## Phase 7 - Runtime-Loaded Config Interpreter

Goal: Implement a firmware-owned bounded runtime config interpreter only if
future approval and source authority exist.

Status: `FUTURE_PHASE`.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=true` before firmware implementation;
`requires_source_research=true`; `requires_firmware_change=true`;
`requires_safety_review=true`.

Engineering/source research can proceed: yes, for
storage/representation/fallback design if prioritized.

Next concrete action: storage, representation, validator, fallback, and rollback
design branch if prioritized. This is not blocked by user domain input unless a
specific product decision is being asked.

Current implementation state: Runtime-loaded config is not implemented.

### Phase 7A - Active Runtime Config State Contract

Goal: Preserve the accepted hot-path parse-status guardrail while defining the
future active-state boundary for runtime config activation.

Status: `READY_FOR_ENGINEERING_DESIGN` / `DESIGN_ACCEPTED` for docs/tools only.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=true` before firmware behavior implementation;
`requires_firmware_change=false` for this contract branch.

Engineering/source research can proceed: yes, for docs/tools checkers and
future implementation-slice design only.

Next concrete action: use the Active Runtime Config State Contract before any
runtime activation source changes. Activation/selection may validate parser,
payload, CRC, materialization, and load state before publishing stable active
state. Output generation may consume only the published active view.

Required evidence: `docs/runtime_config/active_runtime_config_state_contract.md`,
`docs/runtime_config/fixtures/active_runtime_config_state_contract.json`, the
accepted hot-path parse-status guardrail, and checker output.

Accepted next boundary:
`docs/runtime_config/parser_hotpath_postmortem_and_next_boundary.md` records the
Phase 7A diagnostic matrix, the accepted guardrail, and the source-owned
active-state preselection `HARDWARE_PASS`. Source-owned active-state
preselection is the repair architecture baseline. Parser/materialization/load
may happen only before active-state publication; output generation may consume
only the already-selected `RuntimeConfigView`.

Stop conditions: any implementation path that reads parser result state from
`UpdateAnalogOutputs`, an analog hot-path resolver, or
`ResolveActiveRuntimeConfig`; any output path that branches on activation
source or activation status; any runtime-loaded config, storage, WebSerial,
device-write, flashing, or nunchuk validation claim.

Implementation note:

- `runtime-active-config-state-source-owned-preselection` applies the accepted
  contract as a source-authored scaffold: stable active-state selection in
  `GetActiveRuntimeConfigState()`, hot-path selection through
  `ResolveActiveRuntimeConfig()`, and source-owned preselection behavior. This
  branch remains parser-call free in firmware source and adds no storage,
  write, parser payload, transport, or flashing behavior.

Explicit non-goals: no runtime-loaded config, no parsed table materialization,
no storage, no WebSerial/device write, no flashing automation, and no
nunchuk validation claim.

Accepted guardrail: the Phase 7A D5A/D5A-N1/D5A-N2 finding is recorded in
`docs/runtime_config/hot_path_parse_status_guardrail.md`. Future activation
work must compute stable active runtime config state outside the analog output
hot path; `UpdateAnalogOutputs` and any analog hot-path resolver must not read
or branch on parser result status or config-load status.

Required evidence: explicit user approval, storage decision, representation
decision, validator design, fallback policy, build, hardware plan/result, and
rollback plan.

Stop conditions: implementation approval missing, storage/transport source
authority missing, fallback ambiguous, or implementation depends on inferred
behavior.

Explicit non-goals: no device write transport, no schema authority from external
remapper docs, no hardware validation claim without result.

## Phase 8 - WebSerial/Device-Write / Push-To-Device Workflow

Goal: Consider a write-capable workflow only after source authority, policy, and
validation exist.

Status: `FUTURE_PHASE`.

Requirements now: `requires_user_domain_input=false`;
`requires_user_product_approval=true` before implementation;
`requires_source_research=true`; `requires_transport_authority=true`;
`requires_safety_review=true`.

Engineering/source research can proceed: yes, for source-authority and transport
research if prioritized.

Next concrete action: source-authority/transport research branch if prioritized.
No WebSerial/device write, protobuf binary write, hidden device write, or
flashing automation may be implemented from current evidence.

Current implementation state: WebSerial/device write is not implemented.
Protobuf binary write is not implemented. Firmware flashing automation is not
implemented.

Required evidence: official transport/schema authority, no-destructive workflow
policy, explicit approval, round-trip validation, hardware safety plan, and
rollback/recovery plan.

Stop conditions: task requires push-to-device behavior without explicit source
support, reverse-engineering private/encrypted formats, or unsafe/destructive
device actions.

Explicit non-goals: no current implementation, no external-remapper adapter
output, no firmware flashing automation, and no user-facing write path.

## Runtime-Config Step Sequence

This docs-only sequence is the next hardware-gated workflow prep and does not
declare a release.

- Step 14 manual firmware-consuming runtime-config load is blocked before implementation.
- Step 15 source-authority research complete.
- Step 16 WebSerial/device-write implementation is blocked before implementation.
- Step 17 flashing automation is forbidden/not approved; safety boundary complete.
- Step 18 public/manual workflow release-candidate hardware result is recorded for
  applicable doable scope in
  `docs/calibration/glyph_public_manual_workflow_release_candidate_hardware_result_2026-06-07.md`;
  the plan/checklist remain plan-only and no public release or official
  configurator compatibility claim is made.
- Public/manual workflow release-candidate plan and checklist live in `docs/release/public_manual_workflow_release_candidate_plan.md` and `docs/release/public_manual_workflow_release_candidate_checklist.md`.
- Offline official configurator export target contract docs live in
  `docs/export/official_configurator_export_source_authority.md`,
  `docs/export/official_configurator_export_target_contract.md`, and the
  preview/invalid fixtures under `docs/export/fixtures/`; they remain
  offline-only and do not claim production export or official compatibility.
- Runtime-loaded config remains not implemented.
- Runtime-config storage remains not implemented.
- Firmware binary/protobuf parser integration remains not implemented.
- WebSerial/device write remains not implemented.
- Firmware flashing automation remains not implemented.
- Nunchuk remains NOT_TESTED unless explicitly validated.

## Forbidden Policy Items

Status: `FORBIDDEN_BY_POLICY`.

These remain forbidden unless future source authority, legal/safety review, and
explicit product approval change the policy:

- macros;
- turbo;
- timing automation;
- hidden device write;
- unsafe flashing automation;
- external source reuse without license/source review.
