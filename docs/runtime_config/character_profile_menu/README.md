# Character profile menu and Kazuya installation preparation

Status: OWNER_AUTHORIZED_CANDIDATE_IN_VALIDATION. The owner corrected the
visible count to two and explicitly chose native-only Ultimate menu visibility;
see [bounded authority](OWNER_DIRECTIVE.md). Source validation is in progress.
No executable hardware packet or physical acceptance is claimed. This chapter follows the direct owner objective
provided on 2026-10-23; its exact attachment SHA-256 is recorded in ledger.json.
It does not reopen GP-NATIVE-002 or rewrite its historical evidence.

Live canonical was verified as `55ab5984f47728db53a12665d685d16cfad39201`
(`Merge Kazuya v1 offline host candidate`). Work is isolated on
`codex/native-profile-menu-cleanup`; the original checkout and existing edits
are preserved. The objective is the visible native-character list Ultimate,
Kazuya, retaining execution contexts as needed. Device access is read-only for
diagnosis; controller mutations and flashing are excluded from this task.

## Exact retained diagnosis

The latest retained API snapshot is the accepted selector liveness post-test
readback, captured `2026-10-22T22:09:38.885589+00:00` (2026-10-23 in Helsinki).
Its raw Config is 277 bytes, SHA-256
`65ecdcf32ecc4d0ce99edbc9a6b29aa99186ce1cd0c217d626764659d54e71dd`.
See [structured diagnosis](retained_config_diagnosis.json) for original private
provenance and exact field values. These are retained facts, not fresh current
controller verification. No USB serial device was present during this task.

All three rows are MODE_ULTIMATE, named Ultimate Runtime, with legacy embedded
profile index `ultimate_profile_config=0`. All have the ordered identity remaps
RF3→RF3, RF4→RF4, LT3→LT3. All have no activation binding and empty backend
eligibility lists (unrestricted by Eligible for ordinary gameplay backends).
Indices below are zero-based; backend default-mode indices are one-based.

| Row | Engine / stable ID | Preprocessing beyond remaps | Backend default references | Current BuildTargets | Persist native template |
| --- | --- | --- | --- | --- | --- |
| 0 | 0 / 0 | no SOCD pairs | Configurator (default mode 1) | visible ordinary choice | no |
| 1 | 0 / 3 | no SOCD pairs | none | visible ordinary choice | no |
| 2 | 1 / 28 | LF3/LF1 and LF5/LF2, SOCD_2IP | XInput, GameCube, Nintendo Switch (default mode 3) | hidden native template | yes, when backend and exact context match |

Row0 is the supported source fallback; row1 points to retained ID3/schema3
a supported legacy profile. They are not native execution
templates. Neither is needed by Persist to execute native profiles; that does
not prove they are disposable or semantically designated internal scaffolding.
Row0 also has a Configurator default reference. Row2 is the sole retained native
template, needed for the current native selection lane. All rows remain intact.
No separate fourth/hidden template appears in this snapshot.

At the verified canonical source, BuildTargets therefore predicts **two**
visible runtime-named choices plus Ultimate and SEL01–SEL20 for XInput,
GameCube and Nintendo Switch. The owner originally reported **three**, then directly corrected it to **two**,
matching these retained fields and source. No live Config/identity query was
performed; no reconnect, reboot or profile switch occurred. Fresh controller
state remains mandatory before any future mutation.

## Initial semantic finding and later owner resolution

The existing native-placeholder predicate is compact ProfileStore format plus
MODE_ULTIMATE plus engine1. It already hides row2. Engine0 is explicitly
legacy/source fallback in `schema/haybox/config.proto:784`; compact format does
not make it internal infrastructure. Config validation permits engine0 stable
legacy references, migration preserves them, and `mode_selection::set_mode`
activates both engines. See [source investigation](source_investigation.json).

