# G3 - Neutral Profile Integration Boundary Design

Status: complete (architecture boundary design)  
Date: 2026-05-23  
Branch inspected: `docs/senscope-glyph-baseline`  
Authority scope: boundary design only; this is not runtime implementation, firmware change, adapter implementation, export approval, or push-to-device approval.

## 1. Title and status

This document is the G3 neutral profile integration boundary design for the Glyph-side controller/backend workstream.

It describes how Senscope neutral profile concepts may be consumed by a future source-backed backend capability model and realization evaluator. It does not implement runtime backend adapters, alter firmware behavior, alter Senscope neutral profile schema, or change Senscope game-semantic source authority.

## 2. Scope

Inspected:
- Standing workflow and boundary docs:
  - `AGENTS.md`
  - `docs/project/ACTIVE_AGENT_QUEUE.md`
  - `docs/project/AGENT_OPERATING_CONTRACT.md`
  - `docs/project/AGENT_STOP_CONDITIONS.md`
  - `docs/project/GLYPH_WORKSTREAM_BOUNDARIES.md`
  - `docs/project/SENSCOPE_INTEGRATION_TARGET.md`
  - `docs/project/GLYPH_CAPABILITY_MODEL_TARGET.md`
- Prior G docs:
  - `docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md`
  - `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`
- Source/config/reference files needed to keep this boundary grounded:
  - `include/core/state.hpp`
  - `src/core/ControllerMode.cpp`
  - `src/core/InputMode.cpp`
  - `src/core/socd.cpp`
  - `src/modes/Ultimate.cpp`
  - `src/modes/CustomControllerMode.cpp`
  - `HAL/pico/src/comms/ConfiguratorBackend.cpp`
  - `HAL/pico/src/core/Persistence.cpp`
  - `docs/sources/source-manifest.json`
  - `docs/sources/raw/ESAM1.cpp`
  - `docs/sources/raw/ESAM1.hpp`
  - `docs/sources/raw/GlyphUserProfiles.json`

This document decides:
- The conceptual boundary between neutral profile inputs, backend capability facts, realization evaluation, diagnostics, and future adapter outputs.
- A conservative status taxonomy for source-backed, unsupported, unknown, and not-yet-approved cases.
- The near-term evaluation scope: source-evidence classification and static representability only.
- How G2 capability findings should influence integration diagnostics without promoting mode-specific behavior to generic backend support.

This document intentionally defers:
- Runtime adapter implementation.
- Final TypeScript package location or file layout.
- Final JSON/schema definitions.
- Firmware changes.
- Export file generation.
- Host-side push-to-device workflows.
- Deterministic modeling of behavior that is not fully source-backed.
- Solver/search design.

Game semantics and Senscope semantic-source authority are out of scope. This document does not add, modify, choose, or promote Super Smash Bros. Ultimate action meanings, thresholds, semantic maps, no-smash/no-strong-input behavior, or source-authority rules.

## 3. Source basis

G1 is used as the repository architecture baseline. It identifies the core pipeline, mode structure, config/persistence paths, HAL/backend surface, staged source materials, and source-authority gaps. Source: `docs/project/G1_GLYPH_REPO_INVENTORY_AND_ARCHITECTURE_MAP.md`.

G2 is used as the capability extraction baseline. It provides the current claim matrix and classifies controller/backend behaviors as `SOURCE_BACKED`, `INFERRED`, `UNKNOWN`, or `UNSUPPORTED_BY_CURRENT_SOURCE`. Source: `docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`.

