# Bounded owner packet — unexecuted draft

Status: NOT_ACTIONABLE_FOR_MUTATIONS. No approval to flash, switch profiles,
write references/Config, CREATE or DELETE is requested on this incomplete draft.
The immediate next step is the already-authorized read-only diagnosis below.
Fresh operation fences cannot be prefilled from retained evidence. Stop rather
than substitute historical generations, tokens, port, identity or firmware.

## A. Immediate read-only diagnosis

Owner makes the known controller available through its established Configurator
connection. The agent does not reboot, enter a new experimental topology or
change selection. Confirm one current USB serial endpoint and match the known
unit using private historical identity. If unavailable, stop; no write fallback.

Use tools from exact verified canonical or a reviewed preparation descendant.
Create a fresh private evidence directory, with new output/journal files for
each invocation. The following are templates: `PORT` and `CAPTURE` must come
from current endpoint verification and a new private directory; no saved shell
value is authority.

```bash
python3 tools/glyph_profile_store_production_tool.py --port "$PORT" \
  --journal-out "$CAPTURE/status.jsonl" --output "$CAPTURE/status.json" status
python3 tools/glyph_serial_config_tool.py --read --port "$PORT" \
  --backup-out "$CAPTURE/config.json" --timeout-sec 5
```

Capture current runtime identity through `tools/glyph_runtime_identity_tool.py`
with context configurator, a fresh session/token and retained same-unit checks.
A Configurator identity does not prove a GameCube or gameplay active identity.
Use STATUS to verify protocol2, incarnation, store and Config generations,
mutation-token high-water, all recovery/uncertainty flags and mutation feasibility.
Read complete LIST using page0/page-size8 and actual returned cursors until the
terminal cursor. Do not hardcode six pages if current topology differs. Bracket
the directory and READs with STATUS/Config-generation checks; stop on drift.

```bash
python3 tools/glyph_profile_store_production_tool.py --port "$PORT" \
  --journal-out "$CAPTURE/list-0.jsonl" --output "$CAPTURE/list-0.json" \
  list --page 0 --page-size 8
python3 tools/glyph_profile_store_production_tool.py --port "$PORT" \
  --journal-out "$CAPTURE/read-27.jsonl" --output "$CAPTURE/read-27.json" \
  read --profile-id 27
```

READ all records for an exact preservation baseline; require at least ID27 and
all proposed SEL IDs28–47. Decode wrappers through the existing protobuf tools;
compare exact serialized wrapper/body hashes, revisions, names, schema and ranks
with retained_profile_identities.json. Verify ID27 golden identity first. Stop
on any SEL identity/fixture mismatch, unknown record, recovery flag or uncertain
state. Preserve unknown/legacy records, even when absent from the native menu.

Classify every current Config row: zero-based index, mode/name, engine, stable
ID, embedded index, ordered remaps/SOCD, backend eligibility, activation binding,
all default references and Persist eligibility. Read current running firmware
identity through a source-supported facility; do not equate API snapshot with
exact installed UF2 identity. Reconcile three reported visible runtime choices
versus two predicted by the retained Config/current canonical source.

## B. Gates before a write packet can be finalized

1. Resolve native-only menu policy versus preservation of legacy menu choices.
   No display-name test or undocumented discriminator is allowed.
2. Complete exact current diagnosis. If source changes are required, isolate
   the menu predicate, preserve NativeTemplate/Persist, pass focused both-ABI
   selector/menu/native/ProfileStore/persistence/liveness and affected legacy
   correspondence checks, source review and unchanged resource limits.
3. Commit the exact candidate; build `pio run -e glyph_mk6` (established fallback
   only if necessary). Record source commit/tree, build provenance, linked
   resource proof and exact ELF/BIN/UF2 bytes/hashes. Preserve UF2 under
   `local_backups/hardware-artifacts/<candidate>/<UF2-SHA256>/firmware.uf2` and
   rehash readback without following symlinks. No rebuild substitution.
4. Name the exact reviewed recovery artifact/method and owner-controlled
   bootloader procedure. A historical filename alone is insufficient. Produce
   a new candidate-specific flash/preservation/menu packet and return it for
   owner approval before any hardware/controller operation.

None of these firmware candidate gates is claimed complete by this draft.
No new flash procedure can be exact until candidate/custody and recovery exist.

