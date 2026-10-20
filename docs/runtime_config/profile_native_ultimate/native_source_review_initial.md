# Fresh independent source/safety review — profile-native Ultimate

**REQUEST_CHANGES** for candidate `9e16e1c36babdd5c655893b35ae92cd39725c37f` (F). One material P1 resource defect blocks source approval and device handoff. The native semantics, ownership/lease design, and targeted host checks reviewed here otherwise pass their stated source scope; this is not hardware acceptance or chapter completion.

## Exact scope and authority

Read the original attached consolidated owner directive, repository AGENTS/current governance/queue/boundary, architecture proposal/review, immutable M1 freeze, implementation contract and relevant source/evidence. Sole READY GP-NATIVE-001 authorizes the complete bounded chapter. Compared the complete production and host-tool/test delta from source-free authorization A `753932c8fbec3e002d455f4cd2b9b1dbc0ed896f` to F; original product baseline is B `976ba2195b72046b32f7ecdd41063e7bad791ded`.

Detached read-only checkout: `/private/tmp/glyph-native-source-review-20261020`, exact HEAD F. Tracked files remained untouched. The pre-existing untracked `.platformio-home` is a dependency symlink; no repository mutation/publication, firmware build, flash or device/profile operation was performed by this reviewer. Host builds/tests and scratch evidence were written only under `/private/tmp`; Python bytecode was disabled. Default read-only GitHub verification failed DNS, then permitted network-enabled `git ls-remote` succeeded and returned canonical A. No authentication or account mutation occurred.

Closed source/test allowlist: PASS, no non-doc path outside the exact adopted arrays. Production `src/include/HAL/schema` bytes are unchanged from `45d713bee585969ccb923c7551bc6f7c7696816a` through F. Later `fc563760c9488d7f5a95156d262b42b71a62ad18` differs from F only in docs/evidence (source/tools correspondence independently verified); its newly built exact ELF was inspected read-only to confirm the same stack finding in actual linked code. The report verdict remains against F and its identical production source.

## Blocking finding NATIVE-REVIEW-P1-STACK

**[P1] Keep ordinary CREATE within the frozen 2,048-byte core0 stack budget.** Source anchors are `HAL/pico/src/comms/ConfiguratorBackend.cpp:738` (synchronous Create), `HAL/pico/src/core/ProfileStore.cpp:954` (WriteProfile publishes while its frame lives), and newly expanded inline observation in `include/core/RuntimeIdentity.hpp:55` (the production caller `config/glyph/common/src/config.cpp:317` now holds a 192-byte loop frame rather than baseline 40). The protected budget is 2,048/core; physical scratch-bank space 4,096 is not authorization to exceed it.

This is not a blind sum of the archived 2,784-byte function inventory. I resolved actual inlining, caller lifetimes, branch feasibility and tail-call behavior using pinned production O3 ARM objects, their disassembly, source, `.su`/cgraph evidence, and then the exact linked successor ELF. Ordinary fresh file creation takes `lfs_file_rawopencfg`'s new-name commit branch (`lfs.c:2884`), through orphaningcommit → relocatingcommit → splittingcompact → compact. It requires no powerloss, unrelated subdirectory, orphan/half-orphan recovery or inferred hardware fault.

An independent host-only witness against the exact pinned LittleFS source and production 512-KiB geometry creates 64 accepted-length flat-root record-style filenames. A temporary observation counter at compact entry is enabled only around the rawopencfg new-entry `lfs_dir_commit` call. It reports:

`PASS flat-root new-file creation reaches lfs_dir_compact; first_file=16 compact_entries=6`

The observer changes no library behavior and performs no target instrumentation. Scratch sources/executable/result are `/private/tmp/glyph-native-stack-witness/`; source SHA256 `3ede3a5ee496159150b9f5a1bacac98d157eb1f761e19d7d58a9b0fa4528ca6e` matches the manifest. This supplies a concrete feasible branch, not a whole-target stack measurement.

The retained frames on that branch are:

| Function | Bytes |
| --- | ---: |
| main | 48 |
| loop | 192 |
| ConfiguratorBackend::SendReport | 96 |
| ConfiguratorBackend::HandleProfileStore | 312 |
| ProfileStore::Create | 208 |
| ProfileStore::WriteProfile | 256 |
| Publish clone.part.0 | 80 |
| MountedStorage::CheckedWrite | 24 |
| CheckedStorage::WriteFile | 216 |
| lfs_file_open | 16 |
| lfs_file_rawopencfg | 80 |
| lfs_dir_orphaningcommit | 160 |
| lfs_dir_relocatingcommit | 136 |
| lfs_dir_splittingcompact.constprop.0 | 192 |
| lfs_dir_compact | 136 |
| **Total at compact entry** | **2,152** |