Source files relied on:
- `include/core/state.hpp`: `InputState`, `StickDirections`, `OutputState`, byte analog fields.
- `src/core/ControllerMode.cpp`: output pipeline order and base direction-to-analog synthesis.
- `src/core/InputMode.cpp`: config-backed remap and SOCD dispatch.
- `src/core/socd.cpp`: SOCD algorithm implementations.
- `src/modes/Ultimate.cpp`: mode-specific hardcoded digital/analog behavior, D-pad layer, trigger values, nunchuk override.
- `src/modes/CustomControllerMode.cpp`: config-backed custom digital mappings, button combo mappings, stick direction mappings, analog modifiers, analog trigger mappings, nunchuk override.
- `HAL/pico/src/comms/ConfiguratorBackend.cpp`: device-side config get/set command handlers and validation before persistence.
- `HAL/pico/src/core/Persistence.cpp`: LittleFS protobuf config save/load with size and CRC header.
- `docs/sources/source-manifest.json`: staged reference source status.
- `docs/sources/raw/ESAM1.cpp` and `docs/sources/raw/ESAM1.hpp`: copied reference behavior, not direct modern runtime authority.
- `docs/sources/raw/GlyphUserProfiles.json`: copied reference config-like material, not sufficient by itself to prove a stable external export/import workflow.

Uncertain behavior remains `UNKNOWN` rather than assumed. Inferred behavior remains marked as inferred and should not become an implementation dependency without review.

## 4. Neutral profile assumptions consumed from Senscope

G3 may consume these external Senscope assumptions without changing them:
- Senscope owns the neutral profile format.
- A neutral profile may include `dataset_id`.
- A neutral profile may include controller family or backend target metadata.
- Modifier directional maps are profile concepts owned by Senscope.
- Direction keys use FGC/numpad directions `1..9`.
- Direction `5` neutral is first-class neutral profile intent.
- Raw coordinates are the canonical storage truth for directional targets.
- Raw `x` and `y` are byte coordinates in range `0..255`.
- Desired output is a raw left-stick coordinate unless a future source-backed adapter explicitly supports another output target.

This document does not alter these assumptions and does not require Senscope to adopt a Glyph/HayBox private or firmware-native schema as canonical truth.

## 5. Integration boundary overview

The intended boundary is:

```text
NeutralProfile
  -> BackendCapabilityModel
  -> RealizationEvaluator
  -> RealizationReport / Diagnostics
  -> optional future AdapterOutput
```

`NeutralProfile` is external/app-owned Senscope intent. `BackendCapabilityModel` is source-backed Glyph/HayBox-side capability knowledge. `RealizationEvaluator` compares desired neutral targets against the capability model. `RealizationReport` and diagnostics explain exact matches, mismatches, unsupported features, and unknowns.

`AdapterOutput` is optional future work. It is not implemented by G3 and is not approved by this document. Any manual-entry guide, export artifact, or push-to-device workflow must be separately source-backed and explicitly approved.

## 6. Core object concepts

The following are conceptual, non-final TypeScript-like shapes. They are design contracts only, not implementation files or schema changes.

