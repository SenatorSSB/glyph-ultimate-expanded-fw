# Stopped88ab: separate normal-boot read-only adjudication

PREPARED / NOT EXECUTED. A separately authorized human hardware session owns
these actions. Source diagnosis sends no controller command, reset or flash.

The stopped candidate is `88ab0029d464175865e1ce3e9a19b462579ffed4`, tree
`097dd278c8ebccdd9bdf188c38a36410b0d61e4d`; preserved UF2 is994304 bytes,
SHA-256 `f13556e392ec017b1101a8bc608ae2ea568295bae1643c98e383e7967035a627`.
Its one RT2 attempt remains failed regardless of a later normal-boot result.

1. Preserve all existing logs and the operator's RED observation.
   Perform exactly one ordinary normal boot without RT2 or MB1, using the
   established route. No Clean/factory reset, filesystem removal or reflash.
2. Require normal Configurator enumeration and device info `88ab0029`. Capture
   uniquely named raw journals for PULSE, STATUS, all LIST pages, full READ
   IDs1/3/4/22 and GET_CONFIG. Ten-second host ceiling per command; stop at the
   first timeout, identity mismatch, authority mismatch or uncertainty.
3. Compare the retained `88ab-rt2-e5/normal-control-port101`
   baseline: incarnation1, generation166, Config generation1182731055,
   revisions ID1=2, ID3=1, ID4=1, ID22=132, useful profile bytes/names/order/
   references and complete Config. Config protobuf is252 bytes, SHA-256
   `cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0`.
   No pending/armed fault or unresolved transaction/receipt is permitted.
   Record fault-trigger history separately rather than treating it as a new fault.
4. Record stack/heap samples and startup reconciliation observations. Historical
   88ab normal values are core0 free1856, core1 free3716, heap peak8688/capacity
   74224; they are comparison evidence, not guaranteed next-boot values.

No mutation, fault ARM/CLEAR, QUERY-to-force-reconciliation, GC, selection,
cleanup, restore, second RT2 attempt or automatic recovery follows this packet.
Any discrepancy blocks candidate replacement; preserve the stopped state and
report it. A normal-boot PASS does not identify the RT2 cause or erase that
failure. Root/GC V/W physical PASS stays separate; selection remains
NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE. Nunchuk NOT_TESTED.

Evidence caveat: the old capture's `candidate_expected_after_test_flash` and
artifact fields refer to stale template identities. Use actual device-info
version, exact owner report and preserved 88ab UF2 custody for candidate binding;
do not relabel those old fields as88ab. GET_CONFIG proves persisted bytes only.

Silicon is already physically established as chip2/ROM3/B2, E5 flags0. Preserve
`RP2040_E5_PHYSICALLY_INAPPLICABLE_ON_THIS_CONTROLLER`; no E5 test follows.
The failed88ab RED result establishes no repeated recovery-loop observation,
not bus-reset receipt or a non-returning USB task. Historical b075 MAGENTA is a
separate boot and remains unchanged. Do not combine these into one timeline.
