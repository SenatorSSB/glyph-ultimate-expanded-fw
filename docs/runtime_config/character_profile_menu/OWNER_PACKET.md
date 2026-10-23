# Exact character menu / SEL cleanup / Kazuya installation packet

**Status: UNEXECUTED — OWNER APPROVAL REQUIRED.** This packet prepares the next
bounded hardware/controller operation; this task performs none of it. Final
approval is meaningful only with the linked source/build/resource/custody and
independent handoff-review evidence. No candidate hardware or Kazuya gameplay
PASS is claimed. The final safe profile is permanent Ultimate ID27.

## Exact firmware and recovery tuple

- Candidate F: `1de243c7bada73ba85843018058b4f66a06acdda`.
- Candidate tree: `5a25a83705a654480b8db805f20822f4d180d70f`.
- Canonical base: `55ab5984f47728db53a12665d685d16cfad39201`.
- Only production source changed: `src/core/profile_selection.cpp`, BuildTargets.
  Compact MODE_ULTIMATE Config choices are hidden; eligible engine1 templates
  still admit stored schema5 choices. Names are never a discriminator.
  NativeTemplate/Persist/context matching/boot/default persistence are unchanged.
- UF2 bytes: **1046016**.
- UF2 SHA-256: `a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b`.
- Exact UF2: `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/1de243c7bada73ba85843018058b4f66a06acdda/a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b/firmware.uf2`.
- Recovery F: `8b2c75e35bb990aee06de3165e5780082c4f08ad`, historically accepted
  selector/liveness source. Recovery UF21046016bytes, SHA-256
  `ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760`.
- Recovery file: `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/8b2c75e35bb990aee06de3165e5780082c4f08ad/ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760/firmware.uf2`.

Both preserved files were opened without following symlinks and rehashed.
Recheck immediately before their respective future copy. Never substitute
mutable .pio output or a rebuild. The ELF/BIN/custody and all2043 UF2 blocks,
RP2040 family/address/padding correspondence are in `evidence/build_custody.json`
and `evidence/artifact_correspondence.json`. Build provenance/resources/source
review and focused test results are linked by README.md. A host build is not
controller acceptance; no inherited hardware result covers this changed menu.

## Stage0 — Fresh exact read-only preflight

The last host inventory saw RP2 Boot with no Configurator serial endpoint.
That observation neither identifies the unit nor authorizes copying firmware.
If still in bootloader, the owner must return the known controller to its
established normal Configurator connection before this preflight. The agent
performs no experimental reboot, profile selection, CREATE/UPDATE/DELETE,
SET_REFERENCE or Config write during preflight.

Create a fresh private capture directory. Match the known unit and current
endpoint against retained private identity; never reuse a stale port. Capture
runtime identity through the existing supported Configurator identity tool;
that identity does not prove a GameCube/gameplay active profile. Capture:

- Production ProfileStore STATUS: protocol2, mutation protocol2, incarnation,
  store generation, Config generation, mutation-token high-water, clear recovery/
  uncertainty flags, mutation feasibility and capacity. Decode absent protobuf
  scalar fields as their declared defaults; do not mistake missing JSON zeroes
  for missing required protocol semantics. Nonproduction controls must be zero.
- Complete LIST, following **actual** returned page cursors, not assumed pages.
- Current raw Config and all current/default stable references, backend default
  indices, engine/preprocessing/eligibility/binding for every Ultimate row.
- READ every current record for preservation; require exact ID27 and IDs28–47
  identity, wrapper/body, schema, revision, name, rank and fixture lineage.
- Supported current backend/profile runtime identity. If the intended gameplay
  route cannot supply raw identity, retain that limit explicitly; do not infer
  it from Configurator telemetry. Establish the safe ID27 selection on a route
  with the established identity facility before deleting fixtures.

Use `tools/glyph_profile_store_production_tool.py` from the reviewed preparation
ref. It opens a fresh host journal, sends STATUS before every action, checks
production admission, and never retries. Example read-only invocation shapes
(`PORT` and `CAPTURE` are freshly verified local values, not literal defaults):

```bash
python3 tools/glyph_profile_store_production_tool.py --port "$PORT" \
  --journal-out "$CAPTURE/status-0.jsonl" --output "$CAPTURE/status-0.json" status
python3 tools/glyph_serial_config_tool.py --read --port "$PORT" \
  --backup-out "$CAPTURE/config-0.json" --timeout-sec 5
python3 tools/glyph_profile_store_production_tool.py --port "$PORT" \
  --journal-out "$CAPTURE/list-0.jsonl" --output "$CAPTURE/list-0.json" \
  list --page 0 --page-size 8
python3 tools/glyph_profile_store_production_tool.py --port "$PORT" \
  --journal-out "$CAPTURE/read-27.jsonl" --output "$CAPTURE/read-27.json" \
  read --profile-id 27
```

