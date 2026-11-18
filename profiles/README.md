# Native Ultimate profile authoring v1

Status: current offline authoring contract. The compiler emits the existing
schema-5 `UltimateProfile`, GNP5 encoding 1, engine ABI 1. It changes no firmware,
ProfileStore, selector, communication backend, GameCube behavior or native limit.
The human JSON is the source of truth. This format describes finite native input
and raw-output operations; it defines no character or game semantics.

Start with the valid [neutral authoring seed](templates/UltimateNativeSeed.v1.profile.json).
Copy it to a new human source file and keep that source under version control.
The seed has no physical button assumptions: constant-false cardinals, nine
`[128,128]` points, no remaps/SOCD/rules/bindings, disabled Mode/digital/D-pad
gates, and one selectedTable LS effect. It is a starting shape, not a recommended
gameplay profile; it supplies no ordinary gameplay bindings.

For evaluator order, input domains, ownership and advanced design, read
[Profile System](../docs/PROFILE_SYSTEM.md). The authoritative syntax remains
[the v1 schema](schema/glyph-native-ultimate-profile.v1.schema.json) and the
small [single-table](examples/SyntheticSingle.v1.profile.json) or
[sparse-table](examples/SyntheticSparse.v1.profile.json) examples. Both examples
are synthetic, non-product fixtures with arbitrary test coordinates. They are
not suggested controller profiles. The [v0 Ultimate source](ultimate/Ultimate.profile.json)
remains a frozen archival golden representation of retained ID27, with its own
unchanged schema and exact compilation. Do not imitate its historical table
inventory for a new profile.

## Commands

Run from the repository root with Python 3. No command opens a device.

```sh
python3 tools/glyph_native_profile_json.py validate profiles/examples/SyntheticSparse.v1.profile.json

python3 tools/glyph_native_profile_json.py compile \
  profiles/examples/SyntheticSparse.v1.profile.json --output ./SyntheticSparse.pb

python3 tools/glyph_native_profile_json.py compile \
  profiles/examples/SyntheticSparse.v1.profile.json --format protobuf-json \
  --output ./SyntheticSparse.protobuf.json

python3 tools/glyph_native_profile_json.py report \
  profiles/examples/SyntheticSparse.v1.profile.json

# Optional report file:
python3 tools/glyph_native_profile_json.py report \
  profiles/examples/SyntheticSparse.v1.profile.json --output ./SyntheticSparse.report.json

# jsonschema is a test-only dependency; the compiler uses the standard library.
python3 tools/test_glyph_native_profile_json.py -v
python3 tools/test_glyph_native_profile_json_v1.py -v
```

The compiler dispatches only on the explicit integer `formatVersion` (0 or 1).
Missing or unknown versions fail closed. Validation includes the closed JSON
schema, references/stages/priorities, total token pool, body size, and the
existing production native validator in
`tools/convert_glyph_native_ultimate_profile.py`. Standard Draft 2020-12 JSON
Schema validates syntax and local bounds independently. Cross-reference
existence, unique slot values and native graph constraints are additional
compiler checks; passing JSON Schema alone is insufficient.

The JSON loader rejects duplicate keys, including duplicate table names.
Unknown root and semantic fields fail. The small built-in schema checker adds
only `patternProperties`, `minProperties` and `maxProperties` for v1. It is not
a general JSON Schema implementation. Native integer fields require JSON integer
literals; write `1`, not `1.0` or a Boolean. Standard JSON Schema treats `1.0` as
an integer-valued number; the stricter source parser retains the established
integer-literal policy. Both validators agree on the committed contract fixtures.

The report contains the profile name/version; declared tables and name-to-slot
map; neutral-filled slots; condition, condition-token-pool, direction-source,
rule, binding and effect counts; body/wrapper sizes; preprocessing, provenance,
body and wrapper SHA-256 values. `token_count` counts tokens stored in condition
clauses, not every token-valued field. Reports describe compilation, not device
installation or physical acceptance.

## Minimal safe workflow

1. Copy [UltimateNativeSeed](templates/UltimateNativeSeed.v1.profile.json) to
   your own v1 JSON file. Establish the concrete requirements below before adding
   executable rules. Do not copy historical v0 table inventory or Kazuya intent.
