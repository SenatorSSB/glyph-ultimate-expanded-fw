# Character profile menu: final owner operation packet

Packet ID: **CPM-HW-1DE243C7-R2**. Status: **FINAL — UNEXECUTED — OWNER APPROVAL REQUIRED**.
This is packet finalization only. No controller command, flash, reference change,
DELETE, CREATE, reboot or selection change was performed to prepare it.

**Implementation, source review, host/ABI tests, exact build, resource proof and
artifact custody are COMPLETE.** Fresh controller state is the only remaining
execution-time dependency. Read and verify it before writes; do not reuse historical
port, firmware observations, generation/digest, token, directory, references or ranks.
Approval of this exact packet permits only its bounded operations and abort/recovery
path. Kazuya activation and gameplay testing are excluded. Canonical merge is excluded.

## 1. Frozen facts — known now

| Fact | Exact value |
| --- | --- |
| Candidate source | `1de243c7bada73ba85843018058b4f66a06acdda` |
| Candidate tree | `5a25a83705a654480b8db805f20822f4d180d70f` |
| Fixed source branch | `codex/native-profile-menu-candidate` |
| UF2 bytes | `1046016` |
| UF2 SHA-256 | `a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b` |
| Exact retained UF2 | `/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/1de243c7bada73ba85843018058b4f66a06acdda/a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b/firmware.uf2` |
| Build | `pio run -e glyph_mk6`: PASS; no fallback |
| Hardware/menu acceptance | NOT_TESTED for this candidate |
| Kazuya gameplay | NOT_TESTED |

Exact completed gate evidence, relative to this packet:

- `evidence/source_review.json`: reviewed source/test hashes, PASS.
- `validation.json`, `evidence/log_manifest.json`, `evidence/logs/build.log.gz`:
  focused both-ABI selector/menu/persistence/native/legacy checks and exact build.
- `evidence/build_provenance.json`: 259 actual recipes, compiler/dependency identities.
- `evidence/build_custody.json`, `evidence/artifact_correspondence.json`: exact
  ELF/BIN/UF2 hashes, O_NOFOLLOW custody, all2043 UF2 blocks and recovery readback.
- `resource/REPORT.md`, `resource/result.json`, `resource/manifest.json`,
  `evidence/abi-layout.json`, `evidence/menu-target-frames.json`: linked/ABI proof;
  static198288/199632, core0 bound2048/2048, core1 composition1060 within retained1152,
  unchanged limits; BuildTargets frame56 on both target ABIs.
- `evidence/handoff_review.json`: completed original candidate handoff review.
- `packet_final_review.json`: fresh independent review of **this R2 executable packet**,
  its exact SHA-256, audit helper and offline tests. Require PASS before execution.

The additional recovery-harness failure is inherited and identical on canonical
and candidate (`evidence/inherited_recovery_fixture_debt.json`). It is not an open
candidate implementation gate; no aggregate PASS is claimed. Target timing/highwater
NOT_MEASURED, Nunchuk NOT_TESTED and historical root cause UNPROVEN remain unchanged.

**Source semantics:** In compact ProfileStore mode, internal `MODE_ULTIMATE` Config
rows are hidden from the user-visible `.Profile` list. Stored schema-5 profiles
remain visible when a compatible native execution template exists. Precisely,
BuildTargets hides `compact && mode_id == MODE_ULTIMATE` after backend eligibility;
its existing eligible engine1-template admission remains. Exact per-profile
`ContextMatches` is enforced by unchanged `Persist()`. This packet checks the actual
ID27/Kazuya context before writes. `NativeTemplate()`, `Persist()`, context matching,
boot activation and backend/default persistence are preserved. No name filtering.
Noncompact Ultimate and ordinary non-Ultimate menu behavior are unchanged.

### Frozen Kazuya v1 compilation

Canonical source: `profiles/kazuya/Kazuya.profile.json`, unchanged. Fresh offline
validation: **PASS**, format v1, schema5, encoding1, native engine ABI1.