Bracket LIST/READ/Config with fresh STATUS; require stable incarnation/store/
Config generations. Decode READ protobuf wrappers through existing tools and
compare exact serialized bytes. Preserve all journals, raw responses and
receipts privately; seal a public digest inventory without device identifiers.

**Ultimate invariant:** stable ID27, name Ultimate, revision1, schema5,
1985-byte wrapper SHA-256
`30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b`,
1980-byte native body SHA-256
`ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee`.
Never update, delete or recreate it.

**SEL identity:** each exact ID/name/schema/revision/rank/wrapper/body must match
`retained_profile_identities.json` and original fixture lineage. Conditional
operations are ID28/SEL01,29/SEL02,30/SEL03,31/SEL04,32/SEL05,33/SEL06,34/SEL07,
35/SEL08,36/SEL09,37/SEL10,38/SEL11,39/SEL12,40/SEL13,41/SEL14,42/SEL15,
43/SEL16,44/SEL17,45/SEL18,46/SEL19,47/SEL20. Do not trust the range alone.
Mismatch means STOP for that packet; never delete an unknown or renamed record.

The retained Config has row0 engine0/ID0, row1 engine0/ID3 and row2 engine1/ID28,
all MODE_ULTIMATE, with all gameplay defaults pointing to row2. The owner's
corrected two runtime labels match this snapshot. Fresh fields remain authority:
inspect every reference, including nondefault rows. A substantive new context,
other native character or unexpected Config/state difference requires bounded
packet reconciliation before writes. Retain unrelated legacy/unknown records;
never delete them to force a two-item menu. If total differs from43, calculate
counts from the actual snapshot, not the historical23/24 expectations.

## Stage1 — Install exact candidate and verify preservation

After Stage0 is sealed and this packet is owner-approved, the owner enters the
established BOOTSEL mode. Confirm the same physical unit and RP2040 bootloader
volume; rehash exact candidate custody with no symlink following. The owner
manually copies that exact UF2 **once** to the verified RPI-RP2 volume using the
normal firmware-update procedure. No host flashing automation is introduced.
Record source tuple, source-file readback, intended volume, copy completion and
normal reenumeration. An uncertain copy stops; no automatic retry.

Return to the established Configurator mode. Repeat Stage0 STATUS, Config,
complete LIST and every READ. Require raw Config byte-identical and every
record/metadata/reference/generation unchanged from Stage0; recovery remains
clear. Boot does not authorize migration or preservation changes. Stop on any
unexpected change. In particular retain every Config execution context even
though its compact-mode menu entry is hidden.

If the candidate fails to start or is unresponsive, stop and preserve observations.
Under this packet's recovery approval, the owner may use the same known BOOTSEL
procedure and copy the **rehash-verified recovery UF2 once**. Then repeat full
read-only preservation and report outcome. Do not mass-restore files/Config,
recreate profiles, format storage or retry uncertain mutations. Firmware
recovery does not undo store mutations; after an uncertain operation, stop and
reconcile its actual state before any restoration or continuation.

## Stage2 — Safely leave all SEL references before DELETE

Freshly inspect **every** Config stable reference, not only active defaults.
If a row references ID28–47, verify its exact native preprocessing matches ID27
(using the production ordered preprocessing digest/context admission). Plan one
checked reference change to ID27 for that row. If any safe checked switch cannot
be prepared, STOP; do not synthesize preprocessing, clear references or remove
rows. In the retained topology only row2 needs the ID28→ID27 change.

Use production `set-reference --mode-index <zero-based-row> --profile-id 27` with
fresh explicit store incarnation/generation, Config generation and a new token
above the actual combined high-water. Each request/journal/output path must be
new. `--request-out` is fsynced before transmission by the existing production
tool. Verify returned ID27, exact expected Config changes and unchanged store
records/generation. Production set-reference itself does not reboot or change
backend defaults. Never reuse historical tokens or Config digest3717489385.

Then use the **established committed controller menu selection path** to select
Ultimate on the supported identity route, persist the coherent backend/default
destination and reboot. Confirm ID27/revision1/schema5 and its exact native
identity through the established runtime facility, plus responsive controls.
Verify raw Config/runtime references and all records again, with **no** remaining
SEL stable reference in any row. For other gameplay routes, preserve qualified
owner observations and Config destination evidence; do not invent hidden raw
GameCube identity. No DELETE starts before safe active ID27 is established.

## Stage3 — Twenty individually fenced conditional DELETEs

For each exact verified SEL in the listed ascending order:

