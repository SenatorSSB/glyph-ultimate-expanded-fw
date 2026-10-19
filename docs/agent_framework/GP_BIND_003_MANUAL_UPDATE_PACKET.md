# GP-BIND-003 exact-candidate manual update packet

Protocol: `GP_BIND_RUNTIME_ATTESTATION_HW_V1`  
Classification: `SOURCE_FREE_MANUAL_UPDATE_PACKET`  
Status: `OWNER_AUTHORIZED_EXACT_CANDIDATE_UPDATE_PENDING`

This packet covers one exact-candidate manual update and bounded read-only
verification afterward. Direct owner authority in this thread permits reading
and writing the controller in normal, Configurator, and RPI-RP2 states. The
controller is currently in Configurator. This packet does not authorize
Config/ProfileStore writes, profile selection, reset/retry after an uncertain
operation, source edits, merge, unrelated flashing, or any acceptance claim.
It is not HEP PASS. The candidate remains unmerged.

## Frozen subject

| Field | Value |
| --- | --- |
| Work order | `GP-BIND-003` |
| Candidate Git SHA | `307d72347653c079ec8ec6e9b6ecae3c30ae536c` |
| Candidate tree | `56d9622d2e91174be1395a5234097ab6ef1739ac` |
| Canonical base | `bd548dacf453c932b1a88a0684e6e1155080a309` |
| Candidate UF2 | `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/307d72347653c079ec8ec6e9b6ecae3c30ae536c/83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b/firmware.uf2` |
| Candidate size | `979456` bytes |
| Candidate SHA-256 | `83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b` |
| Rollback F | `5994f1657e45e0883c6c75468a19be7e3b49a72c` |
| Rollback UF2 | `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/5994f1657e45e0883c6c75468a19be7e3b49a72c/e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5/firmware.uf2` |
| Rollback size | `796672` bytes |
| Rollback SHA-256 | `e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5` |

The candidate identity and custody values are fixed. Immediately before the
physical update, the daemon must independently verify that the candidate
artifact is a regular non-symlink file with the exact size and SHA-256 above.
Do not rebuild or substitute an artifact. Rollback is reserved for a separate
owner-directed response to a reported failure; this packet does not authorize
using it.

## Single physical action and update

The only human physical action in this packet is: enter the controller's
RPI-RP2 bootloader. Do not unplug/replug, press other controls, reset, or enter
another mode. After this one action, the daemon may passively inventory the
mounted bootloader volume, identify the unique target mount, and copy only the
exact candidate UF2 listed above, after rehashing and size-checking it. Do not
write any other file. Preserve the host copy, operation log, observed mount
result, and copy result. Do not include personal USB identifiers in the
record.

After the copy completes and the bootloader volume has returned/ejected as
expected, the human must physically return the controller to Configurator.
This is the sole required follow-up physical state transition. Do not make a
second attempt if the mount, copy, completion, or return is uncertain; stop
and preserve the evidence for owner review.

## Bounded read-only verification

Once Configurator is visibly restored, first capture fresh read-only
`GET_CONFIG` and ProfileStore `STATUS` using the already approved production
read paths. Compare the raw Config bytes with the preserved pre-update capture
and compare store incarnation, generation, high-water, and recovery flags with
the pre-update capture. Then capture profile status/profile inventory using
only the bounded read-only queries in
[`GP_BIND_003_HARDWARE_PROTOCOL.md`](GP_BIND_003_HARDWARE_PROTOCOL.md), if the
baseline comparisons are exact and the responses are unambiguous. Record the
actual reported firmware identity separately; do not infer it from the mount
name or successful copy.

Fresh pre-update evidence is bound here:

- Session: `/private/tmp/gp-bind-003-prep-20261019-qeMdYS`
- Owner-held verified second copy: `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/gp-bind-003-prep-20261019T121900Z`
- Capture-manifest SHA-256: `92bb28327c1da028a93222b543db014223fe9da2b2fca3845356ab08553dd399`
- Raw Config: 252 bytes; SHA-256 `54fda3988c30e03b653153ec23d0623674da3649492caa75da8aa08fbce6b460`
- ProfileStore: incarnation `1`, generation `172`, transaction-token high-water `17293822569102712070`; full 22-profile ID capture is in the manifest.

Preserve all pre/post journals and outputs in a new owner-held evidence
location. Do not overwrite the evidence session or copy. Do not issue Config or
ProfileStore mutations, select a profile, reset/retry an uncertain request, or
perform any query if the fresh GET_CONFIG or STATUS comparison is changed,
missing, malformed, or ambiguous. Stop immediately on any unexpected state.

## Stop and recovery conditions

Stop before copying if the expected bootloader volume is absent or ambiguous,
candidate custody fails rehash/size verification, or the destination cannot be
uniquely identified. Stop after copying if the operation result is uncertain,
if Configurator does not return, or if read-only verification differs from
the preserved baseline. Never retry automatically and never flash rollback
automatically. Preserve exact logs and partial evidence; request a separate
owner-directed recovery decision. Only that separate response may authorize
the verified rollback artifact above.

This packet performs no physical action and records no hardware result. A
successful update or read-only verification alone is not HEP PASS, does not
accept any hardware row, and does not permit candidate merge. Exact-snapshot
human evidence and independent HEP review remain required by the protocol.
