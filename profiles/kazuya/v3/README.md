# Kazuya v3 — KazTest3

**HOST_VERIFIED; gameplay NOT_TESTED.** This narrow owner-authorized correction
uses exact pushed v2 commit `1381193b0101825d2a9afb46cd7a01009da67cdf` as its
behavioral baseline. Live canonical remains `bf6f1e2e6814c6b6f1eb710175a488961c8295e7`.
Branch: `codex/kazuya-v3-profile`. No canonical merge or gameplay acceptance.

The owner reports frame-by-frame gameplay observations: a forward cancel before
RF5 A can yield unwanted Left Splits Kick even when the attack-time stick is Up;
making Up the first post-neutral direction avoided that reported result. This is
owner-supplied motivation, not a claim about game input buffers or timing rules.

The existing offline draft was inspected, found to contain exactly the requested
coordinate correction, and preserved privately before reuse under v3 paths/name.
V1/v2 source, tests and historical evidence remain byte-identical; the frozen
baseline manifest pins all of them. Firmware, native evaluator, authoring schema,
encoding, preprocessing, SOCD/remaps, ProfileStore and menu implementation are unchanged.

## Exact correction

Every `SpringloadUp` direction1..9 in slot16 is now raw **[128,205]**, measured
as effective **[0,+120]** in the original
[coordinate evidence](../../../tools/fixtures/kazuya/coordinate-evidence.json).
The existing gate is unchanged: RF7+RF5 with RF8 absent, RF6 optional. RF5 A and
RF6 Z/weak geometry remain withheld. The command LS effect remains priority5;
LT6 priority1 still forces neutral+A. All conditions, priorities, sources,
bindings, other tables and right-stick effects are exact v2. Native quadrant
flags remain v2; GameCube uses the raw stick bytes. No facing inference, timers,
history, scripts or delayed activation are introduced. The native binary delta
is restricted to slot16 coordinates and the authored semantic digest.

## Complete RF matrix

These are command contributions; independent buttons may add their own outputs.
LT6 retains its absolute neutral+A override. Retained ordinary null/D-pad and
modifier behavior remain as documented for v2.

| Held RF inputs | Raw geometry | RF5/RF6 digital contribution |
| --- | --- | --- |
| none | Default | none |
| RF5 | pure Up | A |
| RF6 | ordinary RF6; physical7/8/9 straight Up | Z |
| RF5+RF6 | pure Up | A, no Z |
| RF7 | RF7ReleaseNeutral | none |
| RF7+RF5 | pure Up (changed) | none |
| RF7+RF6 | Default physical | none |
| RF7+RF5+RF6 | pure Up (changed) | none |
| RF8 | ForcedDown | none |
| RF8+RF5 | DownDiagonal | A |
| RF8+RF6 | DownDiagonal | Z |
| RF8+RF5+RF6 | DownDiagonal | A, no Z |
| RF8+RF7 | CDArmed | none |
| RF8+RF7+RF5 | CDArmed | none |
| RF8+RF7+RF6 | CDCNeutral | none |
| RF8+RF7+RF5+RF6 | CDCNeutral | none |

Pure Up=[128,205]; neutral=[128,128]. ForcedDown=[128,51] everywhere.
CDArmed: keys4/5/6 → [61,51]/[128,51]/[195,51]; all other keys → neutral.
DownDiagonal: left/middle/right columns → [61,51]/neutral/[195,51].
RF7ReleaseNeutral: keys4/5/6 neutral, other keys full Default.
RF6-only spring-loaded grab keeps Default physical geometry and withholds Z.
RF6 ordinary physical-Up7/8/9 stays straight strong Up; nonphysical-Up weak
sublayers stay exact v2. All existing LT2 conditional Shield and independent
LT1/RF16 contributions remain unchanged.

## Release transition matrix

Each arrow below is an actual manual input transition, without generated delays.
The sequence descriptions refer to RF buttons; hold either physical horizontal
side, any other LF direction or none. The native suite covers all nine directions.

| Starting state | Release order | Successive geometry and command output |
| --- | --- | --- |
| RF8+RF7+RF5+RF6 | RF8, then RF7 | Neutral/no A/Z → Up/no A/Z → Up+A/no Z |
| RF8+RF7+RF5 | RF8, then RF7 | CDArmed/no A → Up/no A → Up+A |
| RF8+RF7+RF5+RF6 | RF7, then RF8 | Neutral/no A/Z → DownDiagonal+A/no Z → Up+A/no Z |
| RF8+RF7+RF5 | RF7, then RF8 | CDArmed/no A → DownDiagonal+A → Up+A |
| Either RF5 starting state | RF8 and RF7 together | Initial geometry → Up+A/no Z |
| RF7+RF5 | Add/remove RF6 | Up/no A/Z throughout |
| RF8+RF7+RF6 | RF8, then RF7 | Neutral/no Z → Default/no Z → ordinary RF6+Z |
| RF8+RF7+RF6 | RF7, then RF8 | Neutral/no Z → DownDiagonal+Z → ordinary RF6+Z |

