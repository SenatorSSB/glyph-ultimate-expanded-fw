# Mac observer and exact-F wire erratum — pending approval

This is an offline-built proposal for this Mac (macOS27.0.1/build26A434) and the owner-reported MOD.WUP-028 adapter. No capture/inspection body has been run. None of these instructions authorizes device access. A flag named approved-session is an execution guard, not owner approval.

The controlling packet is reviewed_packet_exactF_wire_observer_draft.json, derived from independently reviewed offline packet SHA303d74950087a0b8e67ddd1a47d8c8dee0974a4525206f8e7b87070740422f92. It preserves the exact-F resource closure, H10/H11 engineering/review and required addendum. session_plan.md and session_plan_addendum.md are copied verbatim and remain mandatory. The addendum supersedes their specified stale sections. This document adds host observation and the exact-F Switch wire erratum, without changing firmware or protocol scope.

## What can be built, and what remains unverified

The installed native SDK compiles/links mac_input_observer.cpp with IOKit and CoreFoundation. No Python USB/HID module, libusb, tool installation, driver installation or target telemetry is needed for that build. This proves API/type/link feasibility only. Actual discovery, driver ownership, privileges, controller/adapter compatibility, available ports and complete report delivery on macOS27 remain UNKNOWN until separately approved preflight. An access failure is a stop, not permission to detach a driver, seize a device, elevate privileges or change OS settings.

USB XInput uses the candidate's vendor interface(classFF/subclass5D/protocol1), VID0738/PID4726, exact20-byte input report and two interrupt endpoints(max packet32). It is not a HID interface. The native reader selects one matching location/interface, opens it normally for exclusive interface access and queues bounded asynchronous interrupt-IN reads. It does not open the entire USB device, set configuration/alternate settings, seize, reset or send an XInput output/control request. Exact F initializes report_id/report_size to00/00 and transmits the20-byte struct unchanged; the parser preserves that source fact, not a generic00/14 header assumption. All transmitted simultaneous bits, triggers and four signed little-endian axes are retained.

USB Switch uses the stock IOHID raw input-report callback with a normal(nonseizing) device open, VID0f0d/PID0092, reportID0 and exact8-byte payload. The cached HID report descriptor must equal the exact86 bytes extracted from F's retained ELF. Each actual ZL/ZR/shoulder/button/hat/axis field is decoded. No HID output, feature report, GetReport polling or control request is emitted. A different/composite descriptor is refused for explicit review rather than parsed by guesswork. Mac delivery of this Switch-formatted report is not Nintendo Switch-console delivery evidence.

WUP-028 uses VID057e/PID0337, interface0/alternate0, one interrupt-IN and one interrupt-OUT endpoint, expected37-byte input packets headed21 and an explicitly selected port1..4. The source-backed adapter mapping exposes separate GC L/R/Z, buttons/Dpad and six raw adapter-reported analog bytes before Dolphin origin/application processing. This is an adapter USB report, not an electrical pre-adapter Joybus capture or proof of a transparent adapter boundary. No calibration, offset compensation, clamping or axis normalization is applied. Actual adapter transformations/connected status must be observed; mismatches stop comparison.

The adapter may need one OUT byte13 to start polling. That is an explicit proposed nonpersistent adapter operation, not read-only USB input and not a Config/ProfileStore command. It may cause the adapter to issue its normal controller polling/probe/origin traffic. It is absent unless --allow-wup-init13 is explicitly supplied under approval that specifically includes it. Only one asynchronous OUT submission is allowed; errors/timeouts/uncertainty stop with no retry. The proposal does not copy Dolphin's compatibility control request, rumble11 operation, driver detach or other output behavior. If13 alone is insufficient, stop for the concrete access/adapter decision.

## Offline build and pure checks

The exact executed commands, outputs and hashes are in build_commands.json/PINS.json. A native build uses only installed tools:

```sh
clang++ -std=c++17 -O2 -Wall -Wextra -Werror -Wno-deprecated-declarations mac_input_observer.cpp -framework IOKit -framework CoreFoundation -o mac_input_observer
clang++ -std=c++17 -O2 -Wall -Wextra -Werror parser_cli.cpp -o parser_cli
./mac_input_observer --self-test
./mac_input_observer --decode xinput 0000000000000000000000000000000000000000
```

The self-test/decode/invalid-argument branches return before creating a Capture or calling any IOKit device/registry function. parser_cli has no IOKit linkage or device APIs. build_parser_fixtures.py encodes all334×3 expected report cases and validates all1002 complete fieldsets; actual valid-domain production assignments execute with undefined/float-cast-overflow sanitizer enabled. It never executes the11 out-of-range Switch source assignments; those11 fieldsets use the sealed exact-target conversion proof.48 framing/domain/boundary cases and14 synthetic raw-capture/correspondence cases challenge length, IDs, reserved fields, signed axes, every hat, port selection, separate L/R/Z, timestamp/row/field corruption and preflight/candidate separation. These are synthetic host checks, not observations.

