# Exact display hardware packet — owner approval required

**GLYPH-DISPLAY-9E69188D-HW-v1 — FINAL PROPOSAL / UNAPPROVED / UNEXECUTED.**
The exact approval objects are `packet.json` and `PREPARATION_MANIFEST.json`;
their SHA-256 values are in `HANDOFF.json`. This document supplies the operator
sequence. No physical authority exists until the owner approves those exact hashes,
built source and retained UF2. Approval does not mean execution has occurred.

## Frozen candidate and custody

- Built source: `9e69188d857138a3884bcbe243f22188815e9355`.
- Source tree: `cd0d8408b1c8b808a3a41529259b57c0896e2f7c`.
- Branch: `codex/package-active-profile-display-20261112`; later evidence-only
  commits are not rebuilt firmware and do not replace the built source identity.
- UF2: **1296896 bytes**, SHA-256
  `da97bcaec0d4ebedc5aa3fee0efa76a614fc6e5bf971bc9cb82b81ca97ccf1fc`.
- Owner-held immutable locator:
  `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/9e69188d857138a3884bcbe243f22188815e9355/da97bcaec0d4ebedc5aa3fee0efa76a614fc6e5bf971bc9cb82b81ca97ccf1fc/firmware.uf2`.
- All ELF/BIN/map identities and locators: `packet.json`. No rebuild or substitution.
- Resource handoff: ../resource/REPORT.md. Affected renderer948; label path292;
  qualified existing core1 composition1060 within actual reservation2048.
  Timing/highwater remain unmeasured. New display hardware remains NOT_TESTED.

Verify custody immediately before an approved installation, using the original
Glyph checkout's existing **read-only** verifier (never its mutable build output):

```sh
python3 tools/glyph_hardware_artifact_custody.py --pre-handoff-verify \
  --candidate-sha 9e69188d857138a3884bcbe243f22188815e9355 \
  --artifact-sha256 da97bcaec0d4ebedc5aa3fee0efa76a614fc6e5bf971bc9cb82b81ca97ccf1fc
```

A missing, symlinked, nonregular, wrong-size or wrong-hash artifact stops before
installation. A new build is not a remedy. Preparation verified retained bytes;
this command must still be repeated at actual handoff, since custody can change.

## Fixed target and reachable observation

One owner-held Glyph Mk6, private identity record and serial digest bound in
`packet.json`/`BASELINE_BINDING.json`. The raw serial stays private. Fresh exact
USB serial correspondence and unique physical unit/port are mandatory. No stale
port or historical USB observation is reused. Configurator admits VID2e8a with
known PID000a or1092 plus normal Runtime Identity status2/backend8; recovery3,
wrong runtime or multiple units stops. Candidate XInput source declares0738:4726;
fresh USB correspondence and backend2 identity must agree, otherwise stop rather
than guess another route. Neither PID nor runtime identity attests firmware SHA.
BOOTSEL volume selection relies on continuous owner physical custody and one newly
appearing RPI-RP2 volume from that unit, not a stale mount path or a probe write.

The sealed Phase-B after-Config supplies a concrete route that needs **no profile
selection or reference rewrite**: saved USB backend1 = XInput; its saved mode3
(one-based) is existing legacy native record53 / revision1 / name **KazTest5**, row2
(zero-based). Its row plate is unspecified, so expected dashboard is:

| Position | Expected literal text |
| --- | --- |
| Name | KazTest5 |
| Plate | Unknown Plate |
| Backend | XInput |
| Input Viewer name | KazTest5 |

`BASELINE_BINDING.json` was derived only from sealed originals and is not a fresh
device observation. Every bound baseline must pass freshly before any install.
If saved defaults, record53, plate or directory differ, this packet stops; it does
not authorize selecting a replacement, fixing Config or assuming prior state.

The managed record54 / Kazuya Managed has known Plat Fighter plate, but ordinary
managed selection remains blocked. Its execution/display case is **HOST ONLY**.
Do not enter Profile selection, select it, relax guards or rewrite a reference.
Physical known-plate variants, other native profiles/backends and nonnative modes
remain NOT_TESTED here. Retained host tests cover their labels/fallbacks; no physical
PASS is inferred. Existing gameplay acceptance is not retested or enlarged.

## Exact future operation sequence

These stages are a manual owner-present proposal using existing pinned protocol
primitives, not a new live executor. The full allowlist, source hashes, deadlines,
transport settings and terminal rules are in `packet.json`. Before any future
execution, the operator must be able to capture and enforce that exact table;
never substitute the accepted CREATE executor or a CLI that emits implicit STATUS.
`glyph_profile_store_production_tool.py` adds protocol2 STATUS and therefore is
**not** a direct implementation of this table. No silent extra requests are allowed.

