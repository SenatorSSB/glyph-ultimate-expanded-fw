# Validation And Gates

Status label: CURRENT.

Every branch needs a behavior classification before merge recommendation.
The supervisor must execute the required branch, validation, commit, push, and
merge operations when they are in scope; it must not stop at reporting the
commands.

Work orders also receive behavioral-effect risk `H0`, `H1`, `H2`, or `H3` as
defined in `WORK_ORDER_TEMPLATE.md`. Branch classification and hardware risk
are complementary: risk follows actual effect, not file location.

## Current Revision-3 Validation Policy

GLYPH-UD-027 is current progression authority. Historical Revision-2 records,
exact hardware identities and strict DONE correspondence remain evidence;
conflicting global/meta-validation progression rules are superseded, not
retroactively rewritten. This policy does not redesign the production runner,
deadlines, cancellation, resources or isolation.

<!-- revision-three-validation:start -->
```json
{
  "revision": 3,
  "owner_direction": "GLYPH-UD-027",
  "transport_direction": "GLYPH-UD-028",
  "tiers": {
    "1": "ALWAYS_BLOCKING",
    "2": "DIRECTLY_AFFECTED_BLOCKING",
    "3": "NONBLOCKING_UNLESS_CONCRETE_TIER1_OR_TIER2_CONTRADICTION"
  },
  "timeout_is_pass": false,
  "source_free_E_requires_I_catalog": false,
  "accepted_I_requires_catalog": true,
  "future_GP_VAL_requires_UNPROVEN_SAFETY_FACT": true,
  "ordinary_governance_successors_per_product": 1,
  "exceptional_validation_repairs_per_product": 1,
  "third_successor_exceptions": [
    "OWNER_APPROVAL",
    "HARDWARE_FAIL",
    "NEW_FIRMWARE_SOURCE_DEFECT",
    "NEW_PRODUCT_DOMAIN_DECISION"
  ],
  "transport_grants_action_authority": false,
  "rejected_transport_repeated_retry": false,
  "canonical_writers": 1
}
```
<!-- revision-three-validation:end -->

| Tier | Required proof | Progression |
| --- | --- | --- |
| 1 — candidate-critical | Changed behavior/source tests, critical source/build-input correspondence, required target compile/build, exact committed SHA/tree/UF2 hash/size/custody, physical acceptance, Config preservation and changed-path negatives | Always blocking; FAIL, TIMEOUT, INCOMPLETE or UNAVAILABLE never becomes PASS |
| 2 — affected regression | Every directly affected source/validation-interface consumer, neighboring Config behavior and relevant current/historical correspondence | Blocking when directly affected; classify applicability with source-backed evidence and independent review, not to evade a failed gate |
| 3 — framework health | Global aggregate, global synthetic topology, framework performance and broad historical/proof/runtime optimization | Track FAIL/incomplete as FRAMEWORK_VALIDATION_DEBT; nonblocking unless it reveals a concrete Tier-1/Tier-2 contradiction |

A framework failure blocks only when it prevents establishing a named concrete
required safety fact or contradicts candidate-critical/affected proof. A
timeout means execution did not complete within its engineering budget, not
firmware unsafety. Preserve the raw result; never report an unexecuted,
incomplete or failed aggregate as PASS. The 300-second aggregate and 120-second
checker limits remain unchanged. GP-VAL-011 remains OWNER_DEFERRED /
NONEXECUTABLE; this policy is not authority for its redesign.

Framework changes require focused unit/regression tests, actual directly
affected consumers, fresh independent review, and relevant frozen canonical
mutation/isolation proof. Do not require recursive proof of every historical
framework topology or a new meta-governance campaign. Product candidates still
need every applicable Tier-1/Tier-2 gate, exact identity, relevant negative and
correspondence controls, review, custody and required human hardware PASS.

Before a future GP-VAL proposal/authorization, record
`UNPROVEN_SAFETY_FACT` naming a concrete firmware/product safety property with
source/evidence provenance. Framework timeout, runner mechanics, topology and
proof performance alone are framework debt, not that fact. Independent review
must establish substance; a field or checker PASS is not semantic authority.
Use the prospective contract in WORK_ORDER_TEMPLATE.md without rewriting any
existing work order, immutable receipt or DONE record.

