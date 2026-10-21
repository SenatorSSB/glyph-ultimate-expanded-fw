# Candidate334f session plan — DRAFT, NOT APPROVED, NOT_TESTED

This document performs no commands. All commands below are reviewable templates from exact F scripts; unresolved session values are explicit placeholders. No device is opened or physical action requested. Final resource/software gates, independent packet review, actual observer resolution and owner approval of a separate concrete candidate-specific packet precede any controller operation.

## Exact custody and source qualification

Use only retained F334fbd06e4541c120b0db423e5be7e112eb1f6f6/tree0483dbb0cc8f7eb5a1c93cb1d91044f4d3dcf999, UF2 SHA41305f260d42e8206bf4a2fb06c88912416e49cd8a68bc13ce3d3c7605306982/1041408 bytes, ELF SHAa42bd2bf6ab1efd3cac565b27d9e236c0128da3be84a5977e5c739db2697c15d/5597092 bytes. Both custody files were independently rehashed in this preparation. Build RAM197872/delta10528, flash508564; exact generated descriptor hashes are in candidate_packet_draft.json. Retain diagnostics. No rebuild substitutes for these bytes. Wholelinked resource P1 remains OPEN under a separate worker.

The audit correspondence's135/136 unchanged inputs support reuse only for those exact inputs. config.cpp changed: adopted4209 independent review explicitly assessed setup display/migration/backend phase splitting, order and early returns, and unchanged selector/initializer suffix. Final334f source review binds all firmware delta outside its five selected paths to4209, including config.cpp; its protected-call/nonreentry findings and archived both-ABI raw comparisons are limited source/equivalence evidence. This establishes a source-grounded qualification for old fixture reuse; it establishes neither hardware acceptance nor final whole-stack closure.

## H1 and safety/preservation preflight

Confirm actual Mk6 revision, mapped LF6/7/8 physical access, actual primary backend, host OS, existing actual observer and exactly which fields it exposes. Confirm existing MenuButtonHints dashboard is readable. This draft treats every unknown as UNKNOWN. B0XX/InputDisplay show physical input, not OutputState. Validate all planned held sets against the actual fresh Config: no nonempty startup/mode chord may be a subset of any set; replace first-source remaps using native-packet rather than append duplicates. Release everything before reconnect/reboot. Selected rows never use MB1/2/3. Supplemental legacy ordinary33/32/17/26 and other declared controls still need actual unit/chord preflight; source mapping is insufficient to assert actual unit accessibility.

After separate approved session authorization, capture original ordinary baseline on every actual affected route: neutral, four directions/diagonals on both sticks, each ordinary mapped button/trigger and representative simultaneous sets, reconnect. Expected ordinary outputs must be derived from the actual backed-up Config/profile using exact existing source and checked against retained baseline observations. The current original Config is UNKNOWN; no fabricated default baseline appears in this draft. Preserve anomalous/unsupported fields as gaps.

Existing Config read/backup interface:

```sh
python3 <F-script-root>/tools/glyph_serial_config_tool.py --read --port '<approved-port>' --backup-out '<new-original-backup.json>'
python3 <F-script-root>/tools/glyph_profile_store_production_tool.py --port '<approved-port>' --journal-out '<new-status.jsonl>' status --output '<new-status.json>'
python3 <F-script-root>/tools/glyph_profile_store_production_tool.py --port '<approved-port>' --journal-out '<new-list-page.jsonl>' list --page '<actual-page>' --page-size 8 --output '<new-list-page.json>'
python3 <F-script-root>/tools/glyph_profile_store_production_tool.py --port '<approved-port>' --journal-out '<new-read-ID.jsonl>' read --profile-id '<actual-original-ID>' --output '<new-read-ID.json>'
```

Complete pagination and READ every available original ID/revision/payload; capture active refs, identity where supported, schema/engine, incarnation/generations/highwater/receipts and exact raw GET_CONFIG SHA. Validate backup custody/readback before mutation. Public APIs do not export the raw filesystem, unrelated directories, orphan contents, every historical revision, or transaction journal. Preserve supported broader filesystem domain without a pristine-history demand. Any inability to preserve original ordinary state stops mutation. Existing recovery restrictions and RT2 deferral remain; no RT2 diagnostic, erase, format, factory image or recovery experiment is included.

Verify source-supported manual known-good restoration route before first change. Retained accepted GP-BIND-003 source307d72347653c079ec8ec6e9b6ecae3c30ae536c, UF2 SHA83aa255a7843fbc96af37c679e92408808d9de0f004271315f968db73c37747b/979456 bytes was rehashed here. It is custody, not current device identity. The existing owner-reported recessed BOOTSEL/RPI-RP2 manual route must be confirmed applicable in the approved packet. No flashing automation or recovery action is defined by this preparation.

## H2–H8 physical data

