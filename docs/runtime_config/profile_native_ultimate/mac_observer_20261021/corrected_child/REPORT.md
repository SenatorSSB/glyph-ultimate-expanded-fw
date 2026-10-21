# Focused host observer child — two review findings

**The bounded host child is implemented, tested and under SOURCE/PACKET HOLD for the same independent reviewer's repair ACK. No device access or approval is claimed.** Parent `/private/tmp/glyph-native-mac-observer-preparation-20261021` remains immutable, including source, binary, PINS, fixtures and prose. The child writes only this directory. No firmware/source/Git/worktree/target build, network, installation, capture/inspect body, device I/O or owner contact occurred.

## Exact boundary and preserved inputs

Independent parent review REPORT SHA5fce9d5d69fb8c3ac51ac877cef51dd545673d9f387c3c0788bc09ab5b464d12 and PINS SHA560b7e398f6b4b46266dad5ffc96cfd2f958313434d8857b419674e33a4644ac identify exactly two P2 host findings. Copies and runtime witnesses are preserved in independent_parent_review/. Parent source/binary/report/PINS and source-derived originals are bound by parent_baseline_pins.json and immutable_parent_baseline/.

Only mac_input_observer.cpp and verify_capture.py change behavior. Added files are directly coupled host tests/provenance/prose/build/manifests. Both parent-to-child diffs are retained. The exact reviewed-base334-row packet remains SHA **dfd4ab5c81c24e1380095fa637ff0d51de83b478f66641c53d1a69d9f76be744**: every row, native output, profile/context, eleven-field wire derivative, H10/H11, resource closure, required addendum and null/NOT_TESTED observation is unchanged. Exact F/UF2/ELF identity and all target authority boundaries remain unchanged.

## Finding1: actual adapter completion count

The SDK callback's actual count is now retained as uintptr_t plus an explicit completion-received flag. Missing completion is distinguishable from a received zero-byte completion. One-byte initialization succeeds only if the operation status is success, completion is known, exactly one byte completed, and cancellation is not pending. Errors, count0/count2/invalid counts, missing completion, timeout and late-success-after-timeout stop without retry.

The init event records operation IOReturn, callback IOReturn or null, completion presence, actual bytes_written or null, pending state and complete/uncertain outcome. verify_capture.py requires explicit known integer1, both zero statuses, completion_received=true, pending=false and complete outcome for each permitted init record. It continues to enforce explicit WUP approval and at most one init record. The only output submission remains one fixed0x13 adapter byte; no command, operation or fallback is added.

## Finding2: whole pending owner and Capture lifetime

Default deletion is replaced by a noexcept pending-aware USBReader owner policy. Every pending owner exit, including implicit exception unwinding, first detaches the stack Capture pointer and retains the entire allocated reader, buffers, interface and event source until process exit. Returning from a destructor is no longer treated as retention. Both late callbacks tolerate detached Capture; the input callback skips receive when no Capture remains.

The explicit undrained adapter branch snapshots primitive completion data and transfers ownership before fallible journaling. The undrained input branch transfers before any fallible error handling. Settled owners retain their existing event-source/interface close/release behavior. This relies on the existing single-thread CFRunLoop callback contract; no new worker/thread/I/O path is introduced. Unsettled cancellation still means immediate stop/process-exit cleanup, not retry or continued capture.

## Executed finite host evidence

- Actual source-extracted USBReader/deleter, both callbacks, completion snapshot and actual consumer guard run under ASan/UBSan. Nine count/status/unknown cases include success1, success0, success2, UINTPTR_MAX, absent completion, error/count1, timeout/count1, cancellation/count1 and late-success1 after timeout. Only complete known one-byte success passes.
- Four pending exit forms × late input/output completion = eight lifetime cases pass: retention before custody exception, earlier implicit unwinding, explicit input-side retention and scope/return exit. Capture is destroyed before late callbacks, detached pointers remain null, reader/buffer/handles remain live and settled cleanup occurs exactly once. Ordinary settled cleanup also runs exactly once through mocked interface/CF cleanup. No real IOKit method is executed by these fixtures.
- The reviewer's exact parent pending-owner witness independently rebuilds successfully and reproduces ASan heap-use-after-free at runtime. A separately extracted exact parent callback/status-only guard rebuilds successfully and fails the required zero-count refusal at runtime. These are preserved negative controls, not compiler failures.
- Fifteen actual verifier synthetic challenges cover integer1 success;0,2,negative,huge,null,float,string,bool,missing count; failed status/count1; timeout/late1; missing callback; pending1; and callback error1. The parent verifier's zero-byte acceptance is reproduced on the same complete synthetic WUP capture; the child refuses it.
- The host native observer is rebuilt. All1002 complete report vectors,48 framing/boundary cases,14 prior synthetic correspondence cases and five pure native parser/argument branches pass. Eleven unsafe Switch source casts remain unexecuted; their artifact-specific wire fields still come from the unchanged sealed proof.

focused_repair_commands.json, focused_repair_validation.json, count_verifier_tests.json and per-run logs retain commands/outcomes. actual_callback_owner_guard_provenance.json pins extracted actual source fragments and the mock boundary. Initial fixture runs encountered an unsupported macOS leak-detector option and an inherited nonexecutable copied parser before its rebuild; those logs are preserved. Final ASan/UBSan uses supported checks and all required runtime controls pass. No leak-sanitizer or hardware timing claim is made.

## Held result and remaining gate

TECHNICAL_HOLD.json freezes the child code/binary, packet, existing proofs and new focused tests. PINS.json seals the finished child. MAC_OBSERVER_PROCEDURE.md retains the mandatory original session plan/addendum, source-backed cold-entry/watchdog/bookkeeping qualifications and all equipment/route limits, adding only these completion/lifetime repairs. Parent findings are author-addressed; closure remains subject to the same independent reviewer.

Actual Mac interface discovery/open, driver permissions, adapter polling/report delivery and asynchronous cancellation remain UNVERIFIED. Source-backed build/host mocks do not grant physical acceptance. Optional adapter0x13 still requires its separate explicit approval; no registry inspect or capture body has run. Initial approved preflight must forbid runtime/watchdog switching and host Config/ProfileStore mutation; later candidate flash/profile operations require separate approval. Ordinary firmware boot bookkeeping is not promised byte-identical.

Mac raw Switch/WUP observations still cannot transfer console PASS. WUP37 remains an adapter USB report rather than electrical Joybus evidence. All18 families/H1–H12, original backup/restoration, two disposable IDs, H10/H11, native OLED/XInput alias limitations and the preserved exact target tuple remain required. Hardware/Nunchuk NOT_TESTED, timing/highwater NOT_MEASURED, RT2 deferred and root cause UNPROVEN remain unchanged.