Even excluding main completely leaves **2,104**, already above 2,048 before compact calls traverse, a program callback, ROM flash, any interrupt frame or other indirect code. Main/loop/dispatch/storage frames have ordinary calls with work/epilogues after them; relevant library transitions use BL, not frame-releasing tail branches. In particular: WriteProfile calls separate 80-byte `Publish [clone .part.0]`; Publish calls MountedStorage via BLX; WriteFile calls lfs_file_open directly because Open was inlined; rawopencfg calls orphaningcommit at +0x1b8; orphaningcommit calls relocatingcommit at +0xc0; relocatingcommit calls splittingcompact at +0x1ca; splittingcompact calls compact (including +0x504) and retains its frame. The exact final ELF retains the same prologues/call relationships. Thus mutually exclusive function maxima are not being added to establish this lower bound.

The archived collector currently double-counts the separately listed 88-byte Open frame while missing the real 80-byte Publish clone, despite its comment claiming Publish is inlined. Correct this evidence generation as part of the resource repair. Its 2,784/2,632 record-open and 2,184/2,032 decode figures must stay conservative inventories, never feasible peak or PASS claims. The independent lower bound above avoids the uncertain powerloss path entirely.

Required correction: reduce bounded caller/workspace lifetimes or move strictly synchronous core0 scratch into bounded ownership within the already approved static caps; then demonstrate all feasible affected ordinary/decode/recovery branches and required interrupt allowance fit 2,048 using actual repaired build/disassembly. Do not merely remove 104 bytes from compact-entry arithmetic: deeper traversal/callback/flash paths consume additional stack. No SDK edit, stack/reserve/partition increase, extra wire buffer, new runtime diagnostic or hardware claim is authorized by this finding. The change affects an existing shared storage path, and the new inline native identity logic adds 152 bytes to loop; baseline debt does not waive an affected Tier-2 safety contradiction.

## Verified semantic and ownership results

Executed `PYTHONDONTWRITEBYTECODE=1 python3 tools/check_glyph_profile_native_ultimate.py` at exact F: **exit 0**. Full raw output `/private/tmp/glyph-native-source-review-tests.log` and hash are in the machine report. It executes production native codec/evaluator/dispatch/storage, not a second call to a rewritten common legacy resolver. Verified from test source and execution:

- Independent 72-case full-output legacy corpus; exact frozen Stage-C 1,222,420 replay from 37 converted snapshots with original reorder/A-B-A/effect assertions; additional V1/V2/V3 1,124,032 comparisons each. These broader counts are not claimed distinct input vectors.
- Original/pre/post observation, six SOCD policies with history/release sequences, many-to-one and duplicate-physical remap characterization; native control flow calls the existing remapper and SOCD once per frame. The shared default hook delegates unchanged to legacy digital/analogue functions.
- Complete 18-family converter/evaluator coverage: LS/RS direction references; default tables; X1/X2/Y1/Y2; Tilt1/2/3/source combinations; Mode/sublayers; priority/exclusions/fallback; A/B/X/Y/Z; L/R and final-digital trigger guards; multi-output OR; clean genuine Down+A; ordinary forced-table+A; historical LT6 conflicts; RF5/6/7 compounds; C-stick diagonal/axis transforms; Dpad/bypass; null; noncenter/asymmetric 28×9 raw tables. Source checks cover actual backend L/R/Z carriers, without new backend mapping claims.
- Native evaluator has no intrinsic Glyph-slot/phase selectors. Tokens select physical/original, remapped or post inputs; role dependencies/stages are validated before publication. Generic table/binding rebinding witnesses cover 18×60 carriers with old carrier inert. These synthetic rebinding witnesses are distinguished from full source-family correspondence.
- NativeUnavailable clears all bits/sticks/triggers and bypasses legacy/Nunchuk tails. Valid native preserves the accepted legacy-unowned bits and Nunchuk tail; physical Nunchuk remains NOT_TESTED.
- Actual LittleFS 20 independently complete native profiles, revisions/staging/reserve, duplicate/read/health/reboot/two-profile selection, same-kind previous recovery, cross-kind rejection, context mismatch and unavailable paths. Bodies remain individually in flash; no cache-all design, hot swap or new store protocol. Directory64/storage524288/reserve16384 unchanged.
- Active and candidate storage are distinct. Owner address/published view/generation are checked; copied views and changed generations reject. Ultimate latches the active generation. Stored r3 after later update leaves actual active r1 wrapper/body/view/digest until reboot. The actual identity observer tests distinguish this from latest stored metadata.
- Request presence scan binds immutable RX bytes through decode/request hash/transaction. Incoming lease is released and wrapper cleared before frame reuse for response. READ uses separate record wire; prior read lease is released before that wire is overwritten. Duplicate preserves through the one owned candidate before nested admission reads. Config/Persistence/legacy-load embedded callbacks reject native payloads, including legacy schema plus empty tag8, before copies/persistence; transient callbacks are cleared.
- Actual COBS CREATE, 100 READs, checked mode-reference engine persistence, maximum wrapper3341/record3373, mixed-empty-tag rejection and exact response bytes pass. Malformed dimensions/references/domains/stages/cycles/unions/padding/priorities/pool/versions reject before publication.
- Named source mutations fail the intended assertions: intrinsic slot leak, bit identity, repeated SOCD, cancelled A, losing table leakage, array-order priority, copied owner, stale generation, incoming callback alias, encode size, skipped embedded callback, omitted request payload, overwritten/released response lease. The unmutated controls pass; mutation generation alone is not reported as a kill.
- Current Custom default hook 98,304 complete-output comparisons passes. Directly affected historical adapters retain original assertions/fixtures; broad stock consumer suites were not redundantly rerun here because another independent worker owns those regressions. Archived default-enum native proof was inspected; this reviewer reran short-enum, while fresh ARM both-ABI layout was independently owned by the coordinator.

