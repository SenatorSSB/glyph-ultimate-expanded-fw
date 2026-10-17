# Fresh independent RT2 DCD observer source review

Reviewer: fresh_dcd_review (independent review-only agent); 2026-10-17.
Scope: candidate worktree `/private/tmp/glyph-profile-store-rt2-dcd-diagnostics`,
base/parent frozen466 `466f91ed867884640375627734d3473e9fb22c32`.
Authority: direct latest owner attachment7ecf108b (read in full). No controller,
Git, source, or installed framework mutation performed by reviewer.

## Precommit source disposition

Source, completed host validation, and hardware packet APPROVED. No unresolved
blocking finding. One diagnostic edge defect discovered independently was
corrected and re-reviewed below. This source approval does not approve an
artifact that has not yet been frozen. Hardware remains NOT_TESTED and root cause UNPROVEN.

## Independently inspected behavior

- `RecoveryUsbDiagnostics.cpp:78-82`: existing optional TinyUSB event hook
  records monotonic bool receipts only. Pinned `usbd.c:302-305` invokes it after
  queue-send attempt, so reset/SETUP flags prove DCD event publication attempt,
  not successful queue acceptance or later task processing.
- `RecoveryUsbDiagnostics.cpp:84-124`: six wrappers each call the real pinned
  entry with unchanged arguments and preserve its return. Their added work is
  scalar observation, not packet/control/identity mutation, delay, task call,
  MMIO write, or LED emission. The status hook distinguishes address request
  from application of the RP2040 address after its status transaction.
- `RecoveryUsbDiagnostics.cpp:39-71`: raw registers are reads only. Current
  NVIC/PRIMASK/stack/configuration observations are distinct from sticky receipt
  flags. Progress is gated on repeated recovery-loop entry and monotonic.
  Yellow means a sampled post-repeat pull-up ON at least once; it cannot prove
  the pull-up remains currently ON after a later disconnect. Raw SIE/flag
  observations are the current-state discriminator when transport exists.
  Snapshot fields are independently sampled with IRQs live; inconsistent task
  entry/return counts in one snapshot alone do not prove a blocked task.
- `RecoveryStartupDiagnostics.cpp:54-70,95-108`: MB1 pair receives the same
  GRB value, LF4 is dark; the one successful frame records shown_state.
  Unchanged state skips Show even when counters/raw USB flags change. Busy FIFO
  can defer a frame; retry is allowed until successful. The 200us existing
  protocol interval has IRQs enabled and is not a startup sleep. PIO exits
  each bit low and waits for FIFO data in its OUT instruction; ordinary
  clockless pixel latch behavior supports no repeated refresh. Electrical
  LED behavior and USB timing remain physical acceptance boundaries.
- Candidate gating is both the strict-candidate source guard and the Mk6-only
  extra script; linker flags cover the six exact ABI names. Noncandidate APIs
  are inline no-ops. Ordinary recovery constructor and setID1092 are unchanged
  against466; no failed5913 retain000A behavior is included.
- `ConfiguratorBackend.cpp:420-429`: white is installed after complete protobuf
  decode and protocol version validation for supported read-only inspection
  operations in recovery. Existing mutations/refusals and transport code are
  unchanged. New response fields61-70 are bounded uint32 diagnostic output;
  PersistentConfig/Profile schemas and storage semantics are unchanged.

## Pinned source adjudication

The reviewed pin is Arduino-Pico3.6.3 / Adafruit2.3.0 / TinyUSB0.16.0, SDK1.5.1.
DCD init resets USBCTRL/DPRAM, routes PHY, forces VBUS detect, registers the
hardware IRQ, sets EP0 and interrupt masks, enables controller, and connects
pull-up. DCD reset receipt does not itself set TinyUSB connected; pinned
`usbd.c:533-539` sets connected while processing SETUP in task context. Address
is applied by `dcd_edpt0_status_complete`, configuration opens CDC endpoints.
Forced VBUS makes physical unplug modelable as suspend rather than a genuine
unplug notification; subsequent reset is a separate event.

Pinned port uses try-lock task calls and a dynamically claimed software IRQ.
CoordinatedCdcStream releases its guard before both task passes and performs
bounded reads. No identity-specific idle-loop block was found. `tud_task_ext`
drains until queue empty, so a perpetual event storm is not a finite-return
proof;5913 RED is neither a proven SendReport block nor a replacement for466
phase11 physical evidence. LittleFS prog/erase disables interrupts around
core1 parking and flash work then restores them; reads use memcpy. No recovery
inspection or observer path found that resets USBCTRL/disconnects or leaves
USB IRQ disabled. This rejects unsupported source assertions, not unknown
hardware causes.