## C. Future owner-approved sequence

After B, one separately approved bounded operation packet would execute:

1. Repeat A immediately before mutation. Capture Config and complete directory/
   wrapper baseline, current/default references and route identity. Flash only
   the approved exact candidate if needed, using its reviewed procedure; verify
   all Config/store bytes/metadata preserved before proceeding. Installation
   alone is not acceptance. Stop on a preservation mismatch.
2. Inspect **every** Config stable profile reference, including nondefault rows.
   If any references a SEL, prepare one checked production set-reference to27
   per matching row, with fresh incarnation/store generation/Config generation
   and strictly increasing nonexhausted token. Verify context compatibility and
   ID27 admission first. No whole-Config SET or reference clearing fallback.
   Production set-reference does not itself reboot or update backend defaults.
   Use the established committed menu selection path to select Ultimate on the
   intended route, save backend/default coherently and reboot. Verify supported
   runtime identity says ID27/schema5 and Config contains no SEL references.
   Do not infer GameCube raw identity from Configurator telemetry. If the safe
   switch/route verification cannot be prepared, stop before DELETE.
3. Before **each** of twenty conditional DELETEs, take fresh STATUS; verify
   identity/reference invariants and the actual expected generation/incarnation.
   Use `tools/glyph_profile_store_production_tool.py delete` with explicit stable
   ID, fences and fresh monotonic token. Its new `--request-out` receipt is
   fsynced before transmission. The separate fresh journal/output must be
   retained. Verify returned ID, status and expected post-operation state before
   advancing. Update state only from actual responses. Stop on first unexpected
   or uncertain outcome; never automatically retry. No blind batch loop.
4. Re-LIST and verify only the twenty exact fixture records disappeared; all
   other wrappers/revisions/metadata unchanged. Twenty is conditional on A,
   never an ID-range deletion rule. Verify Config valid, no dangling reference,
   health/recovery clear. If initial count43 still applies, expect23 remaining.
5. Recompile unchanged canonical Kazuya and compare all hashes/report and JSON
   roundtrip to this chapter. Read ID27's **current** rank, choose rank1 only if
   adjacent and free, preserve ID27. Use production CREATE with name Kazuya,
   schema5 compiled payload, fresh current fences/token and persisted request.
   Do not edit the compiled JSON, assume allocated ID48, select or activate it.
6. Bind the actual returned stable ID/revision/generation. READ Kazuya and ID27;
   require Kazuya wrapper/body exact to compiled payload and Ultimate wrapper/
   body/metadata byte-identical to preflight. Verify every remaining record,
   no SEL, no unexpected Config/metadata changes and healthy stable store.
   Reconcile exact intended store generation deltas: one per successful DELETE
   and CREATE (21 if twenty deletes); checked references/menu selections change
   Config, not store generation. Config generation is a checked digest, not an
   integer counter to increment arithmetically. If count43 held, final count24.
7. On the intended gameplay backend visually inspect and scroll `.Profile`:
   exactly Ultimate then Kazuya, no runtime labels and no SEL. Report any
   legitimate non-Ultimate choices separately. Test list navigation and safe
   Ultimate selection; leave Kazuya unselected. Verify Ultimate safe active
   state/persistence and responsive menu. A changed candidate needs this exact
   bounded human menu/display acceptance before source integration.
8. Stop. Prepare a separate Kazuya gameplay-test handoff. CREATE, host checks,
   menu visibility, selection infrastructure or flashing cannot establish
   gameplay PASS. Kazuya gameplay acceptance remains NOT_TESTED.

Mutation CLI input contract (templates only, no usable fences are embedded):
`set-reference --mode-index <zero-based-row> --profile-id 27 --config-generation
<fresh-digest>`, `delete --profile-id <verified-ID>`, and `create --name Kazuya
--rank <verified-rank> --profile-json Kazuya.protobuf.json`; each also needs a
verified `--port`, new `--journal-out`, new `--output`, new `--request-out`,
`--incarnation`, `--store-generation` and `--token`. The production tool performs
its own STATUS preflight and refuses stale fences/nonproduction controls. Its
source is part of the eventual reviewed operation packet, not new automation.

Controller mutations performed: NONE

Firmware flashed: NO

SEL records deleted: NO

Kazuya created on controller: NO

Kazuya gameplay acceptance: NOT_TESTED
