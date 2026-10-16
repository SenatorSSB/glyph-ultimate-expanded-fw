# Failed 895: separate one-reset read-only adjudication

Prepared only. No controller command, reset, flash, retry, QUERY or clear was
performed during source diagnosis. This packet requires a separate authorized
human hardware session; it is not executable automation.

1. Bind the failed device to candidate `895109eb662a8ad6b6c99889cb37a254dce49998`,
   tree `94d572cd23bd862a80d7891cd81c994a38f2c5a8`, UF2 980480 bytes / SHA-256
   `62eef01798782459750cb300071564a45f366fe6da94116d21b6db29d861c6f5`.
   Preserve all `895-b9-b10` evidence and its earlier READ gate. Pre-row state
   was incarnation1/generation160, ID22 revision130, useful IDs1/3/4 unchanged,
   pending ticket1 and armed=false after ARM. Current state is UNKNOWN.
2. Perform exactly one controlled ordinary reset/power cycle through the
   established Configurator route. No Clean, factory reset, filesystem removal,
   reflash or automatic retry. Stop if normal boot fails. Reset is expected from
   source to clear volatile fault RAM, but persistent state must be read back;
   startup reconciliation may run.
3. With uniquely named journals, run bounded pulse and STATUS, then LIST pages
   0/8/16, READ ID22 and useful IDs1/3/4, and GET_CONFIG. Each command has at most
   ten seconds; stop on the first timeout or discrepancy. Use the compatible
   895 tool. Its READ tracing contract is supported, but new RX counters are
   unavailable on 895. Record pending/armed/triggered/ticket explicitly.
4. Compare incarnation, generation, all IDs/revisions/profile hashes, Config
   and selection against `895-b9-b10/baseline-reconnected` and pre-row receipts.
   Record volatile reset, transport recovery, persistent-state match and any
   startup reconciliation separately. Do not assume the UPDATE had no effect
   solely from the source-localized pre-decode error.

895 remains permanently `HARDWARE_FAIL —
LARGE_PROFILESTORE_REQUEST_RX_TIMEOUT_DURING_TICKETED_UPDATE`, regardless of the
result. Its separate `MULTI_PROFILE_STORE_895_READ_GATE_HARDWARE_PASS` remains
valid for the observed 84/84 READ scope. Neither outcome grants permission to
retry row A, continue acceptance, or merge. Historical 594/d596 failures remain.