2. Supply explicit preprocessing, named sources and all nine coordinates for
   every declared table. Add conditions/rules, bindings and effects only as
   required. Use [Profile System](../docs/PROFILE_SYSTEM.md) to check stage and
   priority interactions; the schema alone cannot prove those interactions.
3. Run `validate` on your file, then `compile` to a disposable `.pb`, then
   `report`. The Commands section accepts the seed or your file in place of
   SyntheticSparse. Repeat compilation and compare bytes when recording a
   candidate. JSON Schema PASS alone is insufficient.
4. Inspect the table-slot map, neutral-filled slots, counts, body budget and
   hashes. Check intended active effects and their priorities separately from
   merely valid declarations. Compiler admission proves finite native validity,
   not that the design meets a user's requirements.
5. Preserve the human JSON, its concrete requirements/design questions and its
   compilation report. Binary decode cannot recover original v1 symbols or
   sparse declaration intent. Package/install/physical acceptance is separate.

**Authoring JSON is not a complete package.** Validate/compile/report emits
native data; it does not publish a row/record, install a device configuration or
prove physical execution. See [usage](../docs/USAGE.md) and
[capabilities](../docs/CAPABILITIES.md) for the existing management boundaries.

## LLM authoring contract — clarify before encoding

An LLM may transform concrete controller requirements into this existing v1
format. It must establish the following, as applicable, and check the schema and
compiler rather than inventing another format:

| Required intent | Establish explicitly |
| --- | --- |
| Inputs and preprocessing | Physical/logical input IDs; original, pre-SOCD, post-SOCD or final digital observation; ordered remaps; SOCD pairs and policies |
| Direction and tables | Four tokens for each direction source; every declared table's nine raw coordinates; explicit slots and default table |
| Selection and digital behavior | Conditions/stages and table-selection rules; digital outputs and winner-table filters; post-mask if needed |
| Analogue behavior | Target, coordinate mode/source or trigger value, activation, priority, gates/inversion and winner filters |
| Routing and Mode | Required D-pad routing/bypass/digital suppression and stick-digital gates; whether Mode gate behavior is actually required |

Required unknown intent remains unknown. Ask the user or retain an explicit design
question outside executable JSON. If executable data is missing, do not emit a
supposedly finished profile with placeholder strings, invalid sentinel values or
invented coordinates. A valid neutral seed is not a substitute for missing intent.

A goal such as “always get neutral B” does not establish a raw coordinate
threshold. Obtain user-supplied coordinates/constraints, a separately authoritative
game-semantic source, or clarification. `metadata.character` is annotation only;
it must never act as a hidden game-semantic engine. Do not infer facing awareness,
button layout, SOCD policy, game thresholds, macro/timer/script behavior or timed
sequences. The finite native program supplies no arbitrary scripting or timers.

Do not assume all logic reads post-SOCD state. Do not assume selecting a table
changes all outputs: an eligible selectedTable effect must consume it. Keep
independent digital contributions and target-specific priority domains explicit.
A multi-role input can share conditions across table rules and bindings and drive
an effect through finalDigital; this does not require one remap to fan out.

## Feature coverage and source map

The committed examples are synthetic syntax/compilation fixtures. All current
files in `examples/*.v1.profile.json` and `templates/*.v1.profile.json` are checked
by the v1 asset tests; the current package documentation consumer runs that suite
in hosted CI. Independent standard JSON Schema checks run when `jsonschema` is
available; compiler/native admission remains mandatory without it.

| Concept | Seed | SyntheticSingle | SyntheticSparse | Authoritative section |
| --- | --- | --- | --- | --- |
| Minimal layout-free start | Constant-false source; neutral table + LS selectedTable effect | Assumes LF1..LF4 | Assumes LF1..LF4/RF inputs | Schema `directionSources`, `gates`, `analogEffects`; compiler `compile_profile` |
| Full nine-way asymmetry / non-center key 5 | All points neutral | Arbitrary nine distinct points, including 5 | Default and Diagonal_Test-2 asymmetric; ForcedDown includes non-center 5 | Schema `tables`; compiler slot/table block |
| Sparse declared slots / neutral fill | Slot 0 | Slot 27 | Slots 0,7,13,27 | Compiler `slots`, initial neutral table block; report `neutral_filled_slots` |
| Early/late and input domains | No conditions | No conditions | forceDown, alternateInput, resolvedLeft | Schema `conditions`; production `validate_native_body` stage checks |
| Selected-table rules / multi-role input | Default only | Default only, no consuming effect | RF1 → forceDown → ForcedDown + buttonA → finalDigital triggerL | Schema `tableRules`, `digitalBindings`, `analogEffects`; evaluator order in Profile System |
| selectedTable / table / fixed / inline | selectedTable | None | All four declared | Schema coordinate union; compiler effect encoding; native priority admission |
| LS/RS/both sticks and triggers | LS | No effects | All target types declared | Schema target union; production overlapping-priority checks |
| Post-mask / routing | Disabled | Disabled | Post-mask active by condition; D-pad flags false | Schema `digitalPostMask`, `dpad`; evaluator digital routing |

