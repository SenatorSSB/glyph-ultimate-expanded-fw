# Editable native Ultimate profile v0

[Ultimate.profile.json](Ultimate.profile.json) is the human-editable source of the
owner's working native Ultimate profile. [Ultimate.profile.schema.json](Ultimate.profile.schema.json)
describes its finite JSON syntax. The offline compiler emits the existing
schema-5 `UltimateProfile` wrapper and encoding-1 / engine-ABI-1 GNP5 body.
No firmware, device, Config, ProfileStore or selector behavior changes here.
This is a separate authoring/tooling chapter; GP-NATIVE-002 remains DONE.

## Golden recovery and exact proof

The source was recovered from retained read-only campaign captures, without
accessing the controller for this task. The latest capture's manifest binds the
READ wrapper, decoded READ response, directory, Config wrapper and Config JSON.
Four pre/post-selector ID27 copies and the original conversion package are
byte-identical. Their directory/READ metadata confirms ID **27**, revision **1**,
stored name **Ultimate**, schema **5**. This describes retained evidence; no new
live-current device observation is claimed.

| Exact artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Original and compiled protobuf wrapper | 1985 | `30d43278fee3a835ca006f4b5df67963c8e9b11ef059ab3b49329b65c7934c6b` |
| Original and compiled native body | 1980 | `ca9985997471f247d2f44ba1290e95197393a6c6bdf80a5e59a357f2d6c3e5ee` |
| Ordered preprocessing contract | 43 | `3bd30c1151a171c5693319f534772e0427d3d177fcaaa15f823eecf75a25f51f` |

Exact wrapper byte match: **PASS**. Exact native body byte match: **PASS**.
The preprocessing hash equals bytes 28..59 of the recovered native header,
using production `preprocessing_bytes()` from the existing converter.
There are 71 early conditions, 280 tokens, seven direction sources,
19 table rules, 18 digital bindings, 11 analogue effects and 28 nine-way tables.

The public [golden fixture](../../tools/fixtures/native_profile_json/Ultimate.pb)
contains only schema and native body. Stable ID/revision/name, device identifiers,
Config receipts, serial details and session metadata are absent from that binary.
The [portable context](../../tools/fixtures/native_profile_json/preprocessing-context.json),
[sanitized recovery record](../../tools/fixtures/native_profile_json/recovery.json),
[condition-label correspondence](../../tools/fixtures/native_profile_json/naming-correspondence.json)
and [verification record](../../tools/fixtures/native_profile_json/roundtrip.json)
make the public proof reproducible. The separate ignored local proof package is
`local_backups/ultimate-profile-json-20261023/` in the original checkout. It retains
`original-id27.pb`, `compiled-id27.pb`, `original-native.body`,
`compiled-native.body`, `roundtrip.json` and the private recovery witnesses.
Historical campaign evidence was read, never rewritten.

## Commands

Run from the repository root with Python 3. The codec uses the standard library
and the existing production converter's finite validator/context contract.
It never imports serial transport or opens a controller.

```sh
# Decode exact PB, protobuf JSON, or an exported successful READ response.
# The ordered preprocessing context must be supplied and must match its hash.
python3 tools/glyph_native_profile_json.py decode \
  tools/fixtures/native_profile_json/Ultimate.pb \
  --preprocessing tools/fixtures/native_profile_json/preprocessing-context.json \
  --correspondence tools/fixtures/native_profile_json/naming-correspondence.json \
  --output /tmp/Ultimate.decoded.profile.json

python3 tools/glyph_native_profile_json.py validate profiles/ultimate/Ultimate.profile.json

python3 tools/glyph_native_profile_json.py compile \
  profiles/ultimate/Ultimate.profile.json --output /tmp/Ultimate.pb

python3 tools/glyph_native_profile_json.py compile \
  profiles/ultimate/Ultimate.profile.json --format protobuf-json \
  --output /tmp/Ultimate.protobuf.json

cmp tools/fixtures/native_profile_json/Ultimate.pb /tmp/Ultimate.pb

# Test-only dependency for independent standard JSON Schema validation:
python3 -m pip install 'jsonschema>=4.18,<5'
python3 tools/test_glyph_native_profile_json.py -v
```

