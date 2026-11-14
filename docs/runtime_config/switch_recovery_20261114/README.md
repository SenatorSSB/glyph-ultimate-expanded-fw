# Post-Stage-H Switch recovery preparation

Status: offline preparation for supervisory review. This is a separate host-tooling
branch, not firmware acceptance, merge authority or physical-use approval.
The owner's 2026-11-14 “Glyph Switch Readiness — Final Hardware Recovery
Preparation” directive authorizes this bounded work. No controller was accessed.

## Exact operation and identities

`tools/glyph_switch_recovery.py` restores only the complete Config whose sole
change from the retained Stage-H XInput baseline is
`default_usb_backend_config: 4 -> 1` (one-based backend Config indices).
It has no general editing, reset, erase, flashing or rollback facility.

- Accepted firmware source: `0b9ef3afd1834ac7832871bca0651b67147840a2`.
- Accepted evidence parent: `4a5fa494194c366f8a78e324fcdfdb560dd454c5`.
- Exact UF2: `6eb992cda7392b6fb5a52ab48989ef10c94fc97ec77fd733360a863e55cd8a83`, 1,327,104 bytes.
- Previous installed source: `84556d904f067bda5a101e6297689239ecd04aae`.
- Retained Stage-H snapshot JSON: `2087b17b429da7a657288218f9f83297e653e987c45668c2a3ecc35aac344933`.
- Original helper source SHA-256: `7ff3b2094283dd38b4ee942836aa2aace386efe4102e5aa6226479df9811f7c6`.
  The retained accepted worktree and original `/private/tmp` copy match. Its
  historical contract and guards remain unchanged.

| Config expectation | SHA-256 |
| --- | --- |
| Preserved XInput / restored target | `b3f03f33c01111eceda1a602cdb30f6e4d003375f495f20008d5a529b804c8b8` |
| Predicted Switch-selected current | `b4f242caec602cdc75718ad9805bc847de456f1298ed5be82f632fdb89180028` |