candidate_packet_draft.json provides334 rows:190 exact catalog projections and144 new separate M6 data. physical_selection_index.md is a compact index; full native state, all true/false meaningful digital bits, internal bookkeeping, all three literal backend assignment fieldsets, exact profile/context hashes and each ordered history are authoritative in JSON. Execute only the later reviewed/approved subset/order. All78 SOCD rows remain complete in order across all six policies; do not insert releases into those groups. Independent supplemental singleton groups start fresh. For performance/owner burden, route repetition is decided only once real observers are known; a single row is not automatically334×three route passes. Required affected-route coverage may not be silently omitted.

H6's isolated native profile is new validated test data derived from existing F check.program: LF6→digitalL, LF7→digitalR, LF8→buttonR(Z), plus all combinations. Existing complete-profile LF8 supplies one-input A+L+R; LF6/LF7 supply independent A OR. Actual GameCube l/r/z fields must be separately observed. XInput LT/RT255 alone aliases native analog255; observed native dashboard140 together with actual transmitted255 supports source-conditioned digital override inference, never a nonexistent digital-trigger wire bit. Switch requires actual ZL/ZR. GCadapter→Switch does not prove original GC raw L/R/Z/analog bytes.

## Exactly two owned disposable IDs and matched context

Do not overwrite any original ID/payload. Use CREATE's actual allocated stable IDs as testA/testB; never invent numeric IDs. Keep a fresh status/fence and new immutable request/journal for every operation, without automatic retry. Reuse those two IDs by UPDATE through all candidate revisions. Existing mutation admission checks production status, incarnation/generation/token and unknown outcomes. CREATE example:

```sh
python3 <F-script-root>/tools/glyph_profile_store_production_tool.py --port '<approved-port>' --journal-out '<new-createA.jsonl>' create --name GP-NATIVE-A --rank 0 --profile-json '<exact-approved-profile.json>' --incarnation '<fresh-incarnation>' --store-generation '<fresh-generation>' --token '<fresh-unused-token>' --request-out '<new-createA-receipt.json>'
python3 <F-script-root>/tools/glyph_profile_store_production_tool.py --port '<approved-port>' --journal-out '<new-updateA.jsonl>' update --profile-id '<owned-testA-ID>' --profile-revision '<fresh-revision>' --profile-json '<exact-approved-profile.json>' --incarnation '<fresh-incarnation>' --store-generation '<fresh-generation>' --token '<fresh-unused-token>' --request-out '<new-updateA-receipt.json>'
```

Prepare native context using a fresh raw GET_CONFIG backup/SHA and an existing Ultimate row. Without --execute this is host-only:

```sh
python3 <F-script-root>/tools/glyph_serial_config_tool.py --native-packet --expected-current-backup '<fresh-current.json>' --expected-current-sha256 '<raw-sha256>' --session '<approved-session>' --mode-index '<existing-Ultimate-row>' --context-json '<exact-approved-context.json>' --native-profile-json '<matching-profile.json>' --receipt-out '<new-context-receipt.json>' --journal-out '<new-context-journal.jsonl>'
```

Only a separately approved execution adds --execute --exclusive-configurator-session --port '<approved-port>' and fresh custody filenames. This sends existing SET_CONFIG4 once, checks exact fresh bytes/readback and stops on uncertain outcome. SET_CONFIG has no atomic generation CAS, so exclusivity is essential. Following context success, use the checked persistent reference with fresh fences:

```sh
python3 <F-script-root>/tools/glyph_profile_store_production_tool.py --port '<approved-port>' --journal-out '<new-reference.jsonl>' set-reference --profile-id '<owned-test-ID>' --mode-index '<existing-Ultimate-row>' --config-generation '<fresh-Config-CRC>' --incarnation '<fresh-incarnation>' --store-generation '<fresh-generation>' --token '<fresh-unused-token>' --request-out '<new-reference-receipt.json>'
```

Manually reinitialize/reboot under the approved route, all inputs released. Capture fresh Config/store/readback and current gameplay identity. Never write a whole Config from pre-reinitialization live bytes after checked reference; that can overwrite the durable selection. Context and selection are distinct operations.

## H9/H10 two independent complete profiles and truthful identity

Place exact safe complete_sample_1 on testA and complete_sample_2 on testB; they contain independently complete native tables/modifiers/bindings. Capture each payload/profile/body/context pin and allocated revision/ID. Select A with checked reference, reinitialize, confirm current XInput identity and all S021–S029 outputs. Select B, reinitialize, confirm identity and S030–S038. Compare forced output A(78,84) versus B(79,85), plus neutral/A/L+R/OR/SOCD rows. Reboot/reconnect each and repeat decisive output/identity; reselect A and verify its original payload/revision unchanged. Actual20-profile capacity remains host LittleFS proof, never20 physical tests.

