# Same-reviewer deadline repair and V2 packet ACK

**PASS for the focused corrected host child and exact V2 operator/owner-packet correspondence. The concrete Tier2 deadline defect is closed in the reviewed child; no additional bounded defect found.** This ACK authorizes no live action. New owner approval remains mandatory and the device remains STOP in Configurator.

Root identified the parent defect after the original PASS seal. This reviewer independently confirmed it and acknowledges that the original review missed it. Parent source/binary, initial PASS/report/PINS, V1 packet and custody remain byte-identical historical evidence, qualified by this defect. The oldee26 reader must not be substituted for the corrected108e64 child. No old history or negative result has been rewritten.

## Finding and exact closure

The parent's callback captured receipt time before fallible journal sync/fsync, then used that stale time to authorize the next read. The serial deadline timer could not run during the callback. An independent actual-parent-source ASan/UBSan witness records receipt4.9s, journal advance6s, then a second enqueue at6s against deadline5s. Its required-cutoff assertion fails at runtime with exit17 after successful compilation. This is client-code evidence using mocked APIs, not live USB evidence.

The only host source change is a6-line current-clock guard in State::read after buffer clearing/NSError setup and immediately before enqueue. No journal/sync intervenes. Current time at/after deadline or a failed clock read settles the reserved but not queued attempt through existing submit_failed/Finish, without abort or retry. Receipt timestamps, parser, core, descriptor/identity/callback policy and API/operation limits remain unchanged. The guard controls the immediate client submission decision; it is not an atomic OS scheduling or wire-timing guarantee.

Four independently compiled actual-child-source ASan/UBSan cases pass: journal delay past deadline, equality at deadline, failed current clock, and timely positive three-report operation. The first three each have1 actual enqueue,0 late enqueue,0 abort,1 accepted report and cleanup once. The positive case has3 enqueues/reports,0 abort and successful cleanup. Completion/raw/decoded timestamps retain the4.9s receipt value. Engine end.submissions counts logical reservations; a stopped reservation can show2 with only1 actual native enqueue and must not be described as a second transfer or proven SDK enqueue rejection. No counter/schema rewrite occurred.

The full child host program independently rebuilds byte-identically to108e64.... No live entry point was invoked. Author negative/regression inputs were source-inspected and rehashed; previous broad fixture/callback/descriptor evidence carries unchanged with this focused correction. No further broad test/review/build loop was run or requested. `TECHNICAL_REPAIR_REPORT.md`, independent witness sources/journals and command/result JSON preserve the detailed scope and evidence.

## Final immutable correspondence

Reviewed child `/private/tmp/glyph-native-Mac-hostinterface-observer-deadline-repair-20261022`:

- Source f0e246b6b6d15a6cab0b5db0eba86cf1907aa35795038e5190957ebee876e2f2; binary108e64e5eab524ad85d184eb7ee75d9e6075b44bd3df68598ed79dbf92622c83; technical HOLD5661e6a742b456676824fff8ebe31181f4365b8757ab7251884694fee4778c59.
- Final author REPORT992003ab1f30cfeb3a236040506f2168edeb850fa33df65d007a64ebc5149563; OPERATORa920970db775b7e3aec29d3fa5fb8251b22040328bbef7ae6a6b0594c80f7d6f; PINSb97ff6d581a40926f5fcc1fea3460be20b6ae9ff75814e93470b618f8b7d14ef. All64 child final pin entries,25 technical entries and86 parent final entries rehashed.
- Exact GP_NATIVE_001_MAC_HOSTINTERFACE_QUALIFY_V2 MD9707eb4ef20bfacff4ddf66ac6e2b3c1a72055726f06fe77ea9deb2e0a0ca607; JSONdc2b47fd68bef882614ac306e4dffcd4478dc5a8fe7da30735badb7d97ef7827 under `/private/tmp/glyph-native-mac-hostinterface-qualification-20261022/deadline_repair/`.
- Owner-checkout custodyc052ab9505eb588d8cb5852979f6fdc28499e473b60a6a8c8d584fc5eb6260d4. Retained binary/source/core/parser/HOLD match the child. Old custody and old reviewer three-file seal remain unchanged.

The complete machine-packet diff changes only version/parent history, child artifact/custody/report references and deadline/regression/reservation qualifications. Allowed operations, identity expectations, sequencing, normal UID, inspect/capture API scope and limits remain equal to V1. The packet accurately preserves fresh same-unit identity/entry IDs, separate explicit registry-only inspect and one capture with revalidation, ordinary exclusive optionsNone interface ownership, associated-getter/internal-traffic limitation, no OUT/control/config/reset/seize/driver fallback, fixed32-byte backing buffer and20-byte reports,5s receipts/current-clock enqueue cutoff, abort1/grace1s/internal8s/external10s and complete private custody then STOP. SDK call/destruction completion within5s is not promised. The whole State, not merely its32-byte buffer, remains retained when uncertain.

Author operator prose and V2 packet bind108e64 and refuse old reader substitution, retries, stale IDs and acceptance transfer. Approval and hardware result are null. The prior known ordinary restart/CDC identity operation remains root-owned existing bounded scope; this host review neither executes nor newly re-proves that protocol/tool. Its packet rights do not activate until the owner separately approves the exact V2 request.

## Retained gates

No live inspect/capture/registry/query/plugin/init/descriptor/pipe/read/cancel or serial action occurred. Mocked actual source replaced all effectful registry/host APIs; host compiles were private only. No target firmware build/change, Git/worktree/publication, install/network or owner contact occurred.

Actual OS/driver access, associated descriptors, pipe delivery/cancellation and physical behavior remain UNVERIFIED. F334f/tree0483dbb0, ELF/UF2/resource proof, dfd4 hardware packet, source/oracles and limits remain unchanged. No Config/ProfileStore/native/metric request or mutation is added. Success would qualify only this preflight host route/current legacy profile, not native rows, console, HEP, firmware/Git attestation, integration or DONE. Hardware/Nunchuk NOT_TESTED, timing/highwater NOT_MEASURED, RT2 deferred and root cause UNPROVEN remain qualified. Root owns publication and the exact owner approval request.
