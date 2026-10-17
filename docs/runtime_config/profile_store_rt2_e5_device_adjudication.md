# Stopped b075: separate normal-boot read-only adjudication

PREPARED / NOT EXECUTED. A separately authorized human hardware session owns
these actions. Source diagnosis sends no controller command, reset or flash.

The stopped candidate is `b07502866c56a1c7e1e217132aea30366e234461`, tree
`f6274649de4a7e620b19be795d16f95e53550683`; preserved UF2 is991232 bytes,
SHA-256 `8f1a470b75588080640861a8e07915b7d11ddf541fb185f372e5b91f86ee138a`.
Its one RT2 attempt remains failed regardless of a later normal-boot result.

1. Preserve all existing logs and the operator's purple/violet observation.
   Perform exactly one ordinary normal boot without RT2 or MB1, using the
   established route. No Clean/factory reset, filesystem removal or reflash.
2. Require normal Configurator enumeration and device info `b0750286`. Capture
   uniquely named raw journals for PULSE, STATUS, all LIST pages, full READ
   IDs1/3/4/22 and GET_CONFIG. Ten-second host ceiling per command; stop at the
   first timeout, identity mismatch, authority mismatch or uncertainty.
3. Compare the retained `b075-rt2-dcd-diagnostics/normal-control-port101`
   baseline: incarnation1, generation166, Config generation1182731055,
   revisions ID1=2, ID3=1, ID4=1, ID22=132, useful profile bytes/names/order/
   references and complete Config. Config protobuf is252 bytes, SHA-256
   `cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0`.
   No pending/armed fault or unresolved transaction/receipt is permitted.
   Record fault-trigger history separately rather than treating it as a new fault.
4. Record stack/heap samples and startup reconciliation observations. Historical
   b075 normal values are core0 free1928, core1 free3716, heap peak8864/capacity
   74400; they are comparison evidence, not guaranteed next-boot values.

No mutation, fault ARM/CLEAR, QUERY-to-force-reconciliation, GC, selection,
cleanup, restore, second RT2 attempt or automatic recovery follows this packet.
Any discrepancy blocks candidate replacement; preserve the stopped state and
report it. A normal-boot PASS does not identify the RT2 cause or erase that
failure. Root/GC V/W physical PASS stays separate; selection remains
NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE. Nunchuk NOT_TESTED.

Evidence caveat: the old capture's `candidate_expected_after_test_flash` and
artifact fields refer to stale template identities. Use actual device-info
version, exact owner report and preserved b075 UF2 custody for candidate binding;
do not relabel those old fields as b075. GET_CONFIG proves persisted bytes only.
