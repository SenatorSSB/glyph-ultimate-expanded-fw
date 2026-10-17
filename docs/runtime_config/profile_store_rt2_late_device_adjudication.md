# Stopped d30e: one-normal-boot read-only adjudication

PREPARED / NOT_EXECUTED. Controller stopped after ONE d30e RT2 CYAN/OFF/OFF.
No source-agent controller action. Installed d30e5250ef2e5e425cc0f217fd37247b484ca988,
known handoffUF2 SHA256 b4cda73fd4637b90b1ba7420b01a854d07ec1515e0ccd495bc846ec56b54e4f1,
1026560bytes. This replaces the historical stopped88 prerequisite; do not execute
older candidate RT2 packets. Exactly one ordinary normal boot, no RT2 retry.

1. Record controller/host/cable, installed identity and a fresh immutable evidence
   directory. Perform exactly ONE ordinary normal boot without RT2 or MB1.
2. Use working normal Configurator. Device info must identifyd30e5250. If transport
   unavailable, stop; no retry/reflash/cleanup/QUERY-to-repair.
3. PULSE then STATUS once each. Require generation166/incarnation1; no transaction
   uncertainty, unresolved receipt, pending or armed fault. Record root health,
   fault history, full resource flags, both core stack min-free and heap current/
   peak/capacity. Owner-reported normald30e resources1864/3716 min-free, heap10224,
   capacity71664; filesystem147456used/376832free are comparison facts, not acceptance inherited by a new build.
4. LIST every page once. Full READ1/3/4/22. Require accepted useful authority,
   payloads, revisions/names/order/references: ID1 rev2; ID3 rev1; ID4 rev1;
   actual ID22 rev132. Compare all listed IDs to actual retained ledger; do not
   recreate deleted disposable IDs. Normalized sorted compact UTF-8 JSON(profile)
   hashes: ID1 8a195a04745fd5729b26e37a78e7ecf3b43fab2ae94c68010bea052d7bad77c2;
   ID3/22 3d26c57665be91228a30b4577687cfe0d1d5328575d19b6d6461b6c92beb9e49;
   ID4 4aab71e55e92954d96c2fb877c749d6e0ec11004d8a49293c7a88626b96a7f02.
   These are JSON payload hashes, not protobuf hashes. Retain raw response bytes
   and compare original payload if reserialization differs; never normalize away
   a semantic mismatch.
5. GET_CONFIG once. Require Config generation1182731055 and exact accepted252
   bytes SHA256 cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0.
   Preserve raw bytes/hash plus decoded Config. Confirm root/reference/selectors
   consistent with accepted useful authority. No SET/import/restore.
6. Confirm chip2/ROM3/B2/E5flags0 if available. Preserve
   E5_PHYSICALLY_INAPPLICABLE_ON_TEST_CONTROLLER; do not treat absent proto3 zero
   as an unknown flag when actual schema/default establishes0.
7. Record each row PASS/FAIL/UNKNOWN and transcript hashes, then STOP. No QUERY
   repair, mutation, refusal campaign, CLEAR, GC, selection, cleanup or RT2 retry.

Any mismatch, uncertainty, timeout, invalid resource condition or missing useful
readback blocks replacement. This packet itself is not a new hardware PASS.
Authoritative retained source/evidence: profile_store_rt2_late_physical_adjudication.json.
