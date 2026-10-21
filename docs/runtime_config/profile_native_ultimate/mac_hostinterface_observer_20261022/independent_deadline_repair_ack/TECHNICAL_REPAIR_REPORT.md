# Focused deadline repair — technical result

**The corrected frozen child passes the focused source and offline regression review. Final child prose/owner-packet binding remains pending.** Root identified the concrete Tier2 defect after the original review seal. That original PASS missed the cutoff issue and remains unchanged as historical evidence; it must not be treated as approval to use the old reader.

## Confirmed parent defect

The parent completion block captures receipt time before fallible journal flushes, passes that stale time to engine.completion/next, then submits the next read without checking current time. Its timer runs on the same serial queue and cannot interrupt the callback. Slow journal work can therefore queue a fresh read after the five-second cutoff.

The independent exact-parent-source mock witness compiled successfully under ASan/UBSan. A receipt at4.9s followed by journal advancement to6s caused actual parent code to queue its second read at6s against deadline5s, with no abort. The required cutoff test fails at runtime with exit17. Only registry/host/clock/fsync mocks changed; the included source was byte-exact. `confirmed-parent-finding.json` and `parent-witness-commands.json` preserve this independent witness, and `parent_witness/` preserves source/test/binary/journal.

## Exact repair

Child `/private/tmp/glyph-native-Mac-hostinterface-observer-deadline-repair-20261022` technical hold5661e6a742b456676824fff8ebe31181f4365b8757ab7251884694fee4778c59 contains sourcef0e246b6b6d15a6cab0b5db0eba86cf1907aa35795038e5190957ebee876e2f2 and binary108e64e5eab524ad85d184eb7ee75d9e6075b44bd3df68598ed79dbf92622c83. All25 held input entries were independently rehashed. Core/parser/original mock source remain byte-identical to the parent.

The only source change is six lines in State::read after buffer preparation/NSError initialization and immediately before enqueue. It reads the current monotonic clock and requires it strictly precede engine.deadline; clock failure is treated as refusal. No logging or other fallible work intervenes before the SDK call. A reserved but not-yet-queued attempt settles through submit_failed and queued settled cleanup, returning without abort or retry. Source receipt timestamps, decoder/oracles and operation bounds remain unchanged. The existing submissions counter includes reserved attempts; a stopped guard can show two reservations but only one actual SDK enqueue. This is not evidence of two actual transfers or an SDK enqueue rejection.

## Independent affected execution

A separate witness harness reused the independent parent negative's exact actual-source inclusion and replaced only its source input with the byte-exact child. Four ASan/UBSan cases passed:

- Completion receipt4.9s, journal advances6s: one actual enqueue, zero late enqueue, zero abort, one accepted report, unsuccessful stopped result and cleanup once.
- Journal reaches exactly5s: the same refusal; comparison is strict, so equality does not submit.
- Clock fails at the immediate pre-enqueue guard: the same safe refusal and no spurious abort.
- Timely processing remains4.9s: three actual enqueues/reports, successful engine result, no abort and cleanup once.

Completion/raw/decoded receipt timestamps remain4.9s in all generated rows. The original parent witness remains a runtime-negative control. The full corrected host program independently rebuilds byte-identically to108e64...; no live entry point was invoked. Existing source safety/callback/descriptor proof is carried with only this focused correction, and the author's affected regression evidence was inspected. No broader unaffected suite was repeated.

## Limits

The guard establishes a current-clock submission decision immediately before the SDK call. It does not create an OS scheduling or kernel-acceptance timing guarantee. An observation's timestamp remains callback receipt time; raw/decoded custody and process success still require complete flush/close. Late journal completion does not rewrite receipt time. Cancellation still allows at most one asynchronous abort, one-second grace, full retained uncertain State, internal8s process deadline and proposed external10s caller deadline.

No registry/USB/serial action, actual inspect/capture/init/descriptor/pipe/read/cancel, firmware build/change, Git/worktree/publication/install/network action occurred. All actual-source tests replace effectful registry and host APIs. Old source/binary/report/PINS and packet bytes remain immutable. Current device stays STOP in Configurator. This technical result authorizes nothing; final source/binary/operator/corrected owner MD/JSON/custody binding and new owner approval remain required. Firmware F/artifacts/resource/oracles and all physical acceptance non-claims remain unchanged.
