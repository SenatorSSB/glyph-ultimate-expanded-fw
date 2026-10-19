# GP-BIND-003 post-update gap-completion packet

Protocol: `GP_BIND_RUNTIME_ATTESTATION_HW_V1`  
Classification: `SOURCE_FREE_READ_ONLY_GAP_COMPLETION`  
Status: `PENDING_INDEPENDENT_REVIEW`; this packet does not reclassify the
earlier update or its evidence.

## Purpose and chronology

The earlier GP-BIND-003 update and observations are retained as partial
evidence. They established the exact candidate/artifact tuple, current-session
XInput identity, Configurator-neutral response, byte-exact Config retention,
unchanged ProfileStore STATUS, viewer traffic, and one ordinary reconnect.
They did not freeze a candidate-specific A1--A5 result matrix before that
handoff, and do not contain the post-update Profile 4 `READ` required by A3 or
a complete A4 noninterference observation. This packet does not cure either
historical fact. It authorizes only the new, bounded read-only observations
specified below for a later HEP assessment.

## Exact subject

| Field | Frozen value |
| --- | --- |
| Work order | `GP-BIND-003` |
| Candidate branch | `codex/gp-bind-003-runtime-attestation` |
| Candidate Git SHA | `307d72347653c079ec8ec6e9b6ecae3c30ae536c` |
| Candidate tree | `56d9622d2e91174be1395a5234097ab6ef1739ac` |
| Canonical base | `bd548dacf453c932b1a88a0684e6e1155080a309` |
| Candidate UF2 SHA-256 / size | `83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b` / `979456` bytes |
| Protocol | `GP_BIND_RUNTIME_ATTESTATION_HW_V1` |
| Evidence contract | `GLYPH_HARDWARE_EVIDENCE_V2` |
| Pre-update Config | 252 bytes, SHA-256 `54fda3988c30e03b653153ec23d0623674da3649492caa75da8aa08fbce6b460` |
| Pre-update ProfileStore | incarnation 1, generation 172, high-water `17293822569102712070` |

The candidate, custody and prior evidence remain fixed. No rebuild, reflash,
rollback, source edit, Config write, ProfileStore mutation, selection,
activation, reset or automatic retry is allowed.

## Candidate-specific completion matrix

| Row | Expected result | Permitted observation |
| --- | --- | --- |
| G1 / A1 context | Record host platform/operator role and controller model/revision only if a current read-only surface supplies them; otherwise record `UNAVAILABLE`, never infer them from a port name. The exact candidate/artifact tuple above must remain unchanged. | Passive host inventory and retained tuple/custody logs only. |
| G2 / A3 post-update Profile 4 readback | In Configurator, one ProfileStore `READ` of ID 4 returns `PROFILE_STORE_OK`, ID 4, revision **1**, and a deterministic `UltimateProfile` payload. Its bare canonical payload digest must equal the preserved pre-update 3047-byte Profile 4 payload digest `b8583459651f42bfbb108e4558627ce0a192be89bae229cbb5a74fb0e7dcd8d4`. SHA-256 must be calculated over the exact ASCII bytes `Glyph.RuntimeIdentity.UltimateProfile.v1`, then one NUL byte (`0x00`), then the deterministic serialized payload; the result must equal `d12805847da6f8f07096842cb0c7ce275c1606f911a1f5efd188bb9aeaf2b384`, retained at `local_backups/gp-bind-003-update-20261019T122938Z/identity-xinput-001.json` (file SHA-256 `5548da0b244e4873cf1e8dbdb84991bb9f9cb4c20823fa9cc92a84d1fc64c583`). The before/after STATUS must both be incarnation 1, generation 172, high-water `17293822569102712070`, Config generation `1156314366`. Any mismatch, malformed/timeout response, changed revision, or changed STATUS value stops this packet. | Exactly one `python3 tools/glyph_profile_store_production_tool.py --port <current-configurator-port> --timeout 10 --journal-out <new-dir>/profile-4-post-update-read.jsonl read --profile-id 4 --output <new-dir>/profile-4-post-update-read.json` request, with fresh paths. Deterministic serialization/digest uses this exact candidate's tracked schema/options and `UltimateProfile` descriptor, as defined by `docs/runtime_config/gp_bind_003_wire.md`; preserve the request/response framing and the derivation. Follow it with one STATUS read only to prove no mutation. |
| G3 / A4 bounded-query noninterference | In a new ordinary XInput session, exactly two fixed 16-byte identity-only requests defined by `docs/runtime_config/gp_bind_003_wire.md` are sent: token `0x4750423030330101`, bytes `a5475249010110000101333030425047`; then token `0x4750423030330102`, bytes `a5475249010110000201333030425047`. Each must produce one complete unambiguous `persisted` response matching ID 4/revision 1/schema 3/incarnation 1/digest above. During a single 90-second passive CDC capture surrounding those requests, the B0XX stream has only complete 25-byte viewer records apart from clearly framed 72-byte attestation responses, returns to neutral after the owner releases controls, and shows no host-observed unexpected reset/disconnect. The requests must not cause Config/ProfileStore write, selection, activation, reload, or output changes; final Configurator STATUS and GET_CONFIG must remain the frozen values above. | First owner physical action: switch from Configurator to ordinary XInput controller state by the established mode control, then report `connected`. The daemon runs the packet-local, single-owner `tools/glyph_gp_bind_003_gap_capture.py` once with a current normal port, fresh `--raw-out`/`--report-out` paths and a unique session label. It opens once at 115200 with DTR asserted/RTS deasserted; saves every received byte for exactly 90 seconds; writes only the two frozen frames no earlier than 10 and 40 seconds after the open, after a complete-record boundary (waiting at most 250 ms; otherwise stop); and rejects partial, malformed, duplicate or unframed data. It has no operation other than this capture. After the normal capture it may ask the owner to return to Configurator for final read-only STATUS/GET_CONFIG. |

## Stop rules

One request at a time; no automatic retry after a missing, malformed, partial,
ambiguous or unexpected response. Preserve the resulting logs, retain the
earlier partial evidence unchanged, and return the exact gap or failure to HEP.
Do not treat a port change or an owner-directed ordinary reconnect as an
unexpected reset. No current observation may be used to alter the historical
classification of the earlier pre-handoff freeze omission.

## Result boundary

This is a prepared protocol for remaining observations, not an acceptance
record. A fresh independent HEP must assess the combined raw evidence and may
publish only the appropriate PASS, PARTIAL, INCONCLUSIVE, FAIL, or MISMATCH
state under `HARDWARE_EVIDENCE.md`. Candidate source remains unmerged unless
that independent process publishes an exact complete PASS.
