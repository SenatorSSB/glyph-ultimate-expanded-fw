# G5 - Non-Runtime Capability Model Schema Draft

Status: complete (non-runtime schema/design draft)  
Date: 2026-05-23  
Branch: `docs/glyph-capability-model-g5`  
Scope: documentation/design only; not runtime implementation

## 1. Title and Status

This document is the G5 non-runtime capability model schema draft for Glyph/HayBox-side backend realization analysis.

It proposes conceptual schema shapes for a future source-backed backend capability model. These shapes are documentation artifacts only. They are not TypeScript definitions, JSON Schema, runtime adapter code, firmware changes, evaluator tests, or public API commitments.

No firmware/source/runtime implementation was performed for G5.

## 2. Scope

Reviewed:
- `AGENTS.md`
- `docs/project/ACTIVE_AGENT_QUEUE.md`
- `docs/project/AGENT_OPERATING_CONTRACT.md`
- `docs/project/AGENT_STOP_CONDITIONS.md`
- `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`
- `docs/project/SENSCOPE_INTEGRATION_TARGET.md`
- `docs/project/GLYPH_CAPABILITY_MODEL_TARGET.md`
- `docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md`
- `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
- `docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`
- `docs/project/G4_G1_G3_REVIEW_AND_NEXT_QUEUE.md`

Supporting source/reference files were inspected only where needed to keep schema fields and source-reference examples grounded:
- `include/core/state.hpp`
- `src/core/ControllerMode.cpp`
- `src/core/InputMode.cpp`
- `src/modes/Ultimate.cpp`
- `src/modes/CustomControllerMode.cpp`
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`
- `HAL/pico/src/core/Persistence.cpp`
- `HAL/pico/src/comms/GamecubeBackend.cpp`
- `HAL/pico/src/comms/NintendoSwitchBackend.cpp`
- `HAL/pico/src/comms/DInputBackend.cpp`
- `HAL/pico/src/comms/XInputBackend.cpp`
- `docs/sources/source-manifest.json`

This draft proposes:
- conceptual enums for claim status, evidence, scope, and evaluator readiness;
- source-reference shapes and requirements;
- backend identity, input, output, SOCD, remap, chord, modifier, mode, transport, matrix, and diagnostic schema surfaces;
- a conservative illustrative capability object;
- validation rules for future implementation;
- how G6 could later use mock fixtures if explicitly approved.

This draft intentionally does not decide:
- final TypeScript package location;
- final JSON Schema shape;
- final public API names;
- runtime adapter behavior;
- deterministic evaluator implementation;
- firmware behavior changes;
- host-side export format;
- push-to-device workflow;
- Senscope neutral profile schema;
- Super Smash Bros. Ultimate gameplay semantics.

No firmware/source/runtime implementation was performed.

## 3. Design Goals

- Source-backed capability representation: every non-unknown capability claim should point to source evidence.
- Conservative unknown handling: absence of proof remains `UNKNOWN` or `UNSUPPORTED_BY_CURRENT_SOURCE`, not inferred support.
- Mode-specific vs generic scope: mode-specific evidence from `Ultimate` or `CustomControllerMode` must not automatically become generic backend support.
- Neutral profile integration readiness: the model should be able to compare against Senscope-owned neutral profile concepts without changing that profile schema.
- Diagnostic-friendly structure: unsupported, unknown, inferred, and mode-scoped cases should produce clear diagnostics.
- Future evaluator compatibility: the model should support Level 0/1 static checks now and leave room for later deterministic Level 2 checks.
- No game-semantic coupling: the model must not contain action labels, no-smash/no-strong-input predicates, gameplay thresholds, semantic maps, or game-domain equivalence logic.

## 4. Non-Goals

- Runtime adapter implementation.
- Firmware changes.
- Vendor export generation.
- Push-to-device workflow.
- Final TypeScript package location.
- Final public API.
- Final Senscope neutral profile schema.
- Gameplay semantic predicates.
- Macros, turbo, or timing automation.
- Runtime source files or evaluator tests in this batch.

## 5. Source Basis

G1 provides the repository inventory and architecture map. It identifies the firmware core, mode logic, HAL/backend layers, config overlays, staged reference material, and source-authority gaps.

G2 provides the primary capability extraction baseline. It classifies input, output, SOCD, remap, mode, modifier, transport, manual-entry, export, and push surfaces as `SOURCE_BACKED`, `INFERRED`, `UNKNOWN`, or `UNSUPPORTED_BY_CURRENT_SOURCE`.

G3 provides the integration boundary. It keeps Senscope neutral profile concepts external/app-owned, defines conservative realization statuses, separates evaluation levels, and lists diagnostic categories.

G4 confirms G1-G3 are consistent and recommends G5 as a docs/design-only capability schema draft before any G6 code/test scaffold.

Active source files are used here only as supporting evidence for schema examples. Copied references under `docs/sources/raw` are not treated as active runtime authority unless separately proven.

## 6. Classification Enums

Conceptual only:

```text
type CapabilityClaimStatus =
  | "SOURCE_BACKED"
  | "INFERRED"
  | "UNKNOWN"
  | "UNSUPPORTED_BY_CURRENT_SOURCE"
  | "OUT_OF_SCOPE";
```

