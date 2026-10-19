# GP-BIND-003 runtime attestation hardware protocol

Protocol: `GP_BIND_RUNTIME_ATTESTATION_HW_V1`. Status: pre-candidate requirements;
NOT EXECUTED. Contract: `GLYPH_HARDWARE_EVIDENCE_V2` in
[HARDWARE_EVIDENCE.md](HARDWARE_EVIDENCE.md). Risk: H3.

This protocol observes the current-session persisted Ultimate identity; it does
not repair or accept X1. Candidate SHA/base/tree, build path, artifact SHA-256,
size, immutable custody locator, descriptor/domain/wire version, review and
operator/context are UNASSIGNED until the actual reviewed candidate exists.
Before handoff, freeze those exact values and expected responses in a source-free
candidate-specific record. No hardware PASS exists now.

Preconditions: focused actual-source proof and affected consumers pass; fresh
independent review approves false-identity, digest and stream ownership safety;
exact committed Mk6 build/resource proof and non-symlinked content-addressed UF2
custody/readback pass; original Config/profile bytes/hashes and known-good
manual recovery route are retained. Rehash preserved firmware immediately before
any separately approved manual update. A rebuild does not substitute for custody.

The identity service itself performs zero device-state change. A capability probe
must not write, flash, reset or change profiles. A needed manual flash, mode
selection, stored update or reboot uses its concrete separately approved
preparation packet, with exact original-state preservation and recovery; this
pre-candidate protocol is not that execution packet.

| Row | Required observation and expected result |
| --- | --- |
| A1 identity/custody | Exact candidate/artifact/protocol/controller/host tuple and safe original-state backup are recorded; all hashes match. |
| A2 neutral | Current Configurator/no-Ultimate or safely available recovery context reports the correct explicit neutral status and no fabricated persistent identity. Do not induce corruption to create recovery. |
| A3 current session | In the actual primary XInput boot/session, proven active persisted Ultimate reports ID/incarnation/latched revision/schema/full payload digest. Capture separately timed Config, selected row/reference and ProfileStore readback; decoded/re-encoded correspondence uses the pinned descriptor/domain, with raw hash separate. |
| A4 noninterference | Repeated bounded requests preserve ordinary controller responses and complete viewer records/pacing, with no unexpected output, disconnect, reset, save or profile change. Record actual host observation and limits. |
| A5 activation persistence | Approved normal manual reboot/reconnect retains the correct identity when the existing production selection path activates it; requests themselves neither select nor activate. Capture new boot/session scope explicitly. |

Stored-r+1/runtime-r, invalid/missing/corrupt selection, stale ActiveId and
previous-revision cases require actual-source host proof. Physically unsafe or
unavailable recovery cases are HOST_ONLY/NOT_TESTED, never physical PASS; record
source-backed applicability and independent Curator disposition before HEP if a
required row cannot be observed safely. Do not add writes to query testing.

Stop on unexpected stored/selected/runtime disagreement, ambiguous/partial
response, incorrect digest, stream/output anomaly, uncertain write/recovery or
custody/source mismatch. Retain the exact failure and use only approved manual
recovery. Do not retry a failed artifact as accepted or merge it.

HEP independently processes human observations for this exact tuple, preserving
row results, gaps, anomalies and HOST_ONLY limits. Publish source-free R -> E -> I;
no tested-source integration before exact hardware PASS and no DONE before fresh
integration review plus strict completion correspondence. No old H1–H3 result,
old H4 session, V4 acceptance or Nunchuk test transfers to this candidate.
