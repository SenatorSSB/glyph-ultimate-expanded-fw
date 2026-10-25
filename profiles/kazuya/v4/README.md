# Kazuya v4 — KazTest4

**HOST_VERIFIED**, independently reviewed profile-only test candidate. Gameplay
NOT_TESTED. The exact v3 behavioral base is `b2d72b1367ea6c350574727168cdc8b5c2ce3f1d`,
not v1 or canonical's older inventory. Feature branch `codex/kazuya-v4-profile`.
Live canonical matched `bf6f1e2e6814c6b6f1eb710175a488961c8295e7` before edits.
No canonical merge. V1/v2/v3 and archival Ultimate source/tests/evidence remain
unchanged and frozen by exact digests. The owner reports v3 pure-Up spring-loading
substantially improved gameplay; that is attributed feedback, not blanket acceptance.

The direct current owner work order authorizes this precise profile design and
one separate **KazTest4** CREATE only after complete host proof, review and fresh
healthy controller preflight. No firmware/evaluator/schema/encoding/remapper/SOCD/
ProfileStore/menu/backend changes, UF2 rebuild/flash, whole Config/reference write,
UPDATE/DELETE or Crouch Jab loop is included. Existing preprocessing and ordered
RF3/RF4/LT3 identity remaps plus horizontal/vertical2IP SOCD remain exact.
`gates.mode` stays `false`; seven direction sources remain unchanged. Commands
index actual post-SOCD `physicalLeft`, never synthetic Up or inferred facing.

## Directional and digital matrix

These are RF5/RF6 contributions; unrelated physical buttons remain compositional.
RF12 and LT6 fixed effects override LS as described below. Ordinary retained
modifier, null and D-pad priorities remain outside command overrides.

| Held command inputs | Left-stick geometry without LT2 defense | Command digital |
| --- | --- | --- |
| none | Default / retained modifiers | none |
| RF5 | pure Up | A |
| RF6 | ordinary RF6; physical7/8/9 pure Up | Z |
| RF5+RF6 | pure Up | A, no Z |
| RF7 | exact neutral | none |
| RF7+RF5 | pure Up | none |
| RF7+RF6 | Default physical | none |
| RF7+RF5+RF6 | pure Up | none |
| RF8 | ForcedDown | none |
| RF8+RF5 | DownDiagonal | A |
| RF8+RF6 | DownDiagonal | Z |
| RF8+RF5+RF6 | DownDiagonal | A, no Z |
| RF8+RF7 | CDArmed: down by physical horizontal | none |
| RF8+RF7+RF5 | exact neutral | none |
| RF8+RF7+RF6 | exact neutral | none |
| RF8+RF7+RF5+RF6 | exact neutral | none |

Raw coordinates: neutral=[128,128], Up=[128,205], Down=[128,51]. `ForcedDown`
is Down in all9 entries. `CDArmed` is [61,51]/[128,51]/[195,51] by left/no/right
physical horizontal in every vertical row (directions1..9 repeat those3 points).
Preloading physical Up/Down no longer neutralizes CD. No horizontal means Down.
RF7 alone is now neutral for all9 physical directions; release RF7 to expose the
retained ordinary physical/modifier geometry. Simultaneous RF8/RF7 release can
skip neutral entirely; no artificial intermediate frame is generated.

`DownDiagonal` still projects [61,51]/neutral/[195,51] by physical horizontal,
so direct EWGF/Hell's Gate and their no-horizontal neutral fallback remain exact.
`SpringloadUp` remains [128,205] ×9. Pair+RF5 now selects neutral before that Up:
RF8+RF7 → CD; addRF5 → neutral/no A; releaseRF8 → Up/no A; releaseRF7 → Up+A.
Four buttons remain neutral/no A/Z → releaseRF8 → Up/no A/Z → releaseRF7 → Up+A/no Z.
Releasing RF7 first intentionally exposes RF8+RF5 down-diagonal+A; simultaneous
modifier release exposes ordinary RF5 Up+A. RF6-only spring-loaded Default and
all ordinary/physical-Up/weak-sublayer behavior remain byte-for-byte v3 in native
comparisons. RF5 remains exclusive over RF6 Z/weak geometry when applicable.

All raw points are already in the original measured
[coordinate evidence](../../../tools/fixtures/kazuya/coordinate-evidence.json).
Assignments follow the owner's explicit v4 design; no new effective-coordinate
approximation or game-recognition guarantee is introduced.

## LT2 defensive sublayer

