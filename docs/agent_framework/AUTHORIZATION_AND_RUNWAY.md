# Authorization And Runway

Status label: CURRENT.

This contract adapts Revision 2 authorization and liveness semantics to the
Glyph firmware/configurator/backend repository. It is control-plane policy
only and changes no firmware runtime behavior.

## Selected Operating Mode

```text
MINIMAL SUPERVISOR
+ on-demand consultative Planner and Curator
+ durable Ready / Preauthorized authorization
+ hard manual H2/H3 hardware acceptance
```

The human- and source-authority-heavy backlog makes autonomous product
generation inappropriate as the default. Planner and Curator remain usable so
a stale or empty runway can be replenished without redesigning the workflow.
They cannot decide game semantics, infer firmware capabilities, or bypass
explicit approval boundaries.

## Authority Map

| Authority | Canonical artifact |
| --- | --- |
| Current factual state and project phase | `docs/AGENT_CONTEXT.md` and `docs/CURRENT_STATE.md` |
| Executable Ready queue and recorded Preauthorization | `docs/project/ACTIVE_AGENT_QUEUE.md` |
| Work-order shape | `docs/agent_framework/WORK_ORDER_TEMPLATE.md` |
| Roadmap and portfolio direction | `docs/ROADMAP.md` |
| Candidate planning | newest relevant live-verified `planning/portfolio-*` branch; always non-authoritative |
| Actual user direction | `docs/agent_framework/USER_DIRECTION.md` |
| Hardware evidence and protocol | result record conforming to `docs/agent_framework/HARDWARE_EVIDENCE.md` |
| Durable runtime/source decisions | current source-backed runtime-config decision and boundary documents, especially `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`; hypotheses remain explicitly labeled |
| Agent methodology | `docs/agent_framework/` |
| Scheduled/manual task prompts | `docs/agent_framework/SCHEDULED_TASKS.md` |

When canonical sources conflict, stop and resolve authority before
implementation. Historical calibration packets are evidence, not queue or
roadmap authority.

## Authorization States

### Ready

`READY` is immediately executable. Dependencies, evidence, source authority,
architecture, scope, user/product decisions, and validation are resolved. Only
Curator or explicit user work-order authority may place new work in Ready.

### Preauthorized

`PREAUTHORIZED` means Curator has already made the substantive decision that
the work should be done, but objective mechanical conditions are not yet
satisfied. It must include:

- substantive authorization rationale;
- prerequisites;
- mechanical activation conditions;
- invalidation conditions;
- authorization snapshot and provenance;
- automated validation and stop conditions.

The Implementation Supervisor may mechanically activate it only when every
condition is objectively satisfied, no invalidation condition is present, and
no new user, product, architecture, source-authority, evidence, hardware, or
hardware-interpretation judgment is required. Otherwise it returns
`CURATION_REQUIRED`.

Preauthorization binds exact sensitive semantic/source invariants while
allowing only named non-semantic control-plane/test deltas that cannot affect
the successor. Unexpected semantic drift fails closed. A recorded
Preauthorized item may be `ACTIVATABLE`, `WAITING`, `HARDWARE_PENDING`, or
`INVALIDATED`; only `ACTIVATABLE` contributes to effective runway.

## Throughput-Aware Runway

Track separately:

```text
Immediate Ready runway
Recorded Preauthorized runway
Mechanically activatable Preauthorized runway
Invalidated Preauthorized work
Hardware-pending work
Effective authorized runway
Target effective authorized runway and target provenance
```

Effective authorized runway is:

```text
READY items
+ Preauthorized items already mechanically activatable without new judgment
```

Invalidated Preauthorization and hardware-pending Preauthorization are never
effective runway. `RUNWAY_LOW` means positive effective runway below the
recorded target; `RUNWAY_OK` means the target is met or exceeded. The target is
the expected number of Implementation
Supervisor opportunities before the next normal Curator opportunity plus a
small resilience buffer while contracts remain fresh. It is never a quota;
Curator may authorize zero and must not create make-work.

## Planner Packet Freshness

A Planner packet records at least:

```text
packet ID and planning branch
base live configurator SHA
evidence inspected
candidate IDs and dependencies
curation-readiness estimates
hardware/evidence gates
rejected alternatives
broad-audit scope when claiming global scarcity
whether global wait is proposed
whether independent Curator review is required
```

