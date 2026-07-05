# Latest Layout Y2 Port Plan

Status label: PLAN / DOCS-CHECKER ONLY.

This packet compares current `configurator` with
`codex/update-custom-modifier-tables-y2` and records how to reapply the latest
intended Y2/Tilt3 layout without reintroducing failed active-view publication
strategies. This branch does not implement the latest layout, does not validate
hardware for the latest layout, and only defines the port plan.

## Source Inputs

- Base branch: `configurator`.
- Reference branch: `codex/update-custom-modifier-tables-y2`.
- Port-plan branch: `runtime-config-latest-layout-y2-port-plan`.
- Current accepted safe direction: replace source-owned table contents where
  possible, keeping the already-active source-owned `RuntimeConfigView`
  selection path unchanged.
- Hardware evidence: the existing source-owned table-content replacement
  diagnostic passed the failure-sensitive RF5 forced A+Up and LT6 forced A+Down
  hardware tests, but used stale layout content and is not the final desired
  profile.
- Failed evidence: `RuntimeConfigView` replacement and active publication
  replacement paths failed hardware diagnostics.

## Change Classification

### 1. Table-Content-Only Changes

These are the only changes that fit the already-passed source-owned
table-content replacement strategy directly:

- Existing source-owned `kTilt3Table` x/y values changed in
  `src/modes/UltimateIdentityRuntimeTables.hpp`.

The intended `Tilt3` table values are:

| Direction | x | y |
| --- | ---: | ---: |
| 1 | 69 | 82 |
| 2 | 128 | 83 |
| 3 | 187 | 82 |
| 4 | 69 | 128 |
| 5 | 128 | 128 |
| 6 | 187 | 128 |
| 7 | 76 | 169 |
| 8 | 128 | 179 |
| 9 | 180 | 169 |

This is a candidate for a future table-content-only implementation branch.
That future branch would still change active output behavior, so it must carry
its own firmware build and hardware gate before merge.

### 2. Routing, Role, Evaluator, And Interpreter Changes

These changes are not covered by the table-content-only hardware pass and must
be hardware-gated separately if implemented:

- `src/modes/Ultimate.cpp` changes LT3 from L/R digital behavior into the Y2
  role, removes the L+R button behavior, migrates former Y1 sublayer behavior
  onto Y2 combinations, changes forced-up routing, changes RF3/RF4 sublayer
  role selection, and changes Tilt3 selection for `Y2+RT1+RF4`.
- `src/modes/UltimateRuntimeConfigInterpreter.hpp` increases
  `kRuntimeTableCount` from 27 to 28, adds `RuntimeTableId::Y2`, inserts
  `kY2Table` into table name/order arrays, and extends the table lookup/name
  helpers.
- `tools/check_glyph_y2_tilt3_routing.py` on the reference branch records
  evaluator/checker expectations for the new routing. Those are useful as
  source evidence for a future checker, but they are not hardware evidence.
- Generated/current-baseline evaluator fixtures on the reference branch drift
  with the old generated-config path and should not be ported directly unless
  a docs/checker branch explicitly needs them.

The intended `Y2` table values from the reference branch are:

| Direction | x | y |
| --- | ---: | ---: |
| 1 | 69 | 78 |
| 2 | 128 | 78 |
| 3 | 187 | 78 |
| 4 | 61 | 128 |
| 5 | 128 | 128 |
| 6 | 195 | 128 |
| 7 | 61 | 164 |
| 8 | 128 | 174 |
| 9 | 195 | 164 |

On current `configurator`, `Y2` is not an existing source-owned table symbol in
the active 27-table interpreter. Adding it requires interpreter/table-order and
routing changes, so the Y2 portion is not a pure table-content-only port.

The intended routing/role facts recorded by the reference checker are:

- LT3 selects Y2 and emits no L/R digital.
- Y2+RF1 alone keeps base A.
- Y2+RF1+RF4 emits X.
- Y1+RF1 no longer emits X sublayer.
- Y2+RF2 alone keeps base B.
- Y2+RF2 alone does not force up.
- Y2+RF2+RF4 forces up without base B.
- Y1+RF2 no longer forces up.
- Y2+RF3 emits B and uses LayerNormalX where applicable.
- Y1+RF3 no longer emits B sublayer.
- Y2+RF4 uses LayerFlipper where applicable.
- Y1+RF4 no longer flipper sublayer.
- Y2+RT1 selects Tilt2.
- Y2+RT1+RF4 selects Tilt3.
- Y2 priority remains below RT/RF modifiers.

Any routing/role update must be hardware-gated because it changes
`Ultimate.cpp` and interpreter behavior.

### 3. Generated Artifact, Fixture, And Tool Drift

The reference branch also changes generated source-owned artifacts, generated
output fixtures, extracted/interpreter/evaluator fixtures, generator contracts,
source-sync checkers, evaluator helpers, and old source-owned table replacement
tools. Those files are drift from the old generated-path approach.

Do not directly port those generated artifacts unless a docs/checker branch
needs them. Do not reintroduce generated active wrappers,
`RuntimeConfigView` replacement, or generated active-view selection paths.

## Port Plan

Next implementation should split the work:

A. Table-content-only update to current `configurator`.

- Replace only existing source-owned `StickPoint` table x/y contents where the
  target table already exists.
- For the current comparison, the direct candidate is `kTilt3Table`.
- Keep the existing active `RuntimeConfigView` selection and publication path.
- Do not add generated active wrappers.
- Do not port `RuntimeConfigView` replacement artifacts.
- Hardware-gate the implementation branch because active output coordinates
  change.

B. Routing/role update if required.

- Add or otherwise source-back Y2 table identity and routing only on a separate
  implementation branch.
- Treat additions to `Ultimate.cpp`,
  `UltimateRuntimeConfigInterpreter.hpp`, evaluator behavior, and checker
  expectations as separate from table-content-only replacement.
- Hardware-gate the branch before merge because it changes controller routing
  and interpreter behavior.

## Explicit Non-Claims

- This branch does not implement the latest layout.
- This branch does not validate hardware for the latest layout.
- This branch only defines the port plan.
- Hardware test is not required before merge for this docs/checker branch.
- Direct merge of `codex/update-custom-modifier-tables-y2` is not allowed.
- RuntimeConfigView replacement is not allowed.
- Active-view selection change is not allowed.
- Generated active wrapper is not allowed.
- Runtime-loaded config, persistent storage, WebSerial/device write,
  backend/config.pb write paths, and flashing automation remain not
  implemented.
- Nunchuk remains `NOT_TESTED`.
- Root cause for the failed active-publication diagnostics is not proven.
