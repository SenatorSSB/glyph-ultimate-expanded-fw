# Failed4ee route adjudication — owner-only later procedure

Prepared, NOT_EXECUTED. This source task performs no controller command or reset.
The original evidence must remain immutable. Classification:
`ROOT_UNREADABILITY_TEST_ROUTE_INVALID_UNDER_FAULT_CONTROL_V2`, not product FAIL.
Do this adjudication on installed4ee before replacing firmware or attempting the
new route. Hash and retain every exact response and trace in a new directory.

Last known operator state: candidate4ee; token `0xf000000000001c00`; ordinary
QUERY ABORTED; generation165; receipt ID22/revision133; root ticket8 pending/inert;
no clear, reset, reboot, further mutation, GC, selection, RT2 or cleanup.
Baseline actual ID22 revision132 is retained at `root-unreadability/baseline/`.
The receipt is not proof actual ID22 became133. Later observations are unknown.

Authorized future adjudication sequence, performed separately by the owner:

1. Record installed candidate identity and exact USB/controller identity. Retain
   the failed route files; perform exactly one ordinary manual reset. No CLEAR,
   flash, recovery selection, filesystem operation or mutation.
2. PULSE then STATUS, each once; retain complete traces and responses. Require
   pending/armed false and healthy Config/store. Triggered history is volatile.
3. LIST all pages once; retain exact IDs/revisions/names/order.
4. READ actual ID22 once and compare its complete profile against retained
   baseline `read-id22.json`; compare actual revision independently of receipt.
5. READ useful IDs1/3/4 once each, compare complete bytes/metadata to the retained
   pre-attempt authority exports. Do not substitute a fresh CREATE/import.
6. GET_CONFIG once through the read-only serial client; compare retained valid
   Config and selectors/references. Preserve exact raw protobuf hash and JSON.
7. Ordinary QUERY token `0xf000000000001c00` once, with no ticket.

Expected, not assumed: generation165; actual ID22 revision132 and its original
payload; useful profiles and Config unchanged; exact token ABORTED carrying
intended revision133; no volatile pending/armed fault. Ordinary QUERY should not
advance a resolved generation. Stop immediately on any discrepancy/timeout and
retain the device; no automatic retry/reset/restore or cleanup.

Only exact human observations adjudicate this device. These instructions and
host tests do not report a physical PASS. Nunchuk NOT_TESTED.