## Proposed bounded observation preflight, before any candidate flash/profile change

Root first obtains explicit approval for a concrete host report/backup preflight, with no host Config/ProfileStore mutation and separately specified physical entry. A restart is not a promise of byte-identical device state. It must distinguish the optional adapter13 operation from registry/input reads. Confirm the actual unit/revision/LF6–8 access, ordinary raw Configurator-entry route and safe manual recovery. Preserve original state and eligibility using the pinned existing Config/ProfileStore tools under the original session plan/addendum. This native observer never reads/writes Config, creates profiles, changes backend settings, reboots or flashes. Existing firmware can still perform its ordinary boot recovery/migration/bookkeeping; current device firmware is UNKNOWN until separately bound. Do not promise that ordinary restart/public read interfaces preserve all device bytes. If current Configurator entry is not already established, root must separately approve a known raw cold-entry route using source plus owner knowledge before any physical entry, with these current-firmware and boot limits explicit. After actual backup, validate the exact chord/eligibility conditions before proposing another cold entry.

A future approved registry-only step can identify matching target locations without opening a USB/HID user client or sending a USB request:

```sh
./mac_input_observer inspect --route xinput --approved-session '<approved-preflight>' --output '<new-xinput-registry.jsonl>'
./mac_input_observer inspect --route switch --approved-session '<approved-preflight>' --output '<new-switch-registry.jsonl>'
./mac_input_observer inspect --route wup028 --approved-session '<approved-preflight>' --output '<new-adapter-registry.jsonl>'
```

Run only the separately approved routes, not all three automatically. They restrict registry matching to the route's exact VID/PID and record location/registry ID. A registry match is not firmware/unit attestation. The owner must identify the intended physical unit and actual adapter port; ambiguous matches cannot become a capture. No observer discovery has occurred during preparation.

Only after approved matching-location selection, and only when the raw cold-start route is separately approved and verified against actual backup/chord eligibility, a finite report preflight can be proposed:

```sh
./mac_input_observer capture --route xinput --approved-session '<approved-preflight>' --purpose preflight --row PREFLIGHT --location '<actual-location>' --seconds 5 --count 3 --output '<new-xinput-preflight.jsonl>'
./mac_input_observer capture --route switch --approved-session '<approved-preflight>' --purpose preflight --row PREFLIGHT --location '<actual-location>' --seconds 5 --count 3 --output '<new-switch-preflight.jsonl>'
./mac_input_observer capture --route wup028 --approved-session '<approved-preflight>' --purpose preflight --row PREFLIGHT --location '<actual-location>' --port '<actual1..4>' --seconds 5 --count 3 --output '<new-adapter-preflight.jsonl>'
```

The WUP form above performs no adapter OUT. If the approved concrete preflight explicitly includes one polling-init13, its one designated invocation additionally includes --allow-wup-init13. A no-report result does not authorize retrying with13, a control request, a driver workaround or another route. Runtime mode/backend chords and watchdog switching are forbidden in this preflight. F backend_init.cpp has a legacy watchdog-scratch path that can update Config/defaults and call Save; do not describe that path as persistently read-only. Use only the separately approved verified raw cold-start selection after backup/actual-chord eligibility, and retain the ordinary boot bookkeeping/current-firmware limits above. No host Config/ProfileStore mutation or settings write is part of this stage. If the actual source-supported bindings cannot select USB Switch on this Mac by that bounded cold-entry route, record the restriction and stop that route's preflight.

Preflight captures describe current firmware as UNKNOWN until separately bound. Their expected wire-source label is not candidate firmware attestation and they cannot become candidate output evidence; verify_capture.py explicitly refuses purpose=preflight. Actual original Config/ordinary baseline outputs remain session-dependent, not guessed from F fixtures.

## Later exact-candidate observation and route economy

Only a separately reviewed and owner-approved exact-candidate packet permits subsequent firmware/profile/Config operations. Use the exact retained F/UF2 tuple and all original backup/reference/restoration gates. Do not substitute a rebuild or transfer previously accepted firmware evidence. Then each stable held-state capture can use purpose=candidate, its exact row ID and three reports under a new immutable output path. Hold the listed physical inputs/history, capture only after settling, retain paired OLED values where needed, and release everything before reconnect/reboot except a separately approved verified startup chord. Preserve all78 SOCD sequence steps in order; one capture per settled step must not insert extra direction releases.

