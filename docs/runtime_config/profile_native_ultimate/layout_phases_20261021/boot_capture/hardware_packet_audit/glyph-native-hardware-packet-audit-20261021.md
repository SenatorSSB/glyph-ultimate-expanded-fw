# GP-NATIVE-001 finite hardware-packet observation audit

OFFLINE_PREPARATION / NOT_A_DEVICE_PACKET. Final candidate Git SHA, tree, review, ELF/UF2 hashes/bytes and custody are **PENDING**. Resource P1 remains OPEN. All physical rows remain NOT_TESTED; target timing remains NOT_MEASURED. No source/Git mutation, network/device operation, build, fixture regeneration, installation or owner contact occurred. Only private `/private/tmp` audit artifacts were written. Requested/observed model and effort: UNKNOWN, not attested.

## Exact basis and preserved catalog

Source/evidence inspection is frozen to committed feature `a2a5c94d0a0bef3638b1ead1071ff58faaa7528f`; its tree and every inspected feature blob are in the companion JSON and `feature-pins.json`. Current source-free governance was read from supplied canonical `0a346975a452c5a5d00aac4e2a123783a9773db7`, including current frontnotes, GP-NATIVE-001 authority, boundaries and hardware contracts. This audit does not claim fresh remote verification or a final source review. The actively edited source worktree was not read as authority. The original owner directive was read first; SHA256 `05e0023d454d336be2d0a1762f434d5f808d36271c232cf790120ac497ce6d38`.

Read-only consistency checks verified all 69 original-manifest entries and 30 safe-manifest entries against committed bytes; 13 original packages/495 rows and five safe variants/39 rows remain intact. Each safe row matches its corresponding historical expected native state and all three literal serializer-field results under49→6,50→7,51→8. All observed values are null and statuses NOT_TESTED. This is data/hash correspondence, not a fresh production-evaluator run or hardware result. The safe manifest is SHA256 `b8cc4ad3262ad5ca147ab724387d49db96e2cff1b831cb7f6c7beb1d4da7fb1d`; original expected catalog remains `e2cf3540b28519c06dc66a9f11a17a19fb08536cecfc4808e1dd2d3d533481bd`.

The two completed private safe-stimulus/miniscreen inventories were reused. Their inspected source hashes match these pinned inputs; their candidate_hardware_packet_current.md hash changed because its later factual notes were appended. No old probe is silently rebound to final source.

## Existing tools and actual capabilities

| Existing path at pinned source | Actual available function | Output observation limit |
| --- | --- | --- |
| `tools/glyph_runtime_identity_tool.py` | Fixed16-byte identity request;72-byte response/current-session decoding, XInput or Configurator context | Identity only; no controller axes/buttons/report capture. Native body validation is separate; wire alone is not firmware/artifact attestation. |
| `tools/glyph_native_target_metrics_tool.py` | One fixed read-only XInput GET_SNAPSHOT;160-byte metrics response, raw/request custody, strict validity/source/generation decoding | Timing/stack observations only; no OutputState or gamepad-report fields. |
| `tools/glyph_serial_config_tool.py` | GET_CONFIG backup; separately guarded native context/restore packet through existing SET_CONFIG | Config bytes/context, not live virtual outputs or reports. No command execution is proposed here. |
| `tools/glyph_profile_store_production_tool.py` | STATUS/LIST/READ and separately guarded create/update/reference/delete operations | Stored profile/reference metadata and payloads, not gameplay output/report observation. |
| `src/comms/B0XXInputViewer.cpp` / InputDisplay | Physical-input display/25-byte viewer records | Original physical input; not native digital/analog output. |
| MenuButtonHints dashboard | Four native stick integers(raw−128), two raw native analog trigger numbers and one priority output icon | Useful held-state sub-observation. Simultaneous digital bits and actual transmitted report are not displayed. Actual dashboard availability/readability remains unverified. |
| `prepare_hardware_fixtures.py` / `prepare_safe_hardware_fixtures.py` | Offline production evaluator and literal serializer assignment fixtures | Expected outputs only; USB/PIO/host delivery absent. `backend_LR_Z_source_assertions.json` is explicitly HOST_SOURCE_ASSIGNMENTS_ONLY. |
| `dolphin/*.ini` | Static controller binding presets | No bundled capture implementation or established owner observer. Not evidence that Dolphin is installed or supplies raw GC reports. |