Meanings:
- `SOURCE_BACKED`: directly supported by inspected repo source/docs/tests/fixtures or explicit user/domain statement.
- `INFERRED`: reasonable interpretation from structure, but not explicit enough to be implementation truth.
- `UNKNOWN`: not proven by current source or not inspected deeply enough.
- `UNSUPPORTED_BY_CURRENT_SOURCE`: current inspected source does not show support for the capability as stated.
- `OUT_OF_SCOPE`: belongs outside backend capability modeling, usually game semantics or unapproved export/push workflow.

```text
type CapabilityScope =
  | "GENERIC_BACKEND"
  | "MODE_SPECIFIC"
  | "CONFIG_SPECIFIC"
  | "BOARD_SPECIFIC"
  | "TRANSPORT_SPECIFIC"
  | "REFERENCE_ONLY"
  | "UNKNOWN";
```

```text
type EvidenceStrength =
  | "DIRECT_SOURCE"
  | "DOC_REFERENCE"
  | "COPIED_REFERENCE"
  | "INFERRED_FROM_STRUCTURE"
  | "USER_CONFIRMED"
  | "MISSING";
```

```text
type EvaluationReadiness =
  | "LEVEL_0_EVIDENCE_ONLY"
  | "LEVEL_1_STATIC_REPRESENTABILITY"
  | "LEVEL_2_DETERMINISTIC_REALIZATION"
  | "LEVEL_3_EXPORT_OR_MANUAL_ENTRY"
  | "LEVEL_4_PUSH_TO_DEVICE";
```

Near-term recommended readiness remains Level 0/1. Level 2+ requires explicit approval and stronger source-backed behavior modeling. Level 3/4 remain unsupported unless separately approved and source-backed.

## 7. Source Reference Schema

Conceptual shapes:

```text
type SourceRef = {
  path: string;
  symbol?: string;
  line_hint?: string;
  evidence_strength: EvidenceStrength;
  scope?: CapabilityScope;
  note?: string;
};

type SourceRefSet = {
  refs: SourceRef[];
  summary?: string;
  gaps?: string[];
};

type SourceBackedClaim<T> = {
  value: T;
  status: CapabilityClaimStatus;
  scope: CapabilityScope;
  evidence_strength: EvidenceStrength;
  source_refs: SourceRef[];
  notes?: string[];
  unknowns?: string[];
};
```

Requirements:
- Every non-`UNKNOWN` capability claim must have at least one `source_refs` entry.
- `SOURCE_BACKED` claims require `DIRECT_SOURCE`, `DOC_REFERENCE`, or `USER_CONFIRMED` evidence.
- `INFERRED` claims require source references plus `INFERRED_FROM_STRUCTURE` evidence.
- `UNSUPPORTED_BY_CURRENT_SOURCE` claims require source references showing the inspected basis for non-support or absence of a primitive.
- Copied references such as `docs/sources/raw/ESAM1.cpp`, `docs/sources/raw/ESAM1.hpp`, and `docs/sources/raw/GlyphUserProfiles.json` must be marked `REFERENCE_ONLY` unless separately proven as active runtime authority.
- Source refs should include `path` and, where useful, `symbol`, function, type, or line hint.
- Missing source refs should produce `MISSING_SOURCE_REF` diagnostics instead of silent confidence.

## 8. Backend Identity Schema

Conceptual shape:

```text
type BackendIdentity = {
  backend_id: string;
  label: string;
  firmware_family?: string;
  branch_or_revision?: string;
  mode_scope: CapabilityScope;
  board_scope?: CapabilityScope;
  transport_scope?: CapabilityScope;
  source_refs: SourceRef[];
  notes?: string[];
};
```

Guidance:
- `backend_id` should be stable within a draft fixture but is not a public API commitment.
- `mode_scope` must distinguish generic backend facts from `Ultimate`, `CustomControllerMode`, or reference-only evidence.
- Board-specific evidence from Glyph overlays should not become generic firmware-family evidence without source-backed bridging.
- Transport-specific evidence should stay attached to its backend report path.

Example source refs:
- `config/glyph/env.ini` for Glyph env definitions as identified by G1.
- `src/core/mode_selection.cpp` for mode selection and active mode instances as identified by G2.
- `HAL/pico/src/comms/backend_init.cpp` for protocol backend discovery and initialization as identified by G2.

## 9. Input Surface Schema

Conceptual shape:

```text
type BackendInputSurface = {
  physical_buttons: SourceBackedClaim<Array<{
    button_id: string;
    family?: "lf" | "rf" | "lt" | "rt" | "mb" | "UNKNOWN";
  }>>;
  logical_buttons?: SourceBackedClaim<Array<{
    button_id: string;
    scope: CapabilityScope;
  }>>;
  directional_inputs?: SourceBackedClaim<Array<{
    input_id: string;
    source_button_refs?: string[];
    scope: CapabilityScope;
  }>>;
  modifier_like_inputs?: SourceBackedClaim<Array<{
    input_id: string;
    role_source: "MODE_DEFINED" | "CONFIG_DEFINED" | "UNKNOWN";
    scope: CapabilityScope;
  }>>;
  nunchuk_inputs?: SourceBackedClaim<{
    supports_connected_flag: boolean | "UNKNOWN";
    supports_c: boolean | "UNKNOWN";
    supports_z: boolean | "UNKNOWN";
    supports_x_axis: boolean | "UNKNOWN";
    supports_y_axis: boolean | "UNKNOWN";
  }>;
  input_scan_pipeline?: {
    notes: string[];
    source_refs: SourceRef[];
  };
  source_refs: SourceRef[];
  unknowns: string[];
};
```