Both Configs are 368 bytes. Byte offset 263 (zero-based) changes `01 -> 04`
for selection, then `04 -> 01` for recovery. All four rows, references, primary
selector, backend defaults, RGB content and firmware-owned receipts are identical.
The target is the original baseline bytes, not a reconstructed approximation.
Expected store incarnation is 1, generation 234, managed sequence 6, transaction
high-water `17293822569102712138` (snapshot's next-token value ends in 139).
The original 27 ordered entries and complete wrappers are pinned. GameCube default
remains row 3 / KazTest5 / ID53; the retained final XInput identity was ID53 revision1.
Those are retained observations, not new live observations in this invocation.

## Safeguards

`pins.json` binds the controller's serial digest, complete directory fingerprint,
exact resolved existing campaign ledger path and hashes of all 812 retained ledger
files. The real ledger was read only. No prior claim was changed or removed. A new
one-shot key includes the candidate source, controller and
`switch-liveness-stage-h-0b9ef3af-usb-4-to-1`; it never reuses the old incident key.
Changing the ledger path, original entries or any original ledger file fails closed.

`observe` is a narrow future read-only capture for this exact candidate and either
of its two exact checkpoint Configs. It requires a separate expiring read approval,
exact UF2 and endpoint, then exact advertised build/Mk6 identity, STATUS2 and actual
schema-backed package STATUS4 (supported floor2, unfenced, logical NONE0), full
LIST, all27 raw wrapper READs, repeated LIST, Config and final STATUS. It publishes
`snapshot.json` only after a complete closed capture. Original legacy READ replies
omit `profile_health` (zero); full exact wrapper comparison plus healthy STATUS
is required. The retained real LIST/READ/STATUS4 envelopes are replayed in tests.

`prepare` requires that fresh Switch observation (at most15 minutes old). A predicted
Config alone cannot prepare an execution plan. It creates immutable payload and
plan files with exact Config/storage/directory/tooling/frame/controller bindings.
It neither opens serial nor writes the ledger.

`execute` requires an exact fresh owner approval of the immutable plan and frame,
port and controller, with an exclusive Configurator session. Its durable exclusive
claim is burned before serial opens, even if later preflight fails. Durable intent
and exact payload precede SET. Complete preflight repeats identity, both STATUS
protocols, Config, all27 entries/wrappers and repeated directory; immutable inputs,
observation freshness and approval expiry are rechecked at the write boundary.
At most one physical CMD_SET_CONFIG request is attempted. A partial write, missing,
partial, extra or unexpected acknowledgement, readback mismatch or postflight
failure is terminal. Neither a new episode nor renewed approval permits a retry.

Success requires exact complete Config readback and another complete27-profile
comparison, both STATUS protocols and intact historical ledger. Otherwise stop;
retain evidence and claim, with no retry, automatic rollback or compensation.

Legacy SET_CONFIG has no request token or atomic compare-and-swap generation
fence. Empty CMD_SUCCESS6 is correlated by the exclusive sequential connection,
command ID and empty queue, followed by exact readback and complete audit. The
owner must ensure no menu edits or competing writers. The candidate UF2 checksum
and advertised short build/Mk6 identity are custody/endpoint checks, not full
installed-image attestation. API preservation is not raw NOR identity; normal
Config publication rotates `/config-v2.prev`, which is explicitly checked in the
synthetic host proof. No power-loss or physical-durability claim is made.

## Offline reproduction and evidence

Use an existing Python with `pyserial`, `protobuf` and `grpcio-tools`. No dependency
installation, firmware rebuild or controller access is needed. Paths named below
are inputs supplied by the supervising operator; retained controller payloads stay
private. Never substitute predicted evidence for an observed hardware snapshot.

```sh
python3 tools/test_glyph_switch_recovery.py --snapshot STAGE_H_FINAL_SNAPSHOT --xinput-baseline STAGE_H_CONFIG_PB --uf2 EXACT_CANDIDATE_UF2
python3 tools/check_switch_recovery_setconfig.py --repo CANDIDATE_CHECKOUT --dependency-repo CANDIDATE_WITH_HOST_DEPS --seed-namespace SYNTHETIC_XINPUT_NAMESPACE --out NEW_HOST_EVIDENCE --framework PINNED_ARDUINO_PICO_3_6_3
python3 tools/check_switch_recovery_baseline.py --baseline STAGE_H_FINAL_SNAPSHOT --uf2 EXACT_CANDIDATE_UF2 --host-build NEW_HOST_EVIDENCE/build --out NEW_PRIVATE_BASELINE_EVIDENCE
```

The synthetic XInput seed is retained as `synthetic-xinput.namespace.gz` (decompress
outside the repository). It contains synthetic test packages, not controller data.
The production harness script copies the existing transaction fixture and changes
only its host transport framing to CMD_SET_CONFIG. The actual production
ConfiguratorBackend, PacketIO, Persistence, ProfileStore, validators and LittleFS
are compiled unchanged with address/undefined-behavior sanitizers. The synthetic
backend table is arranged XInput1/GameCube2/Configurator3/Switch4. The proof makes
one4->1 SET, verifies empty success and exact live/saved target, and compares every
other namespace file plus the expected prior-Config rotation. Its small synthetic
profile library is not a reconstruction of the physical27-profile flash.

The separate exact368-byte pair passes the actual production Config parser and
semantic validator (`0 1 0` for both); the complete real27-entry/wrapper baseline
and all unrelated Config content are checked independently. Published reports and
compressed logs contain hashes/results, not private Config/profile payloads.
`evidence-manifest.json` binds the retained evidence and tool versions.

Independent review repairs and final verdict are in `review.md`. Review acceptance
still does not authorize hardware use. See the corrected
[physical proposal](../switch_readiness_20261114/physical-proposal.md).

## Future owner-guided capture and restoration

After supervisory acceptance and the separately approved installation/selection,
use `observe --baseline STAGE_H_FINAL_SNAPSHOT --approval READ_APPROVAL --uf2
EXACT_CANDIDATE_UF2 --selector 4 --out NEW_OBSERVED_SNAPSHOT`. After installation,
`--selector 1` can verify the exact candidate's XInput checkpoint first.

READ_APPROVAL must contain exactly `approved`, `scope` (`read-only`), `source`,
`uf2`, `port`, `usbSerial`, `ownerReference`, `approvedAtUtc`, `expiresAtUtc`.
Only actual owner approval sets `approved:true`; use a timezone-aware window of
at most15 minutes and the currently verified endpoint. Never auto-generate owner
approval from this document.

Then use `prepare --snapshot NEW_OBSERVED_SNAPSHOT --xinput-baseline STAGE_H_CONFIG_PB
--ledger EXACT_EXISTING_RESOLVED_LEDGER --out NEW_RESTORATION_EPISODE`.
Present its complete plan, observed guards/current and target hashes and exact
frame to the owner. The separate restoration approval must contain exactly
`approved`, `planSha256`, `frameSha256`, `port`, `usbSerial`, `approvedAtUtc`,
`expiresAtUtc`, `exclusiveConfiguratorSession`, `ownerReference`. Both booleans
must reflect explicit owner approval, with at most15 minutes validity.

Only after that approval: `execute --plan NEW_RESTORATION_EPISODE/plan.json
--approval EXACT_RESTORATION_APPROVAL --uf2 EXACT_CANDIDATE_UF2
--exclusive-configurator-session`. These are future supervised instructions, not
permission to run any device command in this preparation invocation.
