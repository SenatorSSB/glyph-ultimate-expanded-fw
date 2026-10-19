# GP-BIND-003 hardware protocol

Protocol version: `GP_BIND_RUNTIME_ATTESTATION_HW_V1`

Status: `HARDWARE_TEST_REQUIRED`. No physical observation has been recorded.
The exact candidate build and artifact custody are ready; no device update or
other device action is authorized by this handoff. The query order is read-only.
Any physical action, including a firmware update, requires its separately
approved concrete preparation packet and safe manual recovery route.

## Exact candidate handoff

- Candidate branch: `codex/gp-bind-003-runtime-attestation`
- Candidate Git SHA: `307d72347653c079ec8ec6e9b6ecae3c30ae536c`
- Candidate tree: `56d9622d2e91174be1395a5234097ab6ef1739ac`
- Canonical implementation base: `bd548dacf453c932b1a88a0684e6e1155080a309`
- Direct parent: `9482219ffd575f63cf3c863d465afa134cbf0d28`; the candidate is a
  descendant of the recorded canonical base through the frozen wire/digest and
  current-session identity implementation commits.
- Review: amended source approval and final independent source/build/custody
  review are accepted for this exact candidate. This does not establish
  controller acceptance.
- Build: `PASS`, canonical command `pio run -e glyph_mk6`, from a clean
  tracked checkout at `/private/tmp/gp-bind-003-build-307d7234`, exact F SHA
  above. Reported RAM: `187344 / 262144` bytes; flash:
  `477452 / 1568768` bytes.
- UF2: `979456` bytes; SHA-256
  `83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b`.
- Preserved custody, absolute path:
  `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/307d72347653c079ec8ec6e9b6ecae3c30ae536c/83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b/firmware.uf2`
- Build log SHA-256:
  `08d3b92e2ed8b6afbeef690979b70c3b6c7e2fdb8de5fee2b2aeb16924d9a3f0`.
- Focused runtime identity host proof log SHA-256:
  `60df325fcd1ccb95aa5b6929794645b7c37ca1d4f690ed5e7e7b4955153a4b1d`.
- The exact target generated Nanopb files used by the final review are pinned:
  `config.pb.c` SHA-256
  `fce08045cd7da7795357dff85827a634ef6a7f3fb21ec32e89b0e84817c54750` and
  `config.pb.h` SHA-256
  `c2a289d304a74c2a875d3fb2413a9afc0880f758cb1f5d7781c450b7841f51a0`.
  Target Nanopb dependency pins are `.pio/libdeps/glyph_mk6/Nanopb/pb.h`
  SHA-256 `e0db84a27e0d41a2d2d347b8c879e30ceb856d36dc192cce0f1124f833c67bc2`
  and `pb_encode.c` SHA-256
  `debb0714dff8d1515b9724eae45531cad912f12028a0311fc3e2c694689e1fed`.
  The target build resolved `nanopb-arduino` v1.1.1 and the generated header
  identifies Nanopb 0.4.9.2. The exact `config.proto` and `config.options`
  inputs used by the focused proof are pinned to SHA-256
  `81b0aad7568728ac465981b42c738154af8250e16426734d269e0abe7b9d3f49` and
  `612d23b268742d0cc8e4b871d33b3ccba7c6f912ca3352364e329b3fef0096c0`.
  These exact target pins supersede older host-validation generated-file pins.
- Static resource prologue facts retained from the focused proof: service
  object `24` bytes, snapshot `56` bytes, encoded-profile bound `5740` bytes;
  the exercised production schema set is finite at versions 1 through 3.
  Build static RAM/flash are the figures above. These are bounded build/host
  facts. Target query timing and peak stack use are `NOT_MEASURED`; no target
  timing or peak-stack claim is made.

## Capability and current gate

The recorded controller capability is `PARTIAL`: repository/tool access is
available, but no matching serial/filtered USB device is presently available.
This is not a device test and says nothing about unprobed device capability.
Do not probe through a write, reset, flash, reconnect-at-1200, or other
state-changing operation. The hardware evidence result remains null and every
physical row remains `NOT_TESTED`.

The candidate remains unmerged. No flash, Config write, selection, profile
update, reboot, recovery action, or merge occurred. H3 acceptance requires an
exact human report and independent Hardware Evidence Processor (`HEP`) PASS
for this full candidate SHA and exact artifact SHA-256, with no required gaps.

## Required physical evidence after separate preparation approval

Before any physical action, the owner must have the separately approved
candidate-specific preparation packet, safe manual recovery route, preserved
original Config/profile bytes and hashes, and the applicable known-good
rollback custody. Rehash this exact candidate artifact and rollback immediately
before any separately authorized manual update. Stop if custody, identity, or
recovery differs. Give one dependent action at a time and wait for the report.

The eventual HEP packet must separately record:

| Required observation | Acceptance evidence |
| --- | --- |
| Configurator neutral/recovery behavior | Dedicated identity query returns the documented neutral/unavailable status when persisted evaluation correspondence is not proven; malformed or unsupported requests do not mutate state. |
| Current primary XInput session | In the same boot/session, reported backend and actual Ultimate object correspondence, store incarnation, active ID, latched revision, schema, and payload digest agree with the evaluated persisted object. |
| Repeated query and ordinary controls | Repeated bounded queries leave ordinary controls and complete 25-byte viewer records/pacing intact; no stuck or altered output. |
| Manual reboot/reconnect | After the separately approved manual setup, the expected identity is observed in the new primary session and ordinary controls/viewer traffic remain intact. |
| Config and recovery retention | Record exact pre/post raw Config identity where safely available and confirm no query changed persisted state; report recovery/rollback state. |

For every row capture tester/date, controller, backend, host/adapter, profile
context, exact expected and actual observations, result, anomalies, and the
exact F/artifact identity. Unsafe or unavailable cases remain `NOT_TESTED` or
host-only; they do not become physical PASS. Do not infer a prior H4 runtime
identity from Configurator, stored IDs, or historical evidence.

GP-BIND-001/002 failures and their diagnostic remain immutable. Historical H4
runtime identity and X1 root cause remain `UNKNOWN`/`UNPROVEN`; Nunchuk remains
`NOT_TESTED`. The exact candidate and this protocol stay frozen through the
hardware gate. No source integration or strict DONE follows without exact
human HEP PASS and the separate reviewed source-free `R -> E -> I` lifecycle.
