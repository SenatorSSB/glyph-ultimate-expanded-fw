# Kazuya v5 deployment packet — prepared, unexecuted

Status: **HOST_VERIFIED — DEVICE_AUTHORIZATION_PENDING**. This packet grants no
device operation. It is version-specific and does not reuse ACP-20261025-01.

## Exact identities

| role | identity |
| --- | --- |
| v5 source | `profiles/kazuya/v5/KazuyaV5.profile.json`, Git blob `64c2825605082701b9252832149535c82ebb7fc5` |
| v5 wrapper | SHA-256 `72c1d401f65c1884ca5bd37f6114727a196fddd8082298c9c95dd39d4ecfae87` |
| v5 protobuf JSON | SHA-256 `54821170ddf4916f310e254c09a06f78d6ece8e8304f030761c3d03d5c6a8828` |
| v5 body | SHA-256 `30bd0b711e3973527e1d48b59af08aa5c71b6ef8f2dc5b9d932932420d9c0f6f` |
| accepted v4 rollback | ID51/KazTest4 wrapper SHA-256 `46084bbcf55646819ab0ce824b9de9ac778d3bc4d9344a8c8bcbfe5d15f6142c` |
| protected Ultimate/Pikachu | historical ID27, wrapper SHA-256 `30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b` |

The v5 compiler report binds native ABI1/schema5 preprocessing SHA-256
`3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f`.

## Required future owner authorization

The owner/Curator must authorize one bounded ProfileStore **CREATE** of a new,
separately named v5 test record. It must explicitly authorize the exact wrapper
above, its chosen name/rank, the selected physical controller, and the staged
read-only/preflight/write/readback transaction. Profile selection remains an
owner-controlled operation; this packet does not authorize selection, RENAME,
UPDATE, DELETE, firmware flashing, or host reference changes.

## Mandatory execution fences

1. Read fresh health, generation, complete record inventory, current reference,
   USB identity and transaction state. Stop if any differs from the reviewed
   device assumptions, if an unknown native record is present, or if ID27/ID51
   does not exactly match its fresh readback.
2. Make owner-held backups of raw Config and every record that could be read or
   affected. Verify restoration instructions before the transaction.
3. Recompile and hash v5 locally; compare wrapper, body, preprocessing and
   provenance to this packet. Stop on any mismatch or backend incompatibility.
4. Use the existing ProfileStore CREATE safeguard with fresh generation and
   transaction fences. Do not touch IDs 27, 51, 48, 49, 50, unknown records, or
   the active selection during stage one.
5. Read back the created record and compare ID/name/revision/rank/payload body
   and wrapper byte-for-byte. Any mismatch, timeout, generation change, health
   failure, or non-empty recovery signal stops the run.
6. Only after explicit owner selection approval may the operator select the v5
   test record and perform a bounded owner gameplay acceptance. Preserve ID51 as
   the independently selectable rollback profile until replacement acceptance is
   recorded.

## Consolidation is a separate stage

After a reviewed v5 replacement is accepted, a new owner-approved packet may
plan the desired two visible entries, Pikachu and Kazuya. It must first prove
fresh identities/reference status and a preservation/rollback strategy. It may
then consider individually fenced RENAME/DELETE operations for historical IDs
48/49/50 and any superseded v5 test record. Unknown or unrelated records remain
untouched; no rollback record is deleted first.
