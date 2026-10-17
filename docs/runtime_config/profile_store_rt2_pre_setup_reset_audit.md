# Official hardware/source authority audit: late buffer status across reset

Read-only specialist result; only ignored evidence created. Repository frozen input: `0f22b6d3b5d4a1a16fc7fd03866cfa44336de4ff`, tree `4f5fb41553f98da3f11108685b2eaa0942583fc0`. Canonical named base `6b73a7c507f35c111745c6bdd341618b490cbdcd` is unchanged by this role; no live remote assertion. Requested Sol/medium; actual model/effort UNKNOWN absent runtime telemetry. No controller, USB/serial host inspection, capture, build, vendor modification, tracked modification, Git mutation, or publication performed. Physical evidence supplied by root is retained as reported: one exact0f22 RT2, LF4 white/LF3 yellow/LF5 off, black/no host USB/serial, stopped; no root cause inferred.

## Result

The pinned source admits a **conditional** path from a late/stale noncontrol buffer-status bit to `hw_endpoint_xfer_continue` on an inactive, reset-zeroed software endpoint, before any subsequent SETUP branch. The source does not clear BUFF_STATUS in its BUS_RESET cleanup, nor reread the IRQ status after cleanup. Official documentation inspected does not specify whether electrical USB BUS_RESET clears/preserves pending BUFF_STATUS or resolves a completion versus endpoint-disable race. Therefore the hardware premise is UNKNOWN, this is not an established physical sequence, and root cause remains UNPROVEN. A BUS_RESET bit and BUFF_STATUS bit in one status snapshot do not themselves establish reset-induced inactive panic: BUFF_STATUS is processed first in that call, before this call's reset cleanup.

## Exact source and official references

`U` = `/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040` (the compiled Adafruit TinyUSB copy, not SDK bundled TinyUSB).

- U/dcd_rp2040.c SHA256 `92a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12`.
- U/rp2040_usb.c SHA256 `81c24999f3ec9918723d4494619a9abdb2733a21d4bf39573a7c60eb461c5de6`.
- U/rp2040_usb.h SHA256 `5f215d092223581d9de4dd0542aa4cc587d280b7cc85978571621cfb54125524`.
- Official RP2040 datasheet cached at `/private/tmp/glyph-profile-store-rt2-setup-irq/local_backups/setup-irq/official-references/rp2040-datasheet.pdf`, SHA256 `be56fbb75ba0ae9e26558a73c93ac3e75c2ad4e6878d3b6703de2a76d886ea8c`, 5301205 bytes. URL: https://datasheets.raspberrypi.com/rp2040/rp2040_datasheet.pdf . Pinned supplied version: 2025-02-20/build3184e62. Read complete USB chapter PDF pages384-418 via pypdf text extraction; relevant extracts saved beside this audit. Text extraction is used for technical prose/register definitions, not layout assertions.
- Official SDK1.5.1 USB register header cached beside the original PDF, SHA256 `8e292ab4eb7ae6c5177f59a7cadcc03605685355b2c789a0cbf262d4968ec313`, 186332 bytes. URL: https://raw.githubusercontent.com/raspberrypi/pico-sdk/1.5.1/src/rp2040/hardware_regs/include/hardware/regs/usb.h . Matches cited register descriptions.

Datasheet printed pages390-391, sections4.1.2.8.2-3, describe IN/OUT completion setting BUFF_STATUS and buffer control changes. Printed404-405/table406 defines per-direction endpoint bits as WC and reset0. Printed413/table418 defines raw BUFF_STATUS IRQ as any BUFF_STATUS bit set and says to clear all those bits to clear the raw source. Printed416/table421 calls INTS status after masking and forcing. Printed403/table404 defines BUS_RESET as its separate SIE_STATUS bit. The RESET column is a register reset value, not a promise about an electrical USB bus reset. Neither that column nor independent WC fields proves that BUS_RESET preserves or clears BUFF_STATUS.

