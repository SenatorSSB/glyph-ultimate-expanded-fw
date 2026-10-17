# One-attempt RT2 attached-identity A/B hardware packet

Prepared, NOT_EXECUTED. Diagnostic A/B only; no production-final identity choice,
confirmed root cause or canonical merge. Complete installed466 adjudication PASS
first. Use the final handoff's exact candidate/UF2 custody, not a rebuild or .pio
output. Owner performs manual firmware/device operations; source agents do none.

1. Rehash preserved UF2 with native custody pre-handoff verification. Record exact
   SHA/tree/parent/artifact hash, controller, host/cable and new evidence directory.
   Manually install that exact artifact through the ordinary storage-preserving
   procedure. No format or old whole-image restoration.
2. Normal boot without RT2/MB1; prove normal Configurator enumeration and deviceinfo,
   PULSE/STATUS, LIST, full READ1/3/4/22 and GET_CONFIG. Require useful correspondence,
   healthy generation166, unchanged incarnation and no uncertainty/fault. Record
   resources. Normal Configurator's existing2e8a:1092 assignment is unchanged.
3. Enter RT2 exactly once, with MB1 not held. Observe only the MB1 top-left menu
   LED pair. Report its settled color over a10-second bounded observation window;
   no video is required. Black display is expected. Record host USB tree and
   serial node presence/absence and identity. Recovery retains the core attached
   **2e8a:000a** identity; do not filter only for1092 or require usbmodem101.
4. Color interpretation: red=pre-SendReport return; yellow=phase11 or later with
   no connected/configured observation; blue=SETUP/connected but not configured
   (not address proof); green=configured; white=configured and decoded a complete
   supported ProfileStore inspection request. GET_DEVICE_INFO alone need not turn
   white. Missing LED is inconclusive. Scratch3 detailed phases are secondary;
   RUN/power reset can erase them. No observation delay is added in firmware.
5. If no controller USB device/serial endpoint within10s, retain the single settled
   color and USB-tree evidence. Stop immediately in that state. No second RT2,
   retry, reset, cleanup, reflash, GC or selection to seek PASS. If USB tree shows
   device but no serial endpoint, record that narrower stage separately.
6. If endpoint exists, GET_DEVICE_INFO, PULSE/STATUS, LIST, full READ1/3/4 and HEALTH
   once each. Require complete responses, read-only recovery, initialized store,
   unchanged useful authority and valid resources. Capture startup current/previous
   markers and diagnostics version2. White is decoded-command evidence only;
   require actual responses independently.
7. Mutation refusal: valid protocol2 CREATE using retained READ1 profile, a fresh
   unused token above all prior tokens and exact current incarnation/generation,
   no fault ticket. Require IO_FAILURE/read-only with no ID/generation advance.
   Whole Config SET of the exact backed-up current Config once must return
   CMD_ERROR `Recovery state is read-only`. If accepted, stop without compensating
   cleanup/restore. Other mutation types remain source-regression tested.
8. After successful RT2 rows only, reboot once normally without RT2. Prove normal
   Configurator/deviceinfo/PULSE/STATUS/LIST/READ1/3/4/22/GET_CONFIG correspondence,
   unchanged authority, no unresolved fault and valid resources. Then stop.

Record every row PASS/FAIL/NOT_TESTED with exact identities and hashed transcripts.
An RT2 success supports identity timing causality but does not automatically
approve retaining bootstrap identity for production; a clean pre-attach design
or production identity policy is a separate decision. No macOS rejection policy
or final root cause is inferred from host tests. An A/B failure preserves the
current downstream USB boundary for further narrow investigation. Nunchuk,
selection/automatic recovery and broad B1–B8 hardware acceptance are not granted.
