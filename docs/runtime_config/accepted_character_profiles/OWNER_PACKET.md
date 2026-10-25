# ACP-20261025-01 — final Pikachu/Kazuya controller packet

**PREPARED, UNEXECUTED — OWNER APPROVAL REQUIRED.** Preparation performs no
ProfileStore mutation, Config/reference write, firmware build or flash. These
commands are for a later approved execution only. A shell variable is not approval.

## Exact scope and corrected rename method

Keep stable ID27 and ID51 with their exact schema-5 wrappers/bodies and ranks.
Rename store metadata to **Pikachu** and **Kazuya**. The original UPDATE proposal
was source-incompatible: UPDATE ignores name/rank and advances payload revision.
The owner explicitly approved exposing existing checked **RENAME opcode7** in the
production host operator. It preserves payload revision and rank. Expected rename
revisions are **1→1 for both IDs**, not1→2. No firmware/store/schema change.

Only individually proven, unreferenced superseded experiments **48,49,50** may be
deleted. No CREATE, UPDATE, host set-reference, whole Config write, reset, flash,
forced retry, profile redesign or new gameplay campaign. Preserve unknown/legacy
records. [Exact current inventory](CONTROLLER_INVENTORY.md) and
[CONTROLLER_PLAN.json](CONTROLLER_PLAN.json) bind every target's current
name/revision/rank, complete wrapper/body/preprocessing/provenance hashes, source
lineage and sealed historical installation evidence. IDs are proven identities,
not a deletion range or name-prefix heuristic. All22 current legacy records stay.
Unknown future native entries stop the packet rather than being deleted.

The closed operation sequence is: physical safe return to27; RENAME27; DELETE48;
RENAME51; DELETE49; DELETE50; final preservation/menu smoke; leave27 active.
Removing old48 before naming51 Kazuya avoids duplicate visible Kazuya entries.

## Exact tools and physical identity

After actual owner approval, use a dedicated Bash shell, exclusive Configurator
access and no concurrent writer or unresolved mutation. No package installation
or tool substitution. Every unexpected result means STOP and retain all files.

```bash
set -euo pipefail
TOOLROOT='/Users/rasmus.pekkarinen/.codex/worktrees/kazuya-v2-profile/glyph-ultimate-expanded-fw'
PRIVATE='/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups'
PY="$PRIVATE/../.venv/bin/python"
CHECK="$TOOLROOT/docs/runtime_config/accepted_character_profiles/packet_checks.py"
STORE="$TOOLROOT/tools/glyph_profile_store_production_tool.py"
CONFIG="$TOOLROOT/tools/glyph_serial_config_tool.py"
IDENTITY="$TOOLROOT/tools/glyph_runtime_identity_tool.py"
ANCHOR="$PRIVATE/accepted_character_profiles_20261025_l5b_hsi4/physical-unit-anchor.json"
CAPTURE=$(mktemp -d "$PRIVATE/accepted_character_profiles_execution.XXXXXXXX")
export TOOLROOT PRIVATE PY CHECK STORE CONFIG IDENTITY ANCHOR CAPTURE
"$PY" -c 'import serial,google.protobuf,grpc_tools'
"$PY" "$CHECK" attest unused
match_unit() {
  local observed="$1"
  "$PY" - "$ANCHOR" "$observed" <<'PY'
import glob,json,plistlib,subprocess,sys
from pathlib import Path
anchor=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2])
assert not out.exists()
raw=subprocess.check_output(['ioreg','-p','IOUSB','-l','-w','0','-a'])
with out.with_suffix('.plist').open('xb') as f:f.write(raw)
found=[]
def walk(x):
 if isinstance(x,list):
  for v in x:walk(v)
 elif isinstance(x,dict):
  if x.get('USB Serial Number')==anchor['serial'] and x.get('idVendor')==anchor['vid'] and x.get('idProduct')==anchor['pid']:found.append(x)
  for v in x.values():
   if isinstance(v,(dict,list)):walk(v)
walk(plistlib.loads(raw));ports=glob.glob('/dev/cu.usbmodem*')
assert len(found)==1 and len(ports)==1,'physical unit/Configurator endpoint ambiguous or unavailable'
with out.open('x') as f:json.dump({'port':ports[0],'serial':anchor['serial'],'vid':anchor['vid'],'pid':anchor['pid']},f,indent=2);f.write('\n')
print('PASS known physical unit and source-defined Configurator route')
PY
  PORT=$("$PY" -c 'import json,sys;print(json.load(open(sys.argv[1]))["port"])' "$observed")
  export PORT
}
match_unit "$CAPTURE/unit-initial.json"
```