The official BUFF_STATUS description and section4.1.2.8.2 permit immediate reassertion after clearing when two buffers completed. This disproves a general claim that one software clear guarantees no later buffer indication. It does not establish the exact driver's ordinary configuration triggers that mechanism: rp2040_usb.c173-212 sets double-buffered IN to interrupt per double buffer, forces device OUT single, and dcd_init sets only EP0_INT_1BUF, not EP0_DOUBLE_BUF. Do not relabel generic documented reassertion as an observed or necessarily enabled failure here.

## Software reset boundaries

- dcd248: exactly one private masked `status = usb_hw->ints` snapshot.
- dcd251-288 SOF precedes dcd292-296 BUFF_STATUS; dcd298-309 SETUP precedes dcd332-347 BUS_RESET.
- dcd189-216: helper takes a fresh `remaining_buffers = usb_hw->buf_status` once. For each saved bit, clear hardware bit first, map even bit to IN and odd bit to OUT by array position, call continuation, emit completion if done, then reset software transfer. No configured/active guard in helper, no reread after clear, no retry loop over newly appearing bits.
- usb338-346: continuation's lock helper is empty (header107-111); inactive `ep->active == false` explicitly calls panic before buffer-pointer access. No configured guard. Do not derive actual panic occurrence from this source alone.
- dcd338-341 BUS_RESET: address0, `reset_non_control_endpoints`, enqueue bus-reset, clear only SIE BUS_RESET. Not a call to rp2040_usb_init or RESETS block reset.
- dcd230-244 cleanup: zero all EP1-15 endpoint-control words, zero all corresponding software hw_endpoint structs, reclaim next buffer pointer. It does NOT write USB BUFF_STATUS, EP1-15 DPRAM buffer-control words, EP_ABORT/EP_ABORT_DONE, EP0 software state, EP0 buffer-control words, SIE_CTRL, INTE or SETUP_REC. Do not confuse `_hw_endpoint_close` (dcd97-105, clears one buffer-control word too) with reset_non_control_endpoints.
- usb65-80 initialization does a USBCTRL block reset and whole DPRAM zeroing; dcd408-413 zeroes/initializes EP0 and resets noncontrol. This stronger initialization is not ordinary BUS_RESET cleanup.

## Timing matrix

Assume the original handler returns from earlier branches, no unsupported corruption/force writes, and IRQs can dispatch subsequently. T = private INTS read(dcd248); B = helper's independent BUF_STATUS read(dcd191); C = helper per-bit clear(dcd199); R = noncontrol software clear(dcd240). A true completion means hardware accepted/completed the relevant transaction; arbitrary injection is not physical evidence.

| Completion/status timing | Current call | Later consequence / limitation |
| --- | --- | --- |
| Bit set before T; BUFF mask enabled at T | BUFF branch runs, helper reads at B and services bits still set, before SETUP and this call's R | If endpoint already inactive from an earlier reset/completion, conditional panic path; this call's later reset cannot be its cause |
| First bit appears after T with no BUFF bit in private status | BUFF branch skipped even if hardware source now positive; any snapshotted RESET can execute R | If that bit survives to a later IRQ and endpoint remains reset/inactive, helper reaches inactive panic before later SETUP; survival is hardware UNKNOWN |
| BUFF was positive at T for another endpoint; target bit appears before B | Helper includes target in its later snapshot, before this call's reset cleanup | Target can be processed in current call despite absence at T; do not pretend T pins per-endpoint bits |
| Target bit appears after B, including during processing of another saved bit | Target is absent from saved remaining_buffers and not rescanned | If retained through R/next IRQ, conditional inactive path; exact acceptance/retention UNKNOWN |
| Same endpoint bit reasserts after C while helper handles saved completion | Helper removes that saved bit once; if done, transfer reset sets active=false | Later asserted bit can reach inactive state, conditional on actual reassertion/driver configuration; generic double-buffer documentation is not proof for this candidate |
| Completion/writeback overlaps R or endpoint-control disable | No source abort/drain/BUF_STATUS acknowledgement accompanies R | Official inspected documents do not settle acceptance, priority, late writeback or bit retention. Do not claim completion must happen or must be suppressed |
| New ordinary transfer after reset, endpoint still disabled/unopened | No source submission arms this endpoint in that condition | A pending stale indication is a different premise. Cannot claim fresh host traffic alone creates a valid completion on disabled endpoint |
| Bit set while BUFF INTE mask is0; no force | Raw source/BUF_STATUS can be positive while masked BUFF branch is absent | No handling until enabled/otherwise reflected in INTS; masking is not clearing. Actual dcd_init enables BUFF and BUS_RESET does not clear that enable |
| BUFF bit forced in INTF with BUF_STATUS0 | BUFF branch can run but B is0 | Helper calls no continuation; this does not itself cause inactive panic |

