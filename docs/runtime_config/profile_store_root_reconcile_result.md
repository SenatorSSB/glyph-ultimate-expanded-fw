# Candidate root-reconciliation fault route

Disposition: source repair for `MULTI_PROFILE_STORE_ROOT_RECONCILE_FAULT_ROUTE_READY`;
final readiness requires the independent review and exact committed build/custody
record accompanying this document. Hardware remains NOT_TESTED for this candidate.
The owner request is the bounded authority: direct child of frozen4ee, candidate
fault route only, no production persistence redesign, controller action or merge.
Branch classification: FIRMWARE_SOURCE_ACTIVE_BEHAVIOR, hardware gate retained.
Live canonical/base is `6b73a7c507f35c111745c6bdd341618b490cbdcd`.

## Diagnosis and retained physical evidence

`ROOT_UNREADABILITY_TEST_ROUTE_INVALID_UNDER_FAULT_CONTROL_V2` describes the
attempt, **not a product failure**. Frozen candidate
`4ee63e26c912a0954ab9d7028a70a04ff80ced8d`, tree
`317b262f4a980e1762d02faa1b2911963e3632b9`, handled the ordinary QUERY correctly.

Retained evidence is under
`local_backups/hardware-tests/multi-profile-store-strict-hardening-20261016/responses/4ee-b9-b10/root-unreadability/`
in the owner's primary checkout. `baseline/read-id22.json` records actual ID22
revision132 at generation164. `setup/update.json` records ticket7 control-rename
lost acknowledgement, token `0xf000000000001c00`, intended revision133,
COMMIT_UNKNOWN, `directory.rename`, uncertainty8. `root-arm.json` records
pending/inert ticket8. `root-query.json` records ABORTED, intended revision133,
generation165 and ticket8 still pending. Omitted protobuf bools are false.
These observations cannot establish the current authoritative ID22 revision;
the separate read-only adjudication remains required.

Frozen `ConfiguratorBackend::HandleProfileStore` rejects QUERY fault tickets,
reconciles uncertain state before mutation activation, and only calls
`BeginMutation` after replay/admission. `Arm` merely prepares an inert rule.
Ordinary QUERY therefore had no installed hook. Healthy phase3 reconciliation
in `ProfileStore::ReconcileTransaction` publishes an identity-only ABORTED
checkpoint. The receipt retains the intended revision while its directory body
retains prior authority. The observed result is useful evidence for healthy
reconciliation. The old hardware instruction was impossible under v2.

## Exact route and single-attempt scope