| Identity/count | Exact result |
| --- | --- |
| Wrapper | 1839 bytes |
| Wrapper SHA-256 | `60f1715738fb5a46f8ac7cde326a3178e4560e52a8489da54e3a435eb70fd3e8` |
| Native body | 1834 bytes |
| Native body SHA-256 | `44fa76903206c7a86a9f5d5a19c0be5f237e1c7e631dd5adf21cdb27eb3e4405` |
| Preprocessing SHA-256 | `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f` |
| Provenance | authoredSourceV1 |
| Provenance SHA-256 | `09392756ec1fce89479e5008f4653b866f11e31254bec435a0c1c0edf2531ae7` |
| Protobuf JSON SHA-256 | `769c384330bb7fcceaa0ac16a986f24a654892460e659fba205d7ea2f9eabd26` |
| Declared / wire tables | 16 / 28 |
| Neutral-filled wire slots | 16–27 (12 slots) |
| Conditions / tokens | 68 / 220 |
| Direction sources / table rules | 6 / 14 |
| Digital bindings / analog effects | 20 / 11 |

Full exact compile report: `Kazuya.report.json`; refreshed validation/provenance:
`packet_compile_identity.json`. Frozen payloads: `Kazuya.pb`, `Kazuya.protobuf.json`.
The production JSON roundtrips to the exact frozen wrapper. Do not edit any payload
or coordinates. These are host identities, not gameplay acceptance.

## 2. Execution environment and fresh facts

Run commands only after approval, from a dedicated Bash shell. Every error or
unexpected result means **STOP**; never continue merely because a command printed
some valid-looking JSON. One operator, exclusive Configurator session, no concurrent
writer, no pending mutation, and no automatic retry. Keep all raw captures private.

```bash
set -euo pipefail
TOOLROOT='/Users/rasmus.pekkarinen/.codex/worktrees/native-profile-menu-cleanup/glyph-ultimate-expanded-fw'
PY="$TOOLROOT/.venv/bin/python"
PKT="$TOOLROOT/docs/runtime_config/character_profile_menu"
STORE="$TOOLROOT/tools/glyph_profile_store_production_tool.py"
CONFIG="$TOOLROOT/tools/glyph_serial_config_tool.py"
IDENTITY="$TOOLROOT/tools/glyph_runtime_identity_tool.py"
CHECK="$PKT/packet_checks.py"
UF2='/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/1de243c7bada73ba85843018058b4f66a06acdda/a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b/firmware.uf2'
CAPTURE=$(mktemp -d '/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/character_profile_menu_R2.XXXXXXXX')
export TOOLROOT PY PKT STORE CONFIG IDENTITY CHECK UF2 CAPTURE
"$PY" -c 'import serial,google.protobuf,grpc_tools'
"$PY" - <<'PY'
import hashlib,json,os,pathlib
p=pathlib.Path(os.environ['PKT']);r=json.loads((p/'packet_final_review.json').read_text())
assert r['verdict']=='PASS_FOR_OWNER_APPROVAL_PACKET'
assert r['packet_id']=='CPM-HW-1DE243C7-R2'
for name,digest in r['reviewed_files_sha256'].items():
 assert hashlib.sha256((p/name).read_bytes()).hexdigest()==digest,name
print('PASS exact approved packet/helper/payload identities')
PY
```

STOP if interpreter/dependencies/reviewed files are absent or mismatched. Do not
install packages, rebuild firmware or substitute tools to work around it.
`packet_checks.py` only reads saved host files, validates them and writes an offline
snapshot; it never opens a device or sends an operation. Only the established
production tool writes the live store/reference, and it fsyncs a new immutable
request receipt before transmission.

Fresh named facts are: `PORT` (matched current serial endpoint); current firmware/
runtime observations; `INC`, `GEN`, `CFG`, `HWM`, `TOKEN` (from current STATUS);
current directory/read bytes; current references/defaults; `MODE_INDEX` (actual
native context); `KAZUYA_RANK` and returned `KAZUYA_ID`. `CAPTURE`/stage directories
are freshly allocated host evidence paths. None is prefilled from history.

Have the owner connect the known physical controller through its established
Configurator route. If currently in RPI-RP2, first return to the established normal
application/Configurator route; no flash precedes the preservation baseline.

```bash
"$PY" -c 'import glob;print("\n".join(glob.glob("/dev/cu.usbmodem*")))'
PORT='<fresh matched Configurator serial endpoint>'
export PORT
```

Replace only the named fresh placeholder, after matching the known physical unit
and retained private USB identity/location. A port string alone is not unit identity.
STOP on ambiguity, recovery, no endpoint or unexpected current firmware behavior.
Capture current firmware/runtime identity where observable; the72-byte identity
protocol does **not** attest a Git SHA/UF2 hash. Unobservable build identity stays
UNKNOWN; do not infer GameCube runtime identity from Configurator telemetry.