The correspondence option is optional. Without it the decoder assigns neutral
`conditionNN` names. With the exact-body-bound retained correspondence it keeps
the converter's established intrinsic names (`c_any`, `y2sub`, `base_rf3`, etc.),
then `legacyRole01`..`legacyRole22` and `tableRuleGate00`..`tableRuleGate18`.
These are source labels, not independently asserted gameplay meanings.
The decoded file omits optional metadata; that does not affect compiled bytes.
READ exports may use the established snake_case or protobuf camelCase field
spelling. Ambiguous aliases, unsuccessful READ results and unknown fields fail.
The tool has no upload, CREATE, UPDATE or other device operation.

## Source sections

| Section | Meaning |
| --- | --- |
| `format`, `formatVersion` | Fixed format identifier and integer version 0. |
| `name` | Human label; not serialized inside `UltimateProfile` and not a rename command. |
| `provenance` | Explicit preserved historical conversion SHA-256, described below. |
| `preprocessing` | `MODE_ULTIMATE`, ordered remaps, ordered SOCD pairs and policies. |
| `tables` | All 28 named numeric table IDs and all nine absolute raw coordinate pairs. |
| `defaultTable` | Table used when no winning table rule applies. |
| `conditions` | Ordered named finite `all` / `any` / `none` clauses and early/late stage. |
| `directionSources` | Ordered named left/right/down/up token records. |
| `leftStickSource`, `rightStickSource` | Base direction source names. |
| `gates` | Mode-table selection, LS/RS digital and D-pad gates. |
| `tableRules` | Unique priorities, target tables and token gates. |
| `digitalBindings` | Token gates, named output bits and optional winner-table filter (`any`). |
| `analogEffects` | Targets, priorities, activation/additional gates, coordinates or trigger values, winner filters and explicit flags. |
| `digitalPostMask` | Gate, inversion and disjoint named set/clear masks. |
| `dpad` | Independent routing, left-stick bypass and left-stick digital suppression flags. |
| `metadata` | Optional closed description, notes and nullable character; ignored when compiling native bytes. |

Unknown semantic fields fail. Objects have closed shapes. Array order is
preserved. The compiler assigns conditions and sources dense IDs from their
array positions, beginning at 1; names must be unique. Conditions may refer only
to earlier conditions, so forward/cyclic dependencies fail. Early conditions
form a prefix, and base direction sources may use only early conditions.
Late conditions can read resolved cardinal directions. Final digital carriers
are available only to analogue effect gates/activation, after bindings and the
post-mask. No expression parser, scripting, macros or timing program is added.

### Tokens and digital outputs

Tokens are a finite symbolic vocabulary, for example:

```json
{
  "name": "example",
  "stage": "early",
  "all": ["postSocd:LF3", "condition:c_any"],
  "any": [],
  "none": ["original:RF4"]
}
```

`original:`, `preSocd:` and `postSocd:` address the 60 physical/input IDs
LF1..LF16, RF1..RF16, LT1..LT8, RT1..RT8, MB1..MB12. `preSocd` means remapped
before SOCD. `condition:` names a condition; `direction:` names one of eight
resolved LS/RS left/right/down/up activations. `finalDigital:` names a final
output carrier. Constants are `true` and `false` strings.
Every `all` token must be true; an empty `any` imposes no constraint, otherwise
at least one must be true; every `none` token must be false.

Bits 0..11, in order, are `buttonA`, `buttonB`, `buttonX`, `buttonY`, `buttonL`,
`buttonR`, `triggerLDigital`, `triggerRDigital`, `start`, `select`, `home`,
`capture`. These are controller semantic outputs. In particular, internal
`buttonR` is serialized as **GameCube Z**, while `triggerRDigital` is serialized
as **GameCube R**. Trigger analogue values are separate effects. This mapping
is source-backed by `include/core/state.hpp` and
`HAL/pico/src/comms/GamecubeBackend.cpp`; the source does not describe packet bytes.

### Tables and coordinates

Each table explicitly includes its stable `id` and direction keys:

```text
7 8 9
4 5 6
1 2 3
```

Each value is absolute `[x, y]`, both integers 0..255. Direction 5 is stored data;
it is not implicitly centered. The recovered Mode tables deliberately retain
`[128,169]` at direction 5. Asymmetric points and all historical coordinates are
preserved without normalization or inferred gameplay corrections.

