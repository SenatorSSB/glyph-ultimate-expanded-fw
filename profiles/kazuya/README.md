# Kazuya native Ultimate v1 host candidate

`Kazuya.profile.json` is a newly authored, stateless, character-owned candidate
for the GameCube-adapter Ultimate context. It uses the unchanged authoring-v1
contract, schema 5, GNP5 encoding 1 and engine ABI 1. It is not canonical,
installed, gameplay-accepted or hardware-accepted. Nunchuk remains NOT_TESTED.
No firmware, evaluator, backend, schema, selector, ProfileStore or Config changes
are included. Root cause claims are outside this task and remain unproven.

The owner work order in this chat supplies the RF command matrix and bounded
offline authoring/compilation authority. This is an inactive profile/fixture
branch, not an active firmware work order or a campaign queue transition.

## Exact source baseline and applicability

The sole base is `9a2a20730625671f89988e3911242c71e3f3fc5b`,
`Add sparse character-independent native profile authoring v1`. Live
`SenatorSSB/glyph-ultimate-expanded-fw` `configurator` matched it before edits.
The restricted DNS attempt failed; the read-only network-enabled retry succeeded.
Feature branch: `codex/kazuya-profile-v1`. No rebase, merge or canonical write.

The archival `profiles/ultimate/Ultimate.profile.json` remains exact Git blob
`0c25c3d6f85480898f18f6104fa4405ed2e497cb`. Its fixtures and compiled wrapper
remain byte-identical: SHA-256
`30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b`.
Its body remains `ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee`.

Source authorities at that baseline:

- `profiles/schema/glyph-native-ultimate-profile.v1.schema.json`,
  `profiles/README.md`, `profiles/authoring-v1/KAZUYA_PROFILE_DESIGN_HANDOFF.md`
  and `tools/glyph_native_profile_json.py`: authoring, compiler and resources.
- `src/modes/UltimateNativeProfile.cpp`: native admission and limits.
- `src/modes/UltimateNativeEvaluator.cpp`: staged conditions, lowest numeric
  priority, OR digital composition, effect precedence and firmware Nunchuk tail.
- `src/core/ControllerMode.cpp`, `src/core/InputMode.cpp`, `src/core/socd.cpp`:
  original/remapped/post-SOCD context and existing 2IP history.
- `HAL/pico/src/comms/GamecubeBackend.cpp`: A/B/X/Y, Z=`buttonR`,
  L=`triggerLDigital`, R=`triggerRDigital`; stick/trigger bytes passed through.
  `buttonL` is preserved in native output but is not the GameCube L carrier.

The existing native runner requests XInput; `Ultimate::UpdatePreprocessedOutputs`
passes the same backend-independent native evaluator for native ABI1. Thus host
tests prove native `OutputState`; GameCube carrier applicability is source-backed,
not a new Joybus, adapter, console, or gameplay test.

## Preprocessing contract

Ordered remaps: RF3→RF3, RF4→RF4, LT3→LT3. Ordered SOCD pairs:
LF3/LF1 then LF5/LF2, both `secondInputPriority` (existing 2IP).
Production preprocessing SHA-256:
`3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f`.
No entry reordering or policy change. All profile physical predicates use
`postSocd`; the firmware still keeps distinct original, pre-SOCD/remapped and
post-SOCD domains. The native RF graph has no timing/history. Existing SOCD
preprocessing does retain its existing press history.

LF1 is actual right; LF3 actual left; LF2 up; LF5 down. Post-SOCD horizontal
state selects the map column. There is no facing detection. With both physical
horizontal inputs, existing 2IP selects according to the preceding input frame;
from a reset with both pressed simultaneously, neither wins. Both histories,
reactivation on release and simultaneous onset are tested.

## Physical inventory and retained behavior

