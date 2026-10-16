# Independent RT2 diagnostic candidate source review

Review date: 2026-10-16. Role: fresh independent reviewer, separate from the
implementer. Scope: the uncommitted direct-child candidate delta against
`2e0a608622e8363ec7e2ef2aacc224e0810020ed` / tree
`00c321bc0ce4de4e9c67a913c0c0f0be23375c69`, its pinned-source diagnosis,
startup checker and two prepared hardware packets. Canonical/base remains
`6b73a7c507f35c111745c6bdd341618b490cbdcd`.

Disposition: **conditional source APPROVAL for
`MULTI_PROFILE_STORE_RT2_TRANSPORT_DIAGNOSTIC_READY` only**. No proven repair,
physical enumeration PASS, canonical merge, controller operation or exact
committed artifact acceptance is granted by this review. Active firmware
behavior classification applies. The final committed SHA/tree/parent, canonical
build, resource measurements and preserved UF2 custody require the separate
final receipt.

## Independent findings and verification

I independently inspected the exact installed Arduino-Pico3.6.3 package,
Adafruit TinyUSB2.3.0/TinyUSB0.16.0 source, repository USB configuration,
normal/recovery startup paths, linked XInput callbacks and the diagnostic delta.
The core adds default CDC before tud_init/attach. The recovery Serial.begin is
idempotent. The existing physical failure is not reproduced or explained by
that source fact; the late-CDC hypothesis is rejected for this route.

Two preliminary review findings were repaired and re-reviewed: the PIO SM now
remains disabled while all four frame words are preloaded, preventing a USB IRQ
between CPU puts from splitting the LED frame; test-only literal hooks now
exercise the actual inspection and Serial boundaries instead of merely giving
identical executions different timing labels.

Independent commands:

- `python3 tools/check_glyph_rt2_usb_startup.py --output-dir /private/tmp/glyph-rt2-independent-final`:
  PASS under ASan/UBSan. Eleven successful cases per frozen/current source,
  plus the removed-auto-CDC negative oracle detected for each. Frozen2e0 is a
  positive falsification control, never a claimed negative reproduction of the
  physical failure.
- `python3 tools/check_glyph_profile_store_selection_recovery.py`: PASS,
  including actual extracted manual/automatic/filesystem/MB1 routes and retained
  old-source negatives. Its Serial/backend stubs still do not prove USB
  enumeration.
- `git diff --check`: PASS before this review document was added.

The final resource-tool delta only adds `RecoveryStartupDiagnostics.cpp` to
its existing translation-unit selection. I reviewed that one-pattern addition
and independently passed Python compilation and diff whitespace checks; it
adds frame/source-hash coverage without changing firmware or thresholds.

The new checker uses actual pinned descriptor generation, CDC implementation,
USBD/control/event and class-driver code, actual ConfiguratorBackend and
ProfileStore, and the extracted recovery route. It exercises the before/during
inspection, before/after Serial, after-publication and core-before-auto-CDC
boundaries; task progress; complete inspection responses; all new mutation and
whole Config SET refusals; and unchanged modeled persistent state. PIO resource
absence, no free SM, second-PIO fallback, busy FIFO, scratch namespace and direct
normal Configurator inactivity are covered.

DCD packets, target IRQ scheduling, electrical/PIO behavior, Config physical I/O
and macOS driver/node creation remain models. The host omits the target's XInput
app-driver/BOS/vendor overrides; their audited init/reset are no-ops and open
rejects CDC, but this is not full linked production callback closure or an
XInput composite-enumeration test. The documented 64-bit language-ID cast and
Mach-O weak-callback adaptations are visible. No installed dependency is edited.

## Diagnostic safety and packet assessment

Candidate/RP2040 guards leave production diagnostics as inline no-ops. Recovery
alone claims the established LED pin11 and a free four-instruction PIO program/
state machine. There is no new DMA, IRQ handler, heap allocation, pixel buffer,
display/core1 initializer, detach/attach or USB retry. SDK non-required claims
skip unavailable resources. Four nonblocking FIFO puts occur with only that SM
disabled; USB IRQs remain enabled. The fixed200us frame/latch interval is a
documented diagnostic perturbation, not evidence of a USB timing repair.