The inventory pinned341 tracked tool/script source files under tools/scripts (excluding test fixtures), checked explicit host-input/HID/XInput APIs, inspected relevant serial operators and inspected Dolphin presets. **No repository host controller-report reader is identified.** This is not a claim that no external tool exists. The owner's external tools, OS and report-viewer capabilities remain UNKNOWN. SDK build-log hidapi entries are dependency files, not an approved/available chapter report observer.

## Route-specific expected observation boundary

| Actual route | Source-backed transmitted fields | Required concrete observer gap |
| --- | --- | --- |
| USB XInput | A/B/X/Y, LB/RB, LT/RT bytes, start/back/home, D-pad bits/clicks; four scaled signed axes (`XInputBackend.cpp:47–73`) | Identified host and actual report/state observer that records every relevant simultaneous button and both triggers/axes. Serial identity/metrics and OLED do not read these fields. LT/RT have no separate digital-bit representation: digital trigger forces byte255; otherwise native analog byte is used. |
| USB Switch | A/B/X/Y, L/R, ZL/ZR, plus/minus/clicks/home/capture, hat; scaled/inverted four axes (`NintendoSwitchBackend.cpp:125–151`) | Identified host/screen or report observer, exact displayed/report fields and transformations. Native analog trigger values are not serialized by this backend. Generic game behavior or native OLED cannot establish ZL/ZR/report delivery. |
| GameCube adapter→Switch | A/B/X/Y,Z=buttonR,L/R=triggerLDigital/RDigital,start,D-pad; four raw stick bytes and two separate analog trigger bytes (`GamecubeBackend.cpp:45–71`) | No known raw-GC observer in this setup. Adapter model/mode/translation and downstream screen are unidentified. A Switch-side result may describe downstream behavior but cannot directly prove pre-adapter GC L/R/Z bits or original analog bytes. Explicit H6 actual-GC-bit requirement remains open. |

Externally meaningful controller outputs and each route's existing serialization are the acceptance target. Internal LS/RS direction/modifier bookkeeping bits are listed separately in the projection and are not falsely treated as extra wire fields. OLED numeric output is before backend scaling and is asynchronous, without a coherent report/frame latch. No GameCube/Switch acceptance transfers from XInput.

## Safe fixture observation mapping

`safe_expected_observer_mapping.json` carries all39 existing safe rows without editing their expectations: exact physical IDs/names, complete expected native state, externally meaningful digital fields, separate internal bookkeeping, exact three-backend assignment fields, six expected dashboard integers and the first visible output field. It leaves observations null/NOT_TESTED. The first-field name is retained because icon labels also depend on actual Config/backend selection.

| Existing safe stimulus | Source-derived native sub-observation | Necessary report observation |
| --- | --- | --- |
| complete_sample_1/2 step1 `[8]` (LF8) | Four sticks128; A + both digital triggers; native trigger140/140. OLED four zeros,140/140,A icon. | XInput A1,LT255,RT255; Switch A1,ZL1,ZR1; GC A1,L1,R1,Z0,analog140/140. Complete row JSON also supplies all expected false fields. |
| Same package step0 or8 `[]` | Native neutral, trigger0/0, no outputs | Route-specific neutral/control report; XInput catalog center is128, not an assumed hostzero. |
| complete_sample_1 step2 `[6]` then step3 `[6,2]` | LS128/51 then128/128; A remains true through neutral SOCD | Observe actual route axes plus A simultaneously, retaining ordered settled states. OLED supports those native values/A but not frame timing. |
| complete_sample_1 steps4/5 `[7]`, `[6,7]` | LS78/84 and A for both; LS-down bookkeeping differs internally | Required external A/table-output OR/composition observation, without demanding internal bookkeeping as a wire bit. Sample2 gives79/85; OLED(-49,-43), versus sample1(-50,-44). |
| forced_wins/loses/filter step2 `[6,24]` | Winner:79/81,A; loser:128/169,A; filtered loser:128/169,Afalse | Output-distinguishing coordinates and A presence/absence; no table-name-only PASS. Other expected report fields remain part of full row. |

The existing495-row catalog has491 rows with native triggers0/0 and both digital triggers false, and four complete-sample rows with140/140 and both true. The safe39 rows have35 such zero controls and four140/both-true rows. **There is no existing physical fixture with only one digital trigger, digital-true/analog0, or analog255 with digitalfalse.** Do not invent an extra approved isolation fixture. The separate host serializer assertion uses17/23 with L/R/Z set; it is host-only and is not an admitted physical package/stimulus.