LT2+RF7+RF5 keeps Shield while A is withheld; releasing RF7 executes RF5 A and
withholds LT2's own Shield contribution. Independent LT1/RF16 remain active.
Direct EWGF/Hell's Gate and reverse-release distinctions remain v2.

## Verification and identities

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/v3/KazuyaV3.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/v3/KazuyaV3.profile.json --output /tmp/KazuyaV3.pb
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/v3/KazuyaV3.profile.json --format protobuf-json --output /tmp/KazuyaV3.protobuf.json
python3 tools/glyph_native_profile_json.py report profiles/kazuya/v3/KazuyaV3.profile.json
python3 tools/test_glyph_native_profile_json.py -v
python3 tools/test_glyph_native_profile_json_v1.py -v
python3 tools/test_kazuya_profile.py -v
python3 tools/test_kazuya_profile_v2.py -v
python3 tools/test_kazuya_profile_v3.py -v --report /tmp/KazuyaV3.host-results.json
```

This host uses the existing `/private/tmp/glyph-kazuya-test-venv/bin/python`
for test-only jsonschema and the unchanged existing Nanopb dependency. The v3
suite loads an isolated copy of the frozen v2 harness; it changes only the
expected SpringloadUp rows and versioned source/evidence paths. The C++ production
preprocessor, SOCD, admission, Ultimate dispatch and evaluator remain the test subject.
Tests assert full digital masks and raw axes, both SOCD histories and simultaneous
opponents, all16 RF subsets and9 physical directions, release orders, LT2/LT6,
retained modifier/C-stick behavior and v1/archive preservation.

11/11 v3 tests PASS; authoring17/17 and23/23, retained v1 6/6 and v2 8/8 PASS.
74,880 exact native comparisons against v2 permit only spring-loaded LS coordinate
changes;108 focused release frames assert first-frame Up before A. Reinstating
old SpringloadUp fails four dedicated native poses;11 inherited negative controls
also detect leaks and priority defects. Independent native rerun11/11 PASS.

[Host report](../../../tools/fixtures/kazuya/v3/host-results.json),
[compile/resource report](../../../tools/fixtures/kazuya/v3/compile-report.json),
[verification](../../../tools/fixtures/kazuya/v3/verification.json),
[independent review](../../../tools/fixtures/kazuya/v3/independent-review.json),
[frozen baselines](../../../tools/fixtures/kazuya/v3/frozen-baselines.json), and
[owner feedback/authority](../../../tools/fixtures/kazuya/v3/owner-feedback.json)
preserve exact claims and input identities.

| Resource | Actual | Limit | Headroom |
| --- | ---: | ---: | ---: |
| declared_tables | 17 | 28 | 11 |
| condition_count | 67 | 96 | 29 |
| token_count | 221 | 768 | 547 |
| direction_source_count | 7 | 8 | 1 |
| table_rule_count | 16 | 32 | 16 |
| digital_binding_count | 18 | 32 | 14 |
| analog_effect_count | 13 | 16 | 3 |
| body_bytes | 1902 | 3336 | 1434 |

Wrapper 1907 bytes: `1f919177691afc7ba35621229301169f710540c5e74952487b25ed3db0782131`.
Body: `22263a77a2f6b2555747381634ec1f80c5b96e81f793e2aea4027ed5fb142e3d`.
Authored provenance: `10d0692cd7490e07113965bd1569242a837468e92d26d200e9c6a75f5ecc4843`.
Preprocessing: `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f`.
Protobuf JSON file: `1e4e56ebe31ce0b5f2299d6099d5dd3874d8dc44394cbf5320e8f37551f48e10`.

## Device boundary

The current owner work order authorizes at most one new **KazTest3** CREATE
through the unchanged production operator, after fresh physical-unit/Configurator
identity, healthy STATUS/fences, complete directory/Config/record preservation,
compatibility and capacity proof. Use compiled protobuf JSON with a fresh token,
unused name/rank and exclusive journal/request receipt. READ back exact payload;
verify every old record/metadata and raw Config/reference unchanged. Stop on any
uncertainty without retries or further mutation. Do not UPDATE/DELETE KazTest2
or any record, flash firmware, write whole Config or select a host reference.
Private device receipts remain outside Git. This offline evidence snapshot
claims no creation, selection or gameplay acceptance.

See [owner comparison checklist](GAMEPLAY_TEST.md) after separately verified CREATE.