### Reusable read-only capture commands

Paste these functions once. Loops here are **read-only** and bounded by the64-entry
store; there is no mutation loop. Every output/journal path must be new.

```bash
capture_directory() {
  local d="$1" cursor=0 n next
  for n in {0..8}; do
    "$PY" "$STORE" --port "$PORT" --journal-out "$d/list-$cursor.jsonl" \
      --output "$d/list-$cursor.json" list --page "$cursor" --page-size 8
    next=$("$PY" "$CHECK" cursor "$d/list-$cursor.json")
    if [ "$next" = 0 ]; then return 0; fi
    test "$next" -gt "$cursor" || return 1
    cursor="$next"
  done
  return 1
}
capture_all() {
  local d="$1" id
  shift
  mkdir "$d"
  "$PY" "$STORE" --port "$PORT" --journal-out "$d/status-start.jsonl" \
    --output "$d/status-start.json" status
  "$PY" "$CONFIG" --read --port "$PORT" --backup-out "$d/config.json" \
    --timeout-sec 5 > "$d/config-command.log" 2>&1
  "$PY" "$IDENTITY" --port "$PORT" --context configurator \
    --session "CPM-R2-$(basename "$d")" --timeout 2 > "$d/identity.json"
  capture_directory "$d"
  "$PY" "$CHECK" ids "$d" > "$d/ids.txt"
  while IFS= read -r id; do
    "$PY" "$STORE" --port "$PORT" --journal-out "$d/read-$id.jsonl" \
      --output "$d/read-$id.json" read --profile-id "$id"
  done < "$d/ids.txt"
  "$PY" "$STORE" --port "$PORT" --journal-out "$d/status-end.jsonl" \
    --output "$d/status-end.json" status
  "$PY" "$CHECK" snapshot "$d" "$@"
}
```

Expected: Configurator identity `context=configurator`, `status=configurator`,
`primary_backend=8`; any other identity stops the snapshot. Also production
protocol2/mutation2, no diagnostic/fault controls, clear recovery/
uncertainty, mutation feasible, stable incarnation/store generation/Config CRC and
high-water throughout each capture. Config raw CRC32 must equal STATUS Config digest;
all references/defaults must resolve, all native contexts must match their bodies.
The helper preserves legacy directory payload-version and actual READ schema as
separate facts (one retained legacy record differs); neither is silently rewritten.

## 3. Preflash baseline — read-only

```bash
capture_all "$CAPTURE/preflash" --initial
```

Require all21 expected schema5 IDs (Ultimate plus20SEL), no other native character,
and record the **actual** count of all legacy/unknown records. Expected fixtures
are table-bound IDs/names below, with revision1/schema5 and exact original wrapper/
body lineage in `retained_profile_identities.json`. Rank is freshly read metadata;
never substitute historical rank into a fence or overwrite it for convenience.

| ID | Name | ID | Name | ID | Name | ID | Name |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 28 | SEL01 | 33 | SEL06 | 38 | SEL11 | 43 | SEL16 |
| 29 | SEL02 | 34 | SEL07 | 39 | SEL12 | 44 | SEL17 |
| 30 | SEL03 | 35 | SEL08 | 40 | SEL13 | 45 | SEL18 |
| 31 | SEL04 | 36 | SEL09 | 41 | SEL14 | 46 | SEL19 |
| 32 | SEL05 | 37 | SEL10 | 42 | SEL15 | 47 | SEL20 |

**Permanent Ultimate:** ID27, name Ultimate, revision1, schema5,1985-byte wrapper
SHA-256 `30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b`;
1980-byte body SHA-256 `ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee`.
Never UPDATE, delete or recreate ID27. Any golden/fixture mismatch means STOP.
An ID range alone is never deletion authority. An unexpected new native record,
invalid Config, changed context, recovery or uncertainty requires reconciliation
before writes; do not delete unknown records to force a two-item result.

## 4. Install exact UF2, then prove preservation

First rehash the retained source **immediately before use**, without following a symlink:

```bash
"$PY" - <<'PY'
import hashlib,os
p=os.environ['UF2'];fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
with os.fdopen(fd,'rb') as f:b=f.read()
assert len(b)==1046016
assert hashlib.sha256(b).hexdigest()=='a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b'
print('PASS exact UF2 custody')
PY
/usr/bin/open -R "$UF2"
```

Owner-controlled physical procedure, using the established Glyph UF2 update path:

1. Enter the controller's established firmware-update/BOOTSEL path. Confirm that
   the known physical unit is the `RPI-RP2` RP2040 bootloader volume; do not guess
   a volume or copy to another attached device.
2. In Finder, copy the **selected exact retained `firmware.uf2`** once onto that
   verified `RPI-RP2` volume. Do not copy a rebuild or mutable `.pio` file. This
   packet introduces no flashing automation or alternate recovery mechanism.
3. Allow the normal volume disappearance/reboot. Record the copy outcome and
   normal application reenumeration. An uncertain copy means STOP, no automatic retry.
4. Enter Configurator through the established route. Re-enumerate/match `PORT`;
   do not assume the preflash endpoint survived the reboot.

```bash
capture_all "$CAPTURE/postflash" --initial
"$PY" "$CHECK" compare "$CAPTURE/preflash" "$CAPTURE/postflash" --kind preserve
```

Expected: byte-exact raw Config, identical complete directory and every wrapper,
revision/name/rank/schema, unchanged incarnation/generation/Config digest/high-water,
clear recovery and healthy store. **STOP if post-flash preservation differs.**
No cleanup mutation is allowed before this PASS.

Abort/recovery: stop and seal observations if unresponsive, failed boot or unexpected
state. Only the already established owner-controlled BOOTSEL/UF2 path is permitted.
The existing recovery artifact is1046016bytes, SHA-256
`ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760`, at
`/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-artifacts/8b2c75e35bb990aee06de3165e5780082c4f08ad/ca0bb9e800f196ea2a233c42cb921cfd2fecc80b8a9c285340684f1db38fc760/firmware.uf2`.
If recovery is needed, rehash that file with the same O_NOFOLLOW pattern and its
own expected hash, then the owner may copy it **once** by the same verified route.
Repeat full read-only preservation and stop the campaign; do not resume cleanup
on recovery firmware. No formatting, mass restore, Config replacement or profile
recreation. Firmware recovery never undoes store mutations or resolves an uncertain
mutation; retain receipts and stop for state reconciliation.

## 5. Clear every current SEL reference safely

Retained evidence points row2 at SEL01, but discover the actual current rows:

```bash
BEFORE="$CAPTURE/postflash"
"$PY" "$CHECK" references "$BEFORE" > "$CAPTURE/sel-reference-rows.txt"
cat "$CAPTURE/sel-reference-rows.txt"
```

These are zero-based `GameModeConfig.ultimate_profile_id` references, including
nondefault rows. Backend defaults are one-based indices into those same rows.
Historical `profile_reference_result_*` receipt fields are not runtime destinations;
do not hand-edit them. The helper permits only existing engine1 Ultimate contexts
with exact ID27/Kazuya preprocessing. STOP if a referenced row cannot be safely
matched; do not synthesize preprocessing, clear it, delete a row or widen templates.

For **each actual listed row**, perform this complete block manually once, then
advance `BEFORE` to its checked result. There is no mutation loop. `MODE_INDEX` is
a fresh discovered row, not the retained example. Every row is checked separately.

```bash
MODE_INDEX='<one actual row from sel-reference-rows.txt>'
OP="$CAPTURE/reference-$MODE_INDEX"
"$PY" "$CHECK" fences "$BEFORE/status-end.json" > "$OP.fences.txt"
read -r INC GEN CFG HWM TOKEN < "$OP.fences.txt"
"$PY" "$STORE" --port "$PORT" --journal-out "$OP.jsonl" --output "$OP.result.json" \
  set-reference --mode-index "$MODE_INDEX" --profile-id 27 \
  --incarnation "$INC" --store-generation "$GEN" --config-generation "$CFG" \
  --token "$TOKEN" --request-out "$OP.request.json"
capture_all "$OP-after"
"$PY" "$CHECK" compare "$BEFORE" "$OP-after" --kind reference \
  --receipt "$OP.request.json" --result "$OP.result.json"
BEFORE="$OP-after"
```

Expected: returned ID27/OK/token exact, store generation and all records unchanged;
Config changes only that row's stable ID/engine/embedded index and checked-reference
receipt fields. The helper verifies the receipt digest against the immutable request.
`set-reference` **does not** select a backend, change backend defaults, activate the
new profile live or reboot. Its automatic STATUS refuses stale incarnation/store/
Config fences and tokens. Any unexpected/uncertain result means STOP, never retry.