Keep USB identity, raw Config, fences/tokens/journals and all captures private.
Re-run `match_unit` with a **new filename** after every reconnect/route change.
It uses the private preparation anchor and the fresh normal Configurator VID/PID;
no historical port or transaction token is reused.

## Bounded read-only capture

The loops below issue only STATUS/LIST/READ and Config/identity observations.
Every capture stage, output and journal must be a new exclusive path.

```bash
capture_directory() {
  local d="$1" cursor=0 next n
  for n in {0..8}; do
    "$PY" "$STORE" --port "$PORT" --journal-out "$d/list-$cursor.jsonl" \
      --output "$d/list-$cursor.json" list --page "$cursor" --page-size 8 > "$d/list-$cursor.command.log"
    next=$("$PY" "$CHECK" cursor "$d/list-$cursor.json")
    if [ "$next" = 0 ]; then return 0; fi
    test "$next" -gt "$cursor"
    cursor="$next"
  done
  return 1
}
capture_all() {
  local d="$1" id
  shift
  mkdir "$d"
  "$PY" "$IDENTITY" --port "$PORT" --context configurator --session ACP-20261025-01 \
    --timeout 2 > "$d/identity.json"
  "$PY" "$STORE" --port "$PORT" --journal-out "$d/status-start.jsonl" \
    --output "$d/status-start.json" status > "$d/status-start.command.log"
  "$PY" "$CONFIG" --read --port "$PORT" --backup-out "$d/config.json" \
    --timeout-sec 5 > "$d/config.command.log" 2>&1
  capture_directory "$d"
  "$PY" "$CHECK" ids "$d" > "$d/ids.txt"
  while IFS= read -r id; do
    "$PY" "$STORE" --port "$PORT" --journal-out "$d/read-$id.jsonl" \
      --output "$d/read-$id.json" read --profile-id "$id" > "$d/read-$id.command.log"
  done < "$d/ids.txt"
  "$PY" "$STORE" --port "$PORT" --journal-out "$d/status-end.jsonl" \
    --output "$d/status-end.json" status > "$d/status-end.command.log"
  "$PY" "$CHECK" audit "$d" "$@" --output "$d/packet-snapshot.json"
}
capture_all "$CAPTURE/original" --original
```

Require normal Configurator identity, healthy production protocol2/mutation2,
clear recovery/uncertainty and mutation admission, stable incarnation/generation/
Config CRC/token high-water across capture, complete directory/READ metadata,
exact protected/native payloads, preprocessing/provenance and valid references.
Unexpected accepted-profile revision/rank/name/payload drift stops. Before any
DELETE, a referenced candidate stops; return safely and refresh/reconcile first.

## Safe physical return to ID27

Current preparation references ID51. Use the established normal GameCube/Ultimate
route to choose **Ultimate (ID27)**: MB1 → .Profile → Ultimate; MB2/MB3 navigate,
MB4 selects, allow committed reboot. If genuinely already on27, no selection is
needed. Do not use a host reference or whole-Config write. Return through normal
Connect to Configurator, then re-match the fresh endpoint:

```bash
match_unit "$CAPTURE/unit-safe-id27.json"
capture_all "$CAPTURE/safe-id27" --original --safe
"$PY" "$CHECK" compare-selection "$CAPTURE/original" "$CAPTURE/safe-id27"
BEFORE="$CAPTURE/safe-id27"
```

All records/store generation/high-water must remain unchanged. Only the installed
physical selector's matching native context/backend/default destination fields
may change; all other Config fields must be exact. All native execution rows
and the GameCube default must resolve ID27. The comparison also accepts an
already-safe byte-identical Config. Configurator telemetry is not raw GameCube
runtime attestation: retain the genuine owner menu/reboot observation.

## Five individually fenced mutations

This is a closed dispatcher with five explicit calls, **not a mutation loop**.
Each call takes a fresh full preflight, validates exact identity/no references,
requires exact equality to the previous verified checkpoint, prepares an offline
plan, sends one existing guarded production operation,
then READs/compares all records and Config before allowing the next call.
RENAME sends no profile body/rank/revision field: store generation is its real
conflict fence, and the fresh capture pins revision1. The production operator
repeats STATUS, refuses stale fences/tokens/health, fsyncs a new immutable request
receipt before send and never retries an uncertain result.