`lt2Shield` is unchanged: LT2's buttonL + GameCube L/R digital carriers are
withheld for physical RF3, executable RF5 A (RF5 without RF7), or physical
post-SOCD Up+RF1/RF2. Independent LT1/RF16 contributions remain. Analogue L/R140
consume final digital carriers, preventing residual analogue Shield after that
carrier disappears. LT2 alone has no left-stick override.

New states require **semantic lt2Shield**, not raw LT2, and exclude RF5/RF6:

- RF8+RF7+active LT2: exact neutral everywhere, with double Shield.
- RF7+active LT2, RF8 absent: `LT2DefensiveDownBack` (slot17) below.
- RF5/RF6 specialized neutral/Up/Default states keep their own geometry.

| Physical FGC direction | Raw defensive output | Meaning |
| --- | --- | --- |
| 1 | [61,51] | Manual down-left, no flip |
| 2 | [128,51] | Manual Down |
| 3 | [195,51] | Manual down-right, no flip |
| 4 | [195,51] | Opposite physical horizontal, Down |
| 5 | [128,51] | Owner-approved candidate Down fallback |
| 6 | [61,51] | Opposite physical horizontal, Down |
| 7 | [61,205] | Default up-left |
| 8 | [128,205] | Default Up |
| 9 | [195,205] | Default up-right |

Only horizontal-only4/6 flip. Physical Down wins by selecting rows1/2/3;
Up selects ordinary rows7/8/9. There is no character-facing inference.
With physical Right: CD down-right → addLT2 neutral+Shield → releaseRF8
down-left+Shield → releaseRF7 ordinary Right+Shield. Manual Down+Left instead
retains down-left after RF8 release. Release timing is entirely physical.

## RF12 and LT6 fixed effects

| Analogue priority (lower wins) | Input/effect | Raw LS | Digital contribution |
| ---: | --- | --- | --- |
| 1 | RF12 | [128,128] | A independently |
| 2 | LT6 | [128,51] | A independently |
| 5 | Command selected table | Physical source / selected map | Separate bindings |
| 10/20/50/60/80/200 | Retained null/D-pad/RF6/forced/default | Unchanged | Unchanged |

RF12 uses one highest-priority fixed effect and one independent A binding;
LT6 reuses its old fixed effect with new Down coordinates/priority. RF12+LT6
therefore yields neutral+A. Both leave RS and unrelated digital outputs intact.
RF12 itself adds no B/Z/Up/Down. It does **not** extend LT2 Shield suppression;
LT2+RF12 retains LT2 unless an existing release condition applies. Any future
RF12 Shield-release policy needs a separate owner decision. No new constant
coordinate tables or direction source are consumed by these two buttons.
The existing firmware Nunchuk tail still runs after effects and remains NOT_TESTED.

## Selection and effect audit

New early conditions follow `lt2Shield`: `lt2DefensivePrepare`,
`lt2DefensiveDownBack`, `neutralCommand` (the union of command neutral and defense
preparation). `cdcNeutral` now accepts pair+RF5 or RF6; `cdArmed` excludes both.
All other existing conditions and digital bindings are unchanged except the new
RF12 binding. Selected-table priorities are:

| Priority | Table / gate |
| ---: | --- |
| 1 | CDCNeutral / neutralCommand |
| 2 | LT2DefensiveDownBack / lt2DefensiveDownBack |
| 3 | CDArmed / cdArmed |
| 4 | DownDiagonal / downDiagonalCommand |
| 5 | ForcedDown / forcedDown |
| 6 | SpringloadUp / springloadUp |
| 7 | Default / springloadGrab |
| 8 | RF7ReleaseNeutral / rf7ReleaseNeutral |
| 20,30..37 | Retained modifier rules, unchanged |

Table-rule priority and analogue-effect priority are separate domains. LT2
preparation overlaps bare CD and wins at table priority1; defense overlaps
RF7-only neutral and wins at2. Explicit RF5/RF6 exclusions protect spring-loading.
The existing command analogue effect5 beats independent ordinary effects. All
overlapping native target priorities are unique and compiler/native validated.

