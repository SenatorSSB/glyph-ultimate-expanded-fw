# Native Ultimate profile authoring v1

Status: current offline authoring contract. The compiler emits the existing
schema-5 `UltimateProfile`, GNP5 encoding 1, engine ABI 1. It changes no firmware,
ProfileStore, selector, communication backend, GameCube behavior or native limit.
The human JSON is the source of truth. This format describes finite native input
and raw-output operations; it defines no character or game semantics.

Use [the v1 schema](schema/glyph-native-ultimate-profile.v1.schema.json) and the
small [single-table](examples/SyntheticSingle.v1.profile.json) or
[sparse-table](examples/SyntheticSparse.v1.profile.json) examples. Both examples
are synthetic, non-product fixtures with arbitrary test coordinates. They are
not suggested controller profiles. The [v0 Ultimate source](ultimate/README.md)
remains a frozen archival golden representation of retained ID27, with its own
unchanged schema and exact compilation. Do not imitate its historical table
inventory for a new profile.

## Commands

Run from the repository root with Python 3. No command opens a device.

```sh
python3 tools/glyph_native_profile_json.py validate profiles/examples/SyntheticSparse.v1.profile.json

python3 tools/glyph_native_profile_json.py compile \
  profiles/examples/SyntheticSparse.v1.profile.json --output /tmp/SyntheticSparse.pb

python3 tools/glyph_native_profile_json.py compile \
  profiles/examples/SyntheticSparse.v1.profile.json --format protobuf-json \
  --output /tmp/SyntheticSparse.protobuf.json

python3 tools/glyph_native_profile_json.py report \
  profiles/examples/SyntheticSparse.v1.profile.json

# Optional report file:
python3 tools/glyph_native_profile_json.py report \
  profiles/examples/SyntheticSparse.v1.profile.json --output /tmp/SyntheticSparse.report.json

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

## Human concepts

```text
conditions
    ↓
table-selection rules
    ↓
one selected 9-way coordinate table

separate finite sections:
    digital bindings
    analogue effects
```

Conditions combine finite input observations. Table rules choose the selected
coordinate table; the default applies when no rule wins. Several command
combinations can share a table, through separate rules or a shared condition.
The number of physical buttons is not the number of modifier slots. Conditions,
rules, sources, bindings and effects have separate finite capacities; they are
not one slot per physical button.

Digital bindings set named output bits with a token and optional winner-table
filter. Analogue effects separately target `leftStick`, `rightStick`,
`bothSticks`, `triggerL` or `triggerR`. Stick coordinate modes are `selectedTable`,
`table`, `fixed` and `inline`. A trigger effect instead carries one integer byte
`value`. A selected table affects the native selected-table coordinate path;
fixed/inline/table effects can independently supply coordinates according to
the existing evaluator. Digital post-mask and D-pad routing retain the existing
native fields and semantics.

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
within their native overlapping domains. Priority 255 retains native comparison
behavior and is not normalized by the authoring compiler.

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
