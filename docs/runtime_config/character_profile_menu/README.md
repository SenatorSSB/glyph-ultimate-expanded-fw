# Native character profile menu — exact candidate and unexecuted installation

Status: **CANDIDATE_VALIDATED — OWNER_APPROVED_HARDWARE_OPERATION_PENDING**.
The owner corrected the runtime-label count to **two** and explicitly chose to
hide built-in/legacy Ultimate choices in compact mode, retaining their execution
contexts. [Direct authority and bounded order](OWNER_DIRECTIVE.md) resolves the
initial semantic stop without a name heuristic or schema change. Historical
GP-NATIVE-002 evidence and its accepted source remain unchanged.


## Final executable owner packet — R2

[OWNER_PACKET.md](OWNER_PACKET.md) is packet **CPM-HW-1DE243C7-R2**;
[fresh independent review](packet_final_review.json) is
**PASS_FOR_OWNER_APPROVAL_PACKET**, with all35 reviewed file hashes bound.
Implementation, source review, host/ABI tests, exact build, resource proof and
custody are complete. Only fresh controller state remains an execution-time
dependency; exact owner approval remains required before executing this packet.
The packet separates frozen artifacts from fresh port/incarnation/generation/
Config digest/token/directory/reference/rank/recovery observations.

[Offline audit helper](packet_checks.py) verifies saved snapshots, individual
mutation receipts and complete preservation; it cannot open a controller.
[Nine safety tests](test_packet_checks.py), [validation record](packet_finalization_validation.json)
and [concrete canonical Kazuya compile identity](packet_compile_identity.json)
record the packet-only checks. The earlier handoff review remains historical;
R2 review binds this final packet. No controller operations occurred.

## Diagnosis and menu behavior

The exact retained Config has277 API bytes, SHA-256
`65ecdcf32ecc4d0ce99edbc9a6b29aa99186ce1cd0c217d626764659d54e71dd`.
[Structured diagnosis](retained_config_diagnosis.json) retains exact fields,
provenance and the owner correction. Indices below are zero-based. All rows
are MODE_ULTIMATE, name Ultimate Runtime, embedded index0, no activation binding,
unrestricted applicable-backend list, and ordered identity remaps RF3→RF3,
RF4→RF4, LT3→LT3.

| Row | Engine / stable ID | Additional preprocessing | Backend default references | Baseline menu / candidate |
| --- | --- | --- | --- | --- |
| 0 | 0 / 0 | no SOCD pairs | Configurator (one-based mode1) | visible / hidden |
| 1 | 0 / 3 | no SOCD pairs | none | visible / hidden |
| 2 | 1 / 28 | LF3/LF1 and LF5/LF2, SOCD_2IP | XInput, GameCube, Nintendo Switch (mode3) | hidden / hidden |

Row0 is a supported built-in fallback; row1 is a supported legacy profile.
They were visible because the original predicate hid only engine1. They remain
internally and cannot serve as native Persist templates. Row2 is the sole
retained native template, used by native selection when exact context/backend
match; it remains intact. No additional hidden template appears in the retained
snapshot. The corrected two visible labels match these exact rows/source.
This task did not acquire a new live Config or change controller state. Fresh
readback remains mandatory before future mutation; active runtime identity is
UNKNOWN, while the retained saved native reference is SEL01/ID28.

Only production source changed: `src/core/profile_selection.cpp`, BuildTargets.
After unchanged backend eligibility, `compact format && MODE_ULTIMATE` omits
that Config row from visible targets. Independently, an eligible unchanged
NativeTemplate (engine1) still admits stored schema5 records. Thus engine0-only
compact Configs gain no invented native-selection capability. Names are irrelevant.
NativeTemplate, Persist, exact ContextMatches, Config/default persistence,
boot, evaluator and all writers are unchanged. Noncompact Ultimate and ordinary
non-Ultimate choices keep their existing behavior. Sorting, equal-rank directory
stability, list-index keys and full32 stable IDs are unchanged.

## Exact candidate

- Source F: `1de243c7bada73ba85843018058b4f66a06acdda`.
- Tree: `5a25a83705a654480b8db805f20822f4d180d70f`.
- Fixed source ref: `codex/native-profile-menu-candidate`.
- Canonical base: `55ab5984f47728db53a12665d685d16cfad39201`.
- Preparation/evidence ref: `codex/native-profile-menu-cleanup`.
- Classification: FIRMWARE_SOURCE_ACTIVE_BEHAVIOR, menu enumeration only.
- Canonical build `pio run -e glyph_mk6`: PASS, no fallback. RAM198288/262144,
  flash510956/1568768. PlatformIO6.1.19, Python3.14.4, ARM GCC12.3.0.
- UF2:1046016bytes, SHA-256
  `a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b`.
- Preserved UF2: `local_backups/hardware-artifacts/1de243c7bada73ba85843018058b4f66a06acdda/a8a012e3d264d622a08ddfbe1f2e547c441c5406645203069e90314b4996e04b/firmware.uf2`
  under the original owner repository. Exact absolute ELF/BIN/UF2 paths,
  sizes/hashes and O_NOFOLLOW readback are in [custody](evidence/build_custody.json).