```ts
type SourceRef = {
  path: string;
  symbol?: string;
  note?: string;
};

type CapabilityStatus =
  | "SOURCE_BACKED"
  | "INFERRED"
  | "UNKNOWN"
  | "UNSUPPORTED_BY_CURRENT_SOURCE";

type BackendIdentity = {
  backend_id: string;
  label: string;
  firmware_family?: string;
  mode_id?: string;
  mode_scope: "GENERIC" | "MODE_SPECIFIC" | "REFERENCE_ONLY" | "UNKNOWN";
  source_refs: SourceRef[];
};

type BackendCapabilityModel = {
  identity: BackendIdentity;
  input_surface: BackendInputSurface;
  output_surface: BackendOutputSurface;
  modifier_surface: BackendModifierSurface;
  rule_surface: BackendRuleSurface;
  assumptions: string[];
  unknowns: string[];
  source_refs: SourceRef[];
};

type BackendInputSurface = {
  physical_buttons: Array<{
    button_id: string;
    source_refs: SourceRef[];
  }>;
  nunchuk_inputs?: {
    supports_connected_flag: boolean | "UNKNOWN";
    supports_buttons: boolean | "UNKNOWN";
    supports_axes: boolean | "UNKNOWN";
    source_refs: SourceRef[];
  };
};

type BackendOutputSurface = {
  analog_spaces: Array<{
    output_id: "RAW_GC_LEFT_STICK" | "RAW_GC_RIGHT_STICK" | "ANALOG_TRIGGER" | "UNKNOWN";
    axes: string[];
    raw_range?: [number, number];
    default_raw?: Record<string, number>;
    mode_scope: "GENERIC" | "MODE_SPECIFIC" | "UNKNOWN";
    source_refs: SourceRef[];
  }>;
  digital_outputs: Array<{
    output_id: string;
    source_refs: SourceRef[];
  }>;
};

type BackendModifierSurface = {
  supports_first_class_9way_table: boolean | "UNKNOWN";
  supports_direction_5: boolean | "UNKNOWN";
  supports_noncenter_neutral: boolean | "UNKNOWN";
  modifiers: Array<{
    modifier_id: string;
    role: "BUTTON_MASK" | "ANALOG_MODIFIER" | "MODE_SPECIFIC" | "UNKNOWN";
    supported_directions?: Array<1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9>;
    mode_scope: "GENERIC" | "MODE_SPECIFIC" | "UNKNOWN";
    source_refs: SourceRef[];
  }>;
};

type BackendRuleSurface = {
  socd_rules?: {
    status: CapabilityStatus;
    available_types: string[];
    pipeline_position?: string;
    source_refs: SourceRef[];
  };
  remap_rules?: {
    status: CapabilityStatus;
    supports_many_to_one: boolean | "UNKNOWN";
    anti_macro_guard: boolean | "UNKNOWN";
    source_refs: SourceRef[];
  };
  chord_rules?: {
    status: CapabilityStatus;
    mode_scope: "GENERIC" | "MODE_SPECIFIC" | "UNKNOWN";
    source_refs: SourceRef[];
  };
  layer_rules?: {
    status: CapabilityStatus;
    mode_scope: "GENERIC" | "MODE_SPECIFIC" | "UNKNOWN";
    source_refs: SourceRef[];
  };
};

type NeutralProfileInput = {
  profile_id?: string;
  dataset_id: string;
  controller_family?: string;
  backend_target?: string;
  directional_targets: NeutralDirectionalTarget[];
  source_refs?: SourceRef[];
};

type NeutralDirectionalTarget = {
  modifier_id: string;
  direction: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;
  desired_raw: {
    x: number;
    y: number;
  };
  desired_output_id?: "RAW_GC_LEFT_STICK" | string;
  desired_effective_output_id?: string;
  dataset_id: string;
  notes?: string[];
  source_refs?: SourceRef[];
};

type RealizationRequest = {
  neutral_profile: NeutralProfileInput;
  backend_capability_model: BackendCapabilityModel;
  evaluation_level: 0 | 1 | 2 | 3 | 4;
};

type RealizationStatus =
  | "EXACT_RAW_MATCH"
  | "SAME_EFFECTIVE_OUTPUT"
  | "RAW_MISMATCH"
  | "UNSUPPORTED"
  | "UNKNOWN"
  | "SOURCE_EVIDENCE_MISSING"
  | "EXPORT_UNSUPPORTED"
  | "PUSH_UNSUPPORTED";

type RealizationEvaluation = {
  target: NeutralDirectionalTarget;
  status: RealizationStatus;
  realized_raw?: {
    x: number;
    y: number;
  };
  diagnostics: RealizationDiagnostic[];
  source_refs: SourceRef[];
};

type RealizationDiagnostic = {
  code: string;
  severity: "info" | "warning" | "error";
  message: string;
  target_ref?: string;
  source_refs: SourceRef[];
};

type RealizationReport = {
  request_summary: {
    profile_id?: string;
    dataset_id: string;
    backend_id: string;
    evaluation_level: 0 | 1 | 2 | 3 | 4;
  };
  evaluations: RealizationEvaluation[];
  diagnostics: RealizationDiagnostic[];
  adapter_output?: never;
};
```

`adapter_output?: never` is intentional for G3: this document describes where an output layer could attach later, not that it exists now.

## 7. Realization status taxonomy

`EXACT_RAW_MATCH`: Use when the backend realization is source-backed and produces the requested raw `x/y` bytes for the requested output target.

`SAME_EFFECTIVE_OUTPUT`: Use only when Senscope supplies or references a raw-to-effective dataset/equivalence source and the backend realized output differs in raw bytes but matches that supplied effective output. The backend layer must not compute game semantics itself.