1. Fresh STATUS; require healthy production protocol, unchanged incarnation,
   current actual store generation/Config generation/high-water and feasible
   mutation. Confirm no SEL reference has reappeared and selected ID27 is safe.
2. Reverify that record's ID/name/schema/revision/rank/fixture wrapper/body.
3. Choose a new nonexhausted uint64 token strictly above actual high-water.
   Invoke production `delete --profile-id <that-ID>` with exact current
   `--incarnation`, `--store-generation`, `--token`, new `--request-out`, new
   `--journal-out` and new `--output` (plus the verified port).
4. Require fsynced immutable request before send, OK response and returned ID
   exactly equal to requested ID. Capture returned store generation and status.
5. Fresh STATUS and directory verification: actual store generation increments
   once, only that record disappears; all unexpected changes stop the sequence.
   Update fences/token state from actual responses before the next request.

No blind loop, silent skip, assumed success, replay or uncertain-operation retry.
No UPDATEs and no deletion of Ultimate, legacy/non-native or unknown records.
After all20, verify every remaining wrapper/revision/metadata and Config. If
initial count43 held, expect23 retained; otherwise use actual initial count−20.
The visible native list should contain only Ultimate at this checkpoint.

## Stage4 — CREATE exact inactive Kazuya

Revalidate/compile unchanged `profiles/kazuya/Kazuya.profile.json` using the
recorded four compiler commands; compare the committed compile report and
`Kazuya.protobuf.json` roundtrip byte-for-byte. No payload hand editing.

- CREATE name Kazuya, payload schema5, encoding1/native ABI1.
- Wrapper1839bytes, SHA-256
  `60f1715738fb5a46f8ac7cde326a3178e4560e52a8489da54e3a435eb70fd3e8`.
- Body1834bytes, SHA-256
  `44fa76903206c7a86a9f5d5a19c0be5f237e1c7e631dd5adf21cdb27eb3e4405`.
- Production protobuf JSON SHA-256
  `769c384330bb7fcceaa0ac16a986f24a654892460e659fba205d7ea2f9eabd26`.
- Freshly read Ultimate's rank. Retained rank0 proposes Kazuya rank1 if free;
  choose a deterministic available adjacent rank after Ultimate without editing
  ID27. If that cannot preserve ordering, STOP for a bounded rank decision.
- Verify an existing eligible engine1 context matches the compiled native
  preprocessing digest before any installation claim. Do not modify coordinates,
  bindings or Config preprocessing to admit the profile.

Fresh STATUS/fences/new monotonic token and new persisted receipt/journal/output
are required for production `create --name Kazuya --rank <verified-rank>
--profile-json <exact-chapter-Kazuya.protobuf.json>`. Bind **the returned**
nonzero stable ID/revision/generation; never assume ID48. Do not select Kazuya.

## Stage5 — Exact readback, menu acceptance and STOP

READ ID27 and the returned Kazuya ID. Ultimate wrapper/body/revision/name/rank
must be byte-identical to preflight; Kazuya stored wrapper/body must equal local
canonical compilation exactly. Verify all other remaining wrappers and metadata,
no SEL names/IDs remain, Config valid, healthy store/recovery flags clear and
no unexplained generation changes. Exactly20 successful DELETEs plus one CREATE
advance store generation21; checked references/menu saves affect Config generation
(a digest, not an arithmetic counter). Conditional original count43 yields24.

On each affected intended route (XInput, GameCube through the owner's normal
Switch adapter, USB Nintendo Switch), visually inspect and scroll `.Profile`:

```text
.Profile
  Ultimate
  Kazuya
```

Require exactly this current native-character order, no Ultimate Runtime rows,
no SEL choices, responsive navigation and safe **Ultimate** selection/reboot.
Stored menu keys remain indices; the displayed Kazuya entry is not activated.
Capture genuine owner observations per route, supported runtime identity where
available, normal reconnect/persistence and final preservation readback. Report
unexecuted routes as NOT_TESTED; no unsafe powered/no-poll setup is requested.
If current Config intentionally includes non-Ultimate ordinary modes, report
those additional choices honestly and reconcile the target total before PASS.

End on Ultimate. Kazuya activation/gameplay is a separate next owner-approved
phase. Host checks, successful CREATE, display, flashing and selection
infrastructure do not establish gameplay acceptance. Prepare its separate
handoff only after installation/preservation/menu PASS. No source merge before
required exact candidate-specific human menu/display PASS and normal evidence
processing/integration gates.

Current task authority boundary:

```text
Controller mutations performed: NONE
Firmware flashed: NO
SEL records deleted: NO
Kazuya created on controller: NO
Kazuya gameplay acceptance: NOT_TESTED
```