Source-backed examples:
- `InputState` exposes named physical fields `lf1..lf16`, `rf1..rf16`, `lt1..lt8`, `rt1..rt8`, and `mb1..mb12`. Source: `include/core/state.hpp`.
- `InputState` exposes `nunchuk_connected`, `nunchuk_c`, `nunchuk_z`, `nunchuk_x`, and `nunchuk_y`. Source: `include/core/state.hpp`.
- G2 classifies modifier-like physical buttons as mode-defined rather than globally typed. Sources: `src/modes/Ultimate.cpp`, `src/modes/CustomControllerMode.cpp`.

Button names should remain source-backed. Do not invent semantic roles beyond source, such as game action meanings.

## 10. Output Surface Schema

Conceptual shape:

```text
type BackendOutputSurface = {
  digital_outputs: SourceBackedClaim<Array<{
    output_id: string;
    source_field?: string;
  }>>;
  analog_outputs: SourceBackedClaim<Array<{
    output_id: string;
    axes: string[];
    byte_range?: [number, number];
    default_values?: Record<string, number>;
  }>>;
  left_stick_output: SourceBackedClaim<{
    x_field: string;
    y_field: string;
    byte_range?: [number, number];
    default_values?: { x: number; y: number };
    exact_arbitrary_coordinate_support: CapabilityClaimStatus;
  }>;
  right_stick_output: SourceBackedClaim<{
    x_field: string;
    y_field: string;
    byte_range?: [number, number];
    default_values?: { x: number; y: number };
  }>;
  trigger_outputs: SourceBackedClaim<{
    left_analog_field: string;
    right_analog_field: string;
    left_digital_field: string;
    right_digital_field: string;
    byte_range?: [number, number];
  }>;
  transport_specific_packing_caveats: Array<{
    transport_id: string;
    caveat: string;
    source_refs: SourceRef[];
  }>;
  source_refs: SourceRef[];
  unknowns: string[];
};
```

Source-backed examples:
- `OutputState` contains digital output fields and analog byte fields `leftStickX`, `leftStickY`, `rightStickX`, `rightStickY`, `triggerLAnalog`, and `triggerRAnalog`; analog initializer defaults to `{128,128,128,128,0,0}`. Source: `include/core/state.hpp`.
- Base direction synthesis sets stick outputs to neutral first, then min/max based on direction booleans. Source: `src/core/ControllerMode.cpp::UpdateDirections`.
- GameCube report packing consumes left/right stick and trigger fields directly. Source: `HAL/pico/src/comms/GamecubeBackend.cpp`.
- DInput, XInput, and Nintendo Switch paths apply backend-specific scaling or inversion. Sources: `HAL/pico/src/comms/DInputBackend.cpp`, `HAL/pico/src/comms/XInputBackend.cpp`, `HAL/pico/src/comms/NintendoSwitchBackend.cpp`.

Do not treat byte fields alone as proof of generic exact arbitrary-coordinate realization.

## 11. Direction and SOCD Surface Schema

Conceptual shape:

```text
type DirectionResolutionSurface = {
  direction_fields: SourceBackedClaim<{
    horizontal_field?: string;
    vertical_field?: string;
    diagonal_field?: string;
    left_stick_direction_fields?: string[];
    right_stick_direction_fields?: string[];
  }>;
  socd_pairs: SourceBackedClaim<Array<{
    pair_id?: string;
    dir1?: string;
    dir2?: string;
    socd_type: string;
    scope: CapabilityScope;
  }>>;
  socd_algorithm_types: SourceBackedClaim<string[]>;
  pipeline_order: SourceBackedClaim<string[]>;
  state_memory_fields?: SourceBackedClaim<Array<{
    field: string;
    algorithm_scope: string;
  }>>;
  source_refs: SourceRef[];
  unknowns: string[];
};
```

Source-backed examples:
- SOCD handling dispatches `SOCD_NEUTRAL`, `SOCD_2IP`, `SOCD_2IP_NO_REAC`, `SOCD_DIR1_PRIORITY`, and `SOCD_DIR2_PRIORITY`. Sources: `src/core/InputMode.cpp`, `src/core/socd.cpp`, `include/core/socd.hpp`.
- The controller output pipeline is remap -> SOCD -> digital mapping -> analog mapping. Source: `src/core/ControllerMode.cpp::UpdateOutputs`.
- Some SOCD variants use per-pair memory state. Source: `include/core/InputMode.hpp`, `include/core/socd.hpp`, `src/core/socd.cpp` as identified by G2.