`RAW_MISMATCH`: Use when the backend behavior is source-backed and deterministically produces a different raw coordinate than requested.

`UNSUPPORTED`: Use when inspected source proves inability or when the required primitive is absent from current source. Example: no proven first-class generic 9-way directional modifier table in the inspected G2 source basis.

`UNKNOWN`: Use when behavior is not proven, not inspected deeply enough, or not safely classifiable from current source.

`SOURCE_EVIDENCE_MISSING`: Use when a claim would require source support but no source reference supports the needed behavior. This can appear as a diagnostic even when the target-level result is `UNKNOWN`.

`EXPORT_UNSUPPORTED`: Use when generating a stable source-backed export artifact is requested or evaluated but no source-backed stable export format/workflow is confirmed.

`PUSH_UNSUPPORTED`: Use when host-side push-to-device workflow support is requested or evaluated but no approved, source-backed workflow is confirmed.

Important distinctions:
- `UNSUPPORTED` means source-backed inability or absent required primitive.
- `UNKNOWN` means not proven or not inspected enough.
- `SOURCE_EVIDENCE_MISSING` means no source reference supports the needed behavior.
- `EXPORT_UNSUPPORTED` does not imply runtime realization is impossible.
- `PUSH_UNSUPPORTED` does not imply manual-entry is impossible.

## 8. Evaluation levels

Level 0: source-evidence classification only. The evaluator checks whether each needed capability has source references and reports `SOURCE_BACKED`, `INFERRED`, `UNKNOWN`, or `UNSUPPORTED_BY_CURRENT_SOURCE` provenance.

Level 1: static representability check. The evaluator checks whether the capability model appears to contain source-backed primitives for the neutral profile target shape, without simulating firmware rules.

Level 2: deterministic realization evaluation from known backend rules. The evaluator computes realized raw outputs from fully modeled, source-backed backend behavior.

Level 3: export/manual-entry artifact generation. A future adapter produces manual-entry guidance or a source-backed export artifact.

Level 4: push-to-device workflow. A future workflow writes configuration to hardware through an explicitly approved and source-backed path.

Current recommended near-term scope is Level 0 to Level 1 only. Level 2 and above are future work requiring explicit approval and stronger source support. Level 3 export generation and Level 4 push-to-device workflows are not approved by G3.

## 9. Mapping from G2 capabilities to integration implications