Only a strict-hardening candidate protocol2 QUERY with nonzero token, available
storage, uncertain ProfileStore, matching pending inert ticket, and exact
Kind::Root/path2/OpenRead/Before/Fail/**skip0** may activate this route.
`CanBeginReconcileQuery` validates that closed predicate; `BeginReconcileQuery`
revalidates immediately before activation. No arbitrary query-side fault shape
is accepted. Production rejects the ticket even with a synthetic pending state.

The special request bypasses the whole ordinary pre-dispatch reconciliation
block. Its sole `QueryTransaction(token)` owns the internal reconciliation.
A nested RAII scope removes the hook immediately afterward and on an early
trace failure. Later Config loads, diagnostics, mapping, encoding and transport
run without it. No additional store query/reconciliation occurs on that path.
Ordinary QUERY, exact replay and ticketed mutation paths retain their behavior.
STATUS/LIST/READ cannot activate the pending rule, with or without a ticket.

Control loads use Kind::Root, but path2 matches `ultimate-v2-` and excludes
`ultimate-v2.ctrl` and `.ctmp`. Skip0 therefore faults the first actual directory
root OpenRead, `/ultimate-v2-0.bin`. Failed authority leaves uncertainty,
RootInvalid and ReadOnly set. `QueryTransaction` returns UnknownOutcome, mapped
by the existing backend switch to COMMIT_UNKNOWN. No result is hard-coded.
No checkpoint, profile publication, ID allocation or root deletion occurs.

`LoadDirectory` still reads the healthy companion. If root0 held the latest
generation, RAM/response can expose the older companion's generation and record
metadata while read-only. **Require no generation advance, not equality.** This
is existing fail-closed behavior; the route changes no persistence authority.
A fault-free remount reads both physical roots, restores the latest prior body,
and publishes exactly one ABORTED checkpoint at pre-query generation+1.

Aborted intended revision numbers are receipt metadata, not issued authority.
The current `Update` uses authoritative revision+1; it does not reserve a global
high-water counter for abandoned update revision labels. No broader never-reuse
claim for an uncommitted revision label is made. Issued IDs and authoritative
revision/replay protections remain unchanged; an aborted CREATE reserves its ID.

## Host and bounded trace contract

Use `query --reconcile-fault-ticket T --token TOKEN --request-out NEW.json
--trace-out NEW.jsonl`. The special command forces trace, requires exclusive
receipt/journal paths, preflights STATUS, and checks protocol2, candidate and
route capabilities, uncertainty8, pending/armed state, exact ticket and every
shape field including skip0. It sends exactly one QUERY with no retry. The
receipt is fsynced before QUERY transmission. Existing `query --fault-ticket`
remains rejected. Replay accepts mutation receipts only, so cannot replay this
special QUERY receipt.

Additive response fields52–57 expose kind/phase/result/path/skip and route
capability only on candidates; existing ticket/pending/armed/triggered/operation
fields remain authoritative. No new request field or format version is needed.
Trace stages:42 accepted ticket;43 hook active immediately before QueryTransaction;
44 triggered history after scope;45 uncertainty after query;46 armed=false after
scope. Values are ticket/boolean, using the existing bounded32-byte stage frame.
Stages1/2 and8/9 retain their existing meanings. No flash logging or new buffers.

## Verification and resources

`tools/check_glyph_profile_store_root_reconcile.py` compiles the actual backend,
ProfileStore, checked shim and Arduino-Pico3.6.3 LittleFS under ASan/UBSan. Config
is an explicit functional mock whose load boundary rejects an installed hook;
the separate production Persistence suite tests Config outcomes.

The28 cases include bounded trace failures before/after activation and after
the injected query; every exit removes the hook. It exercises frozen4ee ordinary ABORTED/inert-ticket behavior and ticket rejection;
current special UPDATE at both root parities; aborted CREATE ID reservation;
healthy remount and one checkpoint; exact ABORTED identity and changed-token
conflict; prior profile bytes/revision and next ID; second reboot stability;
ordinary QUERY; wrong ticket/kind/path/operation/phase/result/skip/version/token;
STATUS/LIST/READ; exact replay and changed replay presenting a ticket; healthy
QUERY rejection; and non-candidate rejection with uncertain state.

`tools/check_glyph_profile_store_reconcile_cli.py` tests real CLI orchestration
with an unopened offline transport,19 preflight negatives, exact receipt/journal,
one QUERY on unknown/timeout, invalid-preflight refusal and existing-receipt
preservation. Existing v2 mutation, P/Q/R1/S1/T0/U0/T1/U1 Config matrix and B1–B8
suites are required unchanged. Logs and exact commands are retained in custody;
no full global framework aggregate PASS is claimed.

RX/TX implementations,5000ms whole-request RX deadline,2000ms bounded TX deadline,
Arduino-Pico3.6.3 and resource instrumentation remain byte-exact. Final RAM/flash,
ABI, relevant target frames and heap/static accounting are in the immutable
handoff/resource report; no new hardware watermarks are claimed. The only new
persistent RAM payload is the additive static response shape/capability fields.
No new heap-owned instance member, allocation path or full-profile buffer.

[Failed4ee adjudication](profile_store_root_reconcile_device_adjudication.md) and
[new hardware packet](profile_store_root_reconcile_hardware_packet.md) are
prepared only. Nunchuk NOT_TESTED. No canonical acceptance or production redesign.