Do not attach gameplay meaning to SOCD behavior. The model may record algorithm and ordering only.

## 12. Remap and Chord Surface Schema

Conceptual shapes:

```text
type RemapSurface = {
  static_remap_rules: SourceBackedClaim<{
    config_field?: string;
    supports_many_to_one: boolean | "UNKNOWN";
    pipeline_position?: string;
  }>;
  anti_macro_duplicate_physical_remap_guard: SourceBackedClaim<boolean | "UNKNOWN">;
  source_refs: SourceRef[];
  unknowns: string[];
};

type ChordSurface = {
  chord_masks: SourceBackedClaim<Array<{
    source_field?: string;
    max_entries?: number | "UNKNOWN";
    scope: CapabilityScope;
  }>>;
  combo_output_rules: SourceBackedClaim<Array<{
    input_mask_field?: string;
    output_field?: string;
    scope: CapabilityScope;
  }>>;
  suppression_or_passthrough_policy: SourceBackedClaim<{
    suppresses_involved_inputs: boolean | "UNKNOWN";
    pass_through_policy?: string;
  }>;
  source_refs: SourceRef[];
  unknowns: string[];
};
```

Source-backed examples:
- Static remapping uses `GameModeConfig.button_remapping` in `InputMode::HandleRemap`. Source: `src/core/InputMode.cpp`.
- Duplicate physical remaps are ignored to prevent macro behavior. Source: `src/core/InputMode.cpp::HandleRemap`.
- `CustomControllerMode` supports button combo mappings that emit a single digital output and suppress normal behavior for involved inputs via `_buttons_to_ignore` / `_filtered_buttons`. Source: `src/modes/CustomControllerMode.cpp`.

Only record suppression/pass-through policy where source-backed. Do not infer macro capability from chord support.

## 13. Modifier and Analog Transform Surface Schema

Conceptual shapes:

```text
type ModifierSurface = {
  analog_modifier_concepts: SourceBackedClaim<Array<{
    modifier_id?: string;
    activation_source?: string;
    scope: CapabilityScope;
  }>>;
  combination_modes: SourceBackedClaim<string[]>;
  axis_selection: SourceBackedClaim<Array<{
    axis_id: string;
    source_field?: string;
  }>>;
  override_or_compound_behavior: SourceBackedClaim<{
    override_supported: boolean | "UNKNOWN";
    compound_supported: boolean | "UNKNOWN";
    details?: string[];
  }>;
  exact_raw_target_support_status: CapabilityClaimStatus;
  full_9way_table_status: CapabilityClaimStatus;
  neutral_direction_5_status: CapabilityClaimStatus;
  noncenter_neutral_status: CapabilityClaimStatus;
  flipper_transform_status: CapabilityClaimStatus;
  source_refs: SourceRef[];
  unknowns: string[];
};

type AnalogTransformSurface = {
  transform_id: string;
  label: string;
  status: CapabilityClaimStatus;
  scope: CapabilityScope;
  inputs?: string[];
  outputs?: string[];
  source_refs: SourceRef[];
  limitations: string[];
  unknowns: string[];
};
```

Source-backed examples:
- `CustomControllerMode` supports analog modifiers with `COMBINATION_MODE_OVERRIDE` and `COMBINATION_MODE_COMPOUND` behavior paths. Source: `src/modes/CustomControllerMode.cpp`.
- `CustomControllerMode` supports configured stick direction mappings and configurable stick range. Source: `src/modes/CustomControllerMode.cpp`.
- `Ultimate` applies hardcoded modifier/context coordinate offsets. Source: `src/modes/Ultimate.cpp`.

Conservative status requirements:
- Exact raw target support is currently `INFERRED` at generic level because byte-level outputs exist, but generic arbitrary-coordinate realization is not proven by G2.
- Full 9-way directional modifier table support is `UNSUPPORTED_BY_CURRENT_SOURCE` for generic support per G2/G3.
- First-class neutral direction `5` is `UNSUPPORTED_BY_CURRENT_SOURCE` for backend-level first-class representation per G2/G3.
- Non-center neutral support is `UNKNOWN` per G2/G3.
- Flipper transform support is `UNKNOWN` unless future active source proves a named primitive.

Current source does not prove generic full 9-way table realization. Mode-specific hardcoded or configurable analog behavior must remain mode-scoped.

## 14. Mode-Specific Capability Schema

Conceptual shape:

```text
type ModeCapabilityProfile = {
  mode_id: string;
  mode_label: string;
  mode_kind: "HARDCODED" | "CONFIGURABLE" | "REFERENCE_ONLY" | "UNKNOWN";
  capabilities: CapabilityMatrixEntry[];
  limitations: string[];
  source_refs: SourceRef[];
  unknowns: string[];
};
```

Guidance:
- `Ultimate` should be modeled as hardcoded mode-specific evidence. Its D-pad layer, modifier/context coordinate offsets, trigger values, right-stick behavior, and nunchuk override are source-backed for that mode, not generic backend capabilities. Source: `src/modes/Ultimate.cpp`.
- `CustomControllerMode` should be modeled as configurable mode-specific evidence. Its combo mappings, digital mappings, stick direction mappings, analog modifiers, analog trigger mappings, and nunchuk behavior are source-backed for that mode/config path, not proof of complete Senscope-style target coverage. Source: `src/modes/CustomControllerMode.cpp`.
- `ESAM1` should be modeled as reference-only evidence unless otherwise proven. Source: `docs/sources/source-manifest.json`, `docs/sources/raw/ESAM1.cpp`, `docs/sources/raw/ESAM1.hpp`.