Per logical product order: at most one ordinary candidate-governance successor
and one exceptional validation-repair successor. A third (or another over-limit
successor) requires explicit owner approval unless supported by hardware FAIL,
a newly discovered firmware/source defect, or a new product/domain decision.
Record the exact exception/provenance; timeout, runner mechanics, topology and
performance are not exceptions. Do not create a GP-VAL or Planner/Curator loop
merely to complete an already-authorized mechanical transition.

## Branch Classifications

`DOCS_CHECKER_ONLY`

- Docs, schemas, examples, or checkers only.
- Active firmware behavior unchanged.
- Firmware build not required unless build/source files were touched
  unexpectedly.
- Hardware not required.

`INACTIVE_GENERATOR_OR_FIXTURE`

- Generator, fixture, or inactive artifact work only.
- Active firmware behavior unchanged.
- Run relevant generator/checker tests.
- Hardware not required unless active behavior changes.

`FIRMWARE_SOURCE_NON_ACTIVE`

- Firmware source was touched, but active behavior is source-backed as
  unchanged.
- Build proof required.
- Hardware may be required if active behavior uncertainty remains.

`FIRMWARE_SOURCE_ACTIVE_BEHAVIOR`

- Active firmware behavior or active RuntimeConfigView selection changed.
- Build proof required.
- Hardware PASS required before merge.

`FORBIDDEN_OR_UNSAFE`

- Runtime-loaded config activation.
- Active `candidate.view` publication.
- Active `active_storage.view` publication.
- Generated active RuntimeConfigView wrapper publication.
- RuntimeConfigView replacement as customization mechanism.
- RAM-backed active table publication.
- WebSerial/device write.
- Protobuf binary write.
- Backend config.pb write.
- Persistent runtime-config storage.
- Flashing automation.
- Source-authority bypass.

Stop and report.

## Glyph Gates

- Fresh live-remote truth -> attempt ordinary/default read-only verification;
  if restricted-sandbox DNS/network access fails, treat it as inconclusive and
  retry through the permitted network-enabled/escalated path. Do not infer auth
  failure, mutate credentials, request re-login, accept stale tracking refs, or
  return `BLOCKED_EXTERNAL` until all permitted network-capable retries fail or
  are unavailable.
- Active behavior changed -> build proof plus hardware PASS before merge.
- H2/H3 -> automated validation, canonical build, fresh independent review,
  exact candidate publication, full Git SHA plus exact artifact SHA-256, and
  physical controller PASS before merge.
- Normal Implementation cycle with repository mutation and available native
  subagents -> fresh independent post-implementation review. A materially
  separable investigation also requires a bounded specialist; H2/H3 normally
  requires a source-authority or firmware-safety specialist and a separate
  fresh reviewer. Apply the discovery and exception rules in
  `SUBAGENT_CONTRACTS.md` without creating a new approval gate.
- A successful build proves build integrity only. It never proves controller
  acceptance.
- Relevant source/build-input drift invalidates hardware correspondence.
  `HARDWARE_CORRESPONDENCE.md` defines exact critical-input preservation,
  audited non-behavioral metadata evolution, and unknown-path rejection. A
  rebuild is build proof only: the original tested artifact remains pinned
  and is never replaced by the integration build.
- Failed candidate source must not enter `configurator`; a result/evidence
  branch is not source authority.
- Docs/checker-only with active behavior unchanged -> hardware not required.
- Failed active-source branches are evidence only; do not present them as
  current work.
- No destructive Git commands: no reset, clean, stash, revert, or force-push
  unless explicitly approved.
- Artifact hashes need not be rebuild-stable, but the exact hash is mandatory
  evidence identity for H2/H3 testing. Checkers enforce recorded identity and
  locator invariants; they do not require a separate rebuild to reproduce the
  digest.
- Nunchuk remains NOT_TESTED unless the user explicitly reports a test.
- Root cause remains unproven unless direct evidence is found.
- Runtime-loaded config remains not implemented.
- A post-migration `DONE` item requires strict completion evidence: full Git
  SHAs, exact reviewed changed paths, and either direct ancestry or a
  dedicated exact path/tree replay whose integration precedes publication.

## Current Active Path Boundary

The only hardware-proven active path remains source-owned firmware behavior
through the existing active RuntimeConfigView path:

- `GetActiveRuntimeConfigState()`
- `ResolveActiveRuntimeConfig()`
- active publication remains `&kSourceOwnedCurrentBaselineRuntimeConfig`
- active RuntimeConfigView selection remains unchanged