| Physical activation | Observable native behavior |
| --- | --- |
| LF1 / LF3 | Right / left ordinary stick direction after SOCD |
| LF2 / LF5 | Up / down ordinary stick direction after SOCD |
| RF1 / RF2 / RF3 / RF10 | Ordinary A / B / X / Y, with the retained sublayers below |
| LF4 | B; LF4+RF2 gives X when C directions are absent; LF4+RF3 forces Up |
| LT6 | A and forced vertical Down, or Up when a retained forced-Up source wins |
| RF5 | A and forced Up outside RF7/RF8 command overrides |
| RF6 | Z and `RF6LowMagnitude` outside RF7/RF8 command overrides |
| RF7 / RF8 | New command inputs below, with no intrinsic Mode meaning |
| LT1 | `buttonL` + L digital, analogue L=140 |
| RF16 | R digital, analogue R=140 |
| LT2 | `buttonL` + L and R digital, analogue L=R=140 |
| MB7 / MB6 / MB5 / MB4 | start / select / home / capture |
| RT3 / RT4 / RT2 / RT5 | C-stick left / right / down / up |
| RF13 | Ordinary LF-to-D-pad routing, suppressed LS direction flags and neutral LS; commands supersede it |
| RF9 | Both-stick null unless intrinsic RF3/RF4 exceptions apply; commands supersede its LS null, retaining RS null |
| Other unmapped inputs | No added profile contribution; firmware-owned tails remain outside profile data |

LT3 without LF4 and with either RF3 or RF4 is the retained face sublayer:
RF1's ordinary A and RF2's ordinary B are suppressed; LT3+RF3 contributes B;
RF1 contributes X if no C input; RF2 forces Up. RF3 ordinarily contributes X
only without LT3/LF4; RF9 suppresses that X if no C input. These ordinary
contributions may coexist with command A/B/Z. Only the command buttons' own
contributions are exclusive. No global face-button Shield suppression is added.

For RF6 outside new overrides, the low-magnitude map uses ordinary horizontal
state and a vertical direction only when exactly one resolved vertical flag is
active. RF6 therefore takes precedence over RF5's independent forced-Up effect.
RF5+RF6 with no command preserves the archival low-magnitude Up result.

The retained modifier inventory is reconstructed with physical names, not copied
historical `legacyRole`/`tableRuleGate` chains. Most conflicting modifiers cause
Default fallback. Exceptions preserved exactly: LT3+RF3+RF4 may select
`FlippedHorizontal41`; LT3+RT1 without RF4 may select `CompactTilt`.
Intrinsic RF9+ordinary RF3 and table-selection RF9+ordinary RF3+RF4 remain
distinct predicates. Full predicates are the v1 conditions referenced below.

| Retained table | Physical activation before exclusion gates | Observable map / archival coordinate source |
| --- | --- | --- |
| Horizontal35 | LT5 | x raw 93/128/163; archival X1 |
| Horizontal46 | LT4 | x raw 82/128/174; archival X2 |
| VerticalAsymmetric | LT3 without LF4/RF3/RF4 | archival Y2, asymmetric vertical/diagonal values |
| Horizontal41 | LT3+RF3 without LF4 | x raw 87/128/169; LayerNormalX |
| FlippedHorizontal41 | LT3+available RF4 without LF4 or RT1/RF4 custom | x raw 169/128/87; LayerFlipper |
| FlippedTilt | available RF4, LT3 released or LF4, no RT1 or LF4+RF2 | flipped raw x and y47/128/209; Tilt1 |
| CompactTilt | RT1 without RF4 | x88/128/168 and y79/128/177; Tilt2 |
| AsymmetricTilt | RT1+RF4 without table RF9/RF3/RF4 suppression | archival Tilt3 |
| FlippedTilt41 | available RF4+RF2, no LT3/LF4/custom | flipped x169/128/87 and y47/128/209; Tilt1Minus41 |

"Available RF4" differs between intrinsic output effects and table selection,
as it did in the archive. Each selection condition lists the other modifier
predicates that exclude it. These exclusions are tested against the actual
archival native evaluator over all 512 selector combinations, all nine LF
directions, three representative C states and all four ordinary RF5/RF6 states.
Inputs outside RF5/RF6/RF7/RF8/LT2 are also tested individually.

## RF5–RF8 matrix and digital composition

