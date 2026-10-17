# RT2 phase11 identity timing diagnosis and bounded A/B

Disposition: `MULTI_PROFILE_STORE_RT2_IDENTITY_TIMING_DIAGNOSTIC_READY`, subject
to the accompanying fresh review and final exact committed build/custody receipt.
This is a source-supported identity A/B, not a physically confirmed root cause
or a production-final recovery identity decision. Direct owner authority is the
2026-10-17 phase11 request. Frozen parent466f91ed867884640375627734d3473e9fb22c32,
tree6aab0abcfd8a8c6bddd21d96e31432cbbfd31ba7; its parent2e0a608622e8363ec7e2ef2aacc224e0810020ed.
Canonical/base remains6b73a7c507f35c111745c6bdd341618b490cbdcd. Dedicated branch
`codex/profile-store-rt2-identity-timing`; active firmware behavior, hardware
required before any merge. No source-agent controller action or canonical merge.

## Physical adjudication now established

The owner reports normal Configurator on exact466 enumerated at
`/dev/cu.usbmodem101`, generation166, with intact useful Config/profile
correspondence. One RT2 attempt then showed black display, no serial endpoint
within10seconds and no controller USB device in the host USB tree. MB1 pair:
**yellow → brief green → static yellow**, remaining static after RT2 release.

Accept `RT2_PHYSICAL_LAST_PHASE = 11`. On the exact monotonic466 implementation,
yellow phase3 followed by green phase10 and yellow phase11 is source-consistent;
phases4–9 need not have been human-visible. Phase12 blue was not observed.
This establishes completion of recovery inspection, Serial.begin, backend
allocation/construction, read-only installation, publication, loop entry and
return of the first SendReport call. These are no longer unresolved startup
boundaries for this occurrence. It does not prove continued iterations, USB
IRQ/task progress, SET_ADDRESS receipt, pull-up state or host policy.

Supported physical boundary:
`RT2_APPLICATION_RECOVERY_RUNNING_USB_NOT_MOUNTED_CONFIGURED`, with independent
`NO_CONTROLLER_USB_DEVICE_IN_HOST_USB_TREE`. Current device remains stopped in
that failed RT2 boot. Earlier2e0 root/GC V/W PASS at healthy166, actual ID22 rev132
and useful1/3/4 unchanged remain preserved. Selection is NOT_TESTED because its
fixture was not safely constructible, not FAIL. Nunchuk NOT_TESTED.

## Eight exact pinned setID answers

Authority is Arduino-Pico3.6.3 (package1.30603.0), bundled Adafruit TinyUSB2.3.0 /
TinyUSB0.16.0 and target USE_TINYUSB/tusb_config_pico.h. Source hashes, frozen ELF
disassembly and target compile DB are retained with the handoff. Installed
framework files are not edited. USB prefix below is the pinned framework's
`libraries/Adafruit_TinyUSB_Arduino/src/`.

1. `arduino/Adafruit_USBD_Device.cpp:100` assigns idVendor and idProduct only:
   descriptor bytes8–9 and10–11, little endian. Exact466 target disassembly is
   `strh r1,[r0,#8]; strh r2,[r0,#10]; bx lr`. No class/configuration byte changes.
2. `tud_descriptor_device_cb` at Device.cpp:367 returns the address of that same
   live `_desc_device` member. No descriptor snapshot/freeze is made by setID.
3. setID holds no mutex, critical section or IRQ mask; it invokes no other API.
4. RP2040 port USB-triggered software IRQ runs tud_task under __usb_mutex, while
   setID does not acquire it. IRQ descriptor service can preempt foreground
   construction. Foreground cannot resume halfway through that same IRQ's copy.
   The aligned PID halfword write is one target instruction; no torn PID-byte
   claim is needed. The target bootstrap VID already equals the desired VID.
5. setID performs no detach/attach, reset, endpoint reopening or re-enumeration.
6. **Yes, separate device requests can receive old then new identity in one
   enumeration.** `device/usbd.c:1006` obtains the live pointer for each request;
   `device/usbd_control.c:102` copies each EP0 packet into the control buffer.
   EP0 is64 bytes and the complete device descriptor is18, so an already copied
   response is stable, while a later response can contain the new PID.
7. setID has no defined address/configuration state transition in this code.
   SET_ADDRESS sets USBD addressed state and invokes DCD's address API;
   SET_CONFIGURATION parses class descriptors, opens endpoints and records the
   configuration number. Neither uses VID/PID to invalidate state. In the matrix,
   setID after address leaves address5, and after configuration leaves cfg1,
   mounted true and all three CDC endpoints. These are device-side facts, not
   assurances that any host accepts changing identity.
8. Normal startup has display/I2C, Config/store work, backend selection and
   possible default USB backend/500ms console detection before Configurator.
   RT2 takes the early inspection/constructor path. Normal may reach the identity
   change after enumeration; source provides no timing guarantee that it does.
   The physical working control and these differences make the window plausible,
   but do not prove why macOS had no controller device.

Core `main` initializes TinyUSB before setup. Device.begin clears configuration
then auto-registers CDC before tud_init/attach. RT2 Serial.begin is idempotent.
The selected target bootstrap is **2e8a:000a**, proved by compile flags; normal
Configurator sets **2e8a:1092**. The prior harness's generic Adafruit default
239a:cafe was adequate for its CDC test but is not the target identity authority;
this extension explicitly uses the target values.

## Exact enumeration timing matrix

Run `python3 tools/check_glyph_rt2_usb_startup.py --identity-matrix --output-dir NEW`.
Frozen466 and candidate each run32 cases: A–H × initial bootstrap2e8a:000a or
pre-attach Configurator2e8a:1092 control × first device request length8 or18.
The pre-attach control sets ID after configuration clearing and before attach;
it is a test control, not an implemented pre-attach production design.

