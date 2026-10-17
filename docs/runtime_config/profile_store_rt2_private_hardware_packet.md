# One-attempt exact private DCD observer hardware packet

PREPARED / NOT_EXECUTED. No source-agent controller action. First require separate
profile_store_rt2_private_device_adjudication.md PASS on stopped88a36e. Any mismatch
blocks replacement. Do not execute an older RT2 packet.

1. Record controller/host/cable and fresh immutable evidence directory. Use exact
   final SHA/tree/parent and preserved UF2 SHA256/size in sealed HANDOFF.md. Native
   custody rehash of SAME bytes immediately before owner manual installation.
   No substitute rebuild, automated flash, formatting or whole-image restore.
2. After88a36e adjudication PASS, owner installs exact candidate using ordinary
   manual procedure. ONE normal boot without RT2/MB1. Normal Configurator
   GET_DEVICE_INFO/PULSE/STATUS/all LIST/full READ1/3/4/22/GET_CONFIG. Require new
   exact firmware, incarnation1/store166, useful payloads/revisions/references
   (ID1rev2,3rev1,4rev1,22rev132), Config generation1182731055/accepted252bytes
   SHA256 cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0.
   No uncertainty/unresolvedreceipt/pending or armed fault. Record full resource
   flags and both core stack min-free, heap current/peak/capacity. Retain known
   chip2/ROM3/B2/E5-inapplicable control. Stop on mismatch/timeout before RT2.
3. Enter manual RT2 exactly ONCE with known held-button route without MB1. Wait
   10s from recovery handoff with ordinary margin. Record ONE uniform settled
   color on each LARGE LF4/LF3/LF5. Both LEDs per button SAME. MB/menu dark and
   irrelevant. No individual LED roles/orientation, mixed pairs, video, transient
   sequence or human timing judgment. Optional one still photo.

   | Main button | Settled color decoder |
   |---|---|
   |LF4 private status/raw|GREEN valid frozen/no private handler entry/no RAW; MAGENTA no entry/RAW; BLUE entries/no LOCAL SETUP/no RAW; CYAN entries/no LOCAL SETUP/RAW; ORANGE boot SETUP only before enable; YELLOW any enabled LOCAL SETUP; RED intercepted USBCTRL panic override|
   |LF3 first enabled SETUP, else first boot SETUP|OFF none; RED localSETUP/no branch entry; ORANGE branch/pointer reached; YELLOW PIDreset complete; CYAN immediately-before event H6; GREEN event returned H7; WHITE latch-clear-after or normal-return reached|
   |LF5 downstream|OFF none; ORANGE externalSETUP boundary; MAGENTA oldhook; CYAN accepted; YELLOW taskconsumed; BLUE controlbegan; GREEN descriptor/address; WHITE configured-current/inspection; RED SETUPdrop|

   RAW means ANY historical SIE/INTR/INTS positive, not all3/simultaneous/current.
   NoRAW-observed means sampling absence, not SETUP impossible. All-dark/unclear
   UNKNOWN. LF4YELLOW prioritizes enabled privateSETUP over RAW subencoding. LF4ORANGE
   explicitly marks solely pre-enable boot SETUP; its LF3 progress cannot be
   compared with recovery-only LF5 as an event mismatch. LF3 first enabled record,
   otherwise first boot record, never joins different invocations. RED there can be earlier SOF/
   BUFF nonreturn; not alone proof Cbranch failure. WHITE is grouped completion;
   telemetry refines exact marker. Panic masks LF4status/raw; do not infer hidden
   facts. Status in other observer reads is not private local status.
4. Record display, matching IORegistry USB identity present/absent and serial
   endpoint present/absent. Native read-only ioreg corroborates registry identity,
   not on-wire packet transmission. No kernel/logging change, externalcommand
   sent to device, SWD or repeated host reconnect.
5. Serial ABSENT: STOP IN PLACE. No more command, secondRT2/reset/reboot/reflash,
   cleanup/GC/selection, mutation/refusal or repair. Retain this failed boot and
   single settled observation. Do not reset just to read watchdog scratch.
6. Serial PRESENT: bounded read-only GET_DEVICE_INFO/PULSE/STATUS/allLIST/full
   READ1/3/4/22/GET_CONFIG once; HEALTH useful/current only if needed. Save raw
   bytes/hashes, response183–208 privateversion1/valid/captured and exacthistory,
   retained rawSIE/INTR/INTS/task/reset/prebranch/setup fields, panel/resources.
   Require captured=1/valid=1 for frozen private data. Existing rawlive USB fields
   remain separate from frozen rawobserver history. Verify accepted persistent
   authority/Config/no uncertainty/unresolvedreceipt/pendingfault. Stop at first
   mismatch/timeout; no QUERYrepair/GC/selection/cleanup/mutation/refusal/extraRT2.
7. Report exact SHA/UF2hash, normalcontrol/resources, LF4/LF3/LF5, display, USB/
   serial and optional bounded readback/transcript hashes, then STOP.

Decide only after actual physical evidence:

- RAWpositive and boot-lifetime privateSETUPcount0: MULTI_PROFILE_STORE_RT2_SETUP_NOT_SNAPSHOTTED_BY_DCD;
  dispatch/scheduling/timing/hardware residual, not SETUP branch failure.
- PrivateSETUP but no branchentry: inspect prebranch H2/testH3/assembly/fault/
  instrumentation first. No root-cause conclusion from LF3RED alone.
- Branchentered but noH6: MULTI_PROFILE_STORE_RT2_EARLY_SETUP_BRANCH_PHYSICALLY_NARROWED.
- ENABLED-record H6 but no externalentry: inspect exact inline DPRAMcopy/eventconstruction/call
  assembly and build correctness; no repair in this diagnostic run.
- ENABLED-record H7: classify queue/downstream boundary; old noevent boundary did not reproduce.
- Pre-enable-only privateSETUP (LF4ORANGE): retain its history; no cross-window
  event/queue mismatch claim from recovery-only LF5.
- No boot-lifetime privateSETUP and noRAW: MULTI_PROFILE_STORE_RT2_PRIVATE_HANDLER_ATTEMPT_NONDIAGNOSTIC;
  retain variability. Unknown/ambiguous panel remains UNKNOWN.

No forced IRQ/service/rescan/retry/delay/endpoint/clear/reset/descriptor change.
HOST_PACKET_TRACE=NOT_AUTHORITATIVE. Root cause UNPROVEN; exact new hardware
acceptance NOT_TESTED before owner executes this packet. Nunchuk/selection remain
NOT_TESTED. No source agent operated the controller.