A newly arriving SETUP after T is likewise absent from this call's private status. A following IRQ may carry SETUP and BUFF together; BUFF still executes first. If continuation does not return, SETUP emission is not reached. The pre-handler observer's INTS read is a distinct, earlier read and cannot prove the DCD private T value.

## Endpoint-state matrix

| Endpoint lifecycle | Software state relevant to conditional BUFF delivery | What can be concluded |
| --- | --- | --- |
| EP0 IN / EP0 OUT just initialized | Both structs zeroed then initialized with correct addresses/directions, fixed buffer, packet64; active remains false; controls cleared | Normal SETUP has dedicated latch, not a required ordinary EP0 completion. Hypothetical completion before a start reaches inactive panic; ordinary generation is not established |
| EP0 IN / OUT active ordinary control transfer | xfer_start sets active=true; completed helper resets active=false | Current completion expected active; duplicate/late delivered bit after reset_transfer can hit inactive, conditional hardware premise |
| EP0 after BUS_RESET cleanup | reset_non_control_endpoints leaves both software structs and buffer-control words unchanged; reset_ep0_pid on SETUP changes PID only | Cannot explain EP0 becoming inactive by noncontrol R. Its earlier software transfer completion or other lifecycle must be separately shown; retained active can instead be stale |
| EP1-15 never opened / unconfigured | Zero software structs; endpoint controls zero after init/reset | Delivered bit maps to that array slot regardless of configured, sees active=false and panic. A valid new hardware completion is not established merely by the ability to inject a bit |
| EP1-15 opened, before transfer start | Init gives pointers/address/type but does not set active=true | Hypothetical delivered stale bit can panic; opening alone does not guarantee active |
| EP1-15 active before ordinary reset | active=true until completion/reset | A bit in same T is serviced before this call's R, so reset race requires late bit or prior reset, not merely combined snapshot |
| EP1-15 just after BUS_RESET R | Struct is all zero, including active=false, ep_addr=0, pointers0; endpoint controls0, buffer-control words not explicitly cleared | If a pending/late bit reaches later helper before a new start, inactive panic happens before pointer dereference. Panic text can misleadingly say ep0 out because ep_addr was erased; bit index is authoritative identity |
| EP1-15 reopened/started before delayed old bit is serviced | New state may be active with reused DPRAM buffer | Stale indication could act on replacement state instead of inactive panic. Requires separately evidenced ordering; not a root-cause assertion |

## Instrumentation implications and exclusions

An external continuation-entry observer can record the function pointer argument and active/ep_addr before calling real continuation, with entry/return pairing; ep_addr alone cannot recover the array index after reset zeros it. Exact registered DCD pointer entry/return markers plus continuation entry/return and panic call boundary can discriminate more than pre-handler INTS, but cannot reconstruct electrical reset acceptance priority. Do not add a workaround or change cleanup to test the hypothesis; maintain observer-only contract. E5 remains physically inapplicable on owner-established B2, E15 disabled, E16 source130MHz>48MHz mitigated. No new silicon workaround is justified by this audit.
