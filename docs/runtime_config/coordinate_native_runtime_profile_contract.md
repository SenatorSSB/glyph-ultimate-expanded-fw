# Coordinate-Native Runtime Profile Contract

Status label: INACTIVE DESIGN / DOCS-CHECKER ONLY.

This packet is the inert contract scaffold for future coordinate-native runtime
profile support. It is documentation and checker scaffolding only. It does not
modify firmware source, does not change active firmware behavior, and does not
implement runtime interpretation.

## Contract Scope

The contract model names these durable concepts explicitly:

- physical input IDs
- direction resolver
- direction keys `1..9`
- neutral key `5`
- exact raw coordinates
- 9-way modifier tables
- sublayer and routing rules
- priorities
- digital side effects
- version and capability metadata

## Deterministic Selection Semantics

This packet now documents the future dry-run contract in a machine-readable
shape so a later offline resolver can be implemented without inventing
selection behavior.

### Future Input State

The future evaluator input object is named `input_state`. It is a bounded,
explicit object that carries:

- `activations`: the current per-input activation records;
- `resolved_direction_key`: the normalized direction key value selected for
  evaluation;
- `direction_resolver`: the source that produced the resolved direction key;
- `active_role_ids`: the active role ids that participate in routing;
- `active_modifier_ids`: the active modifier ids that participate in routing.

The `activations` entries must identify each input with `input_id`, connect it
to a declared `role_id`, and record whether it is pressed. This avoids hidden
state and keeps the future dry-run input deterministic.

### Role And Modifier Activation

Activation is explicit and per-input. A physical input becomes active only when
its activation record says so. The contract uses an explicit activation-record
shape rather than an implicit boolean shorthand so that multiple active roles
or modifiers remain visible in the input object.

### Direction Key Source

The resolved direction key must come from `resolved_direction_key`. The valid
domain is `1..9`, and `5` is the neutral key. Neutral `5` is not a missing
value or special fallback; it is an ordinary, fully resolvable direction key
that maps to the neutral coordinate.

The canonical raw-coordinate source is `exact_raw_coordinates`. Each
`modifier_tables.direction_points` entry must match the corresponding canonical
coordinate for the same `direction_key`.

### Routing Order And Priority

Routing is deterministic:

1. normalize the `input_state` into activation records;
2. read `resolved_direction_key`;
3. rank routing rules by ascending priority;
4. break equal-priority ambiguity by rejecting the profile as invalid;
5. select the first rule whose referenced modifier table exists;
6. resolve the raw coordinate for the selected table and direction key;
7. merge digital side effects deterministically;
8. emit trace and explanation metadata.

Equal priorities are not a runtime tie-break problem in this contract. They are
invalid profile data and must be rejected. The free-text `condition` field on a
routing rule is explanatory only and does not participate in selection.

### Sublayer Selection

Each routing rule names one sublayer. A sublayer selection must resolve to one
winning rule. The contract does not allow multi-winner sublayer resolution.
When a matching sublayer is absent or a table reference cannot be resolved, the
future dry-run must fail closed rather than guess a fallback.

### Missing Table Behavior

If a routing rule references a table that does not exist, the future dry-run
must return an explicit missing-table result. It must not synthesize a raw
coordinate or silently reuse another table. The missing-table result is a
documented output state, not an implementation accident.

### Digital Side-Effect Merge

Digital side effects are collected after a table has been selected. They are
merged deterministically by routing order and side-effect priority. Duplicate
`effect_id` values are deduplicated, but conflicting duplicates are rejected.
The merge policy must be explicit so the same profile cannot produce different
side-effect sets across implementations.

### Exact Output Shape

The future dry-run output is a `selection_result` object with these required
fields:

- `selection_status`
- `resolved_direction_key`
- `selected_rule_id`
- `selected_table_id`
- `selected_coordinate`
- `selected_side_effect_ids`
- `trace`
- `explanation`

`trace` must record the decision path, the selected rule and table ids, and any
missing-table reason. `explanation` must summarize the winning selection and
any fallback or rejection outcome.

### Future Dry-Run Examples

The contract fixture and positive example fixtures carry annotated
`future_dry_run_examples`. These are not evaluator implementations. They are
machine-readable examples that show the future input shape, the expected
selection result, and the trace markers a later offline resolver should emit.

An offline bridge converter may also transform a validated strict subset of
this profile into the inert source-owned layout-spec packet used by the
generator lane. That bridge is docs/tools only and does not change active
firmware behavior.

The source-owned layout-spec bridge lives in
`tools/convert_coordinate_native_profile_to_source_owned_spec.py`, and the
repo checker exercises it with `--check-layout-spec-bridge`.

## Accepted Evidence

- The source-owned Y2 layout `HARDWARE_PASS` remains the current known-good
  firmware path.
- Active `RuntimeConfigView` selection remains unchanged.
- `GetActiveRuntimeConfigState()` still publishes the source-owned current
  baseline view.
- RuntimeConfigView replacement is not used.
- The generated active wrapper is not used.
- `candidate.view` is not active.
- RAM-backed active table publication is not used.
- Prior active-publication `HARDWARE_FAIL` evidence remains accepted.
- Nunchuk remains `NOT_TESTED`.
- The low-level root cause remains unproven.