- [Artifact correspondence](evidence/artifact_correspondence.json): ELF objcopy
  equals BIN; all2043 UF2 blocks/addresses/family/padding exact; recovery UF2 rehashed.
- [Build provenance](evidence/build_provenance.json): actual259 recipes and source
  pins. The compiledb target removed mutable .pio outputs **after** preservation;
  custody is authoritative. No rebuild substitutes for the candidate.

## Validation and independent review

[Validation ledger](validation.json) and [sealed logs](evidence/log_manifest.json):

- New topology fixture fails the baseline at the intended character-count
  assertion and passes changed source. Exact43-record retained topology yields
  Ultimate+SEL01–20 before cleanup and Ultimate+Kazuya after simulated cleanup/
  addition; every runtime Config row stays internal. No controller cleanup ran.
- Selector/menu/mailbox/persistence plus GameCube idle/no-poll host bridge PASS
  on both enum ABIs. Multiple hidden contexts test engine, backend and exact
  preprocessing resolution, preserving all unrelated Config fields.
- Both-ABI production native evaluator/legacy full-output correspondence PASS;
  both-ABI actual legacy SET phases and independent72-output legacy oracle PASS.
- Production ProfileStore and actual checked Config persistence checks PASS.
- Native ARM ABI/layout probes match the predecessor exactly; both target menu
  frames56bytes. [ABI](evidence/abi-layout.json), [menu frames](evidence/menu-target-frames.json).
- Fresh [source review](evidence/source_review.json) PASS with no findings.
  [Final handoff review](evidence/handoff_review.json) records the separate exact
  tuple/resource/packet judgment. Initial preparation review remains historical.

The additional selection/recovery route-extraction checker FAILS identically on
canonical and candidate: its stale Backend double lacks BackendId/GamecubeBackend/
SelectionIdleAdmitted. [Exact inherited debt](evidence/inherited_recovery_fixture_debt.json)
binds unchanged source/fixture hashes and both failure logs. No checker was
weakened or repaired; actual selector/GC liveness tests pass. No full aggregate
PASS is claimed. This is preserved Revision3 framework fixture debt, with no
concrete new Tier1/Tier2 regression found.

Fresh [linked resource proof](resource/REPORT.md), [result](resource/result.json)
and [hash-addressed evidence](resource/manifest.json) PASS within unchanged caps:
all3059 named frame/call signatures unchanged, only BuildTargets instructions
change;144 relocated literal rows qualified,153 vtables correspond,318 mutable
symbols unchanged,72 SDK and18 vendored pins freshly match. All140/39/14 prior
routes replay to maxima2048/2012/1344; conservative core0=2048/2048 (zero margin).
Core1composition1060 within retained1152/reservation2048; static198288/199632,
phase/layout506/510 within512, heap capacity63660 unchanged. Fresh actual-recipe
resource objects cover53 TUs/1012 frames. Per-function objects do not alone prove
whole-target safety; the linked/source route proof supplies composition.
Target timing/highwater NOT_MEASURED; no cap increase or new scope exclusion.

## Exact store/install plan

[Retained identities](retained_profile_identities.json) verify ID27/revision1/
Ultimate/schema5 against both owner golden hashes and all20 SEL wrappers/bodies
against original fixture bytes. Retained rank0 proposes Kazuya rank1 only after
fresh availability verification. Never update/recreate ID27 or delete a referenced
SEL. Retained row2/ID28 requires a checked switch to Ultimate before deletion if
fresh preflight confirms that state. Fresh Config/current active references remain
future operation inputs; historical tokens/generations are never reused.

[Kazuya verification](kazuya_verification.json), [report](Kazuya.report.json),
[compiled wrapper](Kazuya.pb) and [production protobuf JSON](Kazuya.protobuf.json)
match unchanged canonical source and committed report exactly. Wrapper1839bytes,
SHA-256 `60f1715738fb5a46f8ac7cde326a3178e4560e52a8489da54e3a435eb70fd3e8`;
body1834bytes, SHA-256
`44fa76903206c7a86a9f5d5a19c0be5f237e1c7e631dd5adf21cdb27eb3e4405`.
No gameplay semantics or coordinates changed. CREATE must use its returned
stable ID, never assumed48, and leave Kazuya inactive.

The [exact unexecuted owner packet](OWNER_PACKET.md) covers fresh read-only
preflight, exact firmware installation/recovery and preservation, checked safe
Ultimate selection,20 separately fenced conditional SEL DELETEs, exact Kazuya
CREATE/readback and genuine per-route menu/preservation observations. Conditional
43-record starting topology yields23 before CREATE and24 afterward; otherwise
use actual counts. Keep all legacy/unknown records. Expected native menu is
Ultimate then Kazuya. End safely on Ultimate and STOP before Kazuya gameplay.
No candidate source merge before exact human menu/display PASS and normal
source-free evidence/integration gates. The canonical queue is unchanged.

```text
Controller mutations performed: NONE
Firmware flashed: NO
SEL records deleted: NO
Kazuya created on controller: NO
Kazuya gameplay acceptance: NOT_TESTED
```

Nunchuk NOT_TESTED; historical root cause UNPROVEN. No physical result follows
from host tests, compilation, CREATE preparation, display fixtures or custody.