```bash
execute_one() {
  local label="$1" op="$CAPTURE/$1" inc gen token
  capture_all "$op-before" --safe
  "$PY" "$CHECK" compare-preserve "$BEFORE" "$op-before"
  "$PY" "$CHECK" plan "$op-before" --operation "$label" --output "$op.plan.json"
  "$PY" "$CHECK" fields "$op.plan.json" > "$op.fences.txt"
  read -r inc gen token < "$op.fences.txt"
  case "$label" in
    rename27)
      "$PY" "$STORE" --port "$PORT" --journal-out "$op.jsonl" --output "$op.result.json" \
        rename --profile-id 27 --name Pikachu --incarnation "$inc" --store-generation "$gen" \
        --token "$token" --request-out "$op.request.json" > "$op.command.log" ;;
    delete48|delete49|delete50)
      local ident="${label#delete}"
      "$PY" "$STORE" --port "$PORT" --journal-out "$op.jsonl" --output "$op.result.json" \
        delete --profile-id "$ident" --incarnation "$inc" --store-generation "$gen" \
        --token "$token" --request-out "$op.request.json" > "$op.command.log" ;;
    rename51)
      "$PY" "$STORE" --port "$PORT" --journal-out "$op.jsonl" --output "$op.result.json" \
        rename --profile-id 51 --name Kazuya --incarnation "$inc" --store-generation "$gen" \
        --token "$token" --request-out "$op.request.json" > "$op.command.log" ;;
    *) return 1 ;;
  esac
  capture_all "$op-after" --safe
  "$PY" "$CHECK" compare-mutation "$op-before" "$op-after" --operation "$label" \
    --receipt "$op.request.json" --result "$op.result.json"
  BEFORE="$op-after"
}
execute_one rename27
execute_one delete48
execute_one rename51
execute_one delete49
execute_one delete50
"$PY" "$CHECK" final "$CAPTURE/safe-id27" "$BEFORE" --output "$CAPTURE/final-api-preservation.json"
```

After each RENAME, only the intended name may change: revision/rank/wrapper/body
remain exact. After each DELETE, only its individually proven record disappears.
Raw Config/references remain byte-exact to the safe-ID27 checkpoint throughout
mutations. Returned IDs/tokens/fences and exact requests are checked. Generation
increases exactly5 total, one per RENAME/DELETE; no recovery/uncertainty is accepted.
Never continue because output merely contains plausible-looking JSON.

On lost acknowledgement, mismatch or uncertainty: STOP all mutations; preserve
request/journal/result and perform read-only reconciliation only. No replay,
re-token/retry, restore, delete/update repair or replacement CREATE. Any further
mutation after an anomaly needs explicit owner reconciliation.

## Final physical smoke and preservation

Final native entries:

```text
.Profile
  Pikachu  (ID27, revision1, rank0, original golden payload)
  Kazuya   (ID51, revision1, rank154, exact accepted v4 payload)
```

No Ultimate, KazTest1/2/3/4, old Kazuya experiment, SEL or Ultimate Runtime among
native entries. Report legitimate ordinary non-Ultimate modes separately.
All unrelated/legacy/unknown records remain exact against fresh safe preflight.

Ask the owner for only the bounded normal-route smoke: Pikachu selection/name/
reboot works; Kazuya appears selectable; leave Pikachu active. No full gameplay
campaign is needed merely for metadata names. Do not automate menus or invent
observations. Return through normal Configurator and re-match with new evidence:

```bash
match_unit "$CAPTURE/unit-final.json"
capture_all "$CAPTURE/final-preservation" --safe
"$PY" "$CHECK" final "$CAPTURE/safe-id27" "$CAPTURE/final-preservation" \
  --output "$CAPTURE/final-preservation.json"
```

Require exact final store accounting, both stable IDs, names, unchanged wrapper/
body/revision/rank, no dangling references, valid Config, unchanged unrelated
records and safe ID27 destination. Capture the genuine owner smoke report and
seal all private files. Gameplay-tested ID51 payload is unchanged; metadata
naming does not establish a newly tested payload or timing claim.

## Verbatim future approval

I approve ACP-20261025-01: safely return to ID27 if needed; use checked RENAME for ID27→Pikachu and ID51→Kazuya with payloads, ranks and revisions unchanged; delete only verified unreferenced superseded IDs48,49,50; verify menu/preservation and leave Pikachu active; no firmware or payload changes, Kazuya redesign or additional gameplay campaign.