**Historical strong semantic stop (resolved by OWNER_DIRECTIVE.md):** no existing field identifies rows0/1 as internal
rather than legitimate selectable legacy choices. Their names cannot be used
as that discriminator. Hiding all compact MODE_ULTIMATE rows requires an
explicit policy to hide built-in/legacy Ultimate choices as well, or a
source-backed semantic designation of the internal subset. The owner has now explicitly chosen to hide those legitimate legacy choices
too, preserving them internally. That new product policy supplies the missing
visibility decision; no claim that engine0 is inherently infrastructure follows.
No name heuristic, schema change or Config deletion is used.

The source change is confined to BuildTargets in `src/core/profile_selection.cpp`:
compact format plus MODE_ULTIMATE hides the Config row, independent of name.
NativeTemplate and Persist remain unchanged. The eligible engine1-template gate
still controls whether stored profiles can appear; an engine0-only Config does
not gain a new native selection facility. Noncompact Ultimate and ordinary
non-Ultimate choices remain. Focused tests cover current/cleaned topology,
multiple contexts, backend eligibility, rank/tie ordering, index keys, stable
IDs, read-only enumeration, checked selection and GameCube liveness. Fresh
source review, resource proof and exact committed Mk6 build/custody precede
a separate candidate-specific hardware packet. No inherited hardware PASS applies.

## Offline preservation and installation identities

[Retained identities](retained_profile_identities.json) verify ID27/revision1/
Ultimate/schema5 against the owner golden wrapper and native body; all twenty
ID28–47/SEL01–SEL20 wrappers and bodies match original selector fixtures exactly.
This does not substitute for the future fresh per-ID identity/reference checks.

Ultimate wrapper SHA-256:
`30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b`.
Native body SHA-256:
`ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee`.
Retained rank is 0. Never update/recreate ID27. The retained active/default
native reference is SEL01/ID28 in row2; a safe checked switch to ID27 is required
before deleting any SEL if fresh preflight confirms it. Current live references
and active identity are UNKNOWN.

[Kazuya verification](kazuya_verification.json) records exact unchanged canonical
compilation. [Compile report](Kazuya.report.json) equals the committed Kazuya
report; [production protobuf JSON](Kazuya.protobuf.json) roundtrips byte-exactly
to the [1839-byte wrapper](Kazuya.pb), SHA-256
`60f1715738fb5a46f8ac7cde326a3178e4560e52a8489da54e3a435eb70fd3e8`.
The 1834-byte body SHA-256 is
`44fa76903206c7a86a9f5d5a19c0be5f237e1c7e631dd5adf21cdb27eb3e4405`.
No gameplay semantics or coordinates changed. Proposed Kazuya rank is 1 only
if fresh LIST confirms Ultimate rank0 and that rank1 is available. Allocate
Kazuya's stable ID from CREATE's actual response; never assume ID48.

The conditional plan deletes exactly twenty verified SEL records, retaining
all legacy/unknown records. If the exact retained 43-record topology still
holds, counts become23 before CREATE and24 after CREATE. Desired final visible
list is Ultimate, Kazuya, with Ultimate active. That outcome remains unproven.

## Delivery boundary

[Owner packet](OWNER_PACKET.md) is an **unexecuted, non-actionable draft** plus
an authorized read-only diagnosis packet. It cannot be approved for mutations until candidate tests/review/resource/
build/custody and the actual operation fences are resolved. Candidate source is
in validation; no new ELF/BIN/UF2 or physical menu PASS is claimed at this
checkpoint. Classification: FIRMWARE_SOURCE_ACTIVE_BEHAVIOR, limited to menu
visibility. Historical acceptance remains historical.

Controller mutations performed: NONE. Firmware flashed: NO. SEL records
deleted: NO. Kazuya created on controller: NO. Kazuya gameplay acceptance:
NOT_TESTED. Nunchuk: NOT_TESTED. Historical root cause remains UNPROVEN.

[Validation](validation.json) and [fresh independent preparation review](independent_preparation_review.json)
PASS for this bounded preparation only. Firmware-source review and candidate
acceptance remain outside that verdict.
