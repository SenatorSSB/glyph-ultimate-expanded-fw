# Kazuya v2 — KazTest2

**HOST_VERIFIED** test candidate from live canonical `bf6f1e2e6814c6b6f1eb710175a488961c8295e7`,
on `codex/kazuya-v2-profile`. The direct owner work order attached to this chat
supplies the v2 output specification and conditional authority for exactly one
new production ProfileStore CREATE. No firmware, schema, evaluator, SOCD/remap,
ProfileStore, menu, Config or historical v1 evidence changes. No canonical merge.
This is controller-output verification; gameplay and Nunchuk remain NOT_TESTED.

## Command matrix

LF1/LF3 are actual physical right/left; LF2/LF5 physical up/down. Existing ordered
2IP SOCD and identity RF3/RF4/LT3 preprocessing are unchanged. There is no facing
inference, hidden RF history, delay, script or automatic sequence. All command
maps use a dedicated `physicalLeft` post-SOCD source, never synthetic Up.
Independent physical A/B/menu/trigger/C-stick contributions remain compositional.

| Held inputs | Left-stick geometry | RF5/RF6 contribution |
| --- | --- | --- |
| none | Default | none |
| RF5 | straight Up | A |
| RF6 | RF6 ordinary | Z |
| RF5+RF6 | straight Up | A |
| RF7 | RF7ReleaseNeutral | none |
| RF7+RF5 | SpringloadUp | none |
| RF7+RF6 | Default | none |
| RF7+RF5+RF6 | SpringloadUp | none |
| RF8 | ForcedDown | none |
| RF8+RF5 | DownDiagonal | A |
| RF8+RF6 | DownDiagonal | Z |
| RF8+RF5+RF6 | DownDiagonal | A |
| RF8+RF7 | CDArmed | none |
| RF8+RF7+RF5 | CDArmed | none |
| RF8+RF7+RF6 | CDCNeutral | none |
| RF8+RF7+RF5+RF6 | CDCNeutral | none |

`ForcedDown`: [128,51] in all nine directions. `RF7ReleaseNeutral`: neutral
[128,128] on4/5/6, full Default on1/2/3/7/8/9. `CDArmed`: down-left [61,51] on4,
Down [128,51] on5, down-right [195,51] on6, neutral on all vertical-bearing keys.
`SpringloadUp`: full physical Default except neutral5 becomes straight Up
[128,205]. `CDCNeutral`: exact center everywhere. `DownDiagonal`: left column
[61,51], middle column neutral, right column [195,51], independent of vertical.
Its no-horizontal neutral fallback preserves the documented v1 candidate.

RF5 with no RF7/RF8 supplies straight strong Up+A, also when RF6 is held. RF8+RF5
supplies down-diagonal+A. RF7 withholds its A until release. RF6 supplies Z only
when RF7 and RF5 are absent; RF8+RF6 shares the same DownDiagonal map.

RF6 ordinary table entries7/8/9 are each exactly [128,205], replacing
[89,167], [128,177], [167,167]. Physical Up selects those straight strong entries.
When physical Up is absent, a priority50 inline copy of the original RF6 map
preserves existing synthetic-only Up sublayers and other weak coordinates.
Both RF6 effects are suppressed by RF5/RF7/RF8 as specified. Existing null/D-pad
precedence remains outside commands; LT6 takes highest LS priority.

## LT6 and LT2

LT6 independently contributes A and fixes LS at [128,128], using one priority1
fixed effect above command5/null10/D-pad20/RF6 50/60/forcedUp80/default200.
It does not change RS or suppress independent B/Z or Shield. The existing
firmware Nunchuk tail can subsequently replace stick bytes; it remains untested.
A future LT6-to-Shield suppression policy is outside this work order.

LT2 contributes buttonL + GameCube triggerLDigital + triggerRDigital, and analogue
L/R140 only while each final digital carrier is active. It changes no stick
coordinates. Its shared binding gate withholds the entire LT2 contribution when
physical RF3 is held, RF5 A is executable (RF5 and no RF7), or physical post-SOCD
LF2 is held with RF1 or RF2. Synthetic Up never substitutes for physical LF2.
LT1/RF16 contributions survive independently. RF7+RF5 keeps Shield until RF7
release; Up alone keeps Shield angling. No global digital post-mask is added.

## Reproduction and evidence

From repository root, with Python3, test-only jsonschema, existing Nanopb dependency,
and a C/C++ compiler:

```sh
python3 tools/glyph_native_profile_json.py validate profiles/kazuya/v2/KazuyaV2.profile.json
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/v2/KazuyaV2.profile.json --output /tmp/KazuyaV2.pb
python3 tools/glyph_native_profile_json.py compile profiles/kazuya/v2/KazuyaV2.profile.json --format protobuf-json --output /tmp/KazuyaV2.protobuf.json
python3 tools/glyph_native_profile_json.py report profiles/kazuya/v2/KazuyaV2.profile.json --output /tmp/KazuyaV2.report.json
python3 tools/test_glyph_native_profile_json.py -v
python3 tools/test_glyph_native_profile_json_v1.py -v
python3 tools/test_kazuya_profile.py -v
python3 tools/test_kazuya_profile_v2.py -v --report /tmp/KazuyaV2.host-results.json
```

This host used `/private/tmp/glyph-kazuya-test-venv/bin/python` (default Python
lacks test-only jsonschema) and linked the unchanged existing Nanopb dependency.
Both authoring suites17/17 and23/23, unchanged v1 native6/6 and v2 native8/8 PASS.
The actual C++ native decoder/admission, preprocessing, SOCD, Ultimate dispatch,
and evaluator run in the existing harness. Python contains expected finite rows,
not a replacement evaluator. Tagged native diagnostics prove table and effect
selection where equal numerical points would otherwise hide precedence.

Coverage: all16 RF subsets ×9 directions; both SOCD histories on both axes and
simultaneous opponents; all single RF edges; the specified sequences and reverse/
simultaneous releases; exact full digital masks and all analogue axes;
3,473 LT2/carrier cases;2,016 LT6 overrides;4,176 matrix/priority cases;
2,916 release frames;482 SOCD assertions;13,878 complete ordinary comparisons
against v1 and archival Ultimate;221,184 retained RS/carrier comparisons with
full retained low12-bit digital assertions;9,269 full-output RF6 cases without
physical Up;11 negative controls. Independent review is linked below.

[Compile report](../../../tools/fixtures/kazuya/v2/compile-report.json),
[host results](../../../tools/fixtures/kazuya/v2/host-results.json),
[verification/inventory/priority/digital audit](../../../tools/fixtures/kazuya/v2/verification.json),
[frozen v1/archival hashes](../../../tools/fixtures/kazuya/v2/frozen-baselines.json),
[independent review](../../../tools/fixtures/kazuya/v2/independent-review.json)
preserve exact source and compiled identities. No v1 file or historical result
was rewritten. All declared table points occur in the original measured
[coordinate evidence](../../../tools/fixtures/kazuya/coordinate-evidence.json).

| Resource | Used | Hard limit | Headroom |
| --- | ---: | ---: | ---: |
| declared_tables | 17 | 28 | 11 |
| condition_count | 67 | 96 | 29 |
| token_count | 221 | 768 | 547 |
| direction_source_count | 7 | 8 | 1 |
| table_rule_count | 16 | 32 | 16 |
| digital_binding_count | 18 | 32 | 14 |
| analog_effect_count | 13 | 16 | 3 |
| body_bytes | 1902 | 3336 | 1434 |

Wrapper: 1907 bytes, SHA-256 `b43f5fa595582b076e9af6794a42fd01579eed6931b38da8f92c1537b1fcfa24`.
Body: SHA-256 `9658566f59fd2bb058282b53b4f86610c2ff870a1492c4377ea143ce9cf1f91f`.
Authored provenance: `57abfb736ea2391a6c20eebc915cc0dae1cdbcfaf39fd8c351acc3eed2e6709c`.
Preprocessing: `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f`.
Protobuf JSON file SHA-256: `75d37cc9acaf67136d1f97d4d042cf5232342635b08662b43ee1d2b6e4efbe99`.

## Guarded installation and owner testing

The separately authorized device operation is one CREATE of **KazTest2**, after
fresh normal-Configurator identity, physical-unit matching, healthy production
protocol2 status, complete directory/record/Config backup, compatible native
preprocessing/context and capacity checks. Use only the compiled protobuf JSON
wrapper (not authoring JSON), fresh fences/token, unused rank/name and exclusive
new host journal/request receipt. Do not update/delete any profile, change host
references, flash, reset or retry an uncertain CREATE. After successful CREATE,
read back the exact candidate and verify all prior records/metadata, raw Config,
references and directory preservation before claiming device verification.
Private controller identity/Config/token receipts remain outside Git.

Device creation, gameplay selection and acceptance are separate statuses; the
host evidence does not assert them. See [gameplay test sheet](GAMEPLAY_TEST.md)
for owner selection and actual testing. The feature branch stays unmerged until
owner hardware/gameplay results are reviewed.