Mode-specific evidence may inform future design but cannot satisfy a generic capability requirement without an explicit, source-backed bridging rule.

## 15. Transport/Backend Surface Schema

Conceptual shape:

```text
type TransportCapabilityProfile = {
  transport_id: string;
  label: string;
  output_report_fields: SourceBackedClaim<Array<{
    report_field: string;
    output_state_field: string;
    conversion?: string;
  }>>;
  scaling_or_packing_caveats: Array<{
    caveat: string;
    source_refs: SourceRef[];
  }>;
  supported_outputs: SourceBackedClaim<string[]>;
  source_refs: SourceRef[];
  unknowns: string[];
};
```

Guidance:
- GameCube, Switch, DInput, and XInput backend report details should stay transport-specific and source-refed.
- GameCube consumes `OutputState` stick and trigger fields in report fields. Source: `HAL/pico/src/comms/GamecubeBackend.cpp`.
- Nintendo Switch applies scaling and inversion to stick bytes. Source: `HAL/pico/src/comms/NintendoSwitchBackend.cpp`.
- DInput and XInput apply their own scaling/packing behavior. Sources: `HAL/pico/src/comms/DInputBackend.cpp`, `HAL/pico/src/comms/XInputBackend.cpp`.
- These backend details are non-final for integration until a future evaluator target specifies which transport is being modeled.

## 16. Realization-Relevant Capability Matrix Schema

Conceptual shape:

```text
type CapabilityMatrixEntry = {
  capability_id: string;
  label: string;
  status: CapabilityClaimStatus;
  scope: CapabilityScope;
  evidence_strength: EvidenceStrength;
  evaluation_readiness: EvaluationReadiness;
  source_refs: SourceRef[];
  limitations: string[];
  diagnostics: string[];
  notes?: string[];
};
```

Required capability IDs for future fixtures or docs:

| Capability ID | Conservative G5 status | Scope | Readiness | Notes |
|---|---|---|---|---|
| `exact_raw_left_stick_coordinate_output` | `INFERRED` | `GENERIC_BACKEND` | `LEVEL_0_EVIDENCE_ONLY` | Byte fields exist; arbitrary generic exact realization is not proven. |
| `full_9way_directional_modifier_table` | `UNSUPPORTED_BY_CURRENT_SOURCE` | `GENERIC_BACKEND` | `LEVEL_1_STATIC_REPRESENTABILITY` | No proven first-class generic 9-way table model. |
| `first_class_neutral_direction_5` | `UNSUPPORTED_BY_CURRENT_SOURCE` | `GENERIC_BACKEND` | `LEVEL_1_STATIC_REPRESENTABILITY` | Center default exists; first-class direction `5` field is unproven. |
| `noncenter_neutral_output` | `UNKNOWN` | `GENERIC_BACKEND` | `LEVEL_0_EVIDENCE_ONLY` | Active sources center neutral by default; reference evidence is not runtime authority. |
| `flipper_transform` | `UNKNOWN` | `GENERIC_BACKEND` | `LEVEL_0_EVIDENCE_ONLY` | No explicit named active-source primitive identified by G2. |
| `pre_socd_force_up_b_override` | `UNKNOWN` | `GENERIC_BACKEND` | `LEVEL_0_EVIDENCE_ONLY` | Pipeline source does not prove this primitive. |
| `dynamic_button_layers` | `SOURCE_BACKED` | `MODE_SPECIFIC` | `LEVEL_1_STATIC_REPRESENTABILITY` | Ultimate layer and Custom combo suppression are mode/config specific. |
| `button_chord_rules` | `SOURCE_BACKED` | `MODE_SPECIFIC` | `LEVEL_1_STATIC_REPRESENTABILITY` | Custom combo mappings and mode activation masks are source-backed. |
| `socd_handling` | `SOURCE_BACKED` | `CONFIG_SPECIFIC` | `LEVEL_1_STATIC_REPRESENTABILITY` | Config-driven SOCD pairs and algorithms are source-backed. |
| `static_remapping` | `SOURCE_BACKED` | `CONFIG_SPECIFIC` | `LEVEL_1_STATIC_REPRESENTABILITY` | Remap and anti-macro duplicate guard are source-backed. |
| `analog_modifiers` | `SOURCE_BACKED` | `MODE_SPECIFIC` | `LEVEL_1_STATIC_REPRESENTABILITY` | Source-backed in CustomControllerMode; full target coverage is not proven. |
| `right_stick_output` | `SOURCE_BACKED` | `GENERIC_BACKEND` | `LEVEL_1_STATIC_REPRESENTABILITY` | Output fields exist and are consumed; advanced behavior is mode-specific. |
| `analog_triggers` | `SOURCE_BACKED` | `GENERIC_BACKEND` | `LEVEL_1_STATIC_REPRESENTABILITY` | Output fields exist and are consumed by multiple backends. |
| `manual_entry_support` | `INFERRED` | `UNKNOWN` | `LEVEL_3_EXPORT_OR_MANUAL_ENTRY` | Device/config paths exist; end-user workflow is not proven complete. |
| `export_support` | `UNSUPPORTED_BY_CURRENT_SOURCE` | `UNKNOWN` | `LEVEL_3_EXPORT_OR_MANUAL_ENTRY` | No stable source-backed vendor export artifact workflow confirmed. |
| `push_to_device_support` | `UNSUPPORTED_BY_CURRENT_SOURCE` | `UNKNOWN` | `LEVEL_4_PUSH_TO_DEVICE` | Device-side handlers exist, but host-side push workflow is not approved/source-backed. |