| G2 capability | G2 status | Integration implication | Required diagnostic | G3 recommendation |
|---|---|---|---|---|
| exact raw left-stick coordinate output | `INFERRED` | `OutputState` stores byte-level left-stick fields, but arbitrary exact coordinate realization is not generically proven. | `GENERIC_CAPABILITY_UNKNOWN` or `SOURCE_EVIDENCE_MISSING` | Do not classify as `EXACT_RAW_MATCH` without mode-specific deterministic evidence. |
| full 9-way directional modifier table | `UNSUPPORTED_BY_CURRENT_SOURCE` | No proven first-class generic 9-way modifier table model in active inspected source. | `EXACT_9WAY_TABLE_UNSUPPORTED` | Treat generic full-table realization as unsupported by current source. |
| first-class neutral direction 5 | `UNSUPPORTED_BY_CURRENT_SOURCE` | Centered neutral exists as default analog state, but no explicit backend-level direction `5` field is proven. | `NEUTRAL_5_UNPROVEN` | Evaluate neutral-profile direction `5` as first-class intent while marking backend support unproven/unsupported. |
| non-center neutral output | `UNKNOWN` | Active source centers neutral by default; reference material is not current runtime authority. | `NONCENTER_NEUTRAL_UNKNOWN` | Keep unknown unless a source-backed mode/config path proves non-center neutral realization. |
| flipper transform | `UNKNOWN` | No explicit named active-source primitive found for generic flipper transform behavior. | `FLIPPER_UNSUPPORTED_OR_UNKNOWN` | Do not model as supported until source-backed. |
| pre-SOCD Force Up-B override | `UNKNOWN` | Pipeline source shows remap -> SOCD -> mode output; no explicit primitive with this name is proven. | `PRE_SOCD_OVERRIDE_UNKNOWN` | Keep unknown; do not infer from hardcoded mode behavior. |
| dynamic button layers | `SOURCE_BACKED` | Ultimate D-pad layer and CustomControllerMode combo suppression are source-backed, but mode/config specific. | `MODE_SPECIFIC_ONLY`, `DYNAMIC_LAYER_GENERIC_UNKNOWN` | Preserve mode specificity; do not promote to generic dynamic cluster role reassignment. |
| button chord rules | `SOURCE_BACKED` | CustomControllerMode combo mappings and mode activation masks are source-backed. Generic/export coverage remains unproven. | `MODE_SPECIFIC_ONLY` | Model as source-backed only in the relevant mode/config scope. |
| SOCD handling | `SOURCE_BACKED` | Config-driven pair handling and algorithms are source-backed. | mode-specific or source-ref diagnostics as needed | Include only source-backed SOCD types and pipeline position; do not attach game-semantic meaning. |
| static remapping | `SOURCE_BACKED` | Config-driven button remap and anti-macro duplicate-physical guard are source-backed. | source-ref diagnostics as needed | Include as backend rule surface with source refs. |
| analog multipliers/modifiers | `SOURCE_BACKED` | CustomControllerMode analog modifier paths are source-backed. Full Senscope-style target coverage is not proven. | `MODE_SPECIFIC_ONLY`, `GENERIC_CAPABILITY_UNKNOWN` | Model only as CustomControllerMode-scoped until deterministic representability is reviewed. |
| right-stick/C-stick output | `SOURCE_BACKED` | Output fields and backend consumption are represented; advanced behavior is mode-specific. | `MODE_SPECIFIC_ONLY` when behavior depends on a mode | Include output surface, but default neutral-profile target remains left stick unless future adapter says otherwise. |
| analog triggers | `SOURCE_BACKED` | Analog trigger fields and mappings exist. | source-ref diagnostics as needed | Include output surface; do not use for neutral left-stick realization unless requested by a future approved target. |
| manual-entry support | `INFERRED` | Device/config paths exist, but end-user manual-entry workflow completeness is not proven. | `SOURCE_EVIDENCE_MISSING` or manual-entry caveat | Plan as possible future work, not complete support. |
| export support | `UNSUPPORTED_BY_CURRENT_SOURCE` | No source-backed stable vendor export artifact workflow is confirmed. | `EXPORT_NOT_SUPPORTED` | Mark export unsupported until explicit format/source authority is reviewed. |
| push-to-device support | `INFERRED` | Device-side get/set config paths exist, but public/stable host-side push workflow is not proven or approved. | `PUSH_NOT_SUPPORTED` | Mark push unsupported for integration planning until explicitly approved and source-backed. |

## 10. Neutral directional target handling

A neutral profile target should be represented for evaluation with:
- `modifier_id`: the neutral profile modifier or modifier-like intent identifier.
- `direction`: FGC/numpad direction key `1..9`.
- `desired_raw`: desired raw coordinate, with `x` and `y` byte values in `0..255`.
- `desired_output_id`: optional output target, defaulting to raw left stick for current G3 reasoning.
- `desired_effective_output_id`: optional effective output identifier supplied by Senscope.
- `dataset_id`: source dataset identifier from the neutral profile.
- `notes` and `source_refs`: optional profile-side context supplied by Senscope.

Special handling for direction `5`:
- Direction `5` must be evaluated like any other direction key.
- A non-center desired raw coordinate for direction `5` is allowed by neutral profile intent.
- Backend support for realizing direction `5`, especially non-center direction `5`, may be `UNKNOWN` or `UNSUPPORTED` depending on source evidence.
- Centered firmware default output does not by itself prove support for arbitrary neutral-profile direction `5` realization.

## 11. Exact vs equivalent realization

Exact raw match policy:
- Compare raw `x/y` byte coordinates directly.
- The output target must match, currently expected as raw left stick unless an approved future adapter provides another target.
- Claim `EXACT_RAW_MATCH` only when the backend capability model contains source-backed evidence for the realized raw bytes.

