# One-attempt RT2 DCD diagnostic hardware packet

PREPARED / NOT_EXECUTED. Owner manual actions only. No source-agent device action.
Use the exact preserved UF2 identified in final handoff receipt, never a rebuild
or mutable .pio output. No canonical merge or acceptance inheritance.

## Before replacing stopped5913

Installed5913e49f054eadd2554f94dd1d07908a6178e57e, exact UF2 SHA256
85276331e3f9c58d4654e3edc108766b3ff0daf7a4f6b9130baf6af3002feb41.
Exactly one ordinary normal boot without RT2 or MB1. Prove working normal
Configurator/device info. Save full raw responses and hashes: PULSE then STATUS,
every LIST page, full READ IDs1/3/4/22, GET_CONFIG. Compare retained useful
payloads/revisions/names/order/references and exact Config. Expected latest store
generation166, ID22 rev132, useful IDs1/3/4 unchanged are checks, not assumptions.
Record incarnation, Config generation, root health, pending/armed/triggered fault
history, receipt/transaction uncertainty, heap current/peak/capacity, stack margins
and resource flags. Require healthy useful authority, no unresolved transaction,
no pending/armed fault, no unexpected Config change. Do not reconcile merely to
obtain PASS. A mismatch/timeout/uncertainty blocks replacement; preserve state.
No mutation, CLEAR, cleanup, GC, selection, restore or additional RT2 attempt.
Record this adjudication separately from earlier root/GC PASS.

## New exact candidate

1. Only after adjudication PASS: record host/cable/controller and immutable
   evidence directory. Rehash exact owner-held preserved UF2 with native
   custody --pre-handoff-verify for full candidate/artifact hashes from receipt.
   Owner manually installs that exact UF2 through ordinary procedure preserving
   storage. No format/whole-image restore/automatic flash.
2. Normal boot without RT2/MB1: normal Configurator must enumerate, answer
   deviceinfo/PULSE/STATUS/LIST/READ1/3/4/22/GET_CONFIG, preserve adjudicated useful
   authority/generation/incarnation/Config and valid resources. Stop on mismatch.
3. Enter manual RT2 exactly once without MB1 using known stimulus. Wait10 seconds.
   Report only settled MB1 top-left menu pair color, USB tree controller present/
   absent and serial endpoint present/absent (record identity if present).
   No video/sequence reading. Black display is expected.10s is operator window,
   not a firmware delay. Colors: RED before repeated recovery-loop observation;
   ORANGE repeated loop/pull-up ON not yet sampled; YELLOW post-repeat pull-up ON
   seen/no further DCD milestone; MAGENTA DCD bus reset; BLUE SETUP/device descriptor;
   CYAN SET_ADDRESS; GREEN SET_CONFIGURATION status/mounted; WHITE supported
   complete inspection request decoded. Color is sticky furthest history, not
   current USB status. No LEDs is unknown, not proof of non-entry.
4. If serial endpoint absent: STOP in place. Report
   MANUAL_RT2_RECOVERY_TRANSPORT_UNAVAILABLE with settled color and USB tree.
   No second attempt, reboot, cleanup, reflashing or reset for scratch evidence.
5. If endpoint exists: deviceinfo, PULSE/STATUS, LIST, full READ1/3/4/22, HEALTH
   useful/current records and GET_CONFIG. Require complete valid responses,
   read-only recovery flag, unchanged useful authority/generation/Config and
   valid resources. Capture diagnostics version3, current/previous marker,
   milestone bits, IRQ state, SIE_CTRL/INTE/INTS/INTR/address/main_ctrl and task
   entry/return. WHITE alone does not prove response success. GET_CONFIG is the
   existing bounded read, no persistence action.
6. Full recovery refusal gate: use retained READ1 full valid payload, exact
   current incarnation/generation and fresh unused token greater than all used
   tokens in one protocol2 CREATE; do not arm faults. Require IO_FAILURE read-only
   and no ID/generation change. Submit exact retained current Config once through
   existing whole Config SET; require CMD_ERROR Recovery state is read-only.
   Any accepted mutation or transport loss: STOP, no compensation/cleanup.
   Source harness covers all other mutation types; no physical fault matrix.
7. Only after full recovery service/refusal PASS: one ordinary exit/reboot and
   repeat normal Configurator deviceinfo/PULSE/STATUS/LIST/READ1/3/4/22/GET_CONFIG.
   Require unchanged useful bytes/generation/incarnation/Config and no unresolved
   receipt/fault/uncertainty. Stop. No GC, selection or cleanup.

Record each row PASS/FAIL/NOT_TESTED with exact candidate SHA, UF2 hash and raw
transcript hashes. Nunchuk/selection/automatic-entry remain NOT_TESTED. This
experiment locates a low-level boundary; it does not establish root cause until
physical evidence supports that conclusion. No hardware PASS before owner report.
