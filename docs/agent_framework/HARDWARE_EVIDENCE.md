# Hardware Risk And Evidence Contract

Status label: CURRENT.

Physical controller behavior cannot be proven by source inspection, tests, or
a successful build. This contract is the canonical manual H2/H3 acceptance
lane. No agent may fabricate hardware execution or PASS.

## Lifecycle

```text
READY
  -> IMPLEMENTED
  -> STATIC_VALIDATED
  -> BUILD_VALIDATED
  -> INDEPENDENT_REVIEWED
  -> H0/H1 with sufficient evidence: MERGE_ELIGIBLE
  -> H2/H3: CANDIDATE_ARTIFACT_PUBLISHED
       -> HARDWARE_TEST_REQUIRED
       -> LOCAL_ACCEPTANCE_PENDING
       -> PASS: HARDWARE_VALIDATED -> MERGE_ELIGIBLE
       -> FAIL: HARDWARE_FAILED -> REPAIR_REQUIRED / CURATION_REQUIRED
       -> PARTIAL/INCONCLUSIVE: LOCAL_ACCEPTANCE_PENDING with exact gaps
```

Compilation is build integrity only. Hardware evidence is valid only for the
exact tested Git snapshot and exact tested firmware bytes. A source change
after artifact creation invalidates affected evidence. A failed candidate must
not enter `configurator`.

The mutable `.pio/build/glyph_mk6/firmware.uf2` output is never a durable test
artifact. Before handoff, preserve the exact UF2 at a unique immutable
candidate-SHA/artifact-SHA-addressed locator (for example an approved
release/CI artifact store). If no durable store is available, stop
`BLOCKED_EXTERNAL`; a local build path alone is insufficient. Immediately
before device update, retrieve and re-hash those exact preserved bytes and
require equality with the recorded SHA-256. A rebuild, even at the same Git
SHA, is a different artifact unless its bytes independently match; never
substitute a rebuild for the preserved candidate.

A hardware-result/evidence branch is evidence, not source authority. If it
contains source modifications, treat them as new source changes requiring
fresh implementation review, build, and hardware testing. Never hide failed
active source inside an evidence branch.

Canonical pending and every result status must be published through a
docs/control-plane snapshot based on fresh `configurator` that references the
immutable candidate SHA, artifact hash and locator, and evidence record but
contains none of the candidate source. This applies to PASS, FAIL, PARTIAL,
INCONCLUSIVE, and identity/protocol mismatch. The candidate ref remains pinned
at the built source snapshot until PASS publication recovery completes. A
result branch may descend from the candidate for comparison, but failed source
still cannot enter `configurator`.

Prefer at most one dependent H2/H3 candidate awaiting hardware testing at a
time. Independent H0/H1 work may continue only when it cannot contaminate the
candidate snapshot or its evidence.

## Evidence Record Template

```text
Work-order ID:
Candidate branch:
Candidate Git SHA:
Base/configurator SHA:

Firmware artifact filename/path:
Firmware artifact SHA-256:
Preserved immutable artifact locator:
Pre-update SHA-256 verification:

Controller model/revision:
Relevant firmware/profile state:
Update method:
Relevant host/platform/adapter:

Protocol version:

Preconditions:

Test steps:

Expected result for every step:

Observed result for every step:

Negative/regression checks:

Power-cycle/reconnect checks where relevant:

Result:
PASS | FAIL | PARTIAL | INCONCLUSIVE

Anomalies:

Recovery/rollback performed:

Tester:

Date/time:
```

The full candidate Git SHA and artifact SHA-256 are mandatory for H2/H3
acceptance. Do not require irrelevant sensitive hardware identifiers. The
artifact SHA identifies the exact bytes tested even though this repository's
UF2 hashes are not assumed reproducible across separate rebuilds.

## Evidence Processing

The Hardware Evidence Processor accepts human-supplied observations only. It
verifies candidate Git SHA, artifact SHA-256, protocol version, controller and
context, result completeness, source drift after artifact creation, and exact
candidate correspondence.

- Identity or protocol mismatch: `HARDWARE_EVIDENCE_MISMATCH`.
- Complete exact PASS: `HARDWARE_VALIDATED`.
- FAIL: isolate candidate, record `HARDWARE_FAILED`, and always add supporting
  `REPAIR_REQUIRED`; with zero effective runway the primary state is
  `CURATION_REQUIRED`.
- PARTIAL or INCONCLUSIVE: keep non-merge-eligible and state exact retest needs.

The processor updates evidence and control-plane state only. It does not edit
runtime source or publish source to `configurator`.

## Canonical Queue Result Mapping

- Before testing: `HARDWARE_TEST_REQUIRED`; when a human has the packet and
  preserved bytes: `LOCAL_ACCEPTANCE_PENDING` with `hardware_result: null`.
- Exact complete PASS: `HARDWARE_VALIDATED`, `hardware_result: PASS`, canonical
  evidence reference, and an empty evidence-gap list.
- Exact FAIL: `HARDWARE_FAILED`, `hardware_result: FAIL`, canonical evidence
  reference, and `REPAIR_REQUIRED` or `CURATION_REQUIRED` as the next signal.
- Exact PARTIAL or INCONCLUSIVE: remain `LOCAL_ACCEPTANCE_PENDING`, record the
  corresponding result and exact gaps/retest steps; no merge eligibility.
- Identity/protocol mismatch: keep the prior non-validated status, record
  `HARDWARE_EVIDENCE_MISMATCH` evidence, and do not mutate the exact candidate
  pair into a validated result.

After canonical `HARDWARE_VALIDATED` publication, the Implementation
Supervisor owns publication recovery. It must verify the live candidate ref is
still the recorded SHA, re-hash the preserved bytes, verify the exact PASS
record and absence of source/authority drift, refresh `configurator`, rerun
invalidated gates, and merge only that candidate tree. It then publishes the
queue item as `DONE`. Any mismatch returns to the hardware or curation gate.

## Legacy Evidence Boundary

Hardware reports for source already merged before this Revision-2 contract
remain historical operational acceptance of that already-merged baseline.
Where their candidate Git SHA or artifact SHA-256 was not recorded, identity is
`UNKNOWN`; those reports cannot satisfy, transfer to, or be reused as the
exact-snapshot gate for any new or rebuilt candidate.
