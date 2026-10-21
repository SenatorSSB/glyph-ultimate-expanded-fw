# GP_NATIVE_001_MAC_PREFLIGHT_V1 — owner approval requested

Software work is ready: exact firmware source/review/build/custody and complete stack/resource proof pass, and the corrected Mac reader has passed the same independent reviewer's focused ACK. This packet proposes only a bounded Mac access/backup preflight. **No device action has occurred or is approved yet. Flashing, Config/profile changes and the H1–H12 physical acceptance campaign require a later separate packet and explicit approval.**

## Exact files and current status

Future candidate Git SHA: `334fbd06e4541c120b0db423e5be7e112eb1f6f6`; tree `0483dbb0cc8f7eb5a1c93cb1d91044f4d3dcf999`. Retained instrumented UF2:1041408 bytes, SHA256 `41305f260d42e8206bf4a2fb06c88912416e49cd8a68bc13ce3d3c7605306982`. This preflight does not install it. [Exact source/build/resource facts](exact_candidate_334f_status_20261021.md) retain all caps and broader filesystem support.

Mac observer binary:79536 bytes, SHA256 `24ed913f55ca9e6ebcd6a8f1d13e4d504f122b395e2b7beaa4d8ec8545ffd473`; source `e8e3e2aba80f21bf76fd26dd3fd1a36f27f46513e07f6db00d158aa01a36ece2`; verifier `442110b2ada7eb1e9159ecd4fa38036773d111f3f6c056cdaf62e154a4a8a006`. The [corrected child/procedure](mac_observer_20261021/corrected_child/README.md), [independent repair ACK](mac_observer_20261021/independent_repair_ack/REPORT.md), [regular host custody](mac_observer_20261021/host_artifact_custody.json) and [separate final-review binding](mac_observer_20261021/host_artifact_review_binding.json) are frozen. The original parent/two findings remain preserved; the custody's pending-at-creation label is historical and is resolved only by the separate binding.

The [current334-row packet](hardware_334f_preparation_20261021/current_packet_exactF.json), SHA256 `dfd4ab5c81c24e1380095fa637ff0d51de83b478f66641c53d1a69d9f76be744`, retains all18 families/17 contexts, original observations null, mandatory H10/H11/resource addendum and unchanged coverage. It differs from the historical reviewed303d packet only in11 Switch.lx bytes established by [exact linked-machine/ROM proof](switch_wire_erratum_20261021/README.md). No firmware change or portable out-of-range C++ guarantee is claimed.

[Machine-readable scope and all exact bindings](hardware_preflight_approval_20261021.json) are part of this packet. The owner reports this Mac for XInput, USB Switch and the same MOD.WUP-028 adapter used for GameCube-to-Switch. Host is macOS27.0.1/build26A434. Actual unit/revision, interface ownership/permissions, CDC port, adapter port, current Config and entry bindings remain unverified.

## Proposed operations after explicit approval

1. Identify the intended unit and actual adapter port with the owner. Permit ordinary connection/disconnection with all inputs released. Unknown current firmware can perform ordinary boot recovery, migration or bookkeeping; this is not a promise of byte-identical persistent state after connection.
2. Run at most one registry-only inspection for each owner-connected route (XInput, Switch, WUP-028). Match exact VID/PID and record location; do not open ambiguous matches. Inspection opens no USB/HID user client and sends no USB request.
3. For each already accessible, confirmed route, run at most one5-second capture, stopping at3 complete reports. All controls remain released. Use `purpose=preflight`, row `PREFLIGHT`, a new immutable host file and the confirmed location/port. XInput opens one vendor interface normally and reads its20-byte input; Switch uses a normal nonseizing HID input callback with the exact86-byte descriptor/8-byte payload; WUP reads37-byte adapter reports on the selected port. No XInput/HID output or control request is sent.
4. **Optional separate approval choice:** include exactly one WUP OUT byte `0x13` in its one designated capture. It starts adapter polling and may cause normal controller probe/origin traffic. This is an adapter operation, not read-only USB input. Require known successful completion with exactly one actual completed byte. No retry, rumble0x11, control fallback or driver workaround is permitted. If excluded, do not add it after a no-report result.
5. Only on an already reachable, positively identified ordinary Configurator CDC session, use exact F's existing read tools to retain one Config backup/raw SHA, one explicit STATUS, complete LIST pagination(page size8, at most8 LIST calls/the existing64 entries), READ of every available original ID and one fixed current-Configurator identity query. Each LIST/READ invocation also sends its existing fixed STATUS preflight, giving at most73 STATUS queries across the complete plan. These transmit existing read requests; they send no Config/ProfileStore mutation. Use115200 baud, separate new outputs/journals and no retries. No target-metrics query is sent to unknown existing firmware.
6. Rehash/custody the actual captures and analyze original context, startup/runtime chords, entry/restoration eligibility and full field availability offline. Report access gaps honestly before preparing the separate candidate installation/physical-test packet.