All three root findings are corrected in the actual source: forced policy writes all nine target-table coordinates and adds only an ordinary rule plus independent A (including empty-preprocessing wins/loses); mixed legacy/native source rejects, with raw protobuf field presence checked before normalization; correspondence emits concrete tables/role map/rules/bindings/sources/effects and literal clean-policy changes. No fixed-force side resolver remains.

## Resource and measurement boundaries

PreparedView is exactly560 and active+candidate exactly7800 in both retained ARM ABI probes, satisfying but exhausting their frozen caps; frame data132≤144. New structural validation co-live scratch184≤256 is distinct from the reused SHA path. Static SHA storage uses placement construction only (no heap); observed callers are synchronous core0 admission/initialization/identity after output generation, with no nested call or IRQ/core1 call to that shared scratch found. SHA Final/Transform stack remains part of real call-chain assessment, not hidden by the new-local cap.

Read/hash frames are sequential with filesystem read/open, not co-live with them. The ordinary native read/hash chain has the reported finite1620-byte C inventory before unknown interrupts/ROM; the conservative decoder2184 is not itself proof of a feasible overflow because it adds mutually exclusive substream phases. Neither is a whole-target PASS. The concrete CREATE bound already blocks independently.

Exact F firmware build was pending at review start. Coordinator later supplied the clean source-identical docs successor fc563760 exact ELF SHA256 `51dad8fed79c8e5726827d7702c86db2e578cff3b4663e8a7d808e23b9343b5d`; independently hashed and inspected it. It confirms the retained-frame defect. This report does not adopt its build/UF2/static/flash custody as complete candidate M6 proof and makes no artifact/hardware approval. Final repair needs its own exact build/custody and focused correspondence review. Target polling/activation time, actual whole-stack highwater and final IRQ/ROM bound remain NOT_MEASURED/uncertified; no measurement transport was added. Nunchuk NOT_TESTED; root cause of historical failures UNPROVEN.

`git diff --check A..F` reports whitespace in preserved raw logs/generated evidence, not production source. These evidence-only whitespace findings are not additional behavior defects. No test or path waiver was used to clear P1.

## Evidence custody and return

Machine-readable report: `/private/tmp/glyph-native-source-review-results.json` (includes object hashes, witness and test log hash). Independent disassemblies: `/private/tmp/glyph-native-review-{configurator,store,checked,lfs,config}-disassembly.txt`, linked ELF `/private/tmp/glyph-native-review-final-elf.txt`. Existing writer provenance with exact compiler recipes/source/object hashes is in fc563760 `docs/runtime_config/profile_native_ultimate/stack_branch_evidence/manifest.json`; the original compile identity string remains an intermediate marker, so the separate exact linked ELF is the stronger confirmation.

One bounded source/resource repair is needed. After it is frozen, resume this same independent review for the repaired subset and final source correspondence; no review-of-review loop. Do not hand off device actions, merge or declare DONE before resource closure, exact final build/custody, separately approved concrete device packet and exact human hardware/HEP PASS.
