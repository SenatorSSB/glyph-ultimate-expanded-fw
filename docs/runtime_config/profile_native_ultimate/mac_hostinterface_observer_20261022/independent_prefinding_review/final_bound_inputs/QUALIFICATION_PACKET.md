# GP_NATIVE_001_MAC_HOSTINTERFACE_QUALIFY_V1 — approval required

Installed F334f and its UF2 remain unchanged. The approved preservation check
matched Config252 API bytes and all22 original profile wrappers/revisions exactly,
then stopped in Configurator. Earlier raw-reader/metadata failures remain exact.
This packet requests a **new bounded Mac report-access qualification** using a
separately built SDK-supported IOUSBHostInterface reader. It is a materially
different, source-supported API path; it does not retry or modify the old reader.
[Machine bounds](QUALIFICATION_PACKET.json) and exact artifact hashes are part of
this packet. The host flag/session label is a guard, not owner approval.

## Allowed sequence, each operation once

1. With controls released, the owner uses one familiar ordinary USB disconnect/
   reconnect, returning from current Configurator to the preserved default USB
   XInput backend. Confirm the normal controller display. No BOOTSEL, startup/
   backend/recovery chord,1200-baud or host reset command. Unfamiliar procedure,
   entry failure or unexpected mode stops before access.
2. One standard CDC metadata lookup must uniquely match0738/4726 and the original
   private serial/location0-1, with no port opened during lookup. One unchanged F
   identity request uses a fresh token/current boot label and must match persisted/
   backend2/row3/reference4/incarnation1/active4/revision1/schema3/digestd128…b384,
   exactly as the full JSON. This is current original legacy-profile correspondence,
   not native engine acceptance or cryptographic program/Git attestation.
3. Invoke the exact new native binary once in **inspect** mode. One fixed
   IOUSBHostDevice query and at most32 descendants/depth3 identify one exact
   IOUSBHostInterface number0/FF5D1/alt0/config1 under the unique0738/4726/location
   0x100000 anchor. Record only whitelisted numeric registry properties/IDs and
   bounded structure. No serial/product strings, general dump, plug-in/interface
   init, descriptors, pipe, read or cancellation in this branch. Require the
   complete successful inspect_end and fresh IDs. Old IDs from before the mode
   restart are never reused; location/VID/PID/ancestry are tied to the separately
   verified private unit and are valid only for this boot/connection.
4. If every preceding result passes, invoke **capture** once with those explicit
   fresh IDs and the same session. It repeats bounded identity/ancestry checks;
   changed/missing/multiple/unknown identity or topology stops without choosing
   another interface. There is no automatic capture or fallback after inspect.

## Exact new host access requested

Use retained binary SHA256
`ee26c84cb19eb40017329297732ee504774211941aa5067620cd6a5fb4b5e1a7`
(sourcef525991c…/technical HOLD b6d3003d…), normal real/effective UID502 and the
previously used same-user sandbox-exempt context. Reserve new private counters,
command/source/binary hashes and exclusive journal/stdout/stderr files before
launch; external timeout10seconds for each native invocation. All artifact bytes
are rehashed; no rebuild substitution, privilege or driver/OS-settings workaround.

The SDK-supported init uses **optionsNone** on only the verified vendor interface.
It establishes ordinary exclusive interface ownership and may refuse if already
owned. It is an open-equivalent action. No DeviceCapture/DeviceSeize, driver detach/
install, generic USB device open or permission workaround is permitted.

Permit one associated interface-descriptor getter and one associated configuration-
descriptor getter (at most4096 bytes), validating all lengths, configuration1,
exact interface/alternate and exactly one interrupt-IN32/interval1 plus one OUT32/
interval8. Derive the actual IN address; firmware templates are auto-remapped and
0x81 is not assumed. Permit only that one IN pipe and verify its owner/address and
original/current descriptor bytes. The OUT pipe is never opened.

**Descriptor limitation:** these are associated read-only SDK properties. Their
headers do not establish electrical absence of framework-internal USB traffic.
This request explicitly includes those properties with that limitation; no generic
fetch/device/string descriptor API or application-issued control/configuration/
alternate-setting/clear-stall/reset request is allowed. Unavailable/malformed
associated data stops without a fetch fallback. Ordinary SDK cancellation and
destruction likewise have no proven zero-internal-traffic guarantee.

Permit at most three asynchronous interrupt-IN submissions with one fixed32-byte
buffer and at most one pending read. The SDK requires completionTimeout0 for an
interrupt pipe; an independent deadline bounds observation to5seconds from state
creation, with at most three successful actual20-byte reports. Preserve actual
status/count/raw bytes before the frozen full-field decoder; zero/short/oversize/
error/unexpected-header reports cannot qualify. Host timestamps are receipt times,
not target native frame/activation timing or stack measurements.

At a deadline/failure while pending, permit at most one asynchronous abort and a
one-second drain grace. SDK headers promise no finite abort/destroy return. The
entire pending State/buffer/pipe/interface/queue/journal stays alive until process
exit on uncertain drain; no active callback storage is freed. Settled cleanup is
queued after callback return and destroys the interface once. The independent
process watchdog exits at8seconds; the caller's external limit is10seconds. A
watchdog, partial journal, unsettled cancellation or cleanup uncertainty is STOP,
not a successful capture or permission to retry.

## Stop and retained boundaries

Any refusal, ambiguity, unexpected/partial/error result, identity/fence/session
mismatch, invalid registry iterator/topology, descriptor/pipe uncertainty, read/
parse error, timeout or uncertain completion stops all further actions. No retry,
new discovery, alternative route, recovery or old-reader/probe invocation follows.
Capture succeeds only with its complete custody end record and three valid raw
reports; even that qualifies only this host route on the existing legacy profile.

After selected access, preserve facts and **STOP**. No firmware copy, Config or
ProfileStore request/write, native record/reference/activation, target metrics,
Switch/WUP action, route adapter or H1–H12 physical campaign is included. F/source/
build/resource/identity16/72/protocol/oracles/limits remain unchanged and unmerged.
All18 behavior families, missing backend fields, exact human HEP, tested-source
integration and strict DONE remain gated. Target timing/highwater NOT_MEASURED,
Nunchuk NOT_TESTED, RT2 DEFERRED/UNRESOLVED and root cause UNPROVEN stay qualified.