[SyntheticSingle](examples/SyntheticSingle.v1.profile.json) alone does not consume
its coordinate table: baseline native direction outputs still apply.
[SyntheticSparse](examples/SyntheticSparse.v1.profile.json) already covers the rich
format, so no additional large example is needed. Its fixed bothSticks and inline
LS effects lose to always-active priority-10 stick effects, triggerR activation is
false, and D-pad routing is disabled. These declarations demonstrate valid shapes,
not simultaneous execution of every path. See [subsystems](../docs/PROFILE_SYSTEM.md#subsystems--sublayers)
for small composition patterns and their limits.

## Sparse profile-owned tables

The exact table syntax is a JSON object keyed by profile-defined symbols:

```json
"tables": {
  "MyCoordinates": {
    "slot": 27,
    "directions": {
      "1": [61, 51], "2": [128, 51], "3": [195, 51],
      "4": [61, 128], "5": [129, 130], "6": [195, 128],
      "7": [61, 205], "8": [128, 205], "9": [195, 205]
    }
  }
}
```

Declare 1..28 tables. Names begin with an ASCII letter, followed by up to 63
ASCII letters, digits, underscores or hyphens. Names are case-sensitive; `any`
is reserved for winner filters. Slots are explicit unique integers 0..27.
Names and slots have no character-specific meaning. Every declared table has
exactly keys `slot` and `directions`; directions have exactly keys `1`..`9`.
Each coordinate is absolute raw `[x,y]` with integer components 0..255.
Direction 5 is ordinary stored data and may be non-center. The direction grid is:

```text
7 8 9
4 5 6
1 2 3
```

Every authoring-level reference uses a declared name: `defaultTable`, rule
`table`, coordinate `normalTable`/`modeTable`, and binding/effect `winnerTable`.
Only `winnerTable` also accepts `any`. Numeric references and undeclared names
fail. The compiler resolves each name to its explicitly assigned slot.

The wire always contains all 28 × 9 raw points: a fixed 504-byte table block
following the 96-byte header. The compiler first fills every slot with exactly
nine copies of `[128,128]`, then replaces the declared slots. Undeclared slots
are not selectable authoring tables, cannot be referenced, and inherit no data
from Ultimate, Pikachu or the current firmware defaults. A declared neutral table
is still a declared, selectable table. Unused slots consume their fixed wire
bytes but no semantic rule capacity. Neutral filling is an offline policy;
firmware receives the unchanged full block.

## Generic conditions, sources and Mode

Conditions have unique names, `stage` (`early` or `late`) and finite `all`, `any`,
`none` arrays. `all` requires every token; an empty `any` imposes no constraint,
otherwise it requires at least one; `none` requires every token to be false.
Early conditions form a prefix. A condition may reference only earlier
conditions. Base stick sources may read only early conditions. Later stages
admit resolved directions; final digital carriers are available to analogue
effect activation/gates after bindings and the post-mask. The production
validator enforces these native stage/domain rules.

Tokens are the strings `true`, `false`, or a finite domain plus symbol:
`original:`, `preSocd:`, `postSocd:`, `condition:`, `direction:` and `finalDigital:`.
`preSocd` observes remapped input before SOCD. Input symbols are LF1..LF16,
RF1..RF16, LT1..LT8, RT1..RT8 and MB1..MB12. Direction symbols are the eight
LS/RS cardinal activations listed in the schema. Digital outputs are `buttonA`,
`buttonB`, `buttonX`, `buttonY`, `buttonL`, `buttonR`, `triggerLDigital`,
`triggerRDigital`, `start`, `select`, `home`, `capture`. Named direction sources
carry explicit `left`, `right`, `down`, `up` tokens. Array order assigns dense
condition/source IDs and is preserved. Lower numeric priority wins in the
existing table/effect priority domains; priorities are 1..255 and must be unique
within their native overlapping domains. Priority 255 can win: the evaluator starts each priority domain at 256. The
authoring compiler does not normalize priorities.

Preprocessing remains `MODE_ULTIMATE` with ordered remaps and ordered SOCD
pairs/policies. Its header digest uses the existing production
`preprocessing_bytes()` contract. Reordering preprocessing entries changes it.
No expression language, macro, script or timing program exists.

One native `mode_gate` remains available through the required `gates.mode` key.
A profile that does not need global binary Mode sets it to `"false"`. A profile
that needs it may supply any token admitted by that native header-gate domain.
No Mode-specific condition graph or historical table names are required.
RF8 has no intrinsic Mode meaning; a profile may explicitly reference it like
any other input. No second Mode gate is introduced. Table-coordinate effects
retain both existing table-ID fields:

```json
"coordinates": {
  "mode": "table",
  "normalTable": "MyCoordinates",
  "modeTable": "AlternateCoordinates"
}
```

Both tables must be declared, even with `gates.mode = "false"`. The existing
Mode gate selects the normal versus alternate table in that effect. Mode does
not automatically create table rules or change the profile's inventory.

## Authored-source provenance

Every v1 profile uses the closed object:

```json
"provenance": { "kind": "authoredSourceV1" }
```

Authors never supply a digest. Historical v0
`preservedConversionSourceSha256` is rejected in v1. Compilation derives header
bytes 60..91 as:

```text
SHA256(b"Glyph.Native.Authoring.v1\0" + canonical_semantic_source_utf8)
```

The domain contains exactly one final zero byte. After source validation,
canonical semantic source is the entire JSON object excluding only the root
keys `provenance`, `metadata` and `name`. Canonical serialization is exactly
Python `json.dumps(semantic, sort_keys=True, separators=(',', ':'),
ensure_ascii=False, allow_nan=False).encode('utf-8')`: object keys sort
lexicographically by Unicode code point, arrays retain order, no insignificant
whitespace is emitted, non-ASCII text uses UTF-8 without ASCII escaping, and
no trailing newline is included. No defaults are inserted or source arrays
normalized. All executable fields, symbolic condition/source/table names and
slot assignments are included.

Whitespace and object-key order do not affect provenance. Display-name and
valid metadata-only edits change neither provenance nor compiled bytes.
Executable coordinate/condition/rule edits change provenance automatically.
Renaming a table/condition/source and updating references also changes provenance,
even when the remaining wire semantics are equivalent. This identifies the
semantic authoring source, not merely equivalent evaluator behavior. Metadata
has the same optional closed annotation shape as v0: description, notes and
nullable character. Store identity/revision remain outside this source format.

## Limits and binary decoding

Existing native limits are unchanged:

| Resource | Limit |
| --- | ---: |
| Physical wire table slots | 28 |
| Declared v1 tables | 1..28 |
| Conditions | 96 |
| Tokens per condition: all / any / none | 2 / 4 / 9 |
| Total condition token pool | 768 |
| Direction sources | 1..8 |
| Table rules | 32 |
| Digital bindings | 32 |
| Analogue effects | 16 |
| Native body bytes | 3336 |

A binary body alone cannot reconstruct the original v1 authoring source exactly.
Schema 5 stores no human table, condition or source names, nor which neutral
slots were intentionally undeclared. Keep the v1 JSON. No authoring-label storage
or v1 decoder is added. The existing `decode` command returns only a v0-shaped
wire representation with historical slot labels and generic condition/source
labels (or existing exact-body correspondence for conditions). Those labels do
not recover v1 names or declaration intent. A decoded provenance field preserves
opaque header bytes under the old v0 field name; decoding an authored body does
not establish historical converter provenance. Recompiling that representation
can preserve bytes, but it is not a recovered v1 source.

The existing uploader remains separate at
`tools/glyph_profile_store_production_tool.py`; no upload/device mutation UX is
added. A later reviewed character profile may feed its compiled wrapper through
that established path under separate device authority. This milestone does not
design Kazuya or a Senscope neutral/export schema. Build inputs and firmware
behavior remain unchanged, so hardware acceptance is not required.