1. **A — Fresh before snapshot on installed c439.** Owner uses the established
   heldRT2 startup Configurator binding, with no Profile/USB menu destination
   selection. One exclusive CDC session: command10 identity once; command9 /
   protocol3 PACKAGE_STATUS1 once; command3 GET_CONFIG once; command9 / protocol2
   LIST2 four pages of8 (27 total entries); READ3 once for each of those27 actual
   IDs. Total34 exchanges. No protocol2 STATUS, QUERY or capacity request.
   Require Config SHA913e9db4e3809b36f101ede84b6019c7fa60c3d52e3c94e97254ae95d82e8d42,
   ordered directory hash and all status facts from BASELINE_BINDING. Native53
   must match wrapper72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87.
   Seal all27 raw standalone profile wrappers, full metadata and Config bytes in
   new private append-only host custody. Close port only after settled PASS.
2. **B — One exact manual installation.** Owner reconfirms exact source/UF2 and
   fresh custody result after A, enters BOOTSEL once and copies only the retained
   exact UF2 once to the freshly matched volume. Record the manual result and
   re-enumeration. No automated updater, reboot command, rollback or second copy.
   A lost acknowledgement or unclear result ends the episode UNKNOWN.
3. **C — Existing default XInput display.** Normal no-buttons USB boot; no startup
   destination chord. One existing identity-only request, 10-second host deadline.
   Require persisted/status0, backend2, context row3, ref53, active53/rev1/schema5
   and domain-separated digest matching fresh A READ53. Observe the table above.
   Navigate only top-level Input.Viewer, Back to the top-level menu, then Back
   to dashboard; confirm return dashboard
   and responsiveness. Record literal text/photo or explicitly attributed owner
   observation. No Profile/USB/RGB/default/settings action and no gameplay.
4. **D — Fresh preservation snapshot.** One planned heldRT2 Configurator startup,
   repeat exactly A's34 requests in one new exclusive session. Every raw Config
   byte, all27 directory entries/order and all27 raw standalone profile wrappers
   must match A. Compare inc/generation/CRC/highwater and supported unfenced state.
   Preserve managed54 without activation. Close only after settled PASS.
5. **E — Settle on unchanged normal default.** One planned normal no-buttons XInput
   boot, one identity request and final dashboard observation, same53/defaults.
   Close ownership and record all settlement/cancellation errors, then stop.

Maximums: **70 exchanges, two Configurator sessions, two XInput identity sessions,
one manual install/BOOTSEL entry**, zero mutations/reference rewrites/default
changes/managed activation/automatic retries/reconnects. Planned stage changes are
conditional on the preceding stage's complete settled PASS, not error recovery.
Fresh nonzero uint64 correlation tokens and the actual port paths are execution-time
facts; they do not change the packet. Never use a mutation token or QUERY to infer
an uncertain operation. Identity10s and each other request30s are finite host limits,
not firmware liveness guarantees. DTRtrue/RTSfalse before115200/8N1/no-flow open;
no1200-baud touch or reset. Retain exact TX/RX/COBS bytes and fsync each host request
intent before sending. Do not silently skip unknown/empty/malformed frames.

This proposal deliberately requires no executable CREATE runner or new transport
implementation. Runtime Identity and direct schema/framing primitives already
exist; only the exact permitted requests above may be issued. Operator capture
inability stops before any request, rather than broadening tooling or scope.

## Preservation, uncertainty and result

Raw READ wrapper bytes are the response's ProfileStoreResponse field9 submessage,
not lossy JSON and not merely a reserialization. Validate schema/native header with
pinned validators. The runtime identity digest is SHA256(domain UTF8
`Glyph.RuntimeIdentity.UltimateProfile.v1`, then one NUL byte, then that wrapper).
Compare post-snapshot wrappers byte-for-byte with the fresh before snapshot, plus
all metadata and raw Config, not only record count or requested reference.

All fields/defaults/backend destinations/RGB/references/managed markers must remain
exact. Readback does not export raw managed-record/root envelopes or prove zero
physical storage writes. The canonical parent PASS covers only its accepted CREATE/
readback/preservation episode. It does not accept this9e691 display build.

Any admission, identity, visual or preservation mismatch stops immediately. Any
request/copy timeout, cancellation, lost acknowledgement, disconnect, malformed,
duplicate or wrong-token response, ambiguous re-enumeration or cleanup error is
terminal INCONCLUSIVE/UNKNOWN with exact missing rows; no retry, reconnect to infer
success, QUERY, repair, rollback, recovery, force, profile mutation or second flash.
After ambiguous install, installed build stays UNKNOWN. Any later recovery/rollback
requires separate owner approval; this packet preapproves none.

Report exact approval/packet/source/tree/UF2/target bindings, actual request count,
raw capture custody and settlement, literal display text/backend/route, both runtime
identities, all preservation comparisons and per-row PASS/FAIL/PARTIAL/INCONCLUSIVE/
NOT_TESTED. Physical managed/known-plate/gameplay rows stay NOT_TESTED. No merge,
source repin, additional campaign, firmware repair or further access follows.
