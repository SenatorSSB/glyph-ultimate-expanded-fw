# d596 one-reset read-only adjudication — prepared only

No controller action is authorized for the source-diagnosis agent. This packet
is for a separately authorized human hardware session. Preserve the controller
and existing logs until that session. d596 remains permanently hardware FAIL
regardless of reset outcome; never reuse it for acceptance.

1. Bind failed SHA `d59684b9368be61183881bdfc82adc774ad5f0ba` to UF2
   `1890a459caca3c49af404fb518dfb10b71590af64a83967846a4b3ad1af8975c`
   (976896 bytes). Preserve generation160/incarnation1, all three LIST pages,
   ID22 revision130, prior useful ID1/3/4 profile hashes and Config generation
   3130536755. Use new uniquely named evidence files; retain all historical logs.
2. Perform exactly one controlled ordinary reset/power cycle through the
   established Configurator route. No Clean, factory reset, reflash, filesystem
   deletion, or automatic retry. Stop if normal boot fails.
3. Using the old candidate's compatible tool, one bounded pulse and STATUS;
   then LIST pages0/8/16, one READ each ID1/3/4/22, and GET_CONFIG, stopping on
   the first timeout/discrepancy. Each wait is at most10seconds. Do not request
   READ tracing from old firmware. If using the new receive-journaling tool,
   omit `--trace` for READ because d596 has no READ terminal-stage contract.
4. Compare decoded persistent profiles/IDs/revisions, generation/incarnation,
   exact Config readback and selection to pre-failure evidence. Record reset,
   volatile fault state, transport recovery and persistent-state match as
   separate findings. A reset can run startup reconciliation; report observed
   state rather than assuming it. No pending/armed fault or subsequent mutation
   was reported at the d596 failure.

A restored READ does not identify the blocked physical PC, prove the source
TX defect caused this occurrence, or erase either historical failure. If the
old READ times out again, stop and retain its partial-byte evidence. A failed
adjudication is not permission to continue the fault campaign or flash.