Actual pinned USBD/control/event/CDC and descriptor code execute. The harness
injects the extracted actual recovery function, constructor and one recovery
loop at the named boundary. It captures every device reply, config header/full
bytes, actual USBD addressed/configuration state through read-only appended host
probes, modeled DCD address, mounted/connected state and endpoint-open calls.
No host policy rejecting mixed identity is invented.

| Injection | Frozen bootstrap, first full18 reply | State before constructor | Candidate recovery |
| --- | --- | --- | --- |
| A before any host request, before reset |1092 only|unaddressed/cfg0|000a only|
| B after bus reset, before first device GET |1092 only|unaddressed/cfg0|000a only|
| C between first and repeated device GET |000a→1092|unaddressed/cfg0|000a only|
| D after SET_ADDRESS |000a→1092|addressed/cfg0|000a only|
| E before config request |000a→1092|addressed/cfg0|000a only|
| F after full config request |000a→1092|addressed/cfg0|000a only|
| G before SET_CONFIGURATION |000a→1092|addressed/cfg0|000a only|
| H after SET_CONFIGURATION |000a→1092|addressed/cfg1|000a only|

An8-byte first reply contains no VID/PID: C then has no *observed* mixed identity;
D–H still do because the repeated full reply precedes construction. Frozen has
11 mixed cases overall; candidate has0. Pre-attach1092 controls stay1092 in both.
All64 cases configure under the permissive host model, with three CDC endpoints,
no detach and identical75-byte config SHA256
`e7b2772ab1902cb463e3d4db2006fbada600fbb1c897ae2b23aa73a025fd5279`.
The test reproduces descriptor inconsistency, **not physical enumeration failure**.

The existing startup mode retains22 positive cases/two removed-auto-CDC negatives,
now with exact target VID/PID. Normal direct Configurator asserts1092 and no
recovery PIO claim. A noncandidate compile explicitly requesting the retain
policy still sets1092, proving the A/B is candidate-only. PIO resource absence,
SM exhaustion/fallback, busy FIFO and scratch namespace remain exercised.

## Narrow candidate and hypotheses

A named constructor overload accepts RetainAttachedForRecoveryDiagnostic. Only
strict-hardening candidates honor it. Only recovery passes it; the existing
five-argument normal constructor delegates to the ordinary Configurator policy.
It changes no instance members, CDC registration, transport ordering, USB attach,
backend selection, gameplay/display/core1 initialization or persistent data.
The current early recovery identity remains the core identity already attached.
Do not treat it as a final vendor identity/product compatibility decision.

Late CDC is rejected. Inspection/new/publication/first SendReport hangs are ruled
out as the primary boundary by physical phase11. Live identity timing is accepted
as a credible A/B hypothesis, not proven physical causality. Host/macOS behavior,
DCD IRQ/pull-up and further USB task progress remain unknown. No broader USB
architecture change or Astra escalation was necessary. If the A/B still fails,
retain evidence and review the next downstream DCD/IRQ boundary separately.

## Sticky MB1 observation, detailed scratch retained

Only the top-left MB1 menu LED pair signals state; LF4 is dark. No video and no
phase sleeps. The existing four-word PIO frame/200us wire-and-latch interval and
changed-marker emission cadence are retained, including repeated red frames
for early phases. This avoids adding observation delays or intentionally
removing the old phase-frame timing. It is still diagnostic instrumentation,
not proof of an unchanged electrical/IRQ schedule.

- RED: application has not yet returned from SendReport (phase<11).
- YELLOW: phase11 or later, no configured/connected observation.
- BLUE: USB SETUP/connected observed, not configured. **Not address proof.**
- GREEN: mounted/configured, no valid inspection request decoded yet.
- WHITE: currently mounted and a complete protocol1/2 supported inspection
  request has decoded (PULSE/STATUS/LIST/READ/HEALTH). First byte, unknown command
  or malformed frame is insufficient. It does not prove response delivery or
  successful profile validation. GET_DEVICE_INFO alone does not select white.

Detailed monotonic phases and USB flags remain in namespace-safe scratch3;
selectors0..2 and SDK4..7 remain unchanged. RUN/power reset retention is not
promised. Scratch phase13 still means a first command byte was seen. Response
startup diagnostics version2 identifies this coarse LED contract; no schema or
persistent format is changed. Busy/unavailable PIO fails gracefully; absent LED
is inconclusive, not proof of non-entry. State is sampled at Mark calls, not an
independent hardware/IRQ monitor. A displayed color is the last sampled state.

The real-stack matrix checks red early frames, yellow/blue/green after phase11,
unknown-command non-white and white after decoded inspection; the other pair
remains dark. It also checks full inspection/refusals and unchanged modeled
files/generation. Accepted RX/TX coordination, framing, deadlines, fault controls,
ProfileStore, checked persistence and selection implementation remain untouched.

Target resource deltas, emitted frames/ABI and final immutable UF2 are in the
exact committed handoff. Host DCD/IRQ/electrical/PIO/Config I/O and macOS node
creation remain models; target XInput app-driver/BOS/vendor overrides remain
omitted as explicitly documented in the prior pin audit. No whole-target
SDK/ROM/IRQ stack bound, live heap proof or hardware acceptance is claimed.

Next: [installed466 read-only adjudication](profile_store_rt2_identity_timing_device_adjudication.md),
then [one-attempt A/B packet](profile_store_rt2_identity_timing_hardware_packet.md).
No GC, selection, cleanup, second RT2 attempt or canonical merge.
