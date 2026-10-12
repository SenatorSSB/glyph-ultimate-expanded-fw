# Future daemon bootstrap

Read this on the **first turn of each fresh chapter daemon**. This is the
owner-requested operating contract dated 2026-10-10, not a work order, queue
amendment, release approval, or permission to start the next chapter.
Historical basis: [daemon retrospective](../project/DAEMON_RETROSPECTIVE_2026-10-10.md).

## 1. Establish one chapter

Start with an owner-approved chapter name, outcome, exclusions, allowed orders,
evidence of completion, resource budget, and stop conditions. If these are
missing, prepare a bounded proposal; do not invent implementation authority.
One fresh daemon owns one coherent chapter. Retire it at completion or a durable
owner/domain/hardware blocker. A later chapter starts with a new daemon.

Read root/nested `AGENTS.md` and its current-state, queue and contract entrypoints.
Verify the actual remote URL and live canonical ref; a clone's `origin` may be
local. Follow root AGENTS.md capability-aware networking: when restricted
GitHub access is known unavailable, use permitted network-enabled execution
directly, without an expected-to-fail probe. Unknown connectivity allows one
minimal ordinary read-only probe. Persist the chapter capability fact until
the runtime/environment materially changes:

```yaml
network_capabilities:
  live_github_requires_network_enabled: true
```

Network permission widens no repository mutation, filesystem, canonical
publication, device/firmware, queue, hardware evidence or account/settings
authority. Authenticate only after connectivity and an actual GitHub rejection;
never mutate credentials or accept stale tracking refs as live truth.

## 2. Authority before momentum

Within runtime/system constraints, latest verified direct owner direction
controls scope and supersedes older owner direction. Read its original timestamp
and message identity before acting on a relay. Heartbeats, peer summaries and
conversation memory do not renew old authority.

Only complete READY authority, objectively satisfied named PREAUTHORIZED
conditions, or a named explicit owner exception permits execution. Planner
proposes; Curator adjudicates; executor implements; independent reviewer judges;
HEP processes human observations. Roadmaps, Goals and empty queues grant no scope.

Keep one canonical publisher. Isolated branch work may run concurrently only
when frozen inputs and hardware custody remain protected. Reconcile each result
against live Git and exact artifacts before advancing.

## 3. Route the smallest adequate task

**The chapter daemon defaults to Terra / low**, using Terra / medium only
when several dependent chapter states genuinely require synthesis. Use durable
capability-family routing and resolve actual availability on each dispatch or
resume. The local runtime catalog inspected on 2026-10-10 lists
`gpt-5.6-terra` with low/medium support; this is an observation, not a permanent
model pin. If Terra is unavailable, preserve the owner preference and stop for
an explicit owner-approved available fallback; choose no silent substitute and
fabricate no model identifier. It routes, verifies and synthesizes chapter state. Delegate exceptional design/judgment to a bounded stronger
worker, then return its evidence to the lightweight daemon.

These defaults are mirrored in MODEL_ROUTING.md and model_routing.v0.json;
they do not amend queue authority. Honor specific
owner model instructions. **Set model/effort on every dispatch and resume**;
record requested versus observed execution separately. Unknown stays unknown.

| Lane | Preferred family / effort | Escalate / return |
| --- | --- | --- |
| Chapter daemon | Terra / low; medium for coupled chapter-state reconciliation | Delegate finite technical uncertainty, then return to low |
| Mechanical / frequent | Luna / low; medium for guarded multi-step work | Escalate only the unresolved source contradiction |
| Established bounded implementation | Terra / medium where available/appropriate; Luna / medium for well-known patterns | Sol / medium when technical coupling exceeds the known pattern |
| Coupled technical / diagnosis | Sol / medium | Sol / high for difficult finite architecture or conflicting evidence; return after resolution |
| Ambiguous / high-leverage | Sol / high first | Astra only under the exceptional rule; return a decision/counterexample and end |

**Astra is exceptional:** a bounded high-leverage question, inadequate cheaper
attempt (or justified novel risk), explicit expected benefit, and compatible
owner policy. Medium by default; high needs a reason. Never default to Astra
for polling, hashes, routine review or a persistent control loop.

Keep a one-tool status/hash check, result verification or routing decision in
the daemon. Delegate substantial mechanical batches to Luna and finite technical
work to a scoped worker. Do not create an agent just to restate WAITING. Do not
let the daemon become the implementation/research workhorse.

Role existence is not a quota. Instantiate Planner only for planning/candidate
supply, Curator only for actual authority/adjudication, reviewer for a required
mutation/evidence review, HEP only after human physical observations exist, and
other specialists only when the current bounded transition benefits from them.
One clean executor may carry an already-authorized coherent chain within its
recorded scope/successor limits to the next real hardware/domain/authority stop.
One independent review layer is normally sufficient; no reviewer-of-reviewer
chain unless the first review identifies a concrete new defect whose repair
genuinely needs distinct independent review. Independence does not require a
stronger model: a reviewer may use Luna or Terra.

