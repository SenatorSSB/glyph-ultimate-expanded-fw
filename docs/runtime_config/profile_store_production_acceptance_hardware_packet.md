# Production ProfileStore acceptance packet (prepared; do not execute automatically)

## Exact identities

- Firmware candidate: `af69dd91e629db852f1d2371e8d8c2d6b624fc54`, tree
  `5c3ae998b94e444f7ab890ac51fcce8492944ceb`, parent/base
  `6b73a7c507f35c111745c6bdd341618b490cbdcd`.
- Preserved firmware: `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/af69dd91e629db852f1d2371e8d8c2d6b624fc54/5813756392a669b952982af9468ab3dbb34440bb98e3103ff76fd7faff743c35/firmware.uf2`, 970752 bytes, SHA-256 `5813756392a669b952982af9468ab3dbb34440bb98e3103ff76fd7faff743c35`.
- Host operator is the separately published `codex/profile-store-production-acceptance-tools` commit recorded in its manifest.  It is not firmware identity or artifact attestation.

## Terminal-Codex prompt

```text
Perform exactly this bounded normal ProfileStore acceptance packet.  Do not run
it until the owner explicitly authorizes hardware execution.  Do not attempt
RT2, QUERY, replay, fault controls, reset/recovery, cleanup, a whole-Config
write, or a retry after any failure.

FIRST: adjudicate the controller currently installed, before copying any UF2.
Use only ordinary normal boot and read-only STATUS/LIST/READ.  Record all raw
TX/RX and host-only journals.  Stop at the first unavailable or mismatched fact.
The installed firmware identity is unknown: do not assume it equals the newest
Git branch.  Use its About/device response only as corroboration, never as a
cryptographic artifact claim.

Read-only baseline expected from established witnesses:
store incarnation=1, generation=166, token high-water=0xf000000000001d00;
live IDs 1,3..22 (ID2 absent); ID1 revision=2, IDs3/4 revision=1, ID22
revision=132.  Config generation=1182731055; raw Config size=252 and SHA-256
cbff16ff67c0b0301d188267255322a5abf4453f207858cc716646726dc46dd0; USB
default=1; mode 1 -> ID3 and mode 2 -> ID4.  Compare profile bodies using the
normalization and complete witnesses in
/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-tests/multi-profile-store-20261013/profile-store-transcript.jsonl.
Do not replace that normalization with an ad-hoc JSON comparison.

If and only if that gate passes, manually install exactly this preserved file
using the existing state-preserving normal update/BOOTSEL procedure:
/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/af69dd91e629db852f1d2371e8d8c2d6b624fc54/5813756392a669b952982af9468ab3dbb34440bb98e3103ff76fd7faff743c35/firmware.uf2
Verify 970752 bytes and SHA-256
5813756392a669b952982af9468ab3dbb34440bb98e3103ff76fd7faff743c35 before copy.
Ordinary UF2 installation is not a filesystem erase claim.

After normal boot, use only the host tooling's read-only commands first:
  python3 tools/glyph_profile_store_production_tool.py --port "$PORT" --journal-out status.jsonl status --output status.json
  python3 tools/glyph_profile_store_production_tool.py --port "$PORT" --journal-out list.jsonl list --page 0 --output list.json
Read every listed profile with the same tool and retain complete RX/TX.  Require
STATUS OK, protocol 2, ordinary-production (strict/fault fields default absent),
and the baseline facts above.  Stop at first mismatch.

Only under the separately explicit write authorization below, make exactly one
new unreferenced profile using a full previously verified profile JSON fixture,
32-byte name `PRODUCTION-ACCEPTANCE-0000000001`, and append rank 23.  Allocate
a fresh full uint64 token strictly above the observed high-water; pass observed
incarnation/generation exactly; preserve the tool's exclusive request receipt
and journal before sending.  Capture the CREATE-returned stable ID; never assume
the next numeric ID.  Then make exactly one UPDATE to that returned ID, using
its returned revision and a newly allocated token above the new high-water.
Perform exactly one planned ordinary reboot and read back the new profile.

Before/after compare every original profile's ID, metadata, revision and full
payload, plus original Config bytes/references.  Require only the new fixture
and associated transaction/store state changed.  Record full request/response
bytes and actual packet sizes.  A small transfer does not prove maximum-frame
or fault/stall coverage.  Leave the new profile in place.  No DELETE, cleanup,
rollback, factory erase, reference/selection change, reset, replacement UF2,
QUERY or replay is allowed after any failed/uncertain result.

RT2 remains deferred and unresolved.  Do not test RT2, uncontrolled power cut,
reserve refusal, Runtime-B, Nunchuk, or production resource peaks.
```

The CREATE/UPDATE paragraph is a future explicit bounded authorization block;
preparing this document does not execute or independently authorize it.