Same effective output policy:
- `SAME_EFFECTIVE_OUTPUT` may be acceptable only if Senscope supplies or references raw-to-effective equivalence data.
- The backend layer must not compute game semantics itself.
- The backend layer must not infer action labels, thresholds, semantic maps, no-smash/no-strong-input membership, or effective equivalence.
- If no dataset/effective equivalence is supplied, do not claim `SAME_EFFECTIVE_OUTPUT`; report `RAW_MISMATCH`, `UNKNOWN`, or `SOURCE_EVIDENCE_MISSING` as appropriate.

## 12. Backend capability model boundary

Belongs in the backend capability model:
- Source-backed input fields and button surfaces.
- Source-backed output fields, including digital outputs and analog byte fields.
- Representable buttons, modifiers, layers, chords, and mappings, with mode-specific scope when applicable.
- Analog output representation and raw ranges when source-backed.
- SOCD, remap, priority, and fusion behavior only when source-backed.
- Mode-specific vs generic scope for every claim.
- `source_refs` for every capability claim.
- Unknowns and unsupported-by-current-source findings.

Does not belong in the backend capability model:
- Super Smash Bros. Ultimate action labels.
- no-smash/no-strong-input semantics.
- Semantic map membership.
- Solver hard constraints based on gameplay.
- Private export assumptions.
- Public/stable host-side push support unless explicitly source-backed and approved.
- Universal backend claims inferred from one mode-specific implementation.

## 13. Realization evaluator boundary

Evaluator responsibilities:
- Consume neutral targets and a backend capability model.
- Classify each target as exact raw match, same effective output, raw mismatch, unsupported, unknown, source evidence missing, export unsupported, or push unsupported.
- Emit diagnostics with source refs and mode-specific caveats.
- Preserve direction `5` as a first-class target key.
- Never invent missing behavior.
- Keep source-backed, inferred, unsupported, and unknown findings distinct.
- Keep mode-specific caveats attached to mode-specific evidence.

Evaluator non-responsibilities:
- Generating controller firmware.
- Changing firmware behavior.
- Deciding gameplay semantics.
- Computing game-semantic equivalence.
- Optimizing profiles globally.
- Searching all possible backend configurations unless separately approved.
- Generating vendor export files.
- Pushing to a device.

## 14. Adapter/export/manual-entry boundary

Future adapter layers may include:
- Manual-entry guide: user-facing instructions derived from a source-backed capability model and reviewed workflow.
- Source-backed export artifact: generated only if a stable format and import path are source-backed and approved.
- Push-to-device workflow: implemented only if the protocol, host-side tooling expectations, and safety boundaries are source-backed and explicitly approved.

Current G3 classifications:
- Manual-entry is possible future planning, not proven complete.
- Export is unsupported unless a source-backed stable format is confirmed.
- Push is unsupported unless explicitly approved and source-backed.

Device-side configurator evidence may be noted as source evidence: `HAL/pico/src/comms/ConfiguratorBackend.cpp` has `CMD_GET_CONFIG` and `CMD_SET_CONFIG` handling, and `HAL/pico/src/core/Persistence.cpp` saves/loads protobuf config with validation. This evidence does not by itself approve a public/stable export artifact or host-side push workflow.

## 15. Diagnostics model

Diagnostic category/code names are conceptual:
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
- `RAW_MISMATCH_SOURCE_BACKED`: deterministic source-backed realization differs from requested raw bytes.
- `REFERENCE_ONLY_SOURCE`: evidence comes from copied reference material rather than active runtime source.

## 16. Example evaluation scenarios

Example 1: desired direction `6` exact raw coordinate, backend generic support unknown.
- Neutral target requests modifier `m1`, direction `6`, desired raw left-stick coordinate `{ x: 200, y: 128 }`.
- Capability model has source-backed byte output fields but no source-backed generic arbitrary-coordinate primitive.
- Recommended result at Level 0/1: `UNKNOWN` with `GENERIC_CAPABILITY_UNKNOWN` and `SOURCE_EVIDENCE_MISSING`.

