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

## 4. Keep contexts clean

Use a **fresh subagent context by default for a materially independent
investigation**. Resume only when the same bounded work requires its prior
context, that context is relevant and clean, and role independence survives.
Never reuse a chat just for its convenient model setting. A known mechanical
transition inside the same clean product chain does not require a new chat.
Use native subagents for internal subtasks; creating a user-visible chat requires
the runtime's applicable user authorization.

Bound each worker to one deliverable: exact base, files, exclusions, checks,
budget, stop and return format. Split unrelated work. Fresh review receives
evidence, not the implementer's reasoning history. Summarize verified facts,
SHAs, failed attempts and questions at handoff, compaction or changed authority.
Retire contaminated contexts; never transfer the full chapter transcript.

## 5. Progress without loops

Process completed-worker events immediately when authorized. No standing periodic role wakeups are the default. No watchdog is created.
A future watchdog needs evidence of missed worker-completion events; it may
only detect missed callbacks, an existing executable transition or durable owner
wait, and must not plan, curate, implement or invent work. On callback failure, read the durable
result once and poll compact status; do not repeatedly retry, nag a running
worker, or require the owner to ferry messages.

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

At retirement, report verified completion or the precise durable blocker,
artifact/decision locators and remaining owner action; release locks and stop.
Carry forward accepted evidence, not old pauses, stale prompts, chat identities,
model settings, or assumptions that every historical test applies to new source.