## 17. Diagnostic Schema

Conceptual shape:

```text
type CapabilityDiagnostic = {
  code: string;
  severity: "info" | "warning" | "error";
  message: string;
  related_capability_ids: string[];
  source_refs: SourceRef[];
  recommended_action?: string;
};
```

Conceptual diagnostic codes from G3:
- `MISSING_SOURCE_REF`: required capability claim lacks a source reference.
- `MODE_SPECIFIC_ONLY`: evidence exists only for a specific mode or config path.
- `GENERIC_CAPABILITY_UNKNOWN`: generic backend support is not proven.
- `EXACT_9WAY_TABLE_UNSUPPORTED`: no source-backed generic first-class 9-way directional table exists.
- `NEUTRAL_5_UNPROVEN`: backend support for first-class direction `5` is not proven.
- `NONCENTER_NEUTRAL_UNKNOWN`: non-center neutral target support is unknown.
- `FLIPPER_UNSUPPORTED_OR_UNKNOWN`: flipper transform support is absent or unproven.
- `PRE_SOCD_OVERRIDE_UNKNOWN`: requested pre-SOCD override primitive is unproven.
- `DYNAMIC_LAYER_GENERIC_UNKNOWN`: dynamic role/layer reassignment is not proven generically.
- `EXPORT_NOT_SUPPORTED`: export artifact generation is unsupported by current source.
- `PUSH_NOT_SUPPORTED`: host-side push workflow is unsupported by current source/approval.
- `SAME_EFFECTIVE_REQUIRES_DATASET`: same-effective fallback cannot be evaluated without Senscope-supplied equivalence data.

Severity guidance:
- `info`: source-backed caveat or expected limitation.
- `warning`: unknown, inferred, mode-specific-only, or missing evidence that blocks confidence.
- `error`: requested output path is explicitly unsupported by current source or outside approved scope.

## 18. Example Draft Object

Illustrative only. This is not final API, not JSON Schema, and not a runtime fixture.