Example 2: desired direction `5` non-center neutral, backend support unknown.
- Neutral target requests modifier `m1`, direction `5`, desired raw left-stick coordinate `{ x: 128, y: 172 }`.
- Source shows centered defaults in active base direction handling, while copied reference material is not current runtime authority.
- Recommended result at Level 0/1: `UNKNOWN` with `NEUTRAL_5_UNPROVEN` and `NONCENTER_NEUTRAL_UNKNOWN`.

Example 3: desired flipper transform, no explicit active-source primitive found.
- Neutral intent requires a named transform over directional coordinates.
- Inspected active source does not prove a generic named flipper primitive.
- Recommended result at Level 0/1: `UNKNOWN` or `UNSUPPORTED`, with `FLIPPER_UNSUPPORTED_OR_UNKNOWN`, depending on whether the future capability request requires a primitive absent from source.

Example 4: desired chord rule, source-backed in CustomControllerMode but generic/export support unknown.
- Neutral or integration intent needs a button chord to emit a single output and suppress normal behavior for involved inputs.
- `src/modes/CustomControllerMode.cpp` source-backs combo mappings and suppression in that mode.
- Recommended result at Level 0/1: mode-scoped support only, with `MODE_SPECIFIC_ONLY`; export remains `EXPORT_UNSUPPORTED` unless separately source-backed.

Example 5: desired same-effective fallback requires Senscope dataset equivalence data.
- Backend source-backed raw output differs from desired raw bytes.
- Senscope has not supplied a raw-to-effective equivalence reference for the target.
- Recommended result: do not claim `SAME_EFFECTIVE_OUTPUT`; emit `SAME_EFFECTIVE_REQUIRES_DATASET` and classify as `RAW_MISMATCH` if deterministic, otherwise `UNKNOWN`.

## 17. G3 decisions / recommendations

- Maintain the Senscope neutral profile as app-owned truth.
- Keep the backend capability model source-refed for every claim.
- Use conservative status taxonomy and preserve `UNKNOWN` rather than filling gaps with inference.
- Start with Level 0/1 evaluator design only.
- Require explicit review before runtime adapter implementation.
- Do not proceed to export or push without source authority and explicit approval.
- Keep `Ultimate` D-pad layer behavior and `CustomControllerMode` combo behavior mode-specific.
- Do not treat mode-specific source evidence as generic dynamic cluster role reassignment.
- Do not treat backend realization constraints as game semantics.

## 18. Open questions for post-G3 review

- Which backend mode is the initial target for realization evaluation?
- Should evaluator be prototype-only in docs first or code scaffold next?
- What source evidence is sufficient to classify exact raw coordinate support?
- What source evidence is sufficient to model `CustomControllerMode` analog modifiers deterministically?
- Should ESAM1 behavior influence a new custom mode design or remain reference-only?
- What manual-entry path, if any, is acceptable before export support?

## 19. Recommended next batches after G3

- G4: review/normalize G1-G3 and active queue.
- G5: non-runtime capability model schema draft.
- G6: source-backed evaluator contract tests using mock capabilities.
- G7: firmware custom mode design spike, if explicitly approved.
- G8: realization evaluator prototype, if approved.

Do not implement these from G3. They are options for review and sequencing only.

## 20. Verification

Commands run:
- `git status`: branch `docs/senscope-glyph-baseline`; working tree initially clean and up to date with `origin/docs/senscope-glyph-baseline`.
- `git branch --show-current`: `docs/senscope-glyph-baseline`.
- `git remote -v`: `origin` points to `https://github.com/SenatorSSB/glyph-ultimate-expanded-fw.git`; `upstream` points to `https://github.com/LimitLabs/FW-Glyph.git`.
- `git diff --stat`: clean before edits.
- `find docs/project -maxdepth 1 -type f`: confirmed target document did not already exist.
- Targeted `sed -n` inspections of the required workflow docs, G1/G2 docs, and source/reference files listed in this document.
- Targeted `rg` inspections for capability-relevant terms in G2 and source/reference files.

Build verification:
- Not run. This was a docs-only architecture-boundary task and no code or firmware behavior was changed.