## Reproduction and evidence

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/v4/KazuyaV4.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/v4/KazuyaV4.profile.json --output /tmp/KazuyaV4.pb
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/v4/KazuyaV4.profile.json --format protobuf-json --output /tmp/KazuyaV4.protobuf.json
python3 tools/glyph_native_profile_json.py report profiles/kazuya/v4/KazuyaV4.profile.json
python3 tools/test_glyph_native_profile_json.py -v
python3 tools/test_glyph_native_profile_json_v1.py -v
python3 tools/test_kazuya_profile.py -v
python3 tools/test_kazuya_profile_v2.py -v
python3 tools/test_kazuya_profile_v3.py -v
python3 tools/test_kazuya_profile_v4.py -v --report /tmp/KazuyaV4.host-results.json
```

The existing test venv provides jsonschema; the existing unchanged Nanopb
source dependency and C/C++ compiler build the production native harness.
V4 expected rows are finite requirements assertions. Actual C++ admission,
preprocessing/SOCD, Ultimate dispatch and evaluator are the implementation under
test. An isolated copy of the v2 harness preserves old test module globals;
complex retained behavior is compared to exact v3 native output.

Authoring17/17 and23/23; v1 6/6; v2 8/8; v3 11/11; v4 11/11 PASS. Independent
v4 rerun11/11 PASS plus18,432 additional complete-output v3 comparisons.
Main coverage includes4,176 RF matrix/priority cases,73,728 full v3 comparisons
(36,864 RF6 subsets),3,473 LT2 carrier cases,2,016 cases each for LT6/RF12/both,
9,216 exhaustive RF12/C-stick combinations,2,916 RF release frames,387 extra
Shield/specialized release frames,632 combined SOCD assertions and24 mutants.
Both horizontal sides, all9 LF directions, reverse/simultaneous releases and
RF12's RF1→RF8→RF12 player-controlled sequence are covered. Restoring old
vertical-neutral CD, partial RF7 neutral, manual-Down flipping, RF12 priority
loss or neutral LT6 is detected. Native table tags and paired effect tags
prove otherwise numerically hidden precedence without changing the evaluator.

[Compile report](../../../tools/fixtures/kazuya/v4/compile-report.json),
[host report](../../../tools/fixtures/kazuya/v4/host-results.json),
[exact native transition traces](../../../tools/fixtures/kazuya/v4/native-transitions.json),
[full inventory and audit](../../../tools/fixtures/kazuya/v4/verification.json),
[frozen historical hashes](../../../tools/fixtures/kazuya/v4/frozen-baselines.json),
[independent review](../../../tools/fixtures/kazuya/v4/independent-review.json)
preserve exact evidence. Trace digital words include the existing runner's
unowned0xa0030000 sentinel; all owned digital bits and6 analogue bytes are asserted.

| Native resource | Actual | Hard limit | Headroom |
| --- | ---: | ---: | ---: |
| declared_tables | 18 | 28 | 10 |
| condition_count | 70 | 96 | 26 |
| token_count | 234 | 768 | 534 |
| direction_source_count | 7 | 8 | 1 |
| table_rule_count | 17 | 32 | 15 |
| digital_binding_count | 19 | 32 | 13 |
| analog_effect_count | 14 | 16 | 2 |
| body_bytes | 1979 | 3336 | 1357 |

All28 wire table slots remain present; slots18..27 are exact neutral fill.
Wrapper 1984 bytes: `46084bbcf55646819ab0ce824b9de9ac778d3bc4d9344a8c8bcbfe5d15f6142c`.
Body: `a8b03ed4952f4ea81317ca2053830925e751a2647b05a5777b01a82d40e349d2`.
Authored provenance: `cf8132314b1bf75392761b550f2149d329ce132e79499626fdafcccec87ea01c`.
Preprocessing: `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f`.
Protobuf JSON file: `76df425640e1d435b55a9d72facfcb80b94277921619b17e7ce13b0fbfa4da72`.

## Device and gameplay handoff

After committed-source identity and publication, fresh same-unit normal
Configurator identity, healthy production STATUS, complete directory/record/raw
Config preservation, compatible GameCube native context, capacity and unused
name/rank must precede the owner-authorized one CREATE. Use only compiled protobuf
JSON, fresh store fences/token, exclusive journal and fsynced immutable request.
No automatic retry. READ back the actual allocated ID and exact payload; prove
all older wrappers/metadata, raw Config and references unchanged. Keep private
controller identity/Config/transaction receipts outside Git. No host selection.
This offline evidence snapshot claims no device creation or gameplay acceptance.

After verified creation, follow [GAMEPLAY_TEST.md](GAMEPLAY_TEST.md) for physical
selection and the owner's12 priority tests. Keep KazTest3 for immediate rollback.
[Crouch Jab design is deferred](CROUCH_JAB_DEFERRED.md); no executable loop logic.