These are simultaneous controller contributions, not automated game moves.
Independent buttons keep their ordinary outputs. RF5/RF6 contributions use
mutually exclusive conditions, never array-order clearing.

| RF inputs | Selected geometry | Command digital contribution |
| --- | --- | --- |
| RF5 | Default selected; forced Up effect | A |
| RF6 | Default selected; low-magnitude effect | Z |
| RF5+RF6 | Default selected; low-magnitude effect wins | A+Z |
| RF7 | ForcedDown | none |
| RF8 | ForcedDown | none |
| RF7+RF5 | ForcedDown, ordinary compositional precedence | A |
| RF7+RF6, RF8 absent | DownDiagonal | A |
| RF7+RF6+RF5, RF8 absent | DownDiagonal | A (OR-composed, no Z) |
| RF8+RF5, RF7/RF6 absent | CDCNeutral | A |
| RF8+RF6, RF7 absent | DownDiagonal | Z |
| RF8+RF6+RF5, RF7 absent | DownDiagonal | A+Z |
| RF8+RF7 | DownDiagonal | none |
| RF8+RF7+RF5, RF6 absent | DownDiagonal | B |
| RF8+RF7+RF6, RF5 absent | CDCNeutral | none |
| RF8+RF7+RF6+RF5 | DownBack | none |

`DownDiagonal` shares one coordinate map for Crouch Dash, Hell's Gate and
EWGF purposes; their digital contributions are independent. `DownBack` reverses
the post-SOCD LF horizontal column, not inferred character facing. With no
post-SOCD horizontal input, diagonal/back tables use explicit `[128,128]`.
This neutral fallback is an implementation-selected host candidate using the
archival neutral point, and needs owner gameplay assessment. ForcedDown remains
Down without a horizontal input. All vertical rows of command maps are explicit;
ordinary LF Up/Down cannot displace them.

RF5 contributes A unless RF8+RF7 are held. That pair instead permits its B only
without RF6. RF6 contributes Z unless RF7 is held; RF7+RF6 contributes A only
without RF8. Thus CDC-neutral and four-button commands leak no command A/B/Z.
Unrelated RF1/RF2/LF4/LT6 may still add A/B. Shield remains compositional.
The ordinary quadrant flags reflect source activations rather than forced raw
command geometry; GameCube uses the raw sticks. Host tests check the full mask.

## LT2 Shield and release order

| Inputs with LT2 | L/R carriers and analogue values | Left stick |
| --- | --- | --- |
| LT2 alone, with ordinary directions/modifiers | buttonL + both digital triggers; 140/140 | Ordinary unrestricted profile geometry |
| LT2+RF8+RF7, including RF5/RF6 additions | Same | DefensiveDownBack |
| LT2+RF8 only | Same | DefensiveDownBack remains active |
| LT2+RF7 only | Same | DefensiveDownBack remains active |
| LT2 after both RF8/RF7 released | Same | Ordinary unrestricted geometry returns immediately |
| LT2 released, command held | Ordinary LT1/RF16 only if separately held | Corresponding unshielded command geometry |

The provisional gate is exactly `LT2 && (RF8 || RF7)`. There is no delay,
release simulation, automatic shield-start inference or hidden historical state.
Both release orders are tested frame by frame.

**Open non-CDC interaction:** this broad gate also replaces the stick geometry
of LT2+RF7+RF6 (EWGF-purpose inputs) and LT2+RF8+RF6 (Hell's-Gate-purpose
inputs). Their command A/Z contributions remain. It also covers LT2+RF7 alone
and LT2+RF8+RF5. This is explicitly provisional Shield priority, not proof that
these overlaps are gameplay-safe. The owner must assess this scope before any
installation approval. Stateless schema 5 cannot remember that a complete CDC
was previously held while distinguishing the same singleton after other inputs.

The weaker defensive diagonal is only a source-backed candidate for avoiding
unintended roll/spot-dodge during transitions. It is not independently desirable
and has no demonstrated gameplay safety advantage here.

