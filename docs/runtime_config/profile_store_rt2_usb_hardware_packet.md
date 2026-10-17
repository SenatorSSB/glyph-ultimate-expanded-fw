# Narrow RT2 diagnostic hardware packet

Prepared, NOT_EXECUTED. Owner performs manual actions only after installed2e0
read-only adjudication PASS. Exact new SHA/tree/parent/UF2 hash and read-only
custody locator must come from the final handoff receipt, not mutable .pio
output or a rebuild. No canonical merge. No GC/fault-matrix repeat or cleanup.
The original no-endpoint RT2 row remains FAIL until actual transport succeeds;
this artifact is diagnostic, not an established repair.

1. Rehash exact preserved UF2 using the custody pre-handoff verifier. Record
   identity, controller, cable/host and bounded evidence directory. Manually
   install that exact UF2 through the ordinary owner procedure, preserving
   storage; no format or whole-image restoration.
2. Ordinary boot without RT2/MB1; normal Configurator must enumerate and answer
   device info, PULSE/STATUS, LIST, full READ1/3/4 and GET_CONFIG. Compare installed2e0
   adjudication, incarnation/generation and useful payloads. No unexplained
   Config/persistence change permitted. Record stack/heap/resource diagnostics.
3. Enter manual RT2 exactly once, without MB1, using the known held-button
   stimulus. Start video of MB1 and LF4 LED pairs before the boot stimulus;
   retain colors/stationary phase and any transitions. Black display is expected.
   Wait at most10 seconds for a serial endpoint; record USB device identity,
   endpoint appearance or absence, host USB tree and elapsed time. This10s is
   an operator observation window, not firmware retry/delay behavior.
4. If endpoint absent, record `MANUAL_RT2_RECOVERY_TRANSPORT_UNAVAILABLE`, last
   LED phase and LF4 connected/configured colors using the diagnosis table.
   Stop without reset/second RT2 attempt/cleanup/reflash. No LEDs cannot prove
   non-entry: PIO unavailability, a pre-setup stall or indicator failure remain
   possible. Scratch is optional SWD/warm-reset evidence only; RUN/power reset
   can erase it. Do not perform another reset just to seek scratch evidence.
5. If endpoint exists, open it normally and send device info, PULSE/STATUS,
   LIST, full READ1/3/4, and HEALTH once each. Require read-only recovery flag,
   initialized store inspection, unchanged authority and valid resources.
   Capture current/previous startup marker and diagnostics version1. Init/CDC/
   descriptor/pull-up/connected/configured/DTR flags are separate observations;
   phase13 proves first command byte only, so require every complete response.
6. Refusal gate: use the retained valid full profile from READ1 in a protocol2
   CREATE with a fresh unused token greater than all previously used tokens and
   exact current incarnation/generation. Do not arm a fault. Require
   PROFILE_STORE_IO_FAILURE/read-only with no new ID/generation. Send the exact
   backed-up current Config through whole Config SET once; require CMD_ERROR
   (`Recovery state is read-only`). If either is accepted, stop immediately;
   do not attempt compensating deletion/restore. Further mutation types are
   source-regression tested; no multi-operation physical fault matrix is needed.
7. After successful recovery rows only, manually exit/reboot once to ordinary
   normal boot without RT2. Normal Configurator must enumerate and answer
   deviceinfo/PULSE/STATUS/LIST/READ1/3/4/GET_CONFIG. Compare useful bytes,
   generation/incarnation and Config to baseline; require no pending/armed
   fault or unresolved transaction. Prior scratch marker may be0 after RUN reset.
8. Stop. Record each row PASS/FAIL/NOT_TESTED, exact artifact and hashes of all
   transcripts/video. Nunchuk/selection/automatic entry remain NOT_TESTED unless
   separately observed. No persistence, GC, selection, runtime-output or broad
   B1–B8 hardware acceptance is inherited by this new snapshot.

Stop immediately for transport timeout/loss, reset/hang, impossible LED phase,
invalid stack margin, heap at capacity, storage error, useful-state change,
unknown authority or unexpected mutation acceptance. Preserve device/evidence;
no repeated attempt to obtain PASS. B7 transport remains blocking until reviewed
physical results on this exact SHA/UF2 establish the required headless service.
