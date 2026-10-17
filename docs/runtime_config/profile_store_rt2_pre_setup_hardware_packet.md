# One-attempt external pre-SETUP observer hardware packet

PREPARED / NOT_EXECUTED. Source agents operate no controller. First require the
separate profile_store_rt2_pre_setup_device_adjudication.md PASS on stopped0f22.
Any mismatch blocks replacement. Do not rerun an older diagnostic packet.

1. Record controller/host/cable and a fresh evidence directory. Use exact final
   SHA/tree/parent and preserved UF2 size/SHA256 from sealed HANDOFF.md. Native
   custody rehash of those bytes immediately before owner manual install. No
   substitute rebuild, automated flash, format or whole-image restore.
2. After0f22 adjudication PASS, owner installs exact new UF2 using ordinary manual
   procedure. One normal boot without RT2/MB1. Normal Configurator GET_DEVICE_INFO,
   PULSE, STATUS, all LIST pages, full READ1/3/4/22, GET_CONFIG. Require exact new
   firmware, incarnation1/store166, accepted useful bytes/revisions/references
   (ID1rev2,3rev1,4rev1,22rev132), Config generation1182731055 and accepted252bytes
   SHA256 cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0.
   No uncertainty/unresolved receipt/pending or armed fault. Record both-core
   stack min-free, heap current/peak/capacity and flags; retain B2/E5-inapplicable
   control. Stop on mismatch/timeout before RT2.
3. Enter manual RT2 exactly ONCE with known held-button route without MB1. Wait10s
   from recovery handoff, with ordinary timing margin. Record one UNIFORM settled
   color each on the large LF4/LF3/LF5 main buttons. MB/menu LEDs are irrelevant
   and final MB1 is DARK. No individual LED roles/orientation, mixed pairs, video,
   transient sequence or human timing judgment. Optional one still photo.
4. Record display, matching IORegistry USB controller present/absent and serial
   endpoint present/absent. Native read-only ioreg may corroborate registry
   identity; it does not prove USB packets. No kernel/logging changes or SWD.

   | Button | Color decoder |
   |---|---|
   | LF4 handler | BLUE valid frozen/no IRQ entry; GREEN latest invocation returned; ORANGE same current ID observed<1s; RED same current ID observed>=1s; WHITE USBCTRL-context panic intercepted |
   | LF3 pre-SETUP | OFF none; YELLOW SOF returned; BLUE continuation entered; CYAN continuation returned; ORANGE SOF entered/not returned; MAGENTA inactive endpoint before original call; WHITE exact inactive panic; RED Unhandled IRQ panic; GREEN OtherUsb panic |
   | LF5 SETUP/downstream | OFF none; ORANGE external SETUP boundary; MAGENTA old hook; CYAN accepted; YELLOW consumed; BLUE control began; GREEN descriptor/address; WHITE configured-current/inspection; RED SETUP drop |

   LF4WHITE+LF3WHITE supports the exact inactive-panic call site; WHITE+RED
   Unhandled IRQ; WHITE+GREEN another intercepted USB panic. MAGENTA alone is
   the inactive predicate, without proof of intercepted panic. RED handler is a
   finite same-ID non-return observation, not proof of an infinite hang.
   CYAN continuation return does not prove the entire BUFF_STATUS path returned.
   Branch colors retain history; current association/counters refine via serial.
   All-dark or unclear button/color is UNKNOWN, not no-entry proof. No reset to
   improve visibility or recover a scratch marker.
5. If serial endpoint ABSENT: STOP IN PLACE. No further controller command,
   second RT2, reset/reboot/reflash, cleanup, GC, selection or mutation/refusal
   campaign. Keep this failed boot and the single observation.
6. If serial PRESENT: bounded read-only GET_DEVICE_INFO, PULSE, STATUS, all LIST,
   READ1/3/4/22, HEALTH useful/current records only if needed, GET_CONFIG once.
   Save raw bytes/hashes and response156–182 plus retained task/reset/raw/setup
   fields and Dashboard/times/resources. Require new captured=1/valid=1 for frozen
   pre-SETUP data; existing raw USB fields remain separate live samples. Require
   persistent authority/Config unchanged and no uncertainty/receipt/pending fault.
   Stop on first mismatch/timeout. No QUERY-to-repair, mutation, refusal campaign,
   GC, selection, cleanup or extra RT2.
7. Report exact SHA/UF2 hash, normal control/resources, LF4/LF3/LF5, display,
   USB-tree/serial and optional readback hashes, then STOP. Do not repair in this
   diagnostic run. Root cause UNPROVEN; full B7/Nunchuk/selection remain separate.

Decision after actual physical evidence only:

- Exact inactive panic: MULTI_PROFILE_STORE_RT2_PRE_SETUP_PANIC_PHYSICALLY_SUPPORTED;
  separate source diagnosis/repair proposal for the actual stale-buffer mechanism.
- Handler active/nonreturn without exact panic:
  MULTI_PROFILE_STORE_RT2_DCD_HANDLER_NONRETURN_NARROWED.
- Handler returned + raw SIE/INTR/INTS/no SETUP event:
  MULTI_PROFILE_STORE_RT2_PRIVATE_HANDLER_DIAGNOSTIC_REQUIRED. Evaluate a reproducible
  source-owned copied TU or SWD only in the next bounded step, not an installed
  framework edit or automatic action now.
- SETUP succeeds: classify observed downstream boundary without forcing old hypothesis.

No panic latch is universal no-panic proof: same-TU panic, assertion/fault or early
handoff failures can bypass interception. Handler private status/early branch,
raw-sampling, endpoint identity without readback and hardware BUF_STATUS/reset
arbitration remain residuals. HOST_PACKET_TRACE=NOT_AUTHORITATIVE. No source agent
has proven root cause or operated the controller.