Future action-button Shield suppression is deferred. Its scope must be decided
before adding gates/masks; a future sublayer must suppress the intended digital
carriers and their analogue contributions together. Current trigger effects read
`finalDigital:triggerLDigital` / `finalDigital:triggerRDigital`, so a legitimate
carrier clear cannot leave analogue 140 behind. Tests verify that mechanism in
a disposable diagnostic profile, without introducing a suppression policy.

## Coordinate provenance and effective-output verification

All nine coordinates of each table, exact source identities, table/effect
references, and all 67 distinct measured points are in
[`coordinate-evidence.json`](../../tools/fixtures/kazuya/coordinate-evidence.json).
Every one of the 144 declared table points is covered.

Primary measurement: `GC Left Stick Values & Vectors.xlsx`, `Values` sheet,
SHA-256 `f905dd2c9a44fccc2d8ccfa6d311e355a65ebc7b06884db0a149eccfc4baa1e7`,
read from the owner's adjacent Senscope `data/source/` corpus. Evidence records
the exact A:D cell range for every raw/effective pair. No symmetry formula or
C-stick mapping substitutes for those measurements.

| Raw point | Measured effective point | Exact Values range |
| --- | --- | --- |
| [128,51] | [0,-120] | A29913:D29913 |
| [61,51] | [-83,-99] | A15577:D15577 |
| [195,51] | [83,-99] | A49980:D49980 |
| [128,128] | [0,0] | A32915:D32915 |
| [77,98] | [-83,-34] | A15651:D15651 |
| [179,98] | [83,-34] | A50090:D50090 |

