# Separate device-state adjudication — future operator packet

**PREPARED ONLY. No device action was performed in source diagnosis.**
This packet follows retained-evidence adjudication `ARM_TRANSMISSION_UNPROVEN`.
Old candidate594066d9 may contain an active volatile Record/Write fail-before
rule; its ARM handler performs no storage I/O. No subsequent UPDATE was sent.
Both host waits failed. Treat the current device as unresponsive, not as a
proved corrupt store or proved healthy store.

For a separately authorized hardware operator, with owner present:

1. Preserve the failed-candidate/UF2 identity, last successful generation160,
   ID22 revision130, useful IDs1/3/4 payload hashes, and existing evidence.
   Do not send another mutation or attempt a repair over the hung transport.
2. Perform one controlled ordinary power cycle using the established normal
   Configurator route. No Clean/factory reset, filesystem deletion, automatic
   fallback flash, or unbounded retry. If it does not boot normally, stop.
3. On old firmware, make one bounded STATUS attempt and, only if successful,
   capture all LIST pages, READ IDs1/3/4/22 and GET_CONFIG. Use that old candidate's
   protocol/tool; new pulse/trace/ticket capabilities do not exist on it.
   Verify expected stable IDs/revisions/payloads and source-defined selection
   differences. Stop on discrepancy or another timeout.
4. Report separately whether volatile control reset, transport returned,
   authoritative state matched, and normal boot was observed. Do not overwrite
   the failed campaign result or infer an old ARM response from the new state.

Reset clears old fault RAM and gives startup a fresh USB/task/allocator state.
It cannot reveal whether ARM was transmitted, identify the prior blocked PC,
prove the USB race caused the failure, or convert594066d9 into hardware PASS.
Power loss can change/reconcile an interrupted persistent transaction; report
readback rather than assuming no pending persistence existed. The reported
absence of a later UPDATE narrows that specific fault row, not every possible
execution boundary.

Only after adjudication and the new exact candidate custody checks may the
operator follow the separate resumed campaign packet. This document is not an
instruction for the source-diagnosis agent to operate the controller.