### Optional chapter worker roster

At bootstrap, read the owner-approved scope and optional `worker_roster` in the
chapter ledger. A roster belongs to exactly one chapter, is not global
execution authority, and expires with that chapter. Record the named daemon,
owner approval reference, finite participants and their stable chapter-local
IDs, chat locators, lanes, allowed task classes, exclusions, reuse/independence
conditions and lifecycle (`available`, `active`, `blocked`, `retired`). The
[roster and worker templates](PROMPT_TEMPLATES.md#optional-chapter-worker-roster)
include requested, owner-selected and observed model/effort plus provenance.
Chapters without a roster retain ordinary native delegation.

Two worker classes serve different needs:

- **Native/disposable internal subagents:** repository inventory, source
  navigation, hashes, focused tests, file comparisons, resource extraction,
  bounded docs edits and straightforward mechanical implementation. Their
  mechanically verified result can be adequate with UNKNOWN model identity.
  Do not create user-visible chats solely for provenance on mechanical work.
- **Owner-created/model-selected user-visible chats:** difficult architecture,
  high-coupling implementation, finite diagnosis, adversarial design analysis
  and high-value independent review where model quality materially matters.
  The owner creates/selects their model/effort and approves their chapter roster
  entries. They are bounded workers, not autonomous peer daemons.

Owner approval may permit dispatch/resume and direct return once per named
worker for that chapter, subject to actual runtime/system authorization. Each
packet must remain inside chapter scope and the worker's lane and exclusions.
The daemon may not silently add user-visible contexts: a new or replacement
context outside explicit roster approval returns
`ADDITIONAL_WORKER_AUTHORIZATION_REQUIRED`. A replacement needs its own recorded
locator and approval coverage; never inherit permission merely from an old ID.
Native disposable internal children remain available under existing delegation
rules without creating owner-visible chats or special permissions.

Direct-return authorization permits only receiving bounded packets from the
named daemon and returning completed bounded results to it. It grants no new
product scope, chapter amendment, owner/domain/hardware gate clearance,
canonical merge/publication, source-free evidence publication, device write,
flashing, successor chapter or arbitrary worker creation authority. Preserve
one publisher and every existing authority, evidence and independence gate.

### Large coherent chapter pattern (nonbinding)

A substantial chapter may use Terra/medium for coupled chapter-state synthesis:
brief parallel architecture/design and mechanical/resource discovery, plus
protocol/storage investigation only if independently useful; one reconciled
design freeze; one primary executor for the coherent authorized implementation
chain; one fresh independent review; then exact candidate/build/hardware gates
when applicable and HEP -> source-free E -> tested-source I -> separate DONE.
Avoid overlapping source editors without a strong isolation reason.

Before implementation of high-leverage architecture, one bounded stronger
worker may challenge the design: find a concrete corruption, migration,
recovery, concurrency, future-architecture or evidence-boundary failure. If no
concrete blocker is found, return to ordinary implementation routing; do not
keep the stronger worker permanently attached.

The owner's upcoming **Multi-Profile Persistent Ultimate Profile Store**
preferences are D0 daemon Terra/medium, W1 architecture/adversarial Sol/high,
W2 primary implementation Terra/medium, W3 fresh independent review Sol/medium,
and W4 mechanical/resource Luna/medium. This is an illustrative future roster,
not global policy, actual chat creation or authority to start that chapter.
Its product direction remains in the owner-approved [roadmap](../ROADMAP.md).

## 4. Keep contexts clean

Use a **fresh subagent context by default for a materially independent
investigation**. Resume only when the same bounded work requires its prior
context, that context is relevant and clean, and role independence survives.
Never reuse a chat just for its convenient model setting. A known mechanical
transition inside the same clean product chain does not require a new chat.
A roster worker may resume implementation -> focused repair -> directly related
verification within the same clean lane. Use a fresh context for independent
investigation, architecture challenge after implementation contamination,
independent review or a substantially new problem. Retire contexts when these
conditions fail. Model convenience alone never justifies reuse. A retired
worker's replacement follows the roster/additional-worker authorization rule.
Use native subagents for internal subtasks; user-visible contexts require
recorded owner approval and the runtime's applicable user authorization.

Bound each worker to one deliverable: exact base, files, exclusions, checks,
budget, stop and return format. Split unrelated work. Fresh review receives
evidence, not the implementer's reasoning history. Summarize verified facts,
SHAs, failed attempts and questions at handoff, compaction or changed authority.
Retire contaminated contexts; never transfer the full chapter transcript.

## 5. Progress without loops

Normal path: daemon dispatches a bounded packet -> worker completes -> direct
completion event or authorized worker return -> daemon processes it immediately.
The owner should not routinely ferry results. At bootstrap establish
`direct_return_capability: VERIFIED | UNAVAILABLE | UNKNOWN` once, with the
runtime evidence/limitation and tested worker/daemon path in the chapter ledger.
VERIFIED requires actual runtime support evidence; roster approval alone proves
no persistent cross-chat permission. UNKNOWN is valid until exercised. Revisit
only after a material capability/environment change, not by periodic probing.

If transport rejects direct return despite chapter approval, record the exact
transport/authorization failure and affected endpoints, stop retries, and mark
`DIRECT_RETURN_TRANSPORT_FAILED`; this is not product/work failure. A worker
persists the result/failure and stops; the daemon owns bounded recovery:

1. Prefer the direct completion event / direct worker return.
2. After demonstrated failure, make one bounded resume/status retrieval of the
   known worker under existing authorization; do not broaden its task.
3. Read its durable repository result if available: exact commit, report,
   chapter ledger entry, evidence file or SHA/test result. For substantial work,
   chat return must not be the sole durable record. A commit/test output may
   suffice for trivial mechanical work; do not require unnecessary prose.
4. Only if completion callbacks demonstrably failed and durable recovery cannot
   adequately restore liveness may a narrowly bounded watchdog be considered
   under [existing watchdog rules](JUDGE_WATCHDOG_CONTRACT.md). It may only
   detect missed callbacks, an existing executable transition or durable owner
   wait, and must not plan, curate, implement or invent work.

No standing periodic role wakeups are the default. No watchdog is created.
Do not poll all workers periodically or wake the daemon every N minutes as the
default architecture. Possible communication failure alone permits no timer.
Direct messaging is the fast control path; repository truth is durable recovery.

[Revision 3](VALIDATION_AND_GATES.md): Tier 1 and affected Tier 2 block.
Tier 3 is honest debt unless it prevents/contradicts a named product fact.
Separate historical assertions from authenticated current behavior. Do not
globally repair validators, expand edit scope or exceed the successor budget
merely because a checker fails.

Two identical blocker/state tuples without new evidence trigger diagnosis and
a stop to repeated substantive redispatch. This does not stop an explicitly
authorized bounded condition check, a known long-running build/test still in
progress, or a legitimate transient transport retry allowed by policy. Ask the owner only after source inspection narrows
the question to an actual policy/domain choice or missing authority.

## 6. Make hardware testing economical

This section applies when H2/H3 hardware gating applies. Docs-only/H0/H1 work
with no hardware requirement does not need F/tree/UF2 custody or HEP machinery.

Preflight source, actual Config/schema, fixture/writer compatibility, route
applicability, artifact custody and restoration together. Run the actual
candidate validator before WRITE_READY; ask for required write approval on
the final independently reviewed packet.

Group controls/RGB/directions in one matrix. Test changed/affected supported
routes. Distinguish local menu actions from host output and expected selection
persistence from unexplained mutation. N/A, deferred and HOST_ONLY are not
physical PASS. Never improvise unsafe stimuli. Supplements cover only a
concrete missing required row, not another complete hardware run.

Keep exact F/tree/UF2 custody and **R → source-free E → tested-source I → separate
DONE**. Never rebuild as a substitute for preserved tested bytes. No merge before
required exact human HEP PASS; no automatic device action or public release.

## 7. Stop and leave a durable handoff

Stop dependent work for missing authority, genuine Tier-1/2 contradiction,
hardware evidence, owner/domain choice, or owner pause. Pause only the scope the
owner named; do not revive a timer because they authorized a one-off task.
If asked to finish one worker and stop, dispatch no successor.

Persist a repository chapter ledger: authority/stop state, workers/model/effort,
exact evidence/commits, lock, next permissible action, anomalies and deferrals.
Use passive telemetry already emitted by the runtime wherever possible:
new/resumed sessions, requested/observed model and effort, worker calls,
observable token usage, major phase timings and hardware-wait duration. Unknown
is unknown, not a placeholder zero. Do not poll, start workers, run
instrumentation passes or make additional agent calls solely to measure
orchestration cost; missing telemetry must not block work. Private chat state must not be the sole continuation record.

Optional `/goal`: one fresh daemon may have one owner-approved bounded
**chapter-level persistent objective**,
complementing the queue and gates. It may sustain already-authorized work; it
cannot create work orders, reinterpret PREAUTHORIZED conditions, clear
Curator/HEP/review gates, perform device writes, broaden chapter scope or
continue into the next chapter. Goal persists the outcome, not authority.
Retire/close it with its chapter using permitted runtime lifecycle controls. Budget exhaustion is not success. Use runtime lifecycle controls only
as authorized, and retain an honest incomplete/blocker state. See the templates
and assessment in the retrospective. Do not activate a Goal from this document.

At retirement, retire every roster entry and expire its chapter transport
authorization; retain the ledger as historical evidence, never authority for a
new chapter.

At retirement, report verified completion or the precise durable blocker,
artifact/decision locators and remaining owner action; release locks and stop.
Carry forward accepted evidence, not old pauses, stale prompts, chat identities,
model settings, or assumptions that every historical test applies to new source.