```bash
"$PY" "$CHECK" references "$BEFORE" > "$CAPTURE/remaining-sel-references.txt"
test ! -s "$CAPTURE/remaining-sel-references.txt"
```

Now use the established normal controller path to choose the intended safe XInput
route, enter `.Profile`, select **Ultimate**, and allow its committed selection/reboot.
Do not select Kazuya. This makes the compatible native context and backend/default
destination coherent; checked reference assignment alone is insufficient.

Capture the actual XInput endpoint and native runtime identity after reboot. The
identity facility is source-supported for this route; it is not GameCube telemetry.
`SAFE_MODE` is the actual selected matching context row from current Config/identity.

```bash
PORT='<fresh matched XInput CDC endpoint>'
SAFE_MODE='<actual selected native context row>'
"$PY" "$IDENTITY" --port "$PORT" --context xinput --session CPM-R2-safe-Ultimate \
  --timeout 2 > "$CAPTURE/safe-ultimate-identity.json"
```

Return via the established Configurator route, refresh/match `PORT`, then:

```bash
capture_all "$CAPTURE/safe-ultimate" --safe
"$PY" "$CHECK" compare "$BEFORE" "$CAPTURE/safe-ultimate" --kind selection \
  --mode "$SAFE_MODE" --backend 2
"$PY" "$CHECK" identity "$CAPTURE/safe-ultimate" "$CAPTURE/safe-ultimate-identity.json" \
  --mode "$SAFE_MODE"
```

Expected: persisted XInput backend2, active/requested ID27/revision1/schema5,
exact domain-separated native identity digest and matching context row/incarnation;
no SEL reference in any Config row. Store records/generation/high-water unchanged.
Only the selected row and actual USB backend/default destination may differ in
Config; unchanged values may produce the **same** CRC. No arithmetic increment
assumption is allowed. STOP unless safe active ID27 and no dangling/SEL references
are proven. Do not infer a GameCube raw identity from any Configurator response.

## 6. Twenty separately guarded DELETEs

Start only after stage5 PASS. Exact sequence: **28,29,30,31,32,33,34,35,36,37,
38,39,40,41,42,43,44,45,46,47**, bound to the names/lineage table, not just numbers.
Initialize `PREVIOUS_STATUS` to the checked safe checkpoint:

```bash
PREVIOUS_STATUS="$CAPTURE/safe-ultimate/status-end.json"
```

There is **no DELETE loop**. Repeat the following block manually once per verified
ID; never skip a failure, repeat an uncertain operation or assume later successes.

```bash
SEL_ID='<next exact freshly verified ID from the sequence>'
D="$CAPTURE/delete-$SEL_ID-pre"
mkdir "$D"
"$PY" "$STORE" --port "$PORT" --journal-out "$D/status-start.jsonl" \
  --output "$D/status-start.json" status
"$PY" "$CONFIG" --read --port "$PORT" --backup-out "$D/config.json" \
  --timeout-sec 5 > "$D/config-command.log" 2>&1
capture_directory "$D"
"$PY" "$STORE" --port "$PORT" --journal-out "$D/read-$SEL_ID.jsonl" \
  --output "$D/read-$SEL_ID.json" read --profile-id "$SEL_ID"
"$PY" "$STORE" --port "$PORT" --journal-out "$D/status-end.jsonl" \
  --output "$D/status-end.json" status
"$PY" "$CHECK" one "$D" "$CAPTURE/safe-ultimate" --id "$SEL_ID" \
  --previous-status "$PREVIOUS_STATUS"
"$PY" "$CHECK" fences "$D/status-end.json" > "$D/fences.txt"
read -r INC GEN CFG HWM TOKEN < "$D/fences.txt"
OP="$CAPTURE/delete-$SEL_ID"
"$PY" "$STORE" --port "$PORT" --journal-out "$OP.jsonl" --output "$OP.result.json" \
  delete --profile-id "$SEL_ID" --incarnation "$INC" --store-generation "$GEN" \
  --token "$TOKEN" --request-out "$OP.request.json"
"$PY" "$STORE" --port "$PORT" --journal-out "$OP.post.jsonl" \
  --output "$OP.post.json" status
```

Before advancing, require exact returned ID/OK/token, unchanged incarnation,
post-generation=`GEN+1`, post high-water=`TOKEN`, same Config digest, and healthy
production status. The tool checks ID/status/token and fsyncs the request before
send. The final sequence audit below independently checks every request, result
and post-STATUS; **also check each result immediately**, using:

