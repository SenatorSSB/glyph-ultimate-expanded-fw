# GP-NATIVE-002 bounded GameCube liveness repair

Summary:
- Repair exact8b2c75e3, retaining48989519 ancestry and original334f lineage.
  No-poll pending selection gains a safe core0 service opportunity.
- Independent source review PASS after closing P1 service-gate bypass; target
  header typo fixed in a separate exact commit and reviewed. Failures retained.

Files changed:
- Local pinned Joybus source+provenance, dependency selection, GameCube backend
  and application-loop admission gate. Existing ProfileStore/menu/schema/
  persistence transaction/reboot bodies stay unchanged.
- Source-faithful old/new GC checker and narrow existing selector fixture bridge.

Verification:
- Literal failed source demonstrably exceeds finite no-poll bound. Repaired
  source passes both enum ABIs under ASan/UBSan with actual mailbox, GC bodies,
  actual application gate, actual core0 service/Persistence and success/refusal/
  generation-conflict/uncertain-save outcomes. Tests include partial byte,
  admission races, request beforewait/afterservice/activecommand/afterreport,
  queued TX, no-poll FAST input progress, all command responses and exact report.
- Existing selector metadata0/1/11/20/64, names/ranks/IDs/backends/legacy/context/
  scrolling and actual Persistence A→B→A all4 routes PASS both ABIs. Existing
  native full suites PASS both ABIs; Persistence37, selection recovery and
  strict store PASS. Production exact ELF/259 recipes PASS. ABI layout PASS.
- Canonical pio executable unavailable on PATH; established
  ./scripts/build-glyph-mk6-quiet.sh (PlatformIO6.2.0) PASS exact committed F.
  Exact ELF/BIN/UF2 correspondence+content-addressed readback PASS.
- SDK pioasm regenerated24 instruction words match; sample cycles and all other
  RX/TX wire instructions/relocations checked. Fresh linked proof PASS all
  unchanged resource ceilings; whole core0 has zero conservative margin.
- Source-free handoff navigation/framework/sequence PASS. Agent-surface actual
  FAIL at C024 authentication; unchanged cleanexact3a base fails at the identical
  diagnostic, preserved as FRAMEWORK_VALIDATION_DEBT. Two initial wrong checker
  filenames did not execute tests; corrected canonical commands/results retained.
- Full aggregate not run; no aggregate PASS claimed. Historical original
  candidate framework/menu/snapshot debt remains preserved in its packet.
  Initial compile include failure and interim test opcode expectation failure
  retained separately, not treated as PASS.

Behavior changes:
- Pending-only qualified idle admission pauses receiver, returns to outer core0
  loop and permits existing checked selection service. ALL GC attempts require
  admission, including requests posted before service or during prior TX.
- No-request idle timeout returns to existing FAST scan with receiver running;
  partial command remains protected. No absent byte is dispatched as a command.
- Actual split-POLL tail ERROR uses upstream's existing130us drain/PIO reset
  boundary; no controller/watchdog reset is introduced for protocol errors.
- Ordinary report fields/bytes/poll-tail/send logic and PIO sample phase remain
  source/fixture equivalent. Physical electrical timing remains unmeasured.

Semantic changes:
- No native/game/evaluator/remap/SOCD/schema/storage or selection policy change.

Backend behavior claims:
- Source-backed bounded progress after a pending request with absent traffic;
  finite active commands must complete before admission. Malformed partial
  first byte that never completes remains protected, without a new timeout.
- Menu/core1 produces only; core0 alone owns checked persistence. No body write,
  second writer, unconditional reboot or fake traffic. Target response remains
  a required exact hardware acceptance property, not inferred from host proof.

Historical Stage A stop conditions (superseded by Stage B update below):
- Stage A read-only recovery PASS within API scope; all43 wrappers/metadata
  exact and Config retains SEL01/GameCube. GameCube active identity and raw
  filesystem integrity remain UNKNOWN. No flash/cleanup/restore or merge.

Historical Stage A follow-ups (completed approval and normal rows recorded below):
- Exact Stage B manual-installation and normal-row approval remains pending;
  powered/no-poll row remains separately gated on a verified safe setup. XInput+GC A→B→A, idle progress,
  responsiveness and post-test Config/store preservation remain required.
- Fresh source-free HEP and exact tested-source integration only after PASS.

Delegation:
- Repo SUBAGENT_CONTRACTS explicitly applied; native facility available.
- Bounded Joybus source/safety, independent safe-boundary/test specialist and
  linked-resource specialist; fresh independent source/repaired review.
- Root retained Git, authoritative verification, artifact custody and handoff.
  No new user-owned chat, Planner/Curator invocation or delegated device action.

Stage A details and private custody seals: [recovery summary](recovery_20261023/SUMMARY.md).

Stage B update: [normal hardware results and post-test preservation](hardware_20261023/SUMMARY.md).
Normal GameCube owner-reported PASS; full acceptance INCOMPLETE with no-poll
physical row NOT_TESTED and final XInput output confirmation pending.