Scratch3 is namespace-checked, captured and cleared without touching committed
selectors0..2 or SDK4..7. The recovery route retains its original selector
clearing. Scratch retention across RUN/power reset is explicitly not promised.
LED phases and live USB flags provide observations without USB responses;
unavailable PIO, a pre-setup stall or a failed indicator can still prevent
standalone localization. Those failure boundaries are stated in the packet.
The global filesystem mount precedes setup and is outside route markers.

The diagnostic phases bracket inspection, Serial, allocation/construction,
read-only installation, publication and loop service. Phase13 means a command
byte was seen; it does not imply a complete request or response. Connected,
mounted and DTR are separate observations, not macOS endpoint acceptance.
Response fields58..60 are additive candidate diagnostics; Config/profile/disk
formats and durability logic are unchanged.

The installed2e0 packet requires one ordinary normal boot and read-only
adjudication before replacement, preserves the post-GC ledger and prohibits
cleanup/reconciliation mutations. The new packet requires exact custody,
normal transport before/after, one RT2 attempt, bounded endpoint observation,
complete read-only inspection and valid mutation/whole Config refusal probes.
Failure stops without another attempt or compensating cleanup. No GC/fault
matrix, unsafe selection fixture or broad acceptance is added.

## Required nine answers

1. **Did physical evidence prove RT2 transport unavailable? Yes.** The owner
   reported two bounded attempts with no serial endpoint. This preserves the
   root-reconciliation and GC V/W PASS at healthy generation166, ID22 rev132
   and useful IDs1/3/4 unchanged. Selection remains NOT_TESTED because its
   fixture was not safely constructible; it is not a failure.
2. **Does source prove physical RT2 route entry? No.** The predicate is known
   and host-tested; entry on those physical attempts remains an inference from
   alternate black-screen boot behavior.
3. **What exact pinned condition explains failure? Unknown.** Auto CDC precedes
   device initialization/attach and later begin is idempotent. Neither late CDC
   nor a need for re-enumeration is established. The candidate localizes stages.
4. **Why did normal Configurator work while RT2 did not? Unknown.** Real source
   differences include display/config/store/backend setup, watchdog destination,
   possible prior XInput descriptor rebuild and console-detection timing. The
   side-by-side diagnosis records them without assigning unsupported causality.
5. **Does the fix expose CDC reliably without gameplay initialization? No
   transport fix is claimed.** The frozen and diagnostic routes expose CDC and
   service the actual backend in the pinned host model without gameplay setup.
   Physical reliability remains the narrow hardware gate.
6. **Does it preserve read-only recovery policy? Yes at source/host scope.**
   Validator/checked inspection/BeginRecovery remain; recovery state is installed
   before publication/dispatch. Actual backend tests refuse new mutations and
   whole Config SET without modeled file/generation/save changes. No autoformat
   is introduced. Physical refusal evidence is still required.
7. **Does it preserve normal Configurator, TX/RX and MB1 priority? Yes at the
   reviewed source scope.** Accepted coordination/framing/deadline code is
   unchanged; normal direct Configurator remains diagnostic-inactive in the
   real-stack checker, and extracted MB1 priority passes. This is not a new
   physical regression PASS for the complete normal menu path.
8. **Does it require persistent-format changes? No.** Only response diagnostics
   are appended. No persistent Config/profile, record, root, migration, receipt
   or filesystem format changes are present.
9. **Are B1–B8 unaffected? Their persistence/selection mechanisms are preserved
   by this delta, but an unqualified aggregate claim would be false.** B1/B2/
   B4/B5/B6/B8 implementation is unchanged; B3 priority/selection is preserved.
   B7 transport is the physically blocked requirement being diagnosed, and
   B7 diagnostic behavior changes. No new B1–B8 hardware PASS is granted.

No material source-review blocker remains for this bounded diagnostic handoff.
Final exact build/custody review and installed2e0 adjudication precede the
prepared manual hardware campaign. Nunchuk remains NOT_TESTED; root cause
remains UNPROVEN; no canonical merge is authorized.

Finalization review before the replacement commit: the first PIO instruction
now has an explicit uint16_t cast, preserving its source-audited opcode0x6021
while eliminating the target narrowing warning. The hardware packet's whole
Config refusal text is corrected to `Recovery state is read-only`, matching
HandleSetConfig. Both bounded changes were independently inspected and preserve
this source approval. Superseded candidate607ce458/artifacts are not the final
handoff; the corrected commit requires its own exact build/custody receipt.