For H6, a future direct XInput report255/255 observation is evidence of those transmitted bytes. Combined with actually observed OLED140/140 and the pinned source/fixture, it supports a source-conditioned inference that the digital override produced them; it is not a direct read of a nonexistent XInput digital-trigger wire bit. A report255 alone cannot distinguish native digitaltrue from analog255. GC has separate real L/R bits and analog bytes, so this alias argument cannot replace its explicit bit observation. Switch likewise needs actual ZL/ZR observation. A hides L/R on the OLED in every four complete-sample trigger case.

The existing safe-input preflight still applies: confirm actual Mk6/mapped LF6/7/8 access, exact context replacement, fresh Config startup/mode chords against all planned held sets, release all controls before reconnect/reboot. Source-safe carrier selection is not verification of the owner's unit. Do not use original49/50/51 as physical packet carriers.

## Minimum later packet changes and owner information

1. After resource closure, bind final exact source/tree/review/build/resources/descriptors/artifact/custody and recheck these source/script/fixture pins. Keep old catalogs/manifests and failed checkpoints immutable; append a concrete final packet/selection with explicit PENDING identities until known.
2. Map each selected H1–H12 physical row to exact expected externally meaningful outputs, actual route report fields and an identified observer/capture. Preserve honest sub-observation/partial states. H1/H10/H11/H12 need actual baseline, attestation, safe preflighted negative, and restoration evidence; nothing here supplies those results or approves a corrupting write.
3. At the final hardware gate, obtain only missing concrete context: computer/OS or Switch host; exact observer/test screen and fields it exposes on each route; GC adapter make/model/mode and any already available raw-GC observation setup; confirm unit revision/accessible safe carriers and the actually readable dashboard. Existing serial port, Config/store backups and mode-chord checks belong to the separately approved session's preflight, not an improvised pre-approval device connection.
4. If available observers cannot meet required backend observations, record the concrete gap and request the substantive observer/equipment/validation decision. Do not silently narrow H6, assume adapter equivalence, add firmware output telemetry, install a tool, amend the frozen protocol or infer PASS. No external tool recommendation is made by this audit.
5. Retain exactly the instrumented firmware that is built and physically tested. Source verified: `RuntimeIdentityService.hpp:41–89` creates the observer guard before Snapshot/TX; its destructor records the Poll span after the response has been serialized. Take a second fresh-token snapshot at least1000ms later in the same boot to include the previous call's encoding/TX overhead (`NativeTargetMetrics.cpp:154,205–241`). Final maximum-counter stores are outside their own timed spans; scan publication may lag. Record raw captures, measurement conditions, native generation, sequence/validity/source flags,16-pair timer calibration and explicit PARTIAL/INVALID outcomes. RecordActivation retains only the latest provisional boot interval until the first native frame; do not presume generation1 or2 in final evidence. Session expiry at one-hour uptime is sticky; choose bounded fresh-boot measurement coverage rather than assuming a long495-row session remains valid. Runtime observations do not cover earlier startup or replace structural stack proof; GC/Switch timing remains NOT_MEASURED.

No final owner question is sent now: resource/source/build gates are still open. This is a bounded preparation result, not independent final review, hardware approval, hardware acceptance or strict DONE.

## Durable artifacts

- `/private/tmp/glyph-native-hardware-packet-audit-20261021.json`: audit state, exact trees and pin manifests, consistency outcomes and prior-probe correspondence.
- `/private/tmp/glyph-native-hardware-packet-audit-20261021/feature-pins.json`: every inspected committed feature input, SHA256 and Git blob.
- `/private/tmp/glyph-native-hardware-packet-audit-20261021/initial-pins.json`: canonical current-document pins and both basis trees.
- `/private/tmp/glyph-native-hardware-packet-audit-20261021/host-tool-inventory-search.json`: exact341-file tracked search inventory, regex and results; bounded absence claim only.
- `/private/tmp/glyph-native-hardware-packet-audit-20261021/safe_expected_observer_mapping.json`: all39 safe rows and observation projection.

Nunchuk remains NOT_TESTED, RT2 deferred, root cause UNPROVEN. Earlier accepted firmware custody and source evidence are not transferred to native firmware.