## Independently executed validation

Reviewer independently ran existing `check_glyph_rt2_usb_startup.py` to
`local_backups/dcd/reviewer-startup`: PASS, including normal Configurator
inactive diagnostics and PIO unavailable/no-SM/fallback/busy cases.
Reviewer independently reran the strengthened new harness to
`local_backups/dcd/reviewer-observer`: all13 low-level scenarios PASS under
ASan/UBSan, including hardware IRQ deferred/disabled, PRIMASK masked, software
task deferred, address requested/applied distinction, forced-VBUS suspend/reset
replug, complete read-only inspection/refusals, unchanged persistent files,
10000 idle loops and1000 white loops without refresh, actual MB1 GRB words and
LF4 dark, and negative removed-event-hook detected. This is a source/host proof;
MMIO/electrical/DPRAM completion and NVIC scheduling remain models.

Preliminary ELF independently inspected with ARM nm/objdump: all six incoming
wrapper bindings and wrapper-to-real bindings are present, including weak
status-complete hook. This is provisional; final exact committed artifact must
be independently checked because Mach-O host rename adaptation alone cannot
prove GNU linker wrapping.

## Final precommit review

Reviewed `profile_store_rt2_dcd_diagnosis.md` and
`profile_store_rt2_dcd_hardware_packet.md`. They preserve466 application phase11
and5913 A/B failure, distinguish source inference from physical evidence, retain
root cause UNPROVEN, expose current-versus-sticky and asynchronous snapshot
limits, and identify exact pinned low-level writers and callbacks. The packet
requires one normal5913 read-only adjudication before replacement; one exact
candidate normal control; one RT2 attempt and10-second operator window; stop if
no endpoint; complete service and existing read-only refusals if present; no
second attempt, video, GC, selection, cleanup, or source-agent device action.
It does not claim enumeration repair, hardware PASS, or canonical merge.

The independent review found the original configuration observer tested the
16-bit request wValue while pinned USBD uses an 8-bit cfg_num. A0x0100 request
could therefore falsely record configuration progress. Source now tests
`uint8_t(r->wValue)!=0`; the configured harness case submits0x0100 and requires
cyan, no mounted state, and no ConfigurationComplete before real configuration1.
Reviewer independently reran final checker after this correction: all13 cases,
removed-event negative, strict linker GateEnv on/off gating, and legacy/new
scratch namespace validation PASS under ASan/UBSan. No persistent or identity
behavior change is part of the correction.

Exact committed build/resource/ELF/custody approval is intentionally separate
and must bind the final candidate/tree/parent and actual UF2. The reviewed
source is a diagnostic candidate; no merge or physical PASS authorization
follows from this review.

## Reviewed source hashes


- `HAL/pico/src/core/RecoveryUsbDiagnostics.cpp`: `06750124d9cdcd6eca0ac0729830c9bb51a894e2cf29f4b8d7bfc9950c5a26e0`
- `HAL/pico/src/core/RecoveryStartupDiagnostics.cpp`: `e84d926697b3de91b077a7cb7483f771442d417aab23e4a90351c888313889dd`
- `include/core/RecoveryUsbDiagnostics.hpp`: `beb24e26cc5ac8590956e2afbf37ac29abb9b784c7b1152804b1a9d17d1ff710`
- `include/core/RecoveryStartupDiagnostics.hpp`: `ced92f34a142bb49e8fd255272b36080a94bfde79d9e7d4a3e64e7b0367d1729`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`: `296d8f44feb95c7ed711af136de3a8977c6a57524bc8b0cb239c8cc66ee8f232`
- `builder_scripts/rt2_dcd_observer.py`: `b0ff9156a6188a7ea2f21caeaa54cb8e9b750ccc142d1ac0b8369e8a8dde6955`
- `config/glyph/env.ini`: `bc595b5d2543d5c9dfdb82eb9037b111634748f951a712e8e72df246744d3a1d`
- `schema/haybox/config.proto`: `446026d70fc8a9fac75f4979a15d3869ca7570844834cfe69ab21faaa24b9a25`
- `tools/check_glyph_rt2_dcd_observer.py`: `d2f76c546bd4402a54e99a8efd967103c114cb199840239eb10fbc8f4421db8e`
- `tools/fixtures/rt2_dcd_host/cases.inc`: `ef91228f4db82020b5972d7b4c49e3a148eb98977b58f7f07545d2f084a1e11c`
- `tools/fixtures/rt2_dcd_host/model.inc`: `d0217a0c8451472e126994911bd2aab97d69ff4bf0aed3e6eb8eccb2155fec4c`