The format retains the repository's authoritative runtime enum spellings.
The longer descriptive equivalents from the authoring brief map as follows:

| Source name | Descriptive equivalent |
| --- | --- |
| `MX1`, `MX2`, `MY1` | ModeX1, ModeX2, ModeY1 |
| `MLayerNormalX`, `MLayerFlipper` | ModeLayerNormalX, ModeLayerFlipper |
| `MY1Tilt1`, `MY1LayerFlipper`, `MY1LayerNormalX` | ModeY1Tilt1, ModeY1LayerFlipper, ModeY1LayerNormalX |
| `MTilt1`, `MTilt2`, `MTilt3` | ModeTilt1, ModeTilt2, ModeTilt3 |
| `Lt1LowMagnitude` | LowMagnitudeAirdodge |

Other names match directly. Table IDs and spelling come from
`tools/extract_glyph_identity_runtime_tables.py` / `RuntimeTableId`; the codec
does not read current coordinate constants to replace stored profile values.

### Effects, stages and limits

Targets are `leftStick`, `rightStick`, `bothSticks`, `triggerL`, `triggerR`.
Stick effects select a direction source and one coordinate union:
`selectedTable`, `table` (normal/mode table names), `fixed` (one raw point),
or `inline` (nine raw points). Trigger effects carry one byte `value` and
have no coordinate union or direction source. Gates, inversion, winner filters
and `skipWhenDpadBypass` preserve the corresponding native fields.
Lower numeric priority wins within each table/effect target domain; overlapping
both-stick priorities must also be unique. Priority 255 remains admitted by the
production format and preserves its existing comparison behavior.

The golden effect indexes map to retained converter phases: 0/1 BASE_TABLE
LS/RS; 2 DIRECTION_A; 3 RF6; 4 RF7; 5 RS_DIAGONAL; 6 RF3_VERTICAL;
7 NULL (both sticks); 8/9 TRIGGERS L/R; 10 DPAD. The DIGITAL phase is the
separate post-mask. These labels document correspondence, not extra phases.

Production bounds remain: 28 tables; 96 conditions; per-condition 2 `all`,
4 `any`, 9 `none`; 768 total tokens; 1..8 direction sources; 32 table rules;
32 digital bindings; 16 effects; body at most 3336 bytes. The schema checks
local syntax/limits; compilation additionally checks reference/stage rules,
priorities, masks, union invariants and total body size with the production
native validator. Reserved bytes and inactive union storage must be zero;
nonzero unsupported fields fail rather than disappearing on decode.

## Derived data and historical provenance

Magic `GNP5`, encoding 1, ABI 1, lengths, section counts, dense IDs, token count,
zero reserved fields and preprocessing SHA-256 are derived by the compiler.
The preprocessing bytes are exactly production `preprocessing_bytes()` in
`tools/convert_glyph_native_ultimate_profile.py`. Reordering entries changes
the digest; decode refuses a mismatching supplied context.

`provenance.kind = preservedConversionSourceSha256` is deliberately different:
its digest `f09a210f9fc7400d52673f6455004185451d33575e88eb0fc54abfc73297dda0`
records the historical legacy conversion policy/options/source protobuf. It is
copied into header bytes 60..91. It is neither a checksum of this editable JSON
nor an executable controller behavior. Editing JSON retains that historical
provenance; it does not assert a fresh converter attestation. A future provenance
policy/version can add new source identity separately. Optional annotations and
the human `name` never alter native bytes. Stable ProfileStore ID and revision
are outside the authoring schema.

The existing V1–V3 converter is unchanged. Reusing its production native
validator and preprocessing contract avoids an encoding migration or a broad
converter refactor. Independent native-ABI fixtures and both-ABI legacy/native
output regressions cover compatibility; hardware acceptance is unnecessary
because this chapter changes no firmware and performs no controller mutation.
Nunchuk physical acceptance remains NOT_TESTED; no root-cause claim is added.

## Deferred beta work

Upload UX and mutation review, JSON version migrations, additional friendly
aliases, Senscope export and a browser editor are separate work. This format is
an explicit finite native authoring boundary, not a game-semantic model or a
Senscope neutral-schema decision. Existing upload remains the responsibility of
`tools/glyph_profile_store_production_tool.py` after separate mutation UX review.
