# One-attempt raw SETUP / USBCTRL IRQ hardware packet

PREPARED / NOT_EXECUTED. Source agents operate no controller. Required first:
profile_store_rt2_setup_irq_device_adjudication.md PASS on stopped3761.
No firmware replacement on any adjudication failure. Do not repeat the3761
comprehensive or older3b5c RT2 packet.

1. Use the exact final SHA/tree/parent and preserved UF2 size/SHA256 from the
   sealed HANDOFF.md. Native pre-handoff verification must rehash those preserved
   bytes immediately before owner manual installation. No substitute rebuild,
   automated flashing, format or whole-image restore. Record host/controller/
   cable and a fresh evidence directory. Owner installs the exact candidate by
   ordinary manual procedure only after3761 adjudication PASS.
2. One normal boot without manual RT2/MB1. Normal Configurator GET_DEVICE_INFO,
   PULSE, STATUS, all LIST pages, full READ1/3/4/22, GET_CONFIG. Require expected
   exact candidate version, incarnation1/store166, unchanged useful bytes,
   revisions1:2/3:1/4:1/22:132 and references. Config generation1182731055;
   accepted252bytes SHA256
   cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0.
   No uncertainty, unresolved receipt or pending/armed fault. Record both-core
   minimum-free stack, heap current/peak/capacity and flags. Confirm chip2/ROM3/B2/
   E5flags0; E5 physically inapplicable. Any timeout/mismatch stops before RT2.
3. Optional safe host corroboration may run concurrently with this SAME single
   attempt. HOST_PACKET_TRACE=NOT_AUTHORITATIVE. Unified logs are emitted software
   messages, not proof the host put SETUP on the wire. No sudo, driver install,
   boot argument/kernel tracing or logging configuration change. A failed command
   or empty log is inconclusive and never authorizes another RT2. Human may run
   the following in a terminal, retaining stdout/stderr in the evidence directory:

   ```sh
   /usr/bin/log stream --style compact --level info --timeout 30s --predicate 'subsystem CONTAINS[c] "usb" OR senderImagePath CONTAINS[c] "USB"'
   ```

   The log window must overlap the same RT2 to be useful. If it ends early,
   record INCONCLUSIVE; do not repeat a boot. Ordinary IORegistry read below is
   endpoint/object corroboration only. No USB packet-transmission claim.
4. Enter manual RT2 exactly ONCE using the known held-button route without MB1.
   Wait10seconds from recovery handoff (ordinary timing margin is fine). Record
   ONE settled color for each LARGE main button LF4, LF3, LF5. Both LEDs for each
   selected main button have identical color. MB1/menu buttons are intentionally
   DARK and irrelevant. No within-button roles, orientation, mixed pairs,
   transient sequence, video or human timing judgment. Optional one still photo.
   Record display, matching USB-tree device present/absent and serial endpoint
   present/absent. Ordinary read-only registry command if useful:

   ```sh
   /usr/sbin/ioreg -p IOUSB -l -w 0
   ```

   If a main-button identity/color is unclear, record UNKNOWN and retain the
   still; do not guess or reset to improve observation.
5. Decode one logical state per large button using the exact contract:

   | Button | Settled color |
   |---|---|
   | LF4 raw SIE/INTR/INTS ever-bitset | OFF none; RED SIE; YELLOW INTR; ORANGE SIE+INTR; BLUE INTS; MAGENTA SIE+INTS; CYAN INTR+INTS; WHITE all three |
   | LF3 gate/dispatcher | OFF no raw; YELLOW raw without stronger gate sample; RED INTR/INTE-off sample; ORANGE INTS/core0 NVIC-off sample; MAGENTA INTS/core0 PRIMASK-set sample; BLUE INTS/pending sample; GREEN trampoline entry with raw SETUP-positive pre-read; WHITE trampoline pre/post read sampled INTS |
   | LF5 DCD/queue/downstream | OFF none; ORANGE prequeue external SETUP event boundary; MAGENTA old hook attributed SETUP; CYAN queue accepted; YELLOW task consumed; BLUE control began; GREEN descriptor/address milestone; WHITE configured-current/supported inspection; RED any dropped SETUP overrides |

   Raw bitsets are historical positives, not temporal stage ordering. A sampled
   SIE-only or enabled-INTR/no-INTS mismatch does not establish a stable silicon
   propagation fault: loads are sequential. LF3 shows highest-priority observed
   condition, not absence of earlier masks; a prior unrelated reset IRQ cannot
   establish SETUP delivery. Dispatcher reads are not the real handler's local
   status snapshot. Exact INTE/INTF, all tuples, gate flags, reset histories,
   emission/return/hook/accept/drop counters remain frozen telemetry if readable.
6. If serial ABSENT: STOP IN PLACE, retaining the failed boot. No second RT2,
   reset/reboot/reflash, command, cleanup, GC, selection or mutation/refusal
   campaign. No controller-query workaround. Interpret only observed boundaries.
   No panel means UNKNOWN, not proof of non-entry. The photo cannot reveal every
   reset epoch, tuple or hidden gate history; keep those residuals explicit.
7. If serial PRESENT: bounded read-only diagnostics only. GET_DEVICE_INFO,
   PULSE, STATUS, all LIST pages, full READ1/3/4/22, HEALTH useful/current records
   only if needed, GET_CONFIG once. Save raw transcripts, new diagnostics129–155,
   retained task/reset/queue fields90–128, Dashboard/times, existing separate live
   raw USB fields and resource fields. New captured=1/valid=1 means the frozen
   narrow snapshot shares the panel/task publication; normal/live captured=0 is
   not the frozen failed-boot record. Require persistent authority/Config unchanged
   and no uncertainty/unresolved receipt/pending fault. Stop on first mismatch or
   timeout. No QUERY-to-repair, mutation, refusal campaign, GC, selection or cleanup.
8. Report exact SHA/UF2 hash, normal-control result/resources, LF4/LF3/LF5 color,
   display/USB-tree/serial, optional log and readback hashes, then STOP. Root cause
   remains UNPROVEN; full B7, selection and Nunchuk acceptance are separate.

If evidence ends at completed reset plus SIE observed without sampled INTR/INTS,
and no source-backed writer/mask is found, preserve RAW_REGISTER_SAMPLING_RESIDUAL
and HOST_PHY_SETUP_RESIDUAL. Software cannot establish whether the host never
transmitted or the PHY/controller failed to latch a packet, or reconstruct an
unseen read interval. External USB protocol analysis or genuinely authoritative
host packet trace is the next route. Do not add increasingly invasive firmware
instrumentation without a new safe discriminator. Handler-own status and early
inline branch boundaries remain explicit residuals even after dispatcher entry.
