# G6 - Evaluator Contract Tests With Mock Capabilities

Status: complete (docs-only scaffold)  
Date: 2026-05-23  
Branch: `test/glyph-evaluator-contracts-g6`  
Batch type: docs-only fallback (no suitable lightweight repo-local test convention discovered)

## 1. Title and status

This is the G6 evaluator contract test scaffold using **synthetic mock capabilities**.

This batch is documentation-only. It does not implement runtime adapter code, firmware behavior, export generation, push-to-device workflow, or Super Smash Bros. Ultimate game semantics.

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
- `docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`
- `platformio.ini`

Convention checks run:
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)|package.json|pytest|CMakeLists|platformio.ini'`
- `find . -maxdepth 3 -type d | rg '(^|/)(test|tests|spec)$'`
- `sed -n '1,220p' platformio.ini`

Files added:
- `docs/project/G6_EVALUATOR_CONTRACT_TESTS_WITH_MOCK_CAPABILITIES.md`

Intentionally not implemented:
- no runtime evaluator adapter
- no firmware behavior changes
- no export/push workflow implementation
- no neutral profile schema changes
- no game semantics

## 3. Source basis

This G6 scaffold is derived from:
- G3 status and boundary taxonomy (`docs/project/G3_NEUTRAL_PROFILE_INTEGRATION_BOUNDARY_DESIGN.md`)
- G5 capability schema draft (`docs/project/G5_NON_RUNTIME_CAPABILITY_MODEL_SCHEMA_DRAFT.md`)
- G2 capability matrix and scope qualifiers (`docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md`)

No new firmware behavior claims are introduced in G6. All behavior below is contract-level mock evaluation behavior only.

## 4. Contract test principles

- Mock capabilities are synthetic fixtures, not runtime behavior claims.
- Mode-specific support must not auto-satisfy a generic backend requirement.
- `UNKNOWN` remains `UNKNOWN`; missing evidence must not silently pass.
- `UNSUPPORTED` and `UNKNOWN` are distinct outcomes.
- Export and push support are evaluated separately from representability.
- `SAME_EFFECTIVE_OUTPUT` requires a Senscope-supplied equivalence dataset.
- Evaluator contract must not compute or embed game semantics.

## 5. Mock fixture schema

Conceptual fixture shapes for docs/tests:

```ts
type ClaimStatus =
  | "SOURCE_BACKED"
  | "INFERRED"
  | "UNKNOWN"
  | "UNSUPPORTED_BY_CURRENT_SOURCE";

type EvaluationStatus =
  | "EXACT_RAW_MATCH"
  | "SAME_EFFECTIVE_OUTPUT"
  | "RAW_MISMATCH"
  | "UNSUPPORTED"
  | "UNKNOWN"
  | "SOURCE_EVIDENCE_MISSING"
  | "EXPORT_UNSUPPORTED"
  | "PUSH_UNSUPPORTED";

type MockBackendCapability = {
  backend_id: string;
  scope: "GENERIC_BACKEND" | "MODE_SPECIFIC";
  mode_id?: string;
  exact_raw_left_stick_output: ClaimStatus;
  full_9way_directional_modifier_table: ClaimStatus;
  neutral_direction_5_support: ClaimStatus;
  noncenter_neutral_support: ClaimStatus;
  export_support: ClaimStatus;
  push_to_device_support: ClaimStatus;
  source_refs: string[];
};

type MockNeutralTarget = {
  modifier_id: string;
  direction: 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9;
  desired_raw: { x: number; y: number };
  dataset_id?: string;
};

type MockEvaluationRequest = {
  intent: "REPRESENTABILITY" | "EXPORT" | "PUSH";
  required_scope: "GENERIC_BACKEND" | "MODE_SPECIFIC_OK";
  target: MockNeutralTarget;
  realized_raw?: { x: number; y: number };
  equivalence_dataset?: MockEquivalenceDataset;
};

type MockEquivalenceDataset = {
  dataset_id: string;
  mappings: Array<{
    desired_raw: { x: number; y: number };
    realized_raw: { x: number; y: number };
    effective_output_id: string;
  }>;
};

type ExpectedEvaluation = {
  status: EvaluationStatus;
  diagnostics: string[];
};
```

## 6. Test case matrix

### G6-C01 - SOURCE_BACKED exact raw support mock
- Purpose: confirm exact raw match path.
- Mock inputs:
  - backend `exact_raw_left_stick_output = SOURCE_BACKED`
  - neutral target raw coordinate provided
  - realized raw equals desired raw
- Expected status: `EXACT_RAW_MATCH`
- Expected diagnostics: `[]` or optional informational code
- Non-goals: no claim that current Glyph generically supports arbitrary exact raw output.

### G6-C02 - UNKNOWN exact support mock
- Purpose: unknown evidence must not pass silently.
- Mock inputs:
  - backend `exact_raw_left_stick_output = UNKNOWN`
  - neutral target raw coordinate provided
- Expected status: `UNKNOWN` (or `SOURCE_EVIDENCE_MISSING` by implementation choice)
- Expected diagnostics: includes `SOURCE_EVIDENCE_MISSING` or equivalent unknown-evidence diagnostic
- Non-goals: no inference upgrade from unknown to supported.