**Physical entry boundary:** this approval covers already reachable routes. If Configurator or a backend needs an unknown entry/selection procedure, stop that route. No guessed cold-start chord, saved-backend selection, runtime/watchdog chord or recovery procedure is approved here. A later exact entry may be proposed from verified backup/source and owner knowledge; it needs separate approval. The existing watchdog backend path can save Config/defaults and must not be treated as persistently read-only.

## Exact command forms (not executed)

Use the retained binary at the absolute content-addressed location below. Replace session/location/port/output placeholders only with the approved session and actual confirmed values. Execute only the selected route, never an automatic loop through unknown interfaces.

```sh
GP_NATIVE_OBSERVER='/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/host-observer-artifacts/334fbd06e4541c120b0db423e5be7e112eb1f6f6/24ed913f55ca9e6ebcd6a8f1d13e4d504f122b395e2b7beaa4d8ec8545ffd473/mac_input_observer'
"$GP_NATIVE_OBSERVER" inspect --route '<xinput|switch|wup028>' --approved-session '<approved-preflight-session>' --output '<new-registry.jsonl>'
"$GP_NATIVE_OBSERVER" capture --route '<xinput|switch|wup028>' --approved-session '<same-session>' --purpose preflight --row PREFLIGHT --location '<confirmed-location>' --seconds 5 --count 3 --output '<new-preflight.jsonl>'
```

For WUP only, also specify `--port '<confirmed1..4>'`. Add `--allow-wup-init13` only if the reply explicitly includes the single0x13 operation. The approved-session flag is an execution guard, not evidence of owner approval.

If an ordinary Configurator session is already reachable and identified:

```sh
GP_NATIVE_F='/private/tmp/glyph-profile-native-20261020'
python3 "$GP_NATIVE_F/tools/glyph_serial_config_tool.py" --read --port '<confirmed-CDC>' --backup-out '<new-original-backup.json>'
python3 "$GP_NATIVE_F/tools/glyph_profile_store_production_tool.py" --port '<confirmed-CDC>' --journal-out '<new-status.jsonl>' status --output '<new-status.json>'
python3 "$GP_NATIVE_F/tools/glyph_profile_store_production_tool.py" --port '<confirmed-CDC>' --journal-out '<new-list-page.jsonl>' list --page '<actual-cursor>' --page-size 8 --output '<new-list-page.json>'
python3 "$GP_NATIVE_F/tools/glyph_profile_store_production_tool.py" --port '<confirmed-CDC>' --journal-out '<new-read-ID.jsonl>' read --profile-id '<actual-original-ID>' --output '<new-read-ID.json>'
python3 "$GP_NATIVE_F/tools/glyph_runtime_identity_tool.py" --port '<confirmed-CDC>' --context configurator --token '<fresh-nonzero-token>' --session '<actual-current-Configurator-session>'
```

Retain exact command/stdout/stderr/session provenance in new host files; the identity CLI has no raw-output-file flag. Root must verify the clean F script/source pins and binary hashes before use. No `--write`, native-packet execution, CREATE/UPDATE/set-reference/DELETE, flash/reset or physical test sequence is authorized.

## Stop conditions and evidence limits

Stop on ambiguous unit/location/port, access refusal, incomplete/wrong descriptor/header/report, timeout, non-normal/recovery STATUS, incomplete original-state preservation, unknown entry, or any uncertain operation. Keep durable observations; no automatic retry/reconnect, driver detach/seize/install, privilege/OS-settings workaround, erasure or rollback.

Preflight firmware is UNKNOWN until separately bound. F is the parser's expected-wire source, not cryptographic device/artifact attestation. A preflight capture cannot become candidate output evidence; the actual verifier refuses that promotion. Mac Switch reports do not establish Switch-console acceptance. WUP37 is adapter USB data, not electrical Joybus capture or proof of transparent adapter behavior. The miniscreen shows six values and one priority icon. Public backups omit raw filesystem/unrelated-directory/orphan/history/journal data; logical restoration later cannot promise raw byte rollback.

Hardware/Nunchuk remain NOT_TESTED; timing/highwater NOT_MEASURED; RT2 DEFERRED/UNRESOLVED; root cause UNPROVEN. Later instrumented runtime measurements cannot establish earlier startup peaks; GameCube/Switch timing stays NOT_MEASURED unless separately measured. Complete H1–H12, human HEP PASS, exact tested-source integration, fresh integration review and strict DONE remain required.

The requested decision is **approve this bounded preflight with or without the one WUP0x13 operation, or hold**. This separate approval is required by the owner's hardware boundary, not by an unresolved firmware design or a new review requirement.