```sh
./mac_input_observer capture --route '<approved-route>' --approved-session '<approved-candidate-session>' --purpose candidate --row '<exact-selection-ID>' --location '<actual-location>' --seconds 5 --count 3 --output '<new-row.jsonl>'
python3 verify_capture.py --capture '<new-row.jsonl>' --packet reviewed_packet_exactF_wire_observer_draft.json --row '<exact-selection-ID>' --route '<same-route>' --decoder ./parser_cli
```

WUP also requires the explicit actual port and its separately authorized one-init condition if applicable. The verifier reparses retained raw bytes and compares every expected field. It refuses incomplete/duplicated sessions, partial pairs, field/raw timestamp mismatch, wrong descriptor/route/source/row, malformed packets and any scaling/remapping. It reports only host-capture correspondence, never HEP PASS. Raw bytes and parsed fields share sequence and CLOCK_MONOTONIC receipt timestamp; this is host receipt time, not target evaluation/frame timing or cross-route synchronization.

A final economical route matrix should use the334 rows as the complete logical stimulus coverage, not automatically334 physical repeats on every route. A defensible draft is:

- Primary Mac XInput coverage: all selected modifier/conflict, nine-direction, SOCD, rebound, two-profile, trigger/OR and refusal rows with complete route fields, plus required native OLED140 evidence for trigger aliasing. All18 families/H1–H12 remain mapped.
- Additional raw Mac Switch coverage: all nine Default/Mode representatives and all11 corrected boundary rows, explicit ZL/ZR and direction+A/OR/forced-priority distinctions, and relevant persistence/restore controls. Any omitted duplicate must have an explicit source/coverage rationale in the final reviewed route matrix.
- Additional raw WUP coverage: all isolated L/R/Z controls/combinations, complete-profile A+L+R/OR/direction+A, both analog trigger relationships, representative sticks/Dpad and persistence/restore controls. Explicitly select the actual controller port and require wired connected status.
- Actual USB-Switch-console and GCadapter→Switch observations remain separate: original ordinary recognition/reconnect, both sticks and decisive L/R/Z/trigger/button/profile observations on the identified existing console/game screen, with exact exposed fields and limitations. Raw Mac report correspondence supplements these observations. It never makes their unperformed rows PASS or silently replaces console-route requirements.

The exact physical repetitions/console screen field mapping remain final packet decisions after actual preflight. Nothing here narrows H1–H12/all18 or invents game semantics. If actual console observations cannot distinguish a required field, retain PARTIAL/NOT_TESTED and the concrete missing decision.

OLED remains six native analog numbers plus one priority icon; A can hide L/R. XInput255 aliases digital override and analog255, so observed OLED140 plus actual255 supports only source-conditioned override evidence. Switch requires actual ZL/ZR, and WUP's distinct L/R/Z USB fields remain an adapter-boundary observation. Mac and console route acceptance do not transfer.

## Stop and release

Outputs are new exclusive0600 files with raw bytes fsynced before parsing. Sessions are bounded to1..60 seconds/1..10000 reports; proposed preflight uses5 seconds/3 reports. No new reports, malformed bytes, disconnect, unexpected identity/descriptor/endpoint, exclusive-access/permission failure or uncertain adapter output stops the operation without retry/fallback. A no-report/timeout is NOT_TESTED, never neutral or PASS.

The SDK says interrupt-pipe timeout arguments do not bound interrupt reads, so the implementation uses asynchronous transfers and a host run-loop deadline. Pending IN or adapter13 OUT is aborted only for cancellation and allowed up to1 second to drain. Settled exits unregister callbacks, remove event sources, close/release the interface/HID device and retain durable files. If cancellation does not drain, its state/buffer/interface remain alive until immediate process-exit cleanup; no retry or freed callback buffer is used. Actual asynchronous cancellation/access behavior remains unexecuted and subject to focused code review and approved preflight.

No driver detach/seize/sudo/settings change, USB SetConfiguration/SetAlternateInterface/DeviceRequest, control transfer, HID output/feature, rumble, target diagnostic addition, firmware/profile write, flash, reset, erase or RT2 work is implemented by this observer. Original identity/metrics/backup and restoration instructions remain exactly those reviewed in session_plan.md plus the mandatory addendum. Independent focused observer/erratum review and subsequent explicit owner approval remain required.

Source cold-entry qualification: HAL/pico/src/comms/backend_init.cpp and its actual backup-defined raw backend activation bindings are authoritative. This preparation does not execute a restart, infer the actual current Config, guarantee an untested entry chord, or authorize firmware-owned startup writes. All initial entry/restart operations remain separately specified owner decisions within the preflight.
