# Glyph daemon retrospective — 2026-10-10

Status: historical audit and future operating guidance. **No product work,
queue authority, release approval or next chapter is created by this report.**
The owner allowed the already-running Curator to finish, then authorized only
this retrospective and the [future bootstrap](../agent_framework/FUTURE_DAEMON_BOOTSTRAP.md).

## Findings in brief

The campaign delivered the bounded C020/C014/C017/C021/C022/C023/C024 repair
chain and associated H1 work, but completion required too much owner process
management. Exact artifacts, independent review and human hardware gates were
valuable. Repeated governance transitions, stale context, unnecessarily strong
model routing and incomplete result delivery were not necessary costs of safety.

The most important correction is architectural: **run the daemon on Luna,
normally low reasoning, with medium for coupled orchestration.** Route a finite
technical question to Sol when needed and reserve Astra for genuinely difficult
design or conflicting evidence. Do not keep an Astra conversation alive merely
to monitor workers. The owner's follow-up during this retrospective explicitly
endorsed a lightweight daemon with stronger called chats for high-level design.

Five changes would have prevented much of the steering:

1. Set and verify model/effort on every new **and resumed** assignment; route
   by the current task, not the chat's inherited setting or prestigious role.
2. One fresh daemon per coherent chapter; clean subagent contexts for independent
   questions, reuse only within a relevant, clean chain. Persist the handoff.
3. Advance already-authorized mechanical transitions from completion events;
   reserve Planner/Curator for actual missing decisions. Read failed callbacks
   directly instead of making the owner carry results between chats.
4. Classify every failed check against a named product fact. Preserve historical
   proof separately from current behavior; record unrelated framework failure
   as debt rather than recursively repairing the validation system.
5. Preflight hardware applicability, actual Config/schema, exact artifact custody,
   expected persistence and restoration together. Group observations and ask
   only for a missing safe, required physical fact.

## Evidence, scope and limitations

The primary history is daemon chat `01a0fcbd-2b4c-7d31-9088-42a22e260b57`,
created 2026-10-02 13:10:51 UTC. Historical audit cutoff is the final task request
on 2026-10-10 17:22:56 UTC, physical JSONL line 12764. New audit workers are
excluded from campaign counts. Times below are UTC; line numbers are physical
JSONL lines, not app message ordinals.

Source locator key:

- **D** — [daemon session JSONL](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl).
  `D:2458` means that file's line 2458. This contains original owner messages,
  assistant responses, tool calls/results, turn contexts and usage records.
- **H3** — [persistent executor JSONL](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl).
- **S** — [daemon state file](/Users/rasmus.pekkarinen/.codex/visualizations/2026/10/02/01a0fcbd-2b4c-7d31-9088-42a22e260b57/glyph-daemon-state.json).
  Useful for locating work, not proof of source truth or complete telemetry.