```bash
"$PY" - "$CHECK" "$D/status-end.json" "$OP.request.json" "$OP.result.json" "$OP.post.json" "$SEL_ID" <<'PY'
import importlib.util,sys
s=importlib.util.spec_from_file_location('packet_checks',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
a=m.status(sys.argv[2]);b=m.status(sys.argv[5])
x={'incarnation':a.store_incarnation,'generation':a.store_generation,'high_water':a.transaction_token_high_water}
y={'incarnation':b.store_incarnation,'generation':b.store_generation,'high_water':b.transaction_token_high_water}
m.mutation(x,y,sys.argv[3],sys.argv[4],m.PB.PROFILE_STORE_DELETE,int(sys.argv[6]),1)
m.need(a.config_generation==b.config_generation,'DELETE changed Config digest')
print('PASS this single DELETE; no retry')
PY
PREVIOUS_STATUS="$OP.post.json"
```

The precheck also requires exact continuity with the preceding successful STATUS,
byte-exact safe Config and unchanged remaining directory metadata; an unexpected
intervening mutation or skipped sequence entry stops **before** the next DELETE.

STOP immediately on uncertainty, stale fence, unexpected ID/status/generation,
recovery, reference, name/revision/schema/fixture mismatch or missing receipt.
Do not QUERY/replay/UPDATE or make a compensating write to work around it.

After all20 individual PASS results:

```bash
capture_all "$CAPTURE/after-deletes" --safe
"$PY" "$CHECK" compare "$CAPTURE/safe-ultimate" "$CAPTURE/after-deletes" \
  --kind deletes --receipt "$CAPTURE"
```

Expected: exactly the20 verified fixtures absent, all other records/metadata and
Config unchanged, no dangling references; store generation advanced20 and every
actual token/response/post-state reconciled. Count is actual initial count−20;
if initial count43 still held,23 remain. Never delete legacy/unknown records.

## 7. Compile verification, rank and exact Kazuya CREATE

These commands recompile to fresh host files; they do not access the controller:

```bash
mkdir "$CAPTURE/kazuya-compile"
"$PY" "$TOOLROOT/tools/glyph_native_profile_json.py" validate \
  "$TOOLROOT/profiles/kazuya/Kazuya.profile.json" > "$CAPTURE/kazuya-compile/validate.json"
"$PY" "$TOOLROOT/tools/glyph_native_profile_json.py" compile \
  "$TOOLROOT/profiles/kazuya/Kazuya.profile.json" --output "$CAPTURE/kazuya-compile/Kazuya.pb"
"$PY" "$TOOLROOT/tools/glyph_native_profile_json.py" compile \
  "$TOOLROOT/profiles/kazuya/Kazuya.profile.json" --format protobuf-json \
  --output "$CAPTURE/kazuya-compile/Kazuya.protobuf.json"
"$PY" "$TOOLROOT/tools/glyph_native_profile_json.py" report \
  "$TOOLROOT/profiles/kazuya/Kazuya.profile.json" --output "$CAPTURE/kazuya-compile/Kazuya.report.json"
cmp "$CAPTURE/kazuya-compile/Kazuya.pb" "$PKT/Kazuya.pb"
cmp "$CAPTURE/kazuya-compile/Kazuya.protobuf.json" "$PKT/Kazuya.protobuf.json"
cmp "$CAPTURE/kazuya-compile/Kazuya.report.json" "$PKT/Kazuya.report.json"
```

Require all frozen identities/counts in section1. STOP on any difference; no payload
repair or coordinate edit. Freshly READ ID27 metadata from the current full directory;
choose the **lowest unused uint32 rank strictly above Ultimate's current rank**.
This yields Ultimate then Kazuya without rewriting Ultimate. Other pre-existing
ranks are retained. Rank exhaustion or another native record means STOP.