## Contract Target

The future target is a coordinate-native runtime profile contract with the
primitive:

```text
active role/modifier state + resolved direction key 1..9 -> exact raw coordinate
```

The contract requires:

- Direction keys `1..9`.
- Neutral direction `5`.
- Full 9-way asymmetry.
- Exact raw coordinates as outputs.
- Explicit routing, sublayers, and priorities.

The canonical profile remains neutral, app-owned, and firmware-independent.
Senscope owns game semantics, datasets, and solver authority. Glyph firmware
should remain a deterministic coordinate-output backend and should not own game
semantics.

## Deterministic Selection Semantics

This section is design-only. It defines the future offline dry-run contract so
the checker and fixtures can describe the same deterministic behavior without
implementing an evaluator or changing firmware runtime behavior.

The future evaluator input is an `input_state` object with explicit activation
records. The contract treats each active physical input as one activation
record, with inactive inputs omitted. The minimal input state shape is:

```json
{
  "state_id": "future_dry_run_case",
  "activations": [
    {
      "input_id": "phys_input_a",
      "role_id": "primary",
      "pressed": true
    }
  ],
  "inactive_inputs": [],
  "resolved_direction_key": 5
}
```

Selection uses the resolver output field `resolved_direction_key` as the sole
direction key source. Only keys `1..9` are valid, and key `5` is the neutral
key. Routing always proceeds in this order:

1. Normalize the `input_state` activation records.
2. Read `resolved_direction_key` from the direction resolver output.
3. Rank routing rules by priority, then by sublayer name, then by stable table
   or rule identifier.
4. Select the first rule whose referenced modifier table exists.
5. Resolve the exact raw coordinate for the selected table and direction key.
6. Merge digital side effects deterministically.
7. Emit trace and explanation metadata with the result.

Tie behavior is deterministic and documented. If priorities match, the checker
assumes a stable total order: sublayer name first, then table or rule identifier
next, then document order as the last fallback. Identical same-priority entries
remain a design error for future validator work; this contract does not allow an
ambiguous evaluator result.

Sublayer selection is explicit: the highest-priority routing rule for the active
sublayer wins, and missing sublayers are skipped rather than synthesized.
Missing-table behavior is also explicit: if a routing rule references a table
that is absent, or if the selected table cannot provide the resolved direction
key, the future dry-run result must report `missing_table` and must not invent a
coordinate.

Digital side effects merge in a stable order. The selected table contributes
first, then the selected routing rule, then any additional design-only effect
references. Duplicate effect IDs are deduplicated; if two effects still conflict
after deduplication, the higher-priority effect wins and the suppressed effect
IDs are recorded in trace metadata.

The exact future output shape is a `selection_result` object with these fields:

```json
{
  "selection_status": "selected",
  "resolved_direction_key": 5,
  "selected_rule_id": "primary_rule",
  "selected_table_id": "primary_9way",
  "selected_coordinate": { "x": 128, "y": 128 },
  "selected_side_effect_ids": ["digital_side_effect_primary"],
  "trace": [
    {
      "step": "resolve_direction_key",
      "decision": "use resolver output",
      "reason": "resolved_direction_key is the only direction source",
      "inputs": ["resolved_direction_key=5"]
    }
  ],
  "explanation": "Primary route selected deterministically and neutral key 5 maps to the center coordinate."
}
```

For future offline dry-runs, fixtures also carry at least one positive
`future_dry_run_examples` annotation with `case_id`, `input_state`,
`expected_result`, and `trace_markers` fields. Those annotations are evidence
for deterministic selection semantics only; they are not evaluator code.

## Required Properties

- Active runtime config replacement is not allowed.
- RuntimeConfigView replacement is not allowed.
- Generated active wrapper publication is not allowed.
- `candidate.view` active publication is not allowed.
- RAM-backed active table publication is not allowed.
- Runtime-loaded config is not implemented.
- Runtime-config storage is not implemented.
- WebSerial/device write path is not implemented.
- Backend/config.pb write path is not implemented.
- Firmware flashing automation is not implemented.
- Nunchuk validation is not claimed.
- Hardware test is not required before merge for this docs/checker-only
  scaffold because active behavior is unchanged.

## Future Implementation Gate

This contract scaffold is not approval to implement runtime interpretation,
runtime-loaded config, storage, device write, or active publication changes.
Future implementation must be hardware-gated if active source selection
behavior changes.

Any later runtime-active implementation must preserve the current source-owned
active path unless a separate source-backed and hardware-validated model proves
otherwise. It must still reject runtime-loaded config, persistent storage,
WebSerial/device write, backend/config.pb write paths, firmware flashing
automation, `candidate.view` active publication, and RAM-backed active table
publication unless later evidence changes those boundaries.

## Non-Claims

- This packet does not change active firmware behavior.
- This packet does not prove the low-level failure mechanism.
- This packet does not implement runtime interpretation.
- This packet does not implement runtime-loaded config, persistent storage,
  WebSerial/device write, backend/config.pb write, or flashing automation.
- This packet does not approve active `RuntimeConfigView` replacement.
- This packet does not approve `candidate.view` active publication.
- This packet does not approve RAM-backed active table publication.
- This packet does not claim nunchuk validation.
- This packet does not define or change Senscope game semantics.