Planner estimates may be `CURATION_READY`, `PREAUTHORIZABLE`,
`EVIDENCE_GATED`, `USER_DECISION_GATED`,
`SUBSTANTIVE_DEPENDENCY_GATED`, `RESEARCH`, `HOLD`, or `REJECT`. They are
investigation aids only. Planner cannot mark work Ready or Preauthorized.

A newly published material packet records `curator_review_required: true`,
including a zero-candidate packet that proposes global wait. That routes to
`CURATION_REQUIRED`, not back to Planner. Curator acceptance records review
provenance and clears the flag; rejection or material consumption changes the
packet state instead of leaving a falsely fresh packet.

A packet becomes materially consumed or stale when a leading candidate ships,
hardware results or implementation change assumptions, source/runtime
ownership changes, a candidate is superseded or invalidated, user direction
changes, or new material evidence appears. Time passage, an unrelated docs
commit, or a SHA change alone does not make a packet stale. A partially
consumed packet may remain useful for surviving independent authorized work.

## Zero-Runway Liveness

When effective authorized runway is zero:

- use `PLANNING_REQUIRED` when candidate supply is absent or the latest packet
  is materially stale/consumed and a fresh broad search is needed;
- use `CURATION_REQUIRED` when concrete candidates or invalidated
  Preauthorization exist but need substantive authorization, reauthorization,
  or interpretation;
- never let Implementation self-reseed or promote raw Planner rankings.

Invalidated Preauthorization and failed hardware take precedence over an
absent/stale/consumed Planner packet at zero runway: the primary liveness state
is `CURATION_REQUIRED`, with `REPAIR_REQUIRED` also recorded for hardware
failure. Candidate-local `HARDWARE_TEST_REQUIRED` and `REPAIR_REQUIRED` are
supporting signals, not mutually exclusive portfolio liveness states.

A candidate-local `HARDWARE_TEST_REQUIRED` state does not imply portfolio-wide
hardware scarcity. `GLOBAL_EVIDENCE_WAIT_SUPPORTED` requires a fresh broad
current-`configurator` Planner audit across plausible independent correctness,
source-authority, validation, configurator, integration, safety, recovery, and
usability work; exact missing external evidence; a named resume event; and
independent Curator acceptance, zero effective authorized runway, and exactly
one primary liveness signal. A partially consumed packet cannot establish the
wait. Timer passage alone does not invalidate an accepted global wait.

## Role Separation

Planner proposes. Curator independently judges and authorizes. Implementation
executes one authorized item. The Hardware Evidence Processor validates and
records human-supplied results for an exact candidate/artifact pair. No role may
collapse generation, authorization, execution, review, and hardware acceptance
into self-approval.

Curator owns the queue and may update only narrow control-plane contract tests
whose substantive purpose is to enforce the canonical state Curator changed.
The ordinary Curator test-edit surface is exactly
`tools/check_glyph_agent_framework_docs.py`; navigation-only consequences may
also update `tools/check_glyph_docs_navigation.py`. Changes to
`tools/glyph_checker_context.py`, product/runtime checkers, build gates, or any
other test require a separate governance work order and are outside routine
curation authority.
The anti-cheating rule is:

> Canonical intended control-plane state changed from X to Y; the test encoded
> X and is updated to encode Y while preserving or strengthening the invariant.

Curator may not edit firmware/configurator product code, runtime/product tests,
or weaken authority, provenance, concurrency, activation, hardware, or
publication invariants to make checks pass. Curator-authored governance-test
changes require focused independent review.

## Concurrency And Publication

Worktrees prevent filesystem collisions, not canonical-state collisions. Every
canonical writer must inspect worktrees, dirty state, relevant branches, and
the live remote `configurator` ref before mutation and immediately before
publication. Legitimate concurrent publication yields
`IMPLEMENTATION_DEFERRED_CONCURRENT_WRITER` or
`CURATION_DEFERRED_CONCURRENT_WRITER`.

Normal implementation uses a focused branch compared against live
`configurator`. Hardware/result/evidence branches are compared against their
candidate branch, while failed active source is separately kept out of
`configurator`. H2/H3 pending and every hardware-result queue state is
published separately as a docs/control-plane snapshot based on fresh
`configurator`, referencing the pinned candidate Git SHA, preserved artifact
locator, artifact SHA-256, and evidence record without containing candidate
source. Push, live-verify the exact feature ref, refresh live
`configurator`, reconcile drift, rerun invalidated gates, and never force-push
ordinary work.

Schedules are heartbeats, never quotas. Every scheduled role has a truthful
no-op or deferral result.