### G6-C03 - UNSUPPORTED generic 9-way table mock
- Purpose: explicit unsupported generic 9-way should fail clearly.
- Mock inputs:
  - backend `full_9way_directional_modifier_table = UNSUPPORTED_BY_CURRENT_SOURCE`
- Expected status: `UNSUPPORTED`
- Expected diagnostics: includes `EXACT_9WAY_TABLE_UNSUPPORTED`
- Non-goals: no fallback to mode-specific behavior.

### G6-C04 - Mode-specific-only support mock
- Purpose: mode-specific evidence cannot auto-satisfy generic requirement.
- Mock inputs:
  - backend scope `MODE_SPECIFIC`
  - capability evidence marked `SOURCE_BACKED` but mode-limited
  - request `required_scope = GENERIC_BACKEND`
- Expected status: `UNKNOWN` or `UNSUPPORTED` (implementation choice, must be explicit)
- Expected diagnostics: includes `MODE_SPECIFIC_ONLY` or `GENERIC_CAPABILITY_UNKNOWN`
- Non-goals: no automatic promotion from mode-specific support to generic support.

### G6-C05 - Direction 5 non-center neutral unknown mock
- Purpose: unknown neutral-5/non-center support is preserved.
- Mock inputs:
  - neutral target `direction = 5`
  - target raw is non-center (`x != 128` or `y != 128`)
  - backend `neutral_direction_5_support = UNKNOWN`
  - backend `noncenter_neutral_support = UNKNOWN`
- Expected status: `UNKNOWN`
- Expected diagnostics: includes `NEUTRAL_5_UNPROVEN` and `NONCENTER_NEUTRAL_UNKNOWN`
- Non-goals: no assumption that neutral 5 must center or must be non-center.

### G6-C06 - Export unsupported mock
- Purpose: export capability is separate from representability.
- Mock inputs:
  - representability path may otherwise pass
  - request `intent = EXPORT`
  - backend `export_support = UNSUPPORTED_BY_CURRENT_SOURCE`
- Expected status: `EXPORT_UNSUPPORTED`
- Expected diagnostics: includes `EXPORT_UNSUPPORTED`
- Non-goals: no vendor format synthesis.

### G6-C07 - Push unsupported mock
- Purpose: push capability is separate from representability and source notes.
- Mock inputs:
  - request `intent = PUSH`
  - backend `push_to_device_support = UNSUPPORTED_BY_CURRENT_SOURCE`
- Expected status: `PUSH_UNSUPPORTED`
- Expected diagnostics: includes `PUSH_UNSUPPORTED`
- Non-goals: no host push workflow assumptions from device-side notes.

### G6-C08 - Same-effective requires dataset mock
- Purpose: prevent implicit game-semantic equivalence.
- Mock inputs:
  - desired raw and realized raw mismatch
  - no `equivalence_dataset` supplied
- Expected status: not `SAME_EFFECTIVE_OUTPUT`; expected `RAW_MISMATCH` or `UNKNOWN`
- Expected diagnostics: includes `SAME_EFFECTIVE_REQUIRES_DATASET`
- Non-goals: no internal game semantics or threshold computation.

### G6-C09 - Same-effective allowed with supplied equivalence mock
- Purpose: allow same-effective only when dataset evidence is present.
- Mock inputs:
  - desired raw and realized raw mismatch
  - `equivalence_dataset` supplied and contains mapping proving same effective output
- Expected status: `SAME_EFFECTIVE_OUTPUT`
- Expected diagnostics: includes dataset trace diagnostic (for example `SAME_EFFECTIVE_DATASET_MATCH`)
- Non-goals: evaluator does not derive equivalence itself; it only consumes supplied dataset evidence.

## 7. Files added

- `docs/project/G6_EVALUATOR_CONTRACT_TESTS_WITH_MOCK_CAPABILITIES.md`

No runtime code, firmware code, export code, or push workflow code was added.

## 8. Verification

Inspection commands run:
- `find . -maxdepth 4 -type f | rg '/(test|tests|spec)/|(_test\\.|\\.test\\.|\\.spec\\.)|package.json|pytest|CMakeLists|platformio.ini'`
  - result: only `platformio.ini` and PlatformIO package metadata under `.platformio-home`; no repo-local test/spec convention detected
- `find . -maxdepth 3 -type d | rg '(^|/)(test|tests|spec)$'`
  - result: no matches
- `sed -n '1,220p' platformio.ini`
  - result: PlatformIO firmware build configuration inspected; no lightweight host-side test harness path identified for this batch

Docs-only verification commands run:
- `git status`
  - result: branch `test/glyph-evaluator-contracts-g6`; one modified file (`docs/project/ACTIVE_AGENT_QUEUE.md`) and one untracked file (this G6 document) before staging
- `git diff --stat`
  - result: tracked diff reflects queue update only at that point (`docs/project/ACTIVE_AGENT_QUEUE.md | 10 +++++++---`)

No firmware build/test was run because this batch is docs-only and intentionally avoids firmware/runtime changes.

## 9. Recommended next action

Recommended next step is human review of this G6 contract matrix before any evaluator implementation.

Because this batch is docs-only, decide explicitly whether to introduce a lightweight test framework in a future approved batch, or keep evaluator contract coverage as design fixtures until a stable test convention is selected.

Do not proceed automatically to G7 or G8 without explicit approval.