Default, Down and ordinary diagonals come verbatim from the archival Default
points. CDCNeutral repeats its center. DownDiagonal projects Default directions
1/5/3 into horizontal columns; DownBack projects 3/5/1. The defensive sides
come from the pinned [GRAM Ultimate modifier source, lines 81–84](https://github.com/GRAMCTRL/HayBox-GRAM/blob/ac8f5f5d9f075cbabf232be28906629335cf8555/src/modes/Ultimate.cpp#L81-L84):
`128 + x*51`, `128 + y*30` for shield-modified diagonals, with explicit signed
directions. Both resulting sides were checked independently in the workbook.
This GRAM source is ordinary Ultimate modifier evidence; no Kazuya-specific
manual/source was found locally and none is claimed as reviewed. Applying its
points to the new defensive map remains a Kazuya candidate assignment.

The other ten maps are complete archival tables with descriptive new names,
as documented above. All measured effective values are available in the evidence
file; lookup does not establish command recognition, shield safety, CDC timing
or an optimal diagonal. Crouch Dash travel distance is not optimized by angle;
the owner's supplied gameplay evidence identifies cancel timing instead.

| Table | Slot | Raw points in direction order 1,2,3 / 4,5,6 / 7,8,9 |
| --- | ---: | --- |
| Default | 0 | [61, 51], [128, 51], [195, 51] / [61, 128], [128, 128], [195, 128] / [61, 205], [128, 205], [195, 205] |
| ForcedDown | 1 | [128, 51], [128, 51], [128, 51] / [128, 51], [128, 51], [128, 51] / [128, 51], [128, 51], [128, 51] |
| DownDiagonal | 2 | [61, 51], [128, 128], [195, 51] / [61, 51], [128, 128], [195, 51] / [61, 51], [128, 128], [195, 51] |
| CDCNeutral | 3 | [128, 128], [128, 128], [128, 128] / [128, 128], [128, 128], [128, 128] / [128, 128], [128, 128], [128, 128] |
| DownBack | 4 | [195, 51], [128, 128], [61, 51] / [195, 51], [128, 128], [61, 51] / [195, 51], [128, 128], [61, 51] |
| DefensiveDownBack | 5 | [179, 98], [128, 128], [77, 98] / [179, 98], [128, 128], [77, 98] / [179, 98], [128, 128], [77, 98] |
| Horizontal35 | 6 | [93, 51], [128, 51], [163, 51] / [93, 128], [128, 128], [163, 128] / [93, 205], [128, 205], [163, 205] |
| Horizontal46 | 7 | [82, 51], [128, 51], [174, 51] / [82, 128], [128, 128], [174, 128] / [82, 205], [128, 205], [174, 205] |
| VerticalAsymmetric | 8 | [69, 78], [128, 78], [187, 78] / [61, 128], [128, 128], [195, 128] / [61, 164], [128, 174], [195, 164] |
| Horizontal41 | 9 | [87, 51], [128, 51], [169, 51] / [87, 128], [128, 128], [169, 128] / [87, 205], [128, 205], [169, 205] |
| FlippedHorizontal41 | 10 | [169, 51], [128, 51], [87, 51] / [169, 128], [128, 128], [87, 128] / [169, 205], [128, 205], [87, 205] |
| FlippedTilt | 11 | [187, 47], [128, 47], [69, 47] / [187, 128], [128, 128], [69, 128] / [187, 209], [128, 209], [69, 209] |
| CompactTilt | 12 | [88, 79], [128, 79], [168, 79] / [88, 128], [128, 128], [168, 128] / [88, 177], [128, 177], [168, 177] |
| AsymmetricTilt | 13 | [69, 82], [128, 83], [187, 82] / [69, 128], [128, 128], [187, 128] / [76, 169], [128, 179], [180, 169] |
| FlippedTilt41 | 14 | [169, 47], [128, 47], [87, 47] / [169, 128], [128, 128], [87, 128] / [169, 209], [128, 209], [87, 209] |
| RF6LowMagnitude | 15 | [89, 89], [128, 79], [167, 89] / [79, 128], [128, 128], [177, 128] / [89, 167], [128, 177], [167, 167] |

All points are absolute raw bytes. Every vertical row of a horizontal-only
command map is deliberately identical. The matching effective coordinates are
the exact `measurements` lookup in the evidence file, with no interpolated values.

## Table and effect priorities

Lower numeric priorities win. All table priorities are unique; overlapping
analogue target priorities are unique. Stage-correct conditions form an acyclic
early prefix. Source axes consume early conditions. Digital output bindings run
before effects. `gates.mode` is permanently `false`.

| Priority | Selected table | Exact gate | Supersession |
| ---: | --- | --- | --- |
| 1 | DefensiveDownBack | `condition:defensiveShield` | all commands and ordinary geometry |
| 2 | DownBack | `condition:downBackCommand` | CDC-neutral, diagonal, Down and ordinary |
| 3 | CDCNeutral | `condition:neutralCommand` | diagonal, Down and ordinary |
| 4 | DownDiagonal | `condition:downDiagonalCommand` | Down and ordinary |
| 5 | ForcedDown | `condition:commandActive` | ordinary modifiers |
| 20 | FlippedTilt41 | `condition:rf4RF2Flipped41` | retained modifiers |
| 30 | Horizontal35 | `condition:selectHorizontal35` | Default when exact exclusion gate admits |
| 31 | Horizontal46 | `condition:selectHorizontal46` | Default when exact exclusion gate admits |
| 32 | VerticalAsymmetric | `condition:selectVerticalAsymmetric` | Default when exact exclusion gate admits |
| 33 | Horizontal41 | `condition:selectHorizontal41` | Default when exact exclusion gate admits |
| 34 | FlippedHorizontal41 | `condition:selectFlippedHorizontal41` | Default when exact exclusion gate admits |
| 35 | FlippedTilt | `condition:selectFlippedTilt` | Default when exact exclusion gate admits |
| 36 | CompactTilt | `condition:selectCompactTilt` | Default when exact exclusion gate admits |
| 37 | AsymmetricTilt | `condition:selectAsymmetricTilt` | Default when exact exclusion gate admits |

Each named gate is a finite condition in the JSON. The ordinary physical
activation inventory above and its explicit exclusion lists define its scope.

| Analogue priority | Target | Activation | Source / coordinates |
| ---: | --- | --- | --- |
| 5 | leftStick | `condition:commandActive` | ordinaryLeft / selectedTable |
| 200 | leftStick | `true` | ordinaryLeft / selectedTable |
| 200 | rightStick | `true` | cStick / inline |
| 80 | leftStick | `condition:ordinaryForcedVertical` | forcedVertical / Default |
| 60 | leftStick | `condition:rf6OrdinaryAnalog` | rf6Axes / RF6LowMagnitude |
| 100 | rightStick | `condition:cDiagonal` | cStick / inline |
| 80 | rightStick | `condition:rf3VerticalCWithHorizontal` | angledC / inline |
| 10 | bothSticks | `condition:nullSticks` | neutralAxes / fixed |
| 200 | triggerL | `finalDigital:triggerLDigital` | 140 |
| 200 | triggerR | `finalDigital:triggerRDigital` | 140 |
| 20 | leftStick | `postSocd:RF13` | neutralAxes / Default |

All analogue gates are `true`, all winner filters are `any`, and no gates
are inverted. Only ordinary selected-LS, forced vertical and RF6 effects skip
D-pad bypass. Trigger values are activated exclusively by final trigger carriers.

Command effect priority 5 overrides independent ordinary LS effects, including
null (10), RF13 neutral (20), RF6 (60), forced vertical (80) and selected ordinary
geometry (200). RS null still applies. D-pad routing is gated off while RF7/RF8
is held. Thus a selected command table cannot be displaced by a lower-specificity
analogue effect or a D-pad bypass. These supersessions are deliberate candidate
precedence, covered by command+RF9/RF13 fixtures. Outside commands, the original
D-pad and null precedence is retained exactly.

Right-stick priority 80 is RF3+vertical C+LF horizontal with no C horizontal;
it uses raw x95/128/161 and y91/165. Priority 100 is any C horizontal+vertical,
using x86/128/170 and y60/128/196. Priority 200 is the ordinary raw28/128/228 map.
Both-stick null priority 10 overrides those. C opposing directions retain
independent quadrant flags while raw reduction prefers left/down, as in the
archive. No new Kazuya diagonal-tilt system is implemented. Left-stick steering
of attacks versus modifier+A remains an undecided future design; no executable
attack semantics are added.

## Removed historical functionality

RF8 Mode gate/selection and all Mode maps are removed. RF7's old B and upward
stick override are replaced, LT2's Y1 modifier role is removed, and RF5/RF6
effects are explicitly gated away from commands. Historical role/gate names and
unused conversion-era dependencies are absent. The unreachable RT1RF4Custom
table rule required both RT1 and a predicate that excluded RT1; it is not copied.
Unused Y1-combination tables and Mode-only tables are not declared. The native
wire's undeclared slots 16–27 are deterministically `[128,128]` × 9, not imports
from archival firmware. There are no references to undeclared names.

The existing firmware-owned Nunchuk tail is not duplicated in data. It runs
after native effects and can supersede stick bytes when connected; that existing
scope is source-backed and physically NOT_TESTED. This candidate targets the
ordinary GameCube-adapter context without Nunchuk acceptance claims.

## Tests, resources and review

Run from the repository root with Python 3 and test-only `jsonschema`; the native
harness also uses the existing Nanopb dependency at `.pio/libdeps/glyph_mk6/Nanopb`
and a C/C++ compiler. No firmware build or device is needed. On this host the
tests used an isolated temporary Python venv, after the default Python lacked
jsonschema. The initial dependency-only test failure is not a behavioral result.

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/Kazuya.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/Kazuya.profile.json --output /tmp/Kazuya.pb
python3 tools/glyph_native_profile_json.py report profiles/kazuya/Kazuya.profile.json --output /tmp/Kazuya.report.json
python3 tools/test_glyph_native_profile_json.py -v
python3 tools/test_glyph_native_profile_json_v1.py -v
python3 tools/test_kazuya_profile.py -v --report /tmp/Kazuya.host-results.json
python3 tools/check_glyph_docs_navigation.py
git diff --check
```

The optional `--workbook '/path/to/GC Left Stick Values & Vectors.xlsx'` on the
Kazuya suite checks the exact file hash and all 67 extracted raw/effective rows.
All ordinary behavioral tests remain reproducible without the private-adjacent
corpus. The raw/effective extract is committed, not the workbook.

The focused suite compiles the actual production native decoder, validator,
evaluator, Ultimate dispatch, remapper and SOCD. It checks full masks, all six
analogue axes, selected tables through tagged-coordinate native diagnostics,
and independent analogue winners through tagged-effect diagnostics. These probes
retain the same conditions/rules/gates and run the native evaluator; no Python
controller emulator is used as the implementation under test. Expected command
rows are hand-specified from the work order. Ordinary regression uses the exact
archival binary through the same production evaluator.

Coverage includes all 16 RF5–RF8 subsets, both LT2 states, all nine LF directions,
all 16 C input subsets, unrelated actions/menu buttons, RF9/RF13 precedence,
both 2IP press orders and simultaneous onset, every single RF addition/release,
and both CDC-to-singleton Shield releases. Eleven negative controls detect the
specified historical leaks, effect overrides, Mode contract mutation and residual
analogue triggers. Mode mutation is detected by the explicit contract invariant;
equal normal/mode map references would make it numerically inert.

| Resource | Actual | Planning ceiling | Hard limit | Hard capacity unused |
| --- | ---: | ---: | ---: | ---: |
| Declared tables | 16 | 24 | 28 | 12 |
| Conditions | 68 | 80 | 96 | 28 |
| Condition tokens | 220 | 600 | 768 | 548 |
| Direction sources | 6 | 8 | 8 | 2 |
| Table rules | 14 | 28 | 32 | 18 |
| Digital bindings | 20 | 30 | 32 | 12 |
| Analogue effects | 11 | 14 | 16 | 5 |
| Native body bytes | 1834 | 2860 | 3336 | 1502 |

The wrapper is 1839 bytes. All 28 wire slots consume the fixed
504-byte table block; twelve slots are neutral-filled. No planning exception.
All 68 conditions are early; fixed local clause bounds are enforced by both the
authoring compiler and native C++ admission. There is space for future source,
binding, effect and table work, subject to its own approved semantics.

Compiled wrapper SHA-256: `60f1715738fb5a46f8ac7cde326a3178e4560e52a8489da54e3a435eb70fd3e8`.
Native body SHA-256: `44fa76903206c7a86a9f5d5a19c0be5f237e1c7e631dd5adf21cdb27eb3e4405`.

Current verification: authoring suites 17/17 and 23/23 PASS; focused suite
6/6 PASS, including 110,702 archival differential frames and the corresponding
110,702 LT2 overlay frames. Final machine evidence records exact counts.

[`host-results.json`](../../tools/fixtures/kazuya/host-results.json) records the
actual focused run, tested input hashes and native-source hashes.
[`verification.json`](../../tools/fixtures/kazuya/verification.json) records the
command results and immutable archival checks.
[`independent-review.json`](../../tools/fixtures/kazuya/independent-review.json)
records the separate review, its exact input hashes and any resolved findings.
Initial retained-differential failures identified omitted simultaneous-modifier
exceptions; these were repaired and the complete focused suite rerun. An expanded
C-opponent test also corrected its expected quadrant mask to preserve both flags.

## Remaining gameplay observations and installation boundary

Host controller semantics are reviewable. The profile has not been installed or
hardware-accepted, and no game command success is claimed. Before any separate
owner-controlled installation decision, assess the provisional broad LT2 scope
conflict and the neutral fallback when neither post-SOCD horizontal input wins.

Future gameplay observations must check both physical sides and actual facing
changes; Crouch Dash entry, CDC neutral/cancel timing, Spinning Demon B, independent
four-button down-back, Hell's Gate, EWGF and while-rising A; transition/release
ordering; and whether the defensive points avoid roll/spot dodge without impairing
ordinary shield tilts. Return to full ordinary geometry after both CDC inputs
release must be observed. No delayed release or game shield-state inference is
available in this stateless contract. A timing/history requirement would be a
schema limitation and stop a follow-up implementation, not justify a macro.

Action-button Shield suppression scope and a future angled-tilt design remain
owner decisions. No controller upload, ProfileStore record operation, active
selection, Config mutation, flashing, canonical merge or installation review
approval has occurred in this task.