- **A** — [owner's October 3 orchestration addendum](</Users/rasmus.pekkarinen/.codex/attachments/a652c2f0-14a3-45db-b816-db24634148fa/Pasted text.txt>), supplied at D:1590.
- **G** — canonical `configurator` at
  `5a66ffc7b3a1eaf339b2af900de9b02aed68d8ad`, independently live-verified before
  this audit. The clean local evidence snapshot is
  `/private/tmp/glyph-c024-source-integration`. The primary checkout is older
  (`98c2ca04…`) with an existing writer edit; it is not substituted for G.
- **R** — current-at-G framework contracts, particularly
  `VALIDATION_AND_GATES.md`, `AUTHORIZATION_AND_RUNWAY.md`, `MODEL_ROUTING.md`,
  `SUBAGENT_CONTRACTS.md`, and structured `ACTIVE_AGENT_QUEUE.md`.

An owner directive proves the requested boundary. It does **not**, by itself,
prove that the daemon had already violated it. The tables distinguish admitted
mistakes, evidenced workflow failures, preventive clarification and genuinely
required domain decisions. Pasted worker reports are reports, not independent
verification. Heartbeats and peer relays are not fresh human instructions.
UNKNOWN is retained when creation identity, actual execution model, causation,
cost or timing cannot be recovered. This is an audit of retained evidence, not
a claim that every external hardware-terminal interaction was captured here.

## What happened

| Period | Evidence-backed course | Process consequence |
| --- | --- | --- |
| Oct 2–3 | Initial owner contract preferred full peer roles, one canonical writer and explicit ACK/results (D:12). C020/037 and KBD/040 encountered finite scope/applicability gaps; owner repeatedly relayed results (D:924, 1090, 1543, 1579, 1676, 1737, 1888, 2086). | Several stops were legitimate authority gaps, but the owner became a transport and scheduling operator. The October 3 addendum explicitly required immediate continuation and no-op suppression. |
| Oct 3 | Owner requested Sol/Terra/Luna (D:1657); reused workers stayed on Astra, acknowledged at D:2458. C020 reached a physical handoff; human results arrived at D:3157. | Model preference was applied incompletely. Successful build was correctly kept separate from physical acceptance. |
| Oct 4 | VAL044 aggregate/deadline work produced a policy loop. Owner replaced Revision 2 with Revision 3 (D:5040), authorized transport fallback (D:5783), and replaced chat-per-transition execution with persistent batches (D:7267). | The framework had made global proof health a barrier to bounded product progress. Repeated high-effort curation amplified the barrier. |
| Oct 4–5 | A stale pause relay stopped the campaign (D:7362–7433). Later real overnight/test pauses and resumes were explicit (D:8818, 8889, 9486). | Recency of delivery was confused with recency of authority. Later pause handling needed precise scope and chronology. |
| Oct 7–8 | C017 evidence advanced to C021. Full-width reference safety, VAL038 scope, failed-display proof, C022 defaults and hardware applicability each needed explicit owner direction. Implementation routing became Luna/medium (D:10964). | Some choices were real product decisions; others were avoidable overbroad proof demands. Repeating the Revision-3 instruction showed that writing the policy had not made it operational. |
| Oct 8–9 | C023 completed with explicit first-beta Keyboard deferral. C024/VAL045 needed finite predecessor correspondence and a one-file C012 adapter amendment (D:11725, 11856). C024 fixture preparation required several owner amendments. | Historical fixtures and current consumers had become coupled. Hardware preflight failed to collect schema, writer and compatibility constraints together. |
| Oct 10 | C024 physical evidence was adjudicated, historical build/review receipts recovered, and source integrated after HEP. A historical C019 expectation was mistakenly applied to the repaired selector; owner noticed the idle chat (D:12595). Correct routing enabled DONE. | Context/proof composition, not a new product decision, was blocking completion. Independent review also caught a real forged-integration evidence gap, fixed before publication. |
| Retirement | G has 99 orders, 98 DONE; VAL011 alone remains owner-deferred/nonexecutable. REL001 is absent from the executable queue. Curator prepared a proposal only; owner said stop (D:12743). | C024 DONE does not itself authorize public release or adoption of REL001. This daemon ends with documentation and the unadopted proposal. |

## OWNER_STEERING_THAT_SHOULD_HAVE_BEEN_UNNECESSARY

Each row states the preceding behavior, why it was costly/wrong, the owner's
fix and the bootstrap rule. **D-error** = daemon/execution error;
**F-flaw** = framework design/coordination flaw; **U** = unavoidable uncertainty;
**O-choice** = real owner/domain authority. Several episodes have mixed causes.

| Evidence / owner correction | What needed correction, and why | Prevention rule / classification |
| --- | --- | --- |
| Oct 2–3, D:924–2089: repeated pasted results; “Am I posting them … without any benefit?” | The owner could not tell which results the daemon had consumed. At D:2089 the daemon says it already read those reports, so not every paste proves a missed result. Transport failures and poor visible acknowledgment still made the owner act as message courier. | Durable result ID + consumed status, compact completion snapshot, readback on failed callback. Never require routine owner retransmission. **F-flaw + observability failure.** |
| Oct 3, A / D:1590: event-driven chaining, primary C020 priority, no-op suppression and churn budget | Known activations and predecessor resumes were being treated as separate routing opportunities, with heartbeat delays and generic role recovery risk. The addendum explicitly says the prior WebSerial curation is resolved. | Check the exact unresolved transition; continue immediately under existing authority. Do not repeat settled curation or launch a worker to report known WAITING. **D-error/F-flaw**, with some directives preventive. |
| Oct 3, D:1657, 2453, 2458: use cheaper models, including reused chats | The daemon promised cheaper future chats but resumed existing Astra chats without overrides. It explicitly admitted this. Switching to Sol/high fixed family selection but still did not establish a light mechanical lane. | Always set/verify model and effort on resume; do not confuse “not Astra” with economical routing. **D-error.** |
| Oct 4, D:3895, 4013, 5040: bounded deadline review, then forced Revision 3 | A full aggregate timeout/setup problem could stop an otherwise bounded repair and lead into framework policy review. The owner had to say that revising governance did not need permission from the old governance. | Name the unproved product fact. Owner process amendments are authority, not Planner proposals. Preserve Tier-3 debt; do not recursively prove the proof system. **F-flaw**, plus daemon failure to contain the loop. |
| Oct 4, D:5783: cross-thread MCP authority and fallback | Required ACK/results were vulnerable to approval/transport rejection. Further retries or additional chats would not improve product evidence. | One authorized send, then durable polling/readback on rejection. Transport failure neither grants nor revokes repository scope. **F-flaw/U**, not evidence of unauthorized messaging. |
| Oct 4, D:7267: persistent batch execution | Owner describes many tens of worker/chat calls for too little completed release work. That is a call/churn complaint, not proof of that many newly created chats. One-new-order rules forced repeated context/lock/ACK work. | Reuse a clean executor within one authorized chain; separate canonical lock from safe independent branch work. Fresh contexts for independent investigations, not every mechanical transition. **F-flaw + orchestration inefficiency.** |
| Oct 4, D:7420, 7423, 7430: old pause is not current | Daemon stopped H1/H3 and the timer after a reused chat relayed a days-old pause. It had not verified the original timestamp, and admitted that error. | Resolve original owner message and chronology before changing state. A fresh relay is not a fresh instruction. **D-error.** |
| Oct 4, D:8063: slow heartbeat from 10 to 20 minutes | The owner requested fewer scheduled wakeups. This establishes a cadence preference, not a measured attribution of cost to those wakes. A scheduled wake must not stand in for completion handling. | Prefer events/compact snapshots; owner controls cadence. Batch independent reads; no repeated unchanged narration. **Owner preference/process economy.** |
| Oct 4, D:8376: reserve C014 hardware checkout | Explicit protection was needed for a live physical-test environment while other work continued. The notice does not prove the daemon had already mutated it. | Treat test checkout, candidate and artifact as frozen exclusive custody until evidence no longer needs it. **Preventive safety boundary.** |
| Oct 4, D:8595: inspect original Glyph/HayBox before deciding Keyboard raw output | The owner asked for source comparison rather than choosing a speculative output transformation. Original behavior was a source question; whether to change it was a product question. | Inspect original pipeline first. Ask only about the residual semantic choice. Preserve `PRESERVE_ORIGINAL_RAW_KEYBOARD_OUTPUT`. **Mixed source-resolution opportunity/O-choice.** |
| Oct 5, D:9486, 9515: pause during testing; no need to message inactive chats | A global pause protocol need not generate messages to chats that are already idle. The response says no such messages were sent. | Snapshot liveness and message active work only. Persist the pause locally. **Preventive process correction**, not a proven extra-send incident. |
| Oct 7, D:9532: C017 dynamic RGB applicability | Report cautiously said PARTIAL because direct Switch USB was absent, although SHIFT/XWAVE had actual Mac/XInput output evidence and excluded the GC backend. | Derive required transport from the binding protocol/source; do not turn one untested platform into a universal extra gate. Ask only for a bounded supplement if truly required. **Protocol overconstraint risk**, not proof an extra run occurred. |
| Oct 7, D:9699: validate full decoded reference before narrowing | A real 256→0 truncation defect needed a bounded fix and boundary tests, not a new Planner/product cycle. Existing invalid-zero semantics were not open. | Inspect type flow and test full-width values before casts; preserve messages and valid behavior. **Concrete product defect + correct bounded authority.** |
| Oct 7, D:10226: VAL038 must remain product-bounded | Coupled host literals, zero-checker SETUP_FAILURE and global timeout threatened to keep C021 waiting despite focused evidence. | Repair only actual affected admission/execution; stop expanding once those facts pass. Preserve failures as debt, never PASS. **F-flaw + recurring scope-control failure.** |
| Oct 7, D:10603: failed-display row may be HOST_ONLY | Physically forcing `display.begin()==false` had no safe reviewed route. A mandatory destructive stimulus would test beyond the intended rejection property. | Design safe stimuli first; prove suppression/refusal in host/source when owner-approved physical non-testability applies. Never label it physical PASS. **O-choice for acceptance boundary; preventable protocol-design burden.** |
| Oct 8, D:10782: count 20→11 and LF1 explicitly black | Source defaults were malformed. Count-only repair would change inferred LF1 appearance. The owner selected the intended appearance and required a grouped block-11 observation. | Show the actual before/after table and distinguish source inference from historical physical proof. Group the complete RGB matrix once. **Real O-choice**, not bureaucracy to eliminate. |
| Oct 8, D:10964: all implementation messages Luna/medium | Owner again had to specify economical routing, explicitly linking strong-model use to “proofs on proofs.” | Lightweight daemon; explicit Luna/medium execution default. Escalate only a named finite uncertainty and de-escalate afterward. **Process correction.** |
| Oct 8, D:11151: absent dynamic profiles and normal MB1 menu behavior | C022 fresh Config had only STATIC blocks. MB1 lit and opened the menu without host output. Requiring synthetic animations or interpreting local menu action as gameplay output would widen scope. No such repair is proven to have shipped. | Inventory applicability; local UI and host reports are distinct domains. N/A with source proof is not an evidence gap. Do not create profiles or disable a correct menu just to satisfy a table. **Preventive overconstraint correction.** |
| Oct 8, D:11586: C023 Keyboard deferral and pending-review discrepancy | Owner explicitly removed Keyboard physical support from first-beta requirements and required live resolution of a stale “review pending” note. | Preserve historical protocol plus current supersession; do not re-test deferred rows. Resolve review receipts mechanically. **O-choice + documentation consistency issue.** |
| Oct 9, D:11725: VAL045 synthetic failure and critical drift classification | Worker reported it could not reach review because synthetic predecessor setup and critical-source drift failed. Owner required finite classification against accepted C021/C022/C023 identities. | Separate exact accepted predecessor deltas from arbitrary drift; execute actual consumers. Synthetic topology failure alone is debt. **F-flaw + avoidable overblocking.** |
| Oct 9, D:11856: exactly one C012 checker adapter path | Independent review rejected an edit outside scope even though the affected checker was required to run. Read authority was not edit authority. | Plan proof adapters with implementation scope. When genuinely missing, request the exact path amendment once. Preserve immutable historical assertions and fail closed on unknown current source. **F-flaw in contract completeness; correct authority stop.** |
| Oct 9, D:12059: pause timer; Oct 10 D:12544 | Timer was explicitly paused, yet a later heartbeat arrived and saved schedule was found active. The cause of reactivation is not established. | Treat task execution and timer activation as separate permissions; verify saved pause state and do not infer resume from a one-off instruction. **Observed scheduling inconsistency/U**, not proven intentional disregard. |
| Oct 9, D:12088–12122: duplicate fixture using X1 | Existing Config had no suitable pair. The requested per-profile X1 discriminator was impossible in the current schema; X1 was compiled in. Executor stopped correctly. | Preflight representability before promising a physical protocol. Return a concrete source-backed alternative; do not improvise encoding. **U/O-choice, correct stop.** |
| Oct 9, D:12131: replace existing remaps; locate exact UF2 | Owner found RF1/RF2 identity remaps already existed and warned that appended duplicates would be ignored by first-match handling. Expected artifact was absent from the operator path. | Decode the fresh Config, follow the whole remap pipeline, label both index conventions, and verify terminal-visible custody before handoff. **Avoidable preparation gaps**, with owner amendment needed for the new discriminator. |
| Oct 9, D:12219: narrow duplicate-Ultimate writer exception | The writer's exactly-one-Ultimate guard rejected the authorized fixture. That local guard was not a firmware invariant. | Audit fixture acceptance through every tooling layer in advance. Preserve ordinary safeguards; explicit exact-fixture exception only with authority. **Tooling/contract mismatch; correct fail-closed stop.** |
| Oct 9, D:12276–12295: Layer A C022 compatibility, then duplicate fixture | A write-ready packet passed the fixture guard but not the actual C024 production validator. Daemon caught the known malformed RGB block and retracted it. | Production validation is a prerequisite to WRITE_READY, including legacy compatibility. Gather all required bounded permissions in one preparation packet. **Premature worker readiness claim; daemon caught it.** Layering remained a legitimate owner permission. |
| Oct 10, D:12344: account for expected mutable selection state | GameCube default reference 3→1 followed owner profile selection and source-backed persistence. The owner explicitly supplied that attribution. | Define exact allowed persistence fields and observed actions before diffing; unexplained changes remain anomalies, explained selection is not corruption. **Evidence-interpretation correction**; physical timing attribution still needs the owner. |
| Oct 10, D:12344: retain freeze, no reproduction loop | One freeze recovered on restart and did not reproduce in one authorized repeat. Owner required independent adjudication without erasing it or manufacturing a deterministic defect. | Preserve the anomaly and limits; no endless retests, invented root cause or stability guarantee. **Genuine evidence judgment/O-boundary.** |
| Oct 10, D:12595–12648: idle executor after C019 mismatch | Current C024 selector was tested against the old first-name-match expectation. The executor asked which behavior should govern, although repaired row identity was already authorized. Daemon resolved this from source only after owner noticed inactivity. | Separate historical and current tests; inspect a stopped worker's exact failure before asking the owner. Correct missing propagation, not product policy. **D-error in orchestration + worker proof composition.** |
| Oct 10, D:12743, 12764: finish Curator, then stop; retrospective only | Owner deliberately terminated progression before a new chapter. A completed proposal is not permission to adopt it. | Drain only named work, persist stop, no successor. Retire with a usable handoff. **Owner scope control**, honored rather than treated as a failure. |

### What should still reach the owner

The USB-zero/no-fallback semantics (D:205), LF1 appearance choice, first-beta
Keyboard support, temporary Config mutation and writer exceptions, unsafe-row
acceptance treatment, and final public release are genuine owner decisions.
The improvement is to present them once, after source inspection, with a precise
diff/claim and safe alternatives. “Ask less” must not become unauthorized action.

Likewise, the owner is the source of physical observations. Hashes and tests
cannot establish whether the owner selected a GameCube profile between captures.
The daemon can verify that the reported mutation matches source behavior; it
cannot invent the intervening action.

## Model, session and cost audit

### Quantities that can be established

Before D:12764 the daemon log contains **287 turn-context records: 286
`gpt-6-astra/medium`, one `gpt-6-astra/high`**. These are context records, not
287 independent new chats. There are **181 heartbeat user-message records** and
**11 compaction records**. All of those figures exclude this retrospective.

Summing the `usage` field of 1,806 distinct daemon `token_usage_record.response_id`
records, restricted to its own `thread_id`, yields:

| Recorded daemon usage | Tokens |
| --- | ---: |
| Input, including cached input | 304,262,298 |
| Cached input (subset of input) | 298,883,072 |
| Output | 439,556 |
| Reasoning output (subset; not added again) | 11,545 |
| Input + output | 304,701,854 |

These counts include repeated context presented to requests; they are not unique
text. About 98.2% of input was cached. Cumulative `turn_token_usage` and
`thread_token_usage` were **not summed**. App credit conversion, historical
plan pricing, promotions and an invoice are unavailable; actual spend and
counterfactual savings are **UNKNOWN**. A model-comparison experiment was not run.

For scale only, the official API model comparison fetched on 2026-10-10 lists
input/output rates per million tokens of Astra $10/$50, Sol $2/$10 and Luna
$0.10/$0.50; cache and other pricing differ. These are current API unit prices,
not the cost of these desktop sessions. They support economical routing, not a
retrospective dollar bill. [Official model comparison](https://developers.openai.com/api/docs/models/compare)

The canonical range from initial `3dac79dac4eefcf832510817e8cb5ecd6a27f219`
to G contains **218 first-parent commits / 258 total reachable range commits**.
Those include legitimate implementation, evidence and review work; counting
them does not prove waste. S's `metrics_since_directive` still has zero
mechanical handoffs/no-op counters despite visible dispatches and only partial
per-order timings. Those placeholders cannot support a claim of zero overhead.

### Where strong reasoning helped, and where it did not

Independent review materially helped catch real source/acceptance gaps:
the C020 ABI/source boundary, finite predecessor/source authentication, and the
C024 forged P/F merge that could alter HEP evidence. The last review is directly
recorded in reviewer chat `01a12117-1a6b-7871-9417-33ee33c71846`, final messages
`msg_0d06479834618cf3016aca2b903b10819192f080f0ba30ffb7` and
`msg_0d06479834618cf3016aca2bebd714819181b6043002a4a7de`.
That reviewer ran **Luna/medium**, not Astra. The repaired gate rejected all 22 controls before publication. The useful
contribution was a concrete counterexample and finite repair, not more layers
of global validation.

That does not prove Astra was necessary for those findings. The session
inventory below distinguishes observed execution from requested models. Without
a controlled comparison, “materially helped” means a useful result occurred in
that session; it does not establish superiority over Sol or Luna.

For the daemon's own Astra use, source diagnosis at D:12635 correctly recognized
historical C019 expectations conflicting with C024's intended repair. Original
build-log/review recovery at D:12433–12497 also avoided an unnecessary rebuild.
Those were useful outcomes. Neither required leaving the whole orchestration
chapter on Astra. The historical receipt recovery was a finite mechanical batch
that could have gone to Luna with exact chat/turn identifiers; the source question
was suitable for a bounded Sol investigation if Luna could not resolve it.

Routine `ls-remote`, hash readbacks, queue/status reconciliation, timer updates,
compact worker snapshots and known-path evidence packaging did not justify a
persistent Astra controller. A single such check should stay in a lightweight
daemon; a large repeated batch should go to Luna. Moving every tiny check into
a fresh agent would add more context and messaging than it saves.

After the October 3 correction, the daemon's recorded preference used Sol/high
for complex supervisors/curation, but the owner still had to specify Luna/medium
on October 8. The failure was not simply choosing Astra; it was lacking a
task-level cost/uncertainty rule and an explicit de-escalation step. The daemon
itself remained Astra throughout the audited context records. Its model may
have been an app/thread setting rather than a choice changeable from inside
the turn; the correct response was to recommend a lightweight replacement or
setting change, not silently assume worker overrides solved root cost.

### Specific Astra outcomes and cheaper alternatives

The following are observed work products in Astra sessions; the transcript
links in Appendix A authenticate the model. These examples establish useful
contributions, **not that Astra was uniquely needed**.

| Session/task and final-answer line | Material contribution | Routing assessment |
| --- | --- | --- |
| `01a0fd0e-2288` / `kbd_source`:105 | Traced KeyboardMode remap/SOCD on a copy while `UpdateKeys` consumes original input; distinguished default MB mappings from actual key output. | Useful source synthesis. Sol/medium is the appropriate first attempt; no evidence that Astra was necessary. |
| `01a0fd0f-44e4` / `kbd_host`:138 | Reported 103 observations, eight lifetime cycles, sanitizer agreement, 118 identity negatives and five behavior mutants against production bodies. | Substantial technical work, reasonable delegation. Sol/medium with escalation fits; large proof counts alone do not justify Astra. |
| `01a0fefc-9349` / `validation_audit`:150 | Isolated WebSerial historical scope conflict and ruled out three imagined correspondence blockers. | High-value ambiguity resolution; a bounded strong model can help here. Sol/high first, Astra if unresolved. |
| `01a0fd51-6d0c` / `val040_authority`:60 | Identified the exact three checker edits absent from authority rather than silently widening scope. | Legitimate independent judgment; source-bounded Sol/medium/high. This was not routine mechanical publication. |
| `01a0fd3b-d48e` / `kbd_recovery_preflight`:83 and `01a0fd4f-331b` / `kbd040_source`:103 | Rechecked pinned inventory, critical entries, object availability and unchanged source. | Useful but mostly mechanical; Luna/medium batch, not Astra. Avoid repeated complete preflights when no inputs changed. |
| `01a0fd55-1032` / `val040_stop_review`:114; `01a0fef1-a5aa` / `c020_handoff_review`:133; `01a0feff-7b55` / `blocker_review`:137 | Checked narrow source-free status/handoff publications and unrelated-order preservation. | Independence justified; Astra not justified by this finite task. Use Luna/medium review without unnecessary full-chat creation. |
| `01a10123-fc20` / `runner_policy_v3`:485 and `01a10124-3212` / `accepted_transition_v3`:742 | Reported test-only optimization to 4.36 seconds and 7.4 seconds saved respectively. | Real optimization, but framework performance should not drive the chapter absent a required product fact. Sol/medium if authorized and necessary; cheaper model cannot cure excessive scope by itself. |
| `01a1012a-896d` / `final_review_v3`:615 | Completed exact DONE conformance after 18 Astra/medium contexts. | Review useful; repeated final status verification should resume the same bounded reviewer on Luna after hard findings are resolved. Context count alone cannot identify all 18 turns as waste. |

A concrete context-retirement case supports the clean-session policy. The reused
`01a10410-ff42` worker twice returned stale branch-management instructions
after compaction instead of finishing its current Revision-3 publication task
(D:6543, 6917). The daemon revoked its publisher role,
recorded `RELEASED_CONTEXT_CONTAMINATED_DO_NOT_REUSE`, and created `01a10757-7fe3`
for finite reviewed publication (D:6900–6958). **Creating fresh context here was
justified.** Using Sol/high for the new publication verifier and its own child
verifier was a likely routing excess: the ambiguity had already been reviewed.
Reusing contaminated context to save one chat would have been false economy.

### Delegation evidence and inventory

Inventory methodology and individual session rows follow in Appendix A. A
successful creation/spawn result plus matching session identity proves NEW;
a send/resume to a previously identified session proves REUSED for that call.
First contact alone does not prove creation. Forked/inherited text is not a new
dispatch. Requested overrides are not proof that the destination executed with
them. Native child sessions and full user-visible chats are counted separately.

The initial full-peer topology was owner-requested (D:12), so using major peer
roles was not itself a mistake. The October 4 owner correction changed the
economics: too many repeated transitions/context reloads, not simply too many
distinct IDs. Conversely, retaining the H3 chat titled “Publish C020 candidate
handoff” into C024 made its purpose difficult to see. Reuse was then authorized,
but misleading titles and stale instructions needed active cleanup.

## Framework design flaws and retained safety value

| Design pressure | Failure mode observed | Keep / change |
| --- | --- | --- |
| One-new-order invocation, ACK/RESULT and lock handoff at each step | Repeated redispatch and role context setup for known successors | Keep bounded orders and one publisher; batch a coherent authorized chain in one clean executor. |
| Global aggregate and whole-file historical pins | Timeout/setup/source-shape failures confused with product rejection | Keep exact source authentication and affected execution; separate historical and current modes and classify Tier-3 debt. |
| Many bespoke allowlists and checker consumers | A required consumer could lack edit authority; narrow amendment chains followed | Inventory actual consumers/adapters before authorizing a candidate; never auto-expand the edit list. |
| Role defaults “strong synthesis/high” | Mechanical curation/review inherited expensive models | Route by task uncertainty, verify settings, de-escalate after the decision. Independence is about evidence and role, not model size. |
| Durable state mixed with old narrative/status | Old pauses and stale hardware-step heartbeats outlived their meaning | Separate current authority and stop state from dated evidence; rebuild each heartbeat from durable current state. |
| Protocol rows written before actual Config inspection | Missing profiles, impossible X1 fixture, writer guard and legacy RGB incompatibility surfaced serially | Joint source/Config/tooling/custody preflight before asking for physical work; explicit applicability and grouped matrix. |
| Exact R/E/I ordering and independent review | Prevented source entering evidence commits and caught forged-integration acceptance | Retain. The retrospective is not an excuse to weaken exact hardware acceptance. |

An error must not be called “framework debt” merely because it occurs in a
checker. C024's forged-merge gap was a concrete evidence-integrity contradiction.
C019's obsolete name-match expectation was a test-domain mismatch: historical
proof still had to execute, and actual repaired-source consumers still had to
pass. The distinction requires source-backed classification, not blanket waivers.

## Future model and context policy

The bootstrap contains the operational table. The policy is **lightest reliable
lane, with explicit escalation**, not “always the cheapest model.”

- **Daemon:** Luna/low, medium when reconciling dependent state. Keep tiny reads,
  result verification, authority chronology and dispatch decisions here.
- **Mechanical/frequent worker:** Luna/low; medium for multi-step guarded
  fixtures/evidence. A bounded test failure or contradictory source promotes
  only the unresolved question to the technical lane.
- **Technical/integrative worker:** Luna/medium for known patterns; Sol/medium
  for coupled edits, source correspondence, finite diagnosis or test design
  that exceeds that pattern. Escalate after a concrete failed hypothesis, not
  because a task title says “supervisor.”
- **Ambiguous/high-leverage worker:** Sol/high first. Astra/medium or justified
  high only for novel safety architecture, difficult conflicting evidence or
  root cause beyond a finite cheaper attempt, within owner model policy. Return
  a decision/counterexample and end that session; routine execution returns to
  Luna. Irreversible decisions still require owner authority.

Default to a fresh subagent for an independent investigation. Resume only if
the same scope needs its previous context, the context remains clean and current,
and independence is preserved. Never resume because its model is convenient.
Use native subagents rather than inventing user-visible chats without permission.
A reviewer should get the exact contract/diff/evidence, not the implementer's
entire reasoning transcript. Same reviewer may recheck its own finite finding;
it must not become the author and then approve that change.

A worker owns one finite deliverable or one already-authorized coherent chain
to its next hardware/domain stop. It must not widen into portfolio redesign,
generic framework repair or a second unrelated chapter. Summarize on phase
completion, changed authority and compaction; split if the next question no
longer benefits from prior context. There is no evidence-backed universal
token count at which a session becomes bad. Use relevance, repeated mistakes
and recovery overhead, plus the owner's budget, to decide retirement.

The durable chapter ledger must contain exact current authority, permitted next
action, worker IDs/model/effort, source/evidence identities, lock owner,
unresolved facts, artifact locators and actual usage/timing measurements.
Do not copy this daemon's full state JSON into the next chapter as instructions.

## `/goal` assessment

**Recommendation C: optional complementary chapter-level persistent objective.**
Do not activate one in this retrospective.

Official documentation describes Goals as thread-scoped persistent objectives
with continuation, evidence-based completion and lifecycle/budget controls.
That addresses repeated “continue” prompts, but does not establish project
authority or hardware acceptance. Runtime rules for pausing, blocked status and
completion remain binding. Budget exhaustion must not be reported as success.
[Official Goals guide](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex)

| Existing control plane | What a Goal would add | What it must not replace |
| --- | --- | --- |
| Roadmap chapter | Keep one outcome in view between turns | Owner choice of chapter or exclusions |
| ACTIVE_AGENT_QUEUE / orders | Continue when an existing objective transition becomes executable | READY/PREAUTHORIZED authority or scope |
| Curator / Planner | Track that their finite decision is needed | Independent adjudication or inventing work to maintain momentum |
| Executor / review | Resume known work and check deliverables | Exact implementation gates, independence or honest failed results |
| R → E → I | Remember which transition is next | Reviewed handoff, source-free human evidence or tested-source ancestry |
| Hardware gate | Persist a precise wait reason | Fabricated observations, new physical testing or automatic flashing |
| Revision-3 tiers | Keep candidate safety as the finish condition | Classifying all errors as debt, or requiring all framework debt green |
| Owner/domain stop | Retain an incomplete durable handoff | Continuing because a goal remains active, reopening settled scope or starting a new chapter |
| Heartbeat | May reduce repeated scheduled wakeups for authorized continuation | An independent source of authority or permission to reactivate a paused timer |

A Goal would have helped with unnecessary idle transitions, but an unbounded
“finish the release” Goal could have intensified exactly the proof recursion
seen here. Its constraints, budget and terminal handoff are more important than
its persistence. Fresh daemon per chapter also means a fresh, reviewed Goal;
the old Goal is not portable project memory.

### Generic future `/goal` draft

This is text for future owner review, not an executed command:

```text
/goal Complete the owner-approved chapter <chapter and canonical contract>
to <evidence-verifiable outcome>, within <owner-set resource/time limits>.
Use only complete READY orders, objectively activated named PREAUTHORIZED
work and explicit current owner exceptions. Keep <exclusions> unchanged.
Verify live canonical, exact source/artifact identities, applicable Tier1/2
checks, independent review and required R -> E -> I hardware acceptance.
Record unrelated Tier3 failures honestly without repairing them for their own sake.
Delegate using the bootstrap routing policy; keep this daemon lightweight.
If authority, owner/domain judgment or human hardware evidence is missing,
record the exact blocker, preserved state and next permitted action; stop
dependent work. Use only lifecycle states permitted by the runtime; pause only
on my explicit request, and retain an honest blocker while awaiting input.
Do not interpret the Goal as permission to create work, alter scope, write a
device, publish a release or begin another chapter. Mark completion only when
the stated outcome is actually evidenced. At completion or durable handoff,
release locks, return the chapter record and retire this daemon.
```

The owner supplies any numeric budget explicitly. The runtime controls actual
Goal lifecycle semantics; if a tool requires repeated blocked observations,
that is not authority for extra substantive work between observations.

### Concrete draft: proposed next Glyph chapter

**Example only, conditional on fresh owner chapter approval and valid REL001
adoption.** The completed Curator proposal is not an executable order:
`/private/tmp/glyph-rel001-proposal-20261010/proposal.md`, SHA-256
`e8295e68ed6fb2ad62cf86eb4b00abb3be4346c058835f8bd3b74cbbeb4407e4`.
It proposes H0 release readiness and an endpoint of READY_FOR_OWNER_PUBLICATION.
It was not adopted before retirement.

```text
/goal Prepare the first Glyph public-beta readiness dossier under a newly
verified, complete GP-REL-001 contract. End at READY_FOR_OWNER_PUBLICATION
with an independently reviewed evidence-to-claim matrix, exact package and
rollback identities, recovery instructions and explicit known limitations.
First verify that REL001 is actually authorized; if absent, stop for its
bounded adoption. Candidate proposed for evaluation is C024 F8ab1173b...
and preserved UF2 95de108f...0ba0e6 (803840 bytes), not a new build from the
later canonical tip. Authenticate full identities from canonical evidence.
Preserve Keyboard physical deferral, Nunchuk NOT_TESTED, the C021 failed-display
HOST_ONLY boundary and the unresolved C024 freeze. Earlier feature evidence
must retain its own candidate/artifact scope; it is not new whole-RC testing.
No firmware change, framework cleanup, device action, rebuild, new physical
test or public release is authorized by this Goal. Stop dependent work for any
missing required product fact or owner decision and report the exact blocker.
Follow runtime lifecycle rules; pause only on my explicit request. Retire after the reviewed
dossier or durable blocker; publication remains the owner's separate decision.
```

## Retirement handoff: what the next daemon must not inherit

Verified endpoint: strict C024 DONE at G, direct catalog parent
`b8ff43b36d9286ce39a1cdb21db632233162243d`, genuine integration
`5c5ba4e166c9b67654c0d1b9baa2b0c35677f3d4`. Tested F remains
`8ab1173b0690f5ed3e994f95af797c9e9a265525`; tree
`15ed2d35d561d6b1709499fe42083ca4d789e920`; UF2 SHA-256
`95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6`,
803840 bytes. Reviewed R `36f91089ab60fb68248a2819aee5dd5082fd922c` precedes
source-free E `25f39876c21fa429a47c93dc446205c37d72b8d3`.

The Curator finished its proposal without repository mutation. REL001 remains
absent from executable items, VAL011 remains owner-deferred, and the timer stays
paused. Final human release approval has not been given. The next daemon must
verify fresh truth rather than use this dated endpoint as live authority.

Do **not** inherit Astra as the control-loop default, the C017-focused stale
heartbeat text, historical pauses as current commands, zero-filled counters,
the old worker roster as mandatory infrastructure, an old chat's model setting,
historical whole-file expectations for changed semantics, or a blanket promise
to keep generating work until public release. Do not inherit this primary
checkout's uncommitted writer change as an approved chapter change. Preserve it
and independently establish ownership before any later edit.

The new chapter should inherit only accepted source/evidence, current owner
scope, explicit unresolved limitations and a reviewed chapter contract. In
particular, C024's nonblocking freeze disposition is not a demonstrated fix or
general stability guarantee; Keyboard/Nunchuk have no new physical acceptance.

## Audit production and verification

This audit used two fresh Luna/medium native specialists: one for original owner
steering and one for session/model telemetry. Their scopes were read-only and
independent of each other. Root wrote the two requested documents. Audit-session
work is outside the historical campaign totals. No Goal, product worker,
roadmap chapter, queue change, firmware build or hardware action was started.
A separate fresh Luna/medium reviewer, `/root/retrospective_review`, reviewed
both documents, then resumed only to review the completed inventory and fixes.
Its findings corrected Goal pause wording, unsupported cost attribution,
bootstrap length, ambiguous shortened session IDs and stale-context description.
The final session prefixes are mechanically checked unique across all 145 IDs.

Validation: documentation navigation and framework-docs checkers PASS; both new
files pass local-link existence, balanced-fence and whitespace checks. These
checkers do not prove historical accuracy; the log-based audit/review supplies
that. Only the two requested repository documents were added. The pre-existing
writer edit remains byte-identical (SHA-256
`4de5753855eb42b9d462e2ab2c1a59b2c47d5a8cb43a31ab588e471d2cbc7368`).
No commit, push, queue adoption or bootstrap installation into AGENTS was made.
The next owner-approved daemon must explicitly read the bootstrap; merely
creating this file does not make the app load it automatically.

## Appendix A — individual delegation inventory

The following inventory is generated from retained session and dispatch evidence;
its limitations are part of the result, not silently filled from chat titles.

### A1. Counting rules and direct peers

The daemon referenced 15 other thread IDs: **9 explicit new user-visible chats,
4 pre-existing chats explicitly resumed/messaged, and 2 read-only references**.
The latter two are not delegation events. One is a pre-existing supervisor;
one is an independently created H3 child. The recursively reachable inventory
contains **144 non-root sessions (145 including the daemon)**, not 144 chats
created by the daemon. It includes native descendants and pre-campaign history.
NEW below is established from creation result/session metadata and parent
activity; a subsequent turn in that same ID is reuse, not a new chat.

Each linked 13-character prefix is unique in this inventory; the link contains
the full session ID and actual local transcript. Models/efforts are **executed
turn contexts within the campaign window**, not inferred from names. `×N` counts
contexts, not distinct assignments. Token figures are per-session response usage
in that window, including cached input. Actual spend remains UNKNOWN.

Routing judgments are retrospective recommendations, not measured model comparisons:
**M** = mechanical work should normally use Luna low/medium; **T** = technical
work warrants Luna/medium or Sol/medium, with high/Astra necessity unproven;
**J** = independent policy/authority judgment merits Sol/high only for substantive
ambiguity, Luna for an objective transition. Unknown purpose cannot justify a
model recommendation. Independent review remains required even when the model
is cheaper. A reused session can contain several task types; these labels do
not declare every one of its turns wasteful.

| Session | Creation/interaction proof and purpose | Requested override values (sets, not pairings) | Actual model/effort contexts | Recorded input+output / routing judgment |
| --- | --- | --- | --- | ---: |
| [01a0f9a8-c7c7](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1) | REUSED, [D:62](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:62); Existing Planner: refresh release-policy portfolio packet. | gpt-6.1-sol/high | Sol6.1/medium ×5; Sol6.1/high ×8 | 31,883,689; J |
| [01a0fc9f-0304](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T15-37-54-01a0fc9f-0304-78d1-ae2f-0d77f1cfe901.jsonl:1) | REUSED, [D:74](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:74); Existing Implementation Supervisor: finish GP-CONFIG-013; later completion-report queries. | not observed; UNKNOWN | Luna/high ×9 | 32,133,082; T |
| [01a0fb83-d843](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:1) | REUSED, [D:470](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:470); Existing Curator: adjudicate campaign work-order packets. | gpt-6-luna, gpt-6.1-sol/high, medium | Sol6.1/high ×15; Luna/medium ×1 | 49,024,923; J |
| [01a0fc42-8cff](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T13-56-55-01a0fc42-8cff-7d31-a291-30e583f1397d.jsonl:1) | REFERENCE ONLY; no daemon dispatch, [D:528](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:528); Existing release-safety supervisor chat; read-only single status/review reference. | not observed; UNKNOWN | none in window | 0; UNKNOWN from reference |
| [01a0fd0c-fc95](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-38-01-01a0fd0c-fc95-7c73-a4f2-f9a46bb3cb35.jsonl:1) | NEW, [D:548](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:548); New peer for GP-KBD-001 Keyboard pipeline characterization and handoff. | not observed; UNKNOWN | Astra/medium ×2 | 18,209,469; T |
| [01a0fd4e-004d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-49-03-01a0fd4e-004d-7130-91db-41c2e1d84ae0.jsonl:1) | NEW, [D:762](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:762); New peer for GP-VAL-040 Keyboard correspondence governance. | gpt-6.1-sol/high | Astra/medium ×1; Sol6.1/high ×12 | 64,837,233; T |
| [01a0feea-53d7](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:1) | NEW, [D:1284](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:1284); New persistent C020/H3 implementation and integration executor; continued through C024 and release curation. | gpt-6-luna, gpt-6.1-sol/high, medium | Astra/medium ×4; Sol6.1/high ×35; Sol6/high ×2; Luna/medium ×37 | 687,300,408; T |
| [01a0fefb-64e0](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:1) | NEW, [D:1428](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:1428); New peer for GP-VAL-037 C020 governance implementation. | gpt-6.1-sol/high | Astra/medium ×8; Sol6.1/high ×5 | 175,246,946; T |
| [01a102f9-e845](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:1) | NEW, [D:3183](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:3183); New independent Hardware Evidence Processor for C020, then C014/C017/C021-C024 evidence. | gpt-6.1-sol/high | Sol6.1/high ×17 | 79,951,706; T |
| [01a10410-ff42](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-19-45-01a10410-ff42-7091-a4d7-74fd6ff3310a.jsonl:1) | REUSED, [D:3907](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:3907); Existing peer assigned Revision-3 control-plane and GP-VAL-044 source-free publication work. | gpt-6.1-sol/high | Sol6.1/high ×10 | 42,691,858; T |
| [01a10665-7c42](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:1) | NEW, [D:3922](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:3922); New independent Curator for GP-VAL-044 validation-runway adjudication. | gpt-6.1-sol/high | Sol6.1/high ×9 | 25,567,505; J |
| [01a10677-20a8](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-30-32-01a10677-20a8-77b1-8970-2c7d9d7bdcc1.jsonl:1) | NEW, [D:3993](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:3993); New peer for GP-CONFIG-019 ordinary USB name-selection characterization. | not observed; UNKNOWN | Sol6.1/high ×1 | 11,120,723; T |
| [01a106b7-d244](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T14-41-12-01a106b7-d244-7761-94b7-d593e68ed449.jsonl:1) | NEW, [D:5078](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:5078); New independent Revision-3 review of GP-VAL-044. | gpt-6.1-sol/high | Sol6.1/high ×1 | 1,925,214; T |
| [01a10757-7fe3](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T17-35-37-01a10757-7fe3-76b1-9bde-a3b52bc9088b.jsonl:1) | NEW, [D:6958](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:6958); New independent publication verifier for reviewed Revision-3 control-plane work. | not observed; UNKNOWN | Sol6.1/high ×1 | 5,559,164; T |
| [01a12117-1a6b](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/09/rollout-2026-10-09T17-35-24-01a12117-1a6b-7871-9417-33ee33c71846.jsonl:1) | REFERENCE ONLY; no daemon dispatch, [D:12673](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-10-51-01a0fcbd-2b4c-7d31-9088-42a22e260b57.jsonl:12673); H3 independent C024 review (verified from its own review receipts; purpose absent from daemon read request). | not observed; UNKNOWN | Luna/medium ×9 | 13,113,078; UNKNOWN from reference |

Nine explicit creation results occur at D:548, 762, 1284, 1428, 3183, 3922,
3993, 5078 and 6958. Omitted model overrides are not evidence of execution;
the actual-context column supplies that evidence. Direct peers marked REUSED
were not newly created by this daemon. Their creation details outside the
retained dispatch scope are not inferred.

### A2. Native descendants and prior related sessions

This table covers the remaining 129 IDs. Purpose is the **recorded task label**,
not an invented account of all work done. The parent/line points to the recorded
`SubAgentActivity.started` event; the session link points to identity metadata.
All have subagent metadata and a matched parent event. “NEW native” describes
their original creation, not every later resume. “Pre-window” means creation
predates this daemon, so it must not be counted as this daemon creating a chat.
Individual requested spawn overrides were not fully reconstructed: UNKNOWN;
actual model execution is shown. It is sufficient for the model-use audit but
not a claim that every child honored every request. If no context ran during
the window, no campaign-window adequacy/cost claim is made.

| Session / original task label | New/reused provenance | Actual model/effort contexts | Recorded tokens | Recommended lane |
| --- | --- | --- | ---: | --- |
| [01a0f9a9-6473](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-50-23-01a0f9a9-6473-7c32-86d3-f21e99e25fac.jsonl:1) `usb_audit` | Pre-window native creation; parent [01a0f9a8-c7c7:42](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:42) | none in window | 0 | outside window |
| [01a0f9a9-7731](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-50-28-01a0f9a9-7731-7573-af68-545011f74f60.jsonl:1) `rgb_audit` | Pre-window native creation; parent [01a0f9a8-c7c7:48](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:48) | none in window | 0 | outside window |
| [01a0f9b0-91e0](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-58-13-01a0f9b0-91e0-73d2-a265-2a7e1a0ea9ca.jsonl:1) `delta_review` | Pre-window native creation; parent [01a0f9a8-c7c7:179](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:179) | none in window | 0 | outside window |
| [01a0fb85-9278](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-30-30-01a0fb85-9278-7a12-8fe5-1631b064c273.jsonl:1) `recovery_source_check` | Pre-window native creation; parent [01a0fb83-d843:84](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:84) | none in window | 0 | outside window |
| [01a0fb85-bed0](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-30-41-01a0fb85-bed0-7aa3-b42b-b86f6c2116c7.jsonl:1) `governance_source_check` | Pre-window native creation; parent [01a0fb83-d843:89](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:89) | none in window | 0 | outside window |
| [01a0fb90-b364](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-42-39-01a0fb90-b364-7290-9946-fe7467d8930e.jsonl:1) `campaign_adoption_review` | Pre-window native creation; parent [01a0fb83-d843:232](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:232) | none in window | 0 | outside window |
| [01a0fc43-423d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T13-57-41-01a0fc43-423d-7603-889c-b888e73fb3d0.jsonl:1) `candidate_conformance` | Pre-window native creation; parent [01a0fc42-8cff:43](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T13-56-55-01a0fc42-8cff-7d31-a291-30e583f1397d.jsonl:43) | none in window | 0 | outside window |
| [01a0fc43-5e6e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T13-57-48-01a0fc43-5e6e-71c0-b2ec-6c9f6433b14b.jsonl:1) `contract_audit` | Pre-window native creation; parent [01a0fc42-8cff:48](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T13-56-55-01a0fc42-8cff-7d31-a291-30e583f1397d.jsonl:48) | none in window | 0 | outside window |
| [01a0fca3-713d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T15-42-44-01a0fca3-713d-7650-9348-65e30f390e54.jsonl:1) `gp_config013_independent_review` | Pre-window native creation; parent [01a0fc9f-0304:195](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T15-37-54-01a0fc9f-0304-78d1-ae2f-0d77f1cfe901.jsonl:195) | none in window | 0 | outside window |
| [01a0fcbf-e88e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-13-50-01a0fcbf-e88e-7080-b348-5ebdd261a49c.jsonl:1) `usb_decision_review` | NEW native; parent [01a0f9a8-c7c7:340](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:340) | Sol6.1/medium ×5 | 932,229 | T |
| [01a0fcc1-eba0](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-16-02-01a0fcc1-eba0-7b82-86e8-9de40269da4d.jsonl:1) `c020_source_specialist` | NEW native; parent [01a0fc9f-0304:674](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T15-37-54-01a0fc9f-0304-78d1-ae2f-0d77f1cfe901.jsonl:674) | Luna/high ×5 | 7,965,192 | T |
| [01a0fccd-f90f](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-29-12-01a0fccd-f90f-7100-91ef-784cc8fa4122.jsonl:1) `c020_candidate_review` | NEW native; parent [01a0fc9f-0304:1057](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T15-37-54-01a0fc9f-0304-78d1-ae2f-0d77f1cfe901.jsonl:1057) | Luna/high ×2 | 1,012,717 | T |
| [01a0fcdb-c791](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T16-44-17-01a0fcdb-c791-75e2-a424-1565d016a8e5.jsonl:1) `c020_final_review` | NEW native; parent [01a0fc9f-0304:1588](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T15-37-54-01a0fc9f-0304-78d1-ae2f-0d77f1cfe901.jsonl:1588) | Luna/high ×3 | 2,263,924 | T |
| [01a0fcff-026e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-22-45-01a0fcff-026e-7bf3-b8e7-9b91dfd26624.jsonl:1) `usb_source_1701` | NEW native; parent [01a0fb83-d843:472](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:472) | Sol6.1/high ×2 | 595,968 | T |
| [01a0fcff-a0c9](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-23-26-01a0fcff-a0c9-7680-aeaa-18c0a66f78ca.jsonl:1) `usb_governance_1701` | NEW native; parent [01a0fb83-d843:502](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:502) | Sol6.1/high ×2 | 663,366 | T |
| [01a0fd03-45c7](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-27-25-01a0fd03-45c7-7e33-8021-9cd8b6eb8524.jsonl:1) `usb_adoption_review_1701` | NEW native; parent [01a0fb83-d843:561](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:561) | Sol6.1/high ×3 | 1,114,159 | J |
| [01a0fd0e-2288](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-39-17-01a0fd0e-2288-7663-84b3-e237fcc95dd2.jsonl:1) `kbd_source` | NEW native; parent [01a0fd0c-fc95:58](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-38-01-01a0fd0c-fc95-7c73-a4f2-f9a46bb3cb35.jsonl:58) | Astra/medium ×2 | 1,047,345 | T |
| [01a0fd0f-44e4](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-40-31-01a0fd0f-44e4-7880-aa04-38687ebd55f7.jsonl:1) `kbd_host` | NEW native; parent [01a0fd0c-fc95:94](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-38-01-01a0fd0c-fc95-7c73-a4f2-f9a46bb3cb35.jsonl:94) | Astra/medium ×2 | 1,096,258 | T |
| [01a0fd16-914d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-48-29-01a0fd16-914d-7af3-8898-58d1a8fb2d93.jsonl:1) `kbd_review` | NEW native; parent [01a0fd0c-fc95:359](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-38-01-01a0fd0c-fc95-7c73-a4f2-f9a46bb3cb35.jsonl:359) | Astra/medium ×4 | 1,114,092 | T |
| [01a0fd29-7f66](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-09-10-01a0fd29-7f66-70f0-a4ba-7c6db3e5520c.jsonl:1) `fingerprint_source_kbd` | NEW native; parent [01a0fb83-d843:751](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:751) | Sol6.1/high ×3 | 714,983 | T |
| [01a0fd2b-9d4c](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-11-29-01a0fd2b-9d4c-74e1-bb75-3f8b311eebb2.jsonl:1) `kbd_fingerprint_review` | NEW native; parent [01a0fb83-d843:785](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:785) | Sol6.1/high ×4 | 1,508,891 | T |
| [01a0fd3b-d48e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-29-11-01a0fd3b-d48e-7732-9663-fdf51ad40006.jsonl:1) `kbd_recovery_preflight` | NEW native; parent [01a0fd0c-fc95:688](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-38-01-01a0fd0c-fc95-7c73-a4f2-f9a46bb3cb35.jsonl:688) | Astra/medium ×3 | 608,306 | M |
| [01a0fd43-7ded](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-37-33-01a0fd43-7ded-73b3-8f44-12154a9c2c8e.jsonl:1) `kbd_handoff_review` | NEW native; parent [01a0fd0c-fc95:825](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T17-38-01-01a0fd0c-fc95-7c73-a4f2-f9a46bb3cb35.jsonl:825) | Astra/medium ×3 | 745,741 | M |
| [01a0fd4f-331b](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-50-21-01a0fd4f-331b-7ab1-adfe-7738a8d0a4bb.jsonl:1) `kbd040_source` | NEW native; parent [01a0fd4e-004d:52](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-49-03-01a0fd4e-004d-7130-91db-41c2e1d84ae0.jsonl:52) | Astra/medium ×2 | 1,007,062 | T |
| [01a0fd51-6d0c](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-52-47-01a0fd51-6d0c-7973-aa4c-2edf8e729a79.jsonl:1) `val040_authority` | NEW native; parent [01a0fd4e-004d:127](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-49-03-01a0fd4e-004d-7130-91db-41c2e1d84ae0.jsonl:127) | Astra/medium ×2 | 396,776 | J |
| [01a0fd55-1032](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-56-45-01a0fd55-1032-7a93-8112-997885c6b907.jsonl:1) `val040_stop_review` | NEW native; parent [01a0fd4e-004d:227](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-49-03-01a0fd4e-004d-7130-91db-41c2e1d84ae0.jsonl:227) | Astra/medium ×2 | 753,058 | M |
| [01a0fe99-40ef](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T00-50-51-01a0fe99-40ef-72f3-a097-6a5a81c9e2fa.jsonl:1) `val040_scope_source` | NEW native; parent [01a0fb83-d843:998](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:998) | Sol6.1/high ×4 | 895,154 | J |
| [01a0fea1-5296](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T00-59-40-01a0fea1-5296-7332-8888-2f702cc50819.jsonl:1) `val040_amendment_review` | NEW native; parent [01a0fb83-d843:1123](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:1123) | Sol6.1/high ×5 | 916,437 | T |
| [01a0feba-ce1f](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T01-27-30-01a0feba-ce1f-7db2-a19a-1eb6322484f6.jsonl:1) `val037_predecessor_source` | NEW native; parent [01a0fb83-d843:1352](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:1352) | Sol6.1/high ×3 | 1,518,495 | T |
| [01a0febe-2be0](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T01-31-11-01a0febe-2be0-7ab2-bbb0-df98f4ad7d03.jsonl:1) `val037_curator_review` | NEW native; parent [01a0fb83-d843:1440](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:1440) | Sol6.1/high ×3 | 2,673,493 | J |
| [01a0feeb-0dcc](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-20-12-01a0feeb-0dcc-7510-95ca-76dbfd422723.jsonl:1) `c020_source` | NEW native; parent [01a0feea-53d7:45](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:45) | Astra/medium ×2 | 2,156,156 | T |
| [01a0fef1-a5aa](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-27-24-01a0fef1-a5aa-7c33-8a1b-aa32b20f8a1a.jsonl:1) `c020_handoff_review` | NEW native; parent [01a0feea-53d7:251](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:251) | Astra/medium ×2 | 1,323,251 | M |
| [01a0fefc-3c4f](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-58-01a0fefc-3c4f-7650-8129-66ebe9bf6c34.jsonl:1) `source_audit` | NEW native; parent [01a0fefb-64e0:45](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:45) | Astra/medium ×3 | 1,718,555 | T |
| [01a0fefc-9349](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-39-20-01a0fefc-9349-72c0-812b-e5a00085f1a1.jsonl:1) `validation_audit` | NEW native; parent [01a0fefb-64e0:68](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:68) | Astra/medium ×3 | 1,621,751 | T |
| [01a0feff-7b55](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-42-31-01a0feff-7b55-7c82-a837-ed12845e2d17.jsonl:1) `blocker_review` | NEW native; parent [01a0fefb-64e0:222](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:222) | Astra/medium ×3 | 1,141,140 | M |
| [01a0ff07-d9bc](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-51-39-01a0ff07-d9bc-7682-b7e2-b789f4663f46.jsonl:1) `val037_guard_source` | NEW native; parent [01a0fb83-d843:1672](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:1672) | Sol6.1/high ×4 | 1,431,003 | T |
| [01a0ff0b-3c6e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-55-21-01a0ff0b-3c6e-7b82-a9c7-46da33af671e.jsonl:1) `val037_guard_review` | NEW native; parent [01a0fb83-d843:1734](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:1734) | Sol6.1/high ×5 | 4,999,408 | T |
| [01a0ff1e-47ea](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T03-16-09-01a0ff1e-47ea-7d00-981d-5b61ffc51434.jsonl:1) `resume_source` | NEW native; parent [01a0fefb-64e0:478](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:478) | Astra/medium ×4 | 3,239,115 | T |
| [01a0ff1f-1e85](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T03-17-04-01a0ff1f-1e85-7121-87a7-e1a4f651dc99.jsonl:1) `host_plan` | NEW native; parent [01a0fefb-64e0:499](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:499) | Astra/medium ×4 | 3,170,853 | T |
| [01a0ff22-defa](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T03-21-10-01a0ff22-defa-70e0-b531-e5e3ca57df7f.jsonl:1) `consumer_overlays` | NEW native; parent [01a0fefb-64e0:637](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:637) | Astra/medium ×4 | 2,505,192 | T |
| [01a0ff2d-1639](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T03-32-20-01a0ff2d-1639-7743-ac09-4a288e6d239e.jsonl:1) `implementation_review` | NEW native; parent [01a0fefb-64e0:825](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:825) | Astra/medium ×4 | 3,097,210 | T |
| [01a10111-a297](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T12-21-35-01a10111-a297-74c3-b2b1-39a27ab4fbd0.jsonl:1) `runner_arg_source` | NEW native; parent [01a0fb83-d843:2099](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:2099) | Sol6.1/high ×1 | 1,316,434 | T |
| [01a10111-e5dd](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T12-21-52-01a10111-e5dd-7723-9e67-0b7a4b5c5fed.jsonl:1) `runner_arg_review` | NEW native; parent [01a0fb83-d843:2105](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:2105) | Sol6.1/high ×1 | 2,682,559 | T |
| [01a10123-717d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T12-41-02-01a10123-717d-7be0-8f78-7a5dd6a1eae9.jsonl:1) `activation_audit_v3` | NEW native; parent [01a0fefb-64e0:1120](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:1120) | Astra/medium ×5 | 4,695,424 | T |
| [01a10123-fc20](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T12-41-37-01a10123-fc20-7333-9cc4-dcd98717e7cf.jsonl:1) `runner_policy_v3` | NEW native; parent [01a0fefb-64e0:1142](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:1142) | Astra/medium ×4 | 5,958,185 | J |
| [01a10124-3212](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T12-41-51-01a10124-3212-7e60-96cc-f77ad9a68fa0.jsonl:1) `accepted_transition_v3` | NEW native; parent [01a0fefb-64e0:1148](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:1148) | Astra/medium ×9 | 12,935,558 | T |
| [01a1012a-896d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T12-48-47-01a1012a-896d-7ef2-a638-0873033d275c.jsonl:1) `final_review_v3` | NEW native; parent [01a0fefb-64e0:1398](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:1398) | Astra/medium ×18 | 9,666,016 | T |
| [01a10196-3c38](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T14-46-25-01a10196-3c38-7a30-a7ee-22639da03636.jsonl:1) `c020_build_source` | NEW native; parent [01a0feea-53d7:527](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:527) | Sol6/high ×17 | 53,287,055 | T |
| [01a10198-b09d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T14-49-06-01a10198-b09d-74e3-b6c2-17886161074f.jsonl:1) `c020_firmware_review` | NEW native; parent [01a0feea-53d7:594](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:594) | Sol6/high ×1 | 6,360,748 | T |
| [01a101b3-bc38](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T15-18-38-01a101b3-bc38-7522-8c5e-1f1c7aa7935c.jsonl:1) `c020_abi_source` | NEW native; parent [01a0f9a8-c7c7:684](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:684) | Sol6.1/medium ×2 | 676,115 | T |
| [01a101bd-0b1d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T15-28-48-01a101bd-0b1d-7ea3-aa86-733402f51385.jsonl:1) `c020_packet_review` | NEW native; parent [01a0f9a8-c7c7:795](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:795) | Sol6.1/medium ×2 | 525,082 | T |
| [01a101c7-c0db](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T15-40-30-01a101c7-c0db-7363-9e1c-28b2f74be168.jsonl:1) `c020_abi_curation_source` | NEW native; parent [01a0fb83-d843:2379](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:2379) | Sol6.1/high ×1 | 1,395,666 | T |
| [01a101c8-0212](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T15-40-47-01a101c8-0212-7fa3-959b-38da5ca98d90.jsonl:1) `c020_abi_adoption_review` | NEW native; parent [01a0fb83-d843:2385](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:2385) | Sol6.1/high ×2 | 2,538,592 | J |
| [01a101d7-2ad3](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T15-57-20-01a101d7-2ad3-7000-9d28-9ea380b2424d.jsonl:1) `c020_format_review` | NEW native; parent [01a0f9a8-c7c7:923](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:923) | Sol6.1/low ×1 | 423,604 | M |
| [01a101e3-46dd](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T16-10-34-01a101e3-46dd-7c62-a266-cc90e4ff5aac.jsonl:1) `c020_abi_final_review_1256` | NEW native; parent [01a0fb83-d843:2567](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:2567) | Sol6.1/low ×1 | 2,085,632 | T |
| [01a101f1-f2c3](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T16-26-36-01a101f1-f2c3-7cd3-84a7-8ee06af8bf08.jsonl:1) `abi_source_build` | NEW native; parent [01a0feea-53d7:1121](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:1121) | Sol6/high ×9 | 24,244,773 | T |
| [01a101f2-2821](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T16-26-49-01a101f2-2821-7b41-9746-da1963691ded.jsonl:1) `abi_independent_review` | NEW native; parent [01a0feea-53d7:1127](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:1127) | Sol6/high ×6 | 27,874,817 | T |
| [01a101f3-6aa1](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T16-28-12-01a101f3-6aa1-74c1-ac68-4050c7c3f7fd.jsonl:1) `abi_host_implementation` | NEW native; parent [01a0feea-53d7:1163](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:1163) | Sol6/high ×1 | 3,774,283 | T |
| [01a1020f-676d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T16-58-46-01a1020f-676d-7471-9147-65fb187608d1.jsonl:1) `val043_source_audit` | NEW native; parent [01a0fefb-64e0:3745](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:3745) | Sol6.1/high ×5 | 10,943,221 | T |
| [01a1020f-a508](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T16-59-02-01a1020f-a508-7513-9c41-cf10b86b9edf.jsonl:1) `val043_validation_plan` | NEW native; parent [01a0fefb-64e0:3752](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:3752) | Sol6.1/high ×3 | 8,743,376 | T |
| [01a1021f-280a](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T17-15-58-01a1021f-280a-7440-a5b7-bc49a48424f6.jsonl:1) `val043_independent_review` | NEW native; parent [01a0fefb-64e0:4052](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:4052) | Sol6.1/high ×1 | 17,833,875 | T |
| [01a1027b-88ab](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T18-56-52-01a1027b-88ab-7162-a5ab-8c274fa663db.jsonl:1) `val043_final_review_recovery` | NEW native; parent [01a0fefb-64e0:5888](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:5888) | Sol6.1/high ×2 | 6,655,690 | T |
| [01a102a1-31d8](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T19-38-00-01a102a1-31d8-7b01-a8b3-142a4bd45bab.jsonl:1) `c020_f_build_source` | NEW native; parent [01a0feea-53d7:1838](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:1838) | Sol6/high ×1 | 3,575,758 | T |
| [01a102a1-5d3f](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T19-38-12-01a102a1-5d3f-7683-bc71-f1a39c6df757.jsonl:1) `c020_f_independent_review` | NEW native; parent [01a0feea-53d7:1843](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:1843) | Sol6/high ×1 | 9,089,325 | T |
| [01a102fb-66f6](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-16-32-01a102fb-66f6-7f01-a7ac-f99a691434e5.jsonl:1) `c020_evidence_review` | NEW native; parent [01a102f9-e845:59](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:59) | Sol6.1/high ×2 | 0 | T |
| [01a102fb-f70d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-17-09-01a102fb-f70d-7241-a9f5-c3290f64f157.jsonl:1) `c020_sol_review` | NEW native; parent [01a102f9-e845:72](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:72) | Sol6.1/high ×1 | 3,955,483 | T |
| [01a10309-54d2](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-31-45-01a10309-54d2-7583-b452-88ca2b5fded1.jsonl:1) `c020_ei_source_scope` | NEW native; parent [01a0fb83-d843:2814](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:2814) | Sol6.1/low ×1 | 683,069 | J |
| [01a10309-9329](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-32-01-01a10309-9329-7572-b492-3540c0550390.jsonl:1) `c020_ei_adoption_review` | NEW native; parent [01a0fb83-d843:2819](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:2819) | Sol6.1/low ×1 | 2,229,301 | J |
| [01a1031a-ba97](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-50-45-01a1031a-ba97-7ac0-94ea-e11a8a42580d.jsonl:1) `val044_source` | NEW native; parent [01a0fefb-64e0:6402](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:6402) | Sol6.1/high ×6 | 15,921,310 | T |
| [01a1031b-38ce](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-51-18-01a1031b-38ce-7b93-991e-857c88663a86.jsonl:1) `val044_validation` | NEW native; parent [01a0fefb-64e0:6408](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:6408) | Sol6.1/high ×9 | 21,082,406 | T |
| [01a1031b-ad09](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-51-47-01a1031b-ad09-73e1-9f1c-d008d762d6bb.jsonl:1) `val044_review` | NEW native; parent [01a0fefb-64e0:6414](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-38-03-01a0fefb-64e0-7b31-a718-b964e62382be.jsonl:6414) | Sol6.1/high ×4 | 43,533,818 | T |
| [01a103f8-308e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T01-52-39-01a103f8-308e-72f1-9c04-eb3ae288b1a3.jsonl:1) `val044_timeout_source` | NEW native; parent [01a0fb83-d843:3083](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:3083) | Sol6.1/low ×1 | 744,766 | T |
| [01a103f8-5d6d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T01-52-50-01a103f8-5d6d-7472-9c6f-d86d4a2e9251.jsonl:1) `val044_timeout_review` | NEW native; parent [01a0fb83-d843:3088](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T10-28-36-01a0fb83-d843-7013-a539-fc2fb0c873c6.jsonl:3088) | Sol6.1/low ×2 | 1,712,659 | T |
| [01a10405-956e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-07-17-01a10405-956e-7c13-90cb-a9d829f976b5.jsonl:1) `val044_probe_research` | NEW native; parent [01a0f9a8-c7c7:1027](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1027) | Sol6.1/low ×1 | 572,133 | T |
| [01a10405-c033](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-07-28-01a10405-c033-7be1-80b0-680436446825.jsonl:1) `val044_process_research` | NEW native; parent [01a0f9a8-c7c7:1035](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1035) | Sol6.1/low ×1 | 1,293,436 | J |
| [01a10409-f327](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-12-03-01a10409-f327-76c1-b838-04b280dfb298.jsonl:1) `val044_research_review` | NEW native; parent [01a0f9a8-c7c7:1113](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1113) | Sol6.1/low ×1 | 282,816 | T |
| [01a10412-d6ba](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-21-45-01a10412-d6ba-7a13-8b7c-dc08eb6e6d91.jsonl:1) `val044_recovery_scope` | NEW native; parent [01a10410-ff42:86](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-19-45-01a10410-ff42-7091-a4d7-74fd6ff3310a.jsonl:86) | Sol6.1/high ×4 | 3,087,692 | J |
| [01a10414-6be9](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-23-29-01a10414-6be9-71f2-a693-8dc1df3b5073.jsonl:1) `val044_fresh_review` | NEW native; parent [01a10410-ff42:156](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-19-45-01a10410-ff42-7091-a4d7-74fd6ff3310a.jsonl:156) | Sol6.1/high ×12 | 14,642,992 | T |
| [01a10666-edd5](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-12-51-01a10666-edd5-76f1-90c9-b10952e4f310.jsonl:1) `val044_source_specialist` | NEW native; parent [01a10665-7c42:56](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:56) | Sol6.1/high ×1 | 1,112,919 | T |
| [01a10668-8336](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-14-35-01a10668-8336-7671-9f3a-633c12a18d89.jsonl:1) `val044_independent_review` | NEW native; parent [01a10665-7c42:109](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:109) | Sol6.1/high ×1 | 1,036,555 | T |
| [01a10678-cf53](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-32-23-01a10678-cf53-7de2-a9f1-bf0c8abf1c74.jsonl:1) `usb_name_source` | NEW native; parent [01a10677-20a8:68](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-30-32-01a10677-20a8-77b1-8970-2c7d9d7bdcc1.jsonl:68) | Sol6.1/high ×2 | 1,279,944 | T |
| [01a10681-451e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-41-37-01a10681-451e-79f1-a8ed-fb292dcb8ee5.jsonl:1) `val044_deadline_timing` | NEW native; parent [01a0f9a8-c7c7:1217](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1217) | Sol6.1/low ×1 | 406,905 | M |
| [01a10682-f8b3](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-43-29-01a10682-f8b3-7922-8d34-ac380231a889.jsonl:1) `usb_name_review` | NEW native; parent [01a10677-20a8:230](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-30-32-01a10677-20a8-77b1-8970-2c7d9d7bdcc1.jsonl:230) | Sol6.1/high ×4 | 2,902,899 | T |
| [01a10685-b138](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-46-27-01a10685-b138-7513-8aee-b997cc3b3e49.jsonl:1) `val044_deadline_review` | NEW native; parent [01a0f9a8-c7c7:1298](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1298) | Sol6.1/low ×1 | 422,773 | T |
| [01a1068a-7720](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-51-40-01a1068a-7720-7750-8e0c-1bb79af7b523.jsonl:1) `val044_diagnostic_authority_review` | NEW native; parent [01a10665-7c42:265](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:265) | Sol6.1/high ×1 | 1,210,050 | J |
| [01a1069f-0723](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T14-14-07-01a1069f-0723-76e3-bc9c-bb7c1a19ffca.jsonl:1) `val044_snapshot_reconciliation_review` | NEW native; parent [01a10665-7c42:382](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:382) | Sol6.1/high ×1 | 1,422,550 | M |
| [01a106e4-773e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T15-29-58-01a106e4-773e-7972-9d44-bae106646b33.jsonl:1) `hep_revision3_review` | NEW native; parent [01a102f9-e845:327](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:327) | Sol6.1/high ×2 | 11,519,372 | T |
| [01a106ff-4a58](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T15-59-16-01a106ff-4a58-7473-b4b8-217485b3e127.jsonl:1) `c020_r3_source` | NEW native; parent [01a0feea-53d7:3056](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:3056) | Sol6.1/high ×2 | 4,581,423 | T |
| [01a106ff-cbdb](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T15-59-49-01a106ff-cbdb-7a81-a2d8-4752f443cc9f.jsonl:1) `c020_r3_review` | NEW native; parent [01a0feea-53d7:3062](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:3062) | Sol6.1/high ×1 | 6,920,853 | T |
| [01a1071d-1d4d](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T16-31-51-01a1071d-1d4d-7433-855e-2f3cd03a8f46.jsonl:1) `r3_policy_scope` | NEW native; parent [01a10410-ff42:1964](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-19-45-01a10410-ff42-7091-a4d7-74fd6ff3310a.jsonl:1964) | Sol6.1/high ×3 | 865,177 | J |
| [01a10737-57e6](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T17-00-29-01a10737-57e6-7120-98ff-1bd98ea32995.jsonl:1) `revision3_fresh_review` | NEW native; parent [01a10410-ff42:2463](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T02-19-45-01a10410-ff42-7091-a4d7-74fd6ff3310a.jsonl:2463) | Sol6.1/high ×4 | 8,811,377 | T |
| [01a10758-df05](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T17-37-07-01a10758-df05-7443-97f3-569571d9e315.jsonl:1) `publication_verifier` | NEW native; parent [01a10757-7fe3:59](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T17-35-37-01a10757-7fe3-76b1-9bde-a3b52bc9088b.jsonl:59) | Sol6.1/high ×1 | 1,846,658 | M |
| [01a10764-5175](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T17-49-37-01a10764-5175-7e32-b266-fd0df7eb4d00.jsonl:1) `config014_source` | NEW native; parent [01a0feea-53d7:3602](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:3602) | Sol6.1/high ×10 | 20,895,607 | T |
| [01a10766-6caa](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T17-51-55-01a10766-6caa-7e01-b426-b5c7e783a62a.jsonl:1) `config014_review` | NEW native; parent [01a0feea-53d7:3635](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:3635) | Sol6.1/high ×1 | 23,547,241 | T |
| [01a10774-0fd0](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T18-06-49-01a10774-0fd0-7d22-b222-3b7a0e6046d2.jsonl:1) `config014_host` | NEW native; parent [01a0feea-53d7:3918](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:3918) | Sol6.1/high ×1 | 2,386,110 | T |
| [01a1078f-9c40](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T18-36-54-01a1078f-9c40-7541-81b0-479f587c1aa2.jsonl:1) `h1_source_activation` | NEW native; parent [01a0fd4e-004d:530](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-49-03-01a0fd4e-004d-7130-91db-41c2e1d84ae0.jsonl:530) | Sol6.1/high ×8 | 9,875,051 | T |
| [01a107a3-2687](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T18-58-15-01a107a3-2687-7dc1-a69e-9d601bb7c0b5.jsonl:1) `val040_tier_review` | NEW native; parent [01a0fd4e-004d:736](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-49-03-01a0fd4e-004d-7130-91db-41c2e1d84ae0.jsonl:736) | Sol6.1/high ×13 | 18,878,094 | T |
| [01a107a9-5027](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T19-04-59-01a107a9-5027-7661-9dd0-3c9312288ff3.jsonl:1) `batch029_review` | NEW native; parent [01a0feea-53d7:4751](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:4751) | Sol6.1/high ×2 | 4,826,741 | T |
| [01a107b7-a4e7](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T19-20-38-01a107b7-a4e7-77d1-b8ff-599a33e3b700.jsonl:1) `val034_historical` | NEW native; parent [01a0feea-53d7:5031](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:5031) | Sol6.1/high ×27 | 65,617,650 | T |
| [01a107c0-9ebf](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T19-30-26-01a107c0-9ebf-7193-a2c0-b516eaa6bf33.jsonl:1) `val034_review` | NEW native; parent [01a0feea-53d7:5234](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:5234) | Sol6.1/high ×47 | 119,204,004 | T |
| [01a10870-a749](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T22-42-43-01a10870-a749-7fd1-8d2c-90de3718186a.jsonl:1) `val041_source_scope` | NEW native; parent [01a10665-7c42:655](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:655) | Sol6.1/high ×1 | 1,772,073 | J |
| [01a10870-ee88](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T22-43-01-01a10870-ee88-74c2-a85c-2008b6ea0c35.jsonl:1) `val041_adoption_review` | NEW native; parent [01a10665-7c42:660](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:660) | Sol6.1/high ×1 | 6,335,112 | J |
| [01a10892-6c6b](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T23-19-36-01a10892-6c6b-7481-b488-6636c0d188ba.jsonl:1) `val041_independent_review` | NEW native; parent [01a0fd4e-004d:2386](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T18-49-03-01a0fd4e-004d-7130-91db-41c2e1d84ae0.jsonl:2386) | Sol6.1/high ×10 | 17,206,376 | T |
| [01a108cd-2ebf](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/05/rollout-2026-10-05T00-23-47-01a108cd-2ebf-7803-a8a8-4a7199eacf07.jsonl:1) `kbd_release_research` | NEW native; parent [01a0f9a8-c7c7:1771](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1771) | Sol6.1/low ×1 | 562,035 | T |
| [01a108cd-6b50](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/05/rollout-2026-10-05T00-24-02-01a108cd-6b50-79e2-94f0-c6bdf1827aae.jsonl:1) `usb_name_release_research` | NEW native; parent [01a0f9a8-c7c7:1776](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1776) | Sol6.1/low ×3 | 1,881,232 | T |
| [01a108d8-3a17](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/05/rollout-2026-10-05T00-35-50-01a108d8-3a17-7aa2-b21b-2ece6f699e58.jsonl:1) `post_characterization_packet_review` | NEW native; parent [01a0f9a8-c7c7:1962](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/02/rollout-2026-10-02T01-49-43-01a0f9a8-c7c7-71b0-9d83-794d244f2fe2.jsonl:1962) | Sol6.1/high ×1 | 1,807,189 | T |
| [01a108e9-f2c0](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/05/rollout-2026-10-05T00-55-12-01a108e9-f2c0-7972-9dff-933795f9f807.jsonl:1) `portfolio0028_source_authority` | NEW native; parent [01a10665-7c42:1105](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:1105) | Sol6.1/high ×1 | 1,192,017 | J |
| [01a108f4-05f9](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/05/rollout-2026-10-05T01-06-12-01a108f4-05f9-7130-88c1-8c97360eeda8.jsonl:1) `portfolio0028_adoption_review` | NEW native; parent [01a10665-7c42:1304](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/04/rollout-2026-10-04T13-11-16-01a10665-7c42-7000-ae90-f6b46e44954d.jsonl:1304) | Sol6.1/high ×1 | 1,837,730 | J |
| [01a10920-a0e7](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/05/rollout-2026-10-05T01-54-55-01a10920-a0e7-71d2-bb37-23d3399c5678.jsonl:1) `c014_hep_review` | NEW native; parent [01a102f9-e845:977](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:977) | Sol6.1/high ×2 | 7,267,129 | T |
| [01a1164e-1c7c](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/07/rollout-2026-10-07T15-19-40-01a1164e-1c7c-7612-8008-f7d8b59eaad7.jsonl:1) `c017_hep_review` | NEW native; parent [01a102f9-e845:1596](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:1596) | Sol6.1/high ×1 | 6,994,526 | T |
| [01a11891-3142](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T01-52-10-01a11891-3142-7fb3-b694-cfa772747b92.jsonl:1) `c021_display_proof` | NEW native; parent [01a102f9-e845:2035](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:2035) | Sol6.1/high ×3 | 2,161,652 | T |
| [01a11894-281e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T01-55-25-01a11894-281e-71b1-8de4-a3d177bc12ba.jsonl:1) `c021_hep_review` | NEW native; parent [01a102f9-e845:2176](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:2176) | Sol6.1/high ×3 | 5,888,435 | T |
| [01a118a5-4afb](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T02-14-08-01a118a5-4afb-7ad2-a52c-1280793c2311.jsonl:1) `c021_integration_source` | NEW native; parent [01a0feea-53d7:17613](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:17613) | Sol6.1/high ×13 | 33,292,630 | T |
| [01a118a9-327e](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T02-18-24-01a118a9-327e-7f73-bf69-977545c50ecb.jsonl:1) `c021_integration_review` | NEW native; parent [01a0feea-53d7:17715](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:17715) | Sol6.1/high ×15 | 45,915,285 | T |
| [01a11b5b-95a6](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T14-52-29-01a11b5b-95a6-7030-8e7e-4a2590a2d8d6.jsonl:1) `c022_host_implementation` | NEW native; parent [01a0feea-53d7:19048](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:19048) | Sol6.1/high ×7 | 24,407,154 | T |
| [01a11c5f-a004](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T19-36-31-01a11c5f-a004-7cb2-a315-4fc66746ea29.jsonl:1) `c022_source_applicability` | NEW native; parent [01a102f9-e845:2568](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:2568) | Sol6.1/high ×2 | 1,383,092 | T |
| [01a11c60-cc25](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T19-37-48-01a11c60-cc25-79a2-9601-da29456b613a.jsonl:1) `c022_hep_review` | NEW native; parent [01a102f9-e845:2623](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:2623) | Sol6.1/high ×3 | 4,963,962 | T |
| [01a11c70-1628](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T19-54-30-01a11c70-1628-7c62-b49f-7431633551a6.jsonl:1) `c022_source_specialist` | NEW native; parent [01a0feea-53d7:22437](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:22437) | Luna/medium ×2 | 491,245 | T |
| [01a11c73-7b18](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T19-58-12-01a11c73-7b18-75e2-9f03-d2f8b883d324.jsonl:1) `c022_independent_review` | NEW native; parent [01a0feea-53d7:22771](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:22771) | Luna/medium ×2 | 1,617,511 | T |
| [01a11c79-c634](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T20-05-05-01a11c79-c634-7661-8bf5-95300cfdf842.jsonl:1) `c023_source_applicability` | NEW native; parent [01a0feea-53d7:23239](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:23239) | Luna/medium ×6 | 6,078,532 | T |
| [01a11c7f-8be2](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T20-11-23-01a11c7f-8be2-76c0-9783-44dda7e07552.jsonl:1) `c023_host_proof` | NEW native; parent [01a0feea-53d7:23570](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:23570) | Luna/medium ×3 | 12,143,141 | T |
| [01a11c85-e929](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/08/rollout-2026-10-08T20-18-20-01a11c85-e929-7d63-b388-588b9dcdc069.jsonl:1) `c023_independent_review` | NEW native; parent [01a0feea-53d7:23840](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:23840) | Luna/medium ×25 | 48,252,450 | T |
| [01a11da4-5ae9](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/09/rollout-2026-10-09T01-31-12-01a11da4-5ae9-7bc3-8fbb-52482ab5e1e3.jsonl:1) `c023_source_applicability` | NEW native; parent [01a102f9-e845:3103](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:3103) | Sol6.1/high ×2 | 3,454,999 | T |
| [01a11da7-69e6](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/09/rollout-2026-10-09T01-34-33-01a11da7-69e6-7840-bd98-865c54aa02fe.jsonl:1) `c023_hep_review` | NEW native; parent [01a102f9-e845:3209](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:3209) | Sol6.1/high ×2 | 8,250,882 | T |
| [01a11fd1-12c5](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/09/rollout-2026-10-09T11-39-18-01a11fd1-12c5-7f82-affb-f5643cc439af.jsonl:1) `val045_exact_review` | NEW native; parent [01a0feea-53d7:35573](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:35573) | Luna/medium ×2 | 341,194 | T |
| [01a11fdf-97c8](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/09/rollout-2026-10-09T11-55-09-01a11fdf-97c8-7d40-a29f-dc338209ad2e.jsonl:1) `val045_amended_review` | NEW native; parent [01a0feea-53d7:36005](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:36005) | Luna/medium ×5 | 9,416,047 | T |
| [01a120e7-86ac](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/09/rollout-2026-10-09T16-43-26-01a120e7-86ac-7ee2-bdc8-cde9cedb362e.jsonl:1) `c024_fixture_review` | NEW native; parent [01a0feea-53d7:39089](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T02-19-25-01a0feea-53d7-76e2-82ec-2328e4c18150.jsonl:39089) | Luna/medium ×4 | 2,097,393 | T |
| [01a12572-28eb](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/10/rollout-2026-10-10T13-53-21-01a12572-28eb-7220-b951-ed78a8a890bd.jsonl:1) `c024_source_applicability` | NEW native; parent [01a102f9-e845:3844](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:3844) | Sol6.1/high ×2 | 1,706,307 | T |
| [01a12572-5758](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/10/rollout-2026-10-10T13-53-32-01a12572-5758-7e71-b57f-d23bc55688a4.jsonl:1) `c024_hep_review` | NEW native; parent [01a102f9-e845:3849](/Users/rasmus.pekkarinen/.codex/sessions/2026/10/03/rollout-2026-10-03T21-14-54-01a102f9-e845-77d0-bead-ce79a5d21124.jsonl:3849) | Sol6.1/high ×3 | 9,453,437 | T |

### A3. Reachable-session telemetry, not an invoice

Global deduplication by response ID across reachable session files yields
**19,300 response records** inside the daemon's time window: 2,495,758,131 input
(including 2,436,442,368 cached input), 8,220,390 output, total **2,503,978,521**.
A reused peer's work inside that window is not automatically caused by this
daemon; this is a reachable-session observation envelope, not clean task-cost
attribution. Pre-window activity is excluded here. Root-only figures earlier
are the clearer measure of the daemon itself.

| Actual model family in reachable window | Context records | Input + output tokens |
| --- | ---: | ---: |
| Astra | 387 | 520,292,777 |
| Sol6.1 | 441 | 1,379,579,123 |
| Luna | 115 | 455,822,953 |
| Sol6 | 38 | 148,048,793 |
| Unmapped model | — | 234,875 |

Unmapped usage includes 230,469 input and 4,406 output tokens. No effort-level
credit rates, invoices, or counterfactual savings are available. Cached input,
reasoning output and cumulative thread counters must not be added again.
Many contexts used high reasoning even after routing left Astra; the next daemon
must de-escalate effort as well as model family. High reuse/cache ratios also do
not make stale context safe.