```json
{
  "identity": {
    "backend_id": "example_glyph_capability_model_draft",
    "label": "Example Glyph capability model draft",
    "firmware_family": "glyph-example",
    "branch_or_revision": "docs/glyph-capability-model-g5",
    "mode_scope": "UNKNOWN",
    "board_scope": "BOARD_SPECIFIC",
    "transport_scope": "UNKNOWN",
    "source_refs": [
      {
        "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md",
        "symbol": "Senscope-relevant capability matrix",
        "evidence_strength": "DOC_REFERENCE",
        "scope": "REFERENCE_ONLY",
        "note": "Primary source basis for conservative capability statuses."
      }
    ],
    "notes": [
      "Example IDs are intentionally non-final.",
      "This object does not claim runtime adapter support."
    ]
  },
  "input_surface": {
    "physical_buttons": {
      "value": [
        { "button_id": "lf1", "family": "lf" },
        { "button_id": "rf1", "family": "rf" },
        { "button_id": "lt1", "family": "lt" },
        { "button_id": "rt1", "family": "rt" },
        { "button_id": "mb1", "family": "mb" }
      ],
      "status": "SOURCE_BACKED",
      "scope": "GENERIC_BACKEND",
      "evidence_strength": "DIRECT_SOURCE",
      "source_refs": [
        {
          "path": "include/core/state.hpp",
          "symbol": "InputState",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "GENERIC_BACKEND"
        }
      ]
    },
    "unknowns": [
      "Modifier-like roles are mode/config defined, not globally typed."
    ]
  },
  "capability_matrix": [
    {
      "capability_id": "exact_raw_left_stick_coordinate_output",
      "label": "Exact raw left-stick coordinate output",
      "status": "INFERRED",
      "scope": "GENERIC_BACKEND",
      "evidence_strength": "INFERRED_FROM_STRUCTURE",
      "evaluation_readiness": "LEVEL_0_EVIDENCE_ONLY",
      "source_refs": [
        {
          "path": "include/core/state.hpp",
          "symbol": "OutputState.leftStickX / OutputState.leftStickY",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "GENERIC_BACKEND"
        },
        {
          "path": "src/core/ControllerMode.cpp",
          "symbol": "ControllerMode::UpdateDirections",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "GENERIC_BACKEND"
        }
      ],
      "limitations": [
        "Byte-level fields exist, but generic arbitrary-coordinate realization is not proven."
      ],
      "diagnostics": ["GENERIC_CAPABILITY_UNKNOWN"]
    },
    {
      "capability_id": "full_9way_directional_modifier_table",
      "label": "Full 9-way directional modifier table",
      "status": "UNSUPPORTED_BY_CURRENT_SOURCE",
      "scope": "GENERIC_BACKEND",
      "evidence_strength": "DOC_REFERENCE",
      "evaluation_readiness": "LEVEL_1_STATIC_REPRESENTABILITY",
      "source_refs": [
        {
          "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md",
          "symbol": "Senscope-relevant capability matrix",
          "evidence_strength": "DOC_REFERENCE",
          "scope": "REFERENCE_ONLY"
        },
        {
          "path": "src/modes/CustomControllerMode.cpp",
          "symbol": "CustomControllerMode::UpdateAnalogOutputs",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "MODE_SPECIFIC"
        }
      ],
      "limitations": [
        "No proven first-class generic 9-way table model in current source."
      ],
      "diagnostics": ["EXACT_9WAY_TABLE_UNSUPPORTED", "MODE_SPECIFIC_ONLY"]
    },
    {
      "capability_id": "first_class_neutral_direction_5",
      "label": "First-class neutral direction 5",
      "status": "UNSUPPORTED_BY_CURRENT_SOURCE",
      "scope": "GENERIC_BACKEND",
      "evidence_strength": "DOC_REFERENCE",
      "evaluation_readiness": "LEVEL_1_STATIC_REPRESENTABILITY",
      "source_refs": [
        {
          "path": "docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md",
          "symbol": "Neutral directional target handling",
          "evidence_strength": "DOC_REFERENCE",
          "scope": "REFERENCE_ONLY"
        },
        {
          "path": "src/core/ControllerMode.cpp",
          "symbol": "ControllerMode::UpdateDirections",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "GENERIC_BACKEND"
        }
      ],
      "limitations": [
        "Centered default output does not prove first-class direction 5 realization."
      ],
      "diagnostics": ["NEUTRAL_5_UNPROVEN"]
    },
    {
      "capability_id": "noncenter_neutral_output",
      "label": "Non-center neutral output",
      "status": "UNKNOWN",
      "scope": "GENERIC_BACKEND",
      "evidence_strength": "MISSING",
      "evaluation_readiness": "LEVEL_0_EVIDENCE_ONLY",
      "source_refs": [],
      "limitations": [
        "Current active base behavior centers neutral; copied reference evidence is not active runtime authority."
      ],
      "diagnostics": ["NONCENTER_NEUTRAL_UNKNOWN"]
    },
    {
      "capability_id": "dynamic_button_layers",
      "label": "Dynamic button layers",
      "status": "SOURCE_BACKED",
      "scope": "MODE_SPECIFIC",
      "evidence_strength": "DIRECT_SOURCE",
      "evaluation_readiness": "LEVEL_1_STATIC_REPRESENTABILITY",
      "source_refs": [
        {
          "path": "src/modes/Ultimate.cpp",
          "symbol": "Ultimate::UpdateDigitalOutputs",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "MODE_SPECIFIC",
          "note": "D-pad layer behavior is mode-specific."
        },
        {
          "path": "src/modes/CustomControllerMode.cpp",
          "symbol": "CustomControllerMode::UpdateDigitalOutputs",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "MODE_SPECIFIC",
          "note": "Combo suppression is mode/config-specific."
        }
      ],
      "limitations": [
        "Does not prove a generic dynamic layer framework."
      ],
      "diagnostics": ["MODE_SPECIFIC_ONLY", "DYNAMIC_LAYER_GENERIC_UNKNOWN"]
    },
    {
      "capability_id": "export_support",
      "label": "Export support",
      "status": "UNSUPPORTED_BY_CURRENT_SOURCE",
      "scope": "UNKNOWN",
      "evidence_strength": "DOC_REFERENCE",
      "evaluation_readiness": "LEVEL_3_EXPORT_OR_MANUAL_ENTRY",
      "source_refs": [
        {
          "path": "docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md",
          "symbol": "Adapter/export/manual-entry boundary",
          "evidence_strength": "DOC_REFERENCE",
          "scope": "REFERENCE_ONLY"
        }
      ],
      "limitations": [
        "No stable source-backed vendor export artifact workflow is confirmed."
      ],
      "diagnostics": ["EXPORT_NOT_SUPPORTED"]
    },
    {
      "capability_id": "push_to_device_support",
      "label": "Push-to-device support",
      "status": "UNSUPPORTED_BY_CURRENT_SOURCE",
      "scope": "UNKNOWN",
      "evidence_strength": "DOC_REFERENCE",
      "evaluation_readiness": "LEVEL_4_PUSH_TO_DEVICE",
      "source_refs": [
        {
          "path": "HAL/pico/src/comms/ConfiguratorBackend.cpp",
          "symbol": "CMD_SET_CONFIG handling",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "TRANSPORT_SPECIFIC",
          "note": "Device-side handler evidence does not approve host-side push workflow."
        },
        {
          "path": "HAL/pico/src/core/Persistence.cpp",
          "symbol": "Persistence::SaveConfig",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "BOARD_SPECIFIC"
        }
      ],
      "limitations": [
        "Host-side push workflow is not approved or source-backed as an integration feature."
      ],
      "diagnostics": ["PUSH_NOT_SUPPORTED"]
    }
  ],
  "mode_profiles": [
    {
      "mode_id": "example_ultimate_mode",
      "mode_label": "Ultimate",
      "mode_kind": "HARDCODED",
      "source_refs": [
        {
          "path": "src/modes/Ultimate.cpp",
          "symbol": "Ultimate::UpdateDigitalOutputs / Ultimate::UpdateAnalogOutputs",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "MODE_SPECIFIC"
        }
      ],
      "limitations": ["Hardcoded mode-specific evidence only."]
    },
    {
      "mode_id": "example_custom_controller_mode",
      "mode_label": "CustomControllerMode",
      "mode_kind": "CONFIGURABLE",
      "source_refs": [
        {
          "path": "src/modes/CustomControllerMode.cpp",
          "symbol": "CustomControllerMode::UpdateDigitalOutputs / CustomControllerMode::UpdateAnalogOutputs",
          "evidence_strength": "DIRECT_SOURCE",
          "scope": "MODE_SPECIFIC"
        }
      ],
      "limitations": ["Configurable mode-specific evidence; full Senscope-style table coverage unproven."]
    }
  ]
}
```