Identity decoder payload digest is SHA256 of literal domain `Glyph.RuntimeIdentity.UltimateProfile.v1\0` plus deterministic profile wrapper bytes. Native context digest inside each validated body is separately bound. schema5 by itself cannot establish active native correspondence. Match actual current session/backend/row/requested reference, incarnation, active ID/revision, schema and payload digest. Engine1/encoding1 validation remains separate from72-byte wire; source SHA label is not cryptographic device/artifact attestation.

```sh
python3 <F-script-root>/tools/glyph_runtime_identity_tool.py --port '<approved-XInput-CDC-port>' --context xinput --token '<fresh-token>' --session '<actual-current-boot>'
```

Retain decoder JSON and exact request/session/candidate provenance. This existing identity CLI does not expose a raw-output-file flag; do not invent one or a report-reader capability. Configurator identity observes current Configurator status, not an earlier gameplay session. Stored UPDATE in Configurator must not be described as observing a newer active gameplay program. The source/host latched-program test remains separate where no supported same-session update route exists. No concurrent writer/hot update is proposed just to manufacture an observation.

Diagnostics use the existing fixed read-only XInput snapshot and exact retained F source label:

```sh
python3 <F-script-root>/tools/glyph_native_target_metrics_tool.py --port '<approved-XInput-CDC-port>' --token '<fresh-token>' --session '<actual-boot>' --expected-source-sha 334fbd06e4541c120b0db423e5be7e112eb1f6f6 --request-out '<new-request.json>' --raw-out '<new-response.bin>'
```

Take another fresh-token snapshot at least1000ms later in the same boot for previous observer encoding/TX overhead. Preserve raw captures, sequence/validity/source/generation flags,16-pair calibration, actual stimulus conditions and PARTIAL/INVALID flags. Current response excludes its own exit maximum; final max stores and scan publication lag remain. One-hour expiry is sticky: use bounded fresh-boot sessions. No presumed native generation1/2, WCET/cycle/startup peak, GC/Switch timing or structural-stack acceptance.

## H11 valid mismatch refusal — component-tested, final session preflight pending

The separate refusal_context_mismatch profile is byte-exact compatibility body/contextdigest-empty combined with the existing safe complete_sample_1 context (SOCD6↔2). Both parts are individually valid. Actual F SetConfig selects NativeUnavailable and all six tested held sets produce fully neutral native state; no legacy-slot fallback. Runtime identity source implies snapshot_unavailable in this state, with neutral persistent identity fields. This identity status was source-inspected, not independently executed in this new component test.

Proposed reversible sequence uses only the two owned IDs: first valid complete profile A plus matched safe context; leave that safe context intact, then checked-reference valid wrong-context compatibility profile B and reinitialize. Do not use native-packet to write a malformed/mismatched Config: its guard correctly refuses a mismatched profile/context pair. PerformCheckedReference validates the existing mode/record/Config and commits engine1; Ultimate later performs context match. Final independent packet review must preflight the full existing checked-reference/durable Config/reboot/recovery path, including validation admission, before this becomes an approved physical negative. Recovery is checked-reference back to known matching A under unchanged safe context and approved reinitialize. No corrupting bytes or original profile edit is needed. Stop on any uncertain write, unexpected engine/status or failure to regain ordinary control.

## H12 logical restoration and final stop

Capture fresh current backup/SHA. Prepare exact original logical restoration with native-packet:

```sh
python3 <F-script-root>/tools/glyph_serial_config_tool.py --native-packet --expected-current-backup '<fresh-current.json>' --expected-current-sha256 '<current-raw-sha>' --restore-original-backup '<original.json>' --original-sha256 '<original-raw-sha>' --session '<approved-restore-session>' --receipt-out '<new-restore-receipt.json>' --journal-out '<new-restore-journal.jsonl>'
```

The same separately approved execution/exclusivity/port flags apply. It preserves current firmware-owned root/migration/transaction receipt metadata and rejects other incarnation. Restore original ordinary fields/references first; reinitialize, verify ordinary output against captured H1 baseline and original profile bytes/checksums/identity. Only then DELETE exactly owned testA and testB with fresh explicit incarnation/generation/token and new receipt/journal, as in pinned native_context_operator.md. Re-read complete available store directory/original IDs/payloads and Config; record anomalies and exact permitted differences.

Highwater IDs, tokens, generations, retained revisions and transaction metadata are monotonic. Cleanup is logical ordinary-state restoration, not raw filesystem byte rollback. Existing public interfaces cannot reconstruct an original raw filesystem image. Do not delete original IDs or claim erased metadata. Preserve unrelated directories and admitted recovery states. Any uncertainty stops mutation with durable readback and no retry; do not auto-flash, factory-erase or reopen RT2. Hardware results remain NOT_TESTED until genuine owner evidence, and no route acceptance transfers.