```bash
capture_all "$CAPTURE/before-create" --safe
"$PY" "$CHECK" compare "$CAPTURE/after-deletes" "$CAPTURE/before-create" --kind preserve
KAZUYA_RANK=$("$PY" "$CHECK" rank "$CAPTURE/before-create")
"$PY" "$CHECK" fences "$CAPTURE/before-create/status-end.json" > "$CAPTURE/create.fences.txt"
read -r INC GEN CFG HWM TOKEN < "$CAPTURE/create.fences.txt"
"$PY" "$STORE" --port "$PORT" --journal-out "$CAPTURE/create.jsonl" \
  --output "$CAPTURE/create.result.json" create --name Kazuya --rank "$KAZUYA_RANK" \
  --profile-json "$PKT/Kazuya.protobuf.json" --incarnation "$INC" \
  --store-generation "$GEN" --token "$TOKEN" --request-out "$CAPTURE/create.request.json"
KAZUYA_ID=$("$PY" - "$CAPTURE/create.result.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))['response'];assert x.get('status','PROFILE_STORE_OK')=='PROFILE_STORE_OK'
v=int(x['profile_id']);assert v>0;print(v)
PY
)
capture_all "$CAPTURE/after-create" --safe
"$PY" "$CHECK" compare "$CAPTURE/before-create" "$CAPTURE/after-create" --kind create \
  --receipt "$CAPTURE/create.request.json" --result "$CAPTURE/create.result.json"
```

Expected: returned **actual** stable ID, never assumed48; revision1/name Kazuya/
schema5/rank chosen above, exact wrapper/body bytes to canonical compilation.
Generation advances1; actual high-water equals that request token; Config unchanged.
ID27 and **every** non-SEL pre-existing record remain exact (wrapper, body, name,
revision, schema, directory payload-version and rank). AllSEL IDs/names are absent;
no dangling Config references; store healthy/recovery clear. The composed audits
prove total store delta exactly21 (20 successful DELETEs+1CREATE), no arithmetic
assumption about Config generations and no silent change to any preserved record.
Do not select or activate Kazuya.

## 8. Visible menu acceptance, final preservation and STOP

Exit Configurator through the established normal route and boot the intended gameplay
backend. For XInput and each affected intended route (normal Switch/GameCube adapter,
USB Nintendo Switch), record genuine owner results for:

- `.Profile` shows native entries **Ultimate**, **Kazuya**, in that order;
- no Ultimate Runtime or SEL01–SEL20 entries;
- scrolling, list entry visibility and controls remain responsive;
- select **Ultimate only**, allow normal reboot, verify persistence after ordinary
  reconnect and that `.Profile` remains correct/responsive;
- verify ID27 runtime identity where source-supported; qualify normal GameCube
  observations as owner-reported, never as Configurator-derived raw identity.

If legitimate non-Ultimate ordinary modes are present, list them separately and
reconcile the total honestly. Do not suppress them or falsify a two-item total.
Unexecuted routes stay NOT_TESTED; no unsafe/no-poll hardware setup is requested.
A failure means STOP; no ad hoc repair, another flash or broader testing.

After these observations, return once to Configurator and capture final preservation:

```bash
capture_all "$CAPTURE/final-preservation" --safe
```

Compare all records, store generation/high-water and Ultimate/Kazuya identities to
`after-create`; they must be unchanged. Config may differ **only** by the actual
approved normal Ultimate/backend destination selections. For each route transition,
retain before/after snapshots and use the section5 `--kind selection` audit with
its actual selected context and source-defined backend ID; USB backend7 is Nintendo
Switch, non-USB backend3 is GameCube. No profile-reference receipt or unrelated
Config field may change. Config digest must match actual raw Config CRC at every
snapshot; it may stay equal after saving unchanged fields. STOP on unexplained drift.

Finish by exiting Configurator through the established path to the owner's intended
gameplay route, with **Ultimate** selected, and record the final normal boot/visible
state. Do not leave the controller in Configurator and call that an active gameplay
profile. Kazuya must remain stored but inactive. Seal all private journals, receipts,
full directory/wrapper snapshots, mutation accounting and genuine owner reports.

**STOP BEFORE KAZUYA GAMEPLAY.** Storage, CREATE, display and selection infrastructure
are not gameplay acceptance. Kazuya gameplay remains **NOT_TESTED**. Exact menu hardware
PASS and ordinary independent evidence/integration gates are still required before
source merge; this packet authorizes no merge or subsequent gameplay phase.

Current task: Controller mutations NONE; firmware flashed NO; SEL deleted NO;
Kazuya CREATE NO; selection changes NONE; Kazuya gameplay NOT_TESTED.

## Approval sentence

I approve packet CPM-HW-1DE243C7-R2 only: install its exact candidate, verify preservation, return safely to Ultimate, delete the20 individually verified SEL fixtures, CREATE canonical Kazuya and verify the menu; leave Ultimate active and stop before Kazuya activation or gameplay testing.