This example intentionally contains no gameplay semantics.

## 19. Validation Rules for Future Implementation

Future code/schema work should enforce:
- `source_refs` are required for `SOURCE_BACKED`, `INFERRED`, `UNSUPPORTED_BY_CURRENT_SOURCE`, and `OUT_OF_SCOPE` claims.
- `UNKNOWN` is allowed and expected.
- `UNKNOWN` claims may have empty `source_refs`, but should include `unknowns`, limitations, or diagnostics.
- Mode-specific claims cannot satisfy generic requirements without an explicit source-backed bridging rule.
- Config-specific claims cannot satisfy generic requirements without an explicit source-backed bridging rule.
- Transport-specific packing behavior cannot satisfy another transport without source-backed evidence.
- `REFERENCE_ONLY` and `COPIED_REFERENCE` evidence cannot become active runtime support without approval and source proof.
- Export and push statuses must remain unsupported unless separately approved and source-backed.
- No game-semantic fields are allowed in the backend capability model.
- Disallowed fields include action labels, gameplay thresholds, no-smash/no-strong-input membership, semantic map IDs, and game predicate names.
- Same-effective evaluation requires Senscope-supplied or Senscope-referenced dataset/equivalence data; the backend layer must not invent it.

## 20. Relationship to Future G6 Evaluator Tests

If the user explicitly approves G6 later, this draft can support mock capability fixtures for evaluator contract tests.

Potential mock fixtures:
- Mock `SOURCE_BACKED` exact support: a synthetic backend fixture that explicitly supports exact raw left-stick targets, used to test exact-match evaluator behavior without claiming Glyph currently supports generic exact realization.
- Mock `UNKNOWN` support: a fixture where exact support, neutral `5`, or non-center neutral output is unknown, used to test conservative diagnostics.
- Mock mode-specific-only support: a fixture where `CustomControllerMode` or `Ultimate` evidence exists but generic support remains unavailable, used to test `MODE_SPECIFIC_ONLY` behavior.
- Mock export unsupported: a fixture that has static representability but `export_support` remains `UNSUPPORTED_BY_CURRENT_SOURCE`, used to keep export separate from realization.
- Mock same-effective requires dataset: a fixture where raw output differs and no dataset equivalence exists, used to require `SAME_EFFECTIVE_REQUIRES_DATASET`.

Do not create these tests in G5. G6 should not start automatically.

## 21. Open Questions

- What is the first concrete backend target: Ultimate mode, CustomControllerMode, or a future custom mode?
- What evidence is sufficient to promote exact raw coordinate support from inferred to source-backed?
- Should the schema become TypeScript later, JSON Schema later, or stay Markdown until evaluator design stabilizes?
- What source references are acceptable for external HayBox-proto / configurator claims?
- How should copied ESAM1 evidence be tracked if a future custom mode design uses it?

## 22. Recommended Next Action

Recommend human review after G5.

G6 should not start automatically. It should only begin if the user explicitly approves code/test scaffolding for evaluator contract tests using mock capabilities.

## 23. Verification

Commands run for G5:
- `git checkout configurator`: succeeded; branch was already `configurator`.
- `git pull origin configurator`: succeeded; already up to date.
- `git status`: clean on `configurator` before branch creation.
- `git branch --show-current`: reported `configurator` before branch creation.
- `git branch --list docs/glyph-capability-model-g5`: no local branch existed.
- `git checkout -b docs/glyph-capability-model-g5`: succeeded.
- `sed -n '1,260p' ...` and continuation reads for required project docs.
- Targeted `sed -n` and `rg` inspections of supporting source/reference files listed in this document.
- `git status`: run after edits.
- `git diff --stat`: run after edits.

Build was not run because this is a docs-only task and must not be build-affecting.
