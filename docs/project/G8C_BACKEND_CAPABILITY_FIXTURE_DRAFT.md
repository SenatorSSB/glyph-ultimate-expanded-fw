# G8c - Backend Capability Fixture Draft

Status: docs-only fixture-shape draft (non-runtime)
Date: 2026-05-23

## Scope note

This document is docs-only and fixture-shape-only.

Any JSON-like examples below are conceptual and synthetic. They are not production data, not firmware runtime behavior, and not a claim that current Glyph/HayBox runtime supports those exact capabilities.

## Purpose

Define a conservative mock fixture shape for software-side realization evaluator design and contract testing.

The fixture shape is intended to preserve source-authority and fail-closed behavior:

1. Unknown remains unknown.
2. Inferred remains inferred.
3. Mode-specific support is not promoted to generic backend support.
4. Same-effective output is not allowed without a Senscope-supplied equivalence dataset.

## Claim status vocabulary

Use the same conservative vocabulary used across prior G5/G6/G8 docs:

- `SOURCE_BACKED`
- `INFERRED`
- `UNKNOWN`
- `UNSUPPORTED_BY_CURRENT_SOURCE`

## Conceptual fixture shape

```json
{
  "fixture_id": "string",
  "backend_id": "string",
  "fixture_kind": "MOCK_BACKEND_CAPABILITY",
  "scope": "GENERIC_BACKEND | MODE_SPECIFIC",
  "claim_status": {
    "vocabulary": [
      "SOURCE_BACKED",
      "INFERRED",
      "UNKNOWN",
      "UNSUPPORTED_BY_CURRENT_SOURCE"
    ]
  },
  "source_refs": [
    {
      "path": "string",
      "symbol": "optional string",
      "note": "optional string"
    }
  ],
  "capabilities": {
    "exact_raw_left_stick_output": "SOURCE_BACKED | INFERRED | UNKNOWN | UNSUPPORTED_BY_CURRENT_SOURCE",
    "full_9way_directional_modifier_table": "SOURCE_BACKED | INFERRED | UNKNOWN | UNSUPPORTED_BY_CURRENT_SOURCE",
    "neutral_direction_5_support": "SOURCE_BACKED | INFERRED | UNKNOWN | UNSUPPORTED_BY_CURRENT_SOURCE",
    "noncenter_neutral_support": "SOURCE_BACKED | INFERRED | UNKNOWN | UNSUPPORTED_BY_CURRENT_SOURCE",
    "selected_runtime_only_support": "SOURCE_BACKED | INFERRED | UNKNOWN | UNSUPPORTED_BY_CURRENT_SOURCE",
    "export_support": "SOURCE_BACKED | INFERRED | UNKNOWN | UNSUPPORTED_BY_CURRENT_SOURCE",
    "push_to_device_support": "SOURCE_BACKED | INFERRED | UNKNOWN | UNSUPPORTED_BY_CURRENT_SOURCE"
  },
  "notes": ["string"],
  "unknowns": ["string"],
  "diagnostics_expected": ["string"]
}
```

## Synthetic fixture examples

All examples are synthetic evaluator-fixture inputs. They are not runtime capability claims.

### 1) `mock_source_backed_exact_raw_backend`

```json
{
  "fixture_id": "mock_source_backed_exact_raw_backend",
  "backend_id": "mock.backend.synthetic.exactraw.v1",
  "fixture_kind": "MOCK_BACKEND_CAPABILITY",
  "scope": "GENERIC_BACKEND",
  "claim_status": {
    "vocabulary": [
      "SOURCE_BACKED",
      "INFERRED",
      "UNKNOWN",
      "UNSUPPORTED_BY_CURRENT_SOURCE"
    ]
  },
  "source_refs": [
    {
      "path": "docs/project/G8C_BACKEND_CAPABILITY_FIXTURE_DRAFT.md",
      "note": "Synthetic fixture example only"
    }
  ],
  "capabilities": {
    "exact_raw_left_stick_output": "SOURCE_BACKED",
    "full_9way_directional_modifier_table": "UNKNOWN",
    "neutral_direction_5_support": "UNKNOWN",
    "noncenter_neutral_support": "UNKNOWN",
    "selected_runtime_only_support": "UNSUPPORTED_BY_CURRENT_SOURCE",
    "export_support": "UNSUPPORTED_BY_CURRENT_SOURCE",
    "push_to_device_support": "UNSUPPORTED_BY_CURRENT_SOURCE"
  },
  "notes": [
    "Clearly synthetic fixture.",
    "Exact raw support is SOURCE_BACKED only within this synthetic fixture context.",
    "Not a claim about current Glyph runtime behavior."
  ],
  "unknowns": [
    "No claim here about generic 9-way table support.",
    "No claim here about neutral direction-5 or non-center neutral support."
  ],
  "diagnostics_expected": [
    "EVIDENCE_SYNTHETIC_FIXTURE",
    "EXPORT_UNSUPPORTED",
    "PUSH_UNSUPPORTED"
  ]
}
```

### 2) `mock_unknown_current_glyph_backend`

```json
{
  "fixture_id": "mock_unknown_current_glyph_backend",
  "backend_id": "glyph.current.audit.unknown.v1",
  "fixture_kind": "MOCK_BACKEND_CAPABILITY",
  "scope": "GENERIC_BACKEND",
  "claim_status": {
    "vocabulary": [
      "SOURCE_BACKED",
      "INFERRED",
      "UNKNOWN",
      "UNSUPPORTED_BY_CURRENT_SOURCE"
    ]
  },
  "source_refs": [
    {
      "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md",
      "note": "Used as source-audit baseline for unknown/unsupported placeholders"
    },
    {
      "path": "docs/project/G8_MOCK_EVALUATOR_CONTRACT.md",
      "note": "Contract-level status behavior"
    }
  ],
  "capabilities": {
    "exact_raw_left_stick_output": "UNKNOWN",
    "full_9way_directional_modifier_table": "UNSUPPORTED_BY_CURRENT_SOURCE",
    "neutral_direction_5_support": "UNKNOWN",
    "noncenter_neutral_support": "UNKNOWN",
    "selected_runtime_only_support": "UNKNOWN",
    "export_support": "UNSUPPORTED_BY_CURRENT_SOURCE",
    "push_to_device_support": "UNSUPPORTED_BY_CURRENT_SOURCE"
  },
  "notes": [
    "Does not claim arbitrary exact raw output support.",
    "Preserves fail-closed unknown/unsupported behavior."
  ],
  "unknowns": [
    "Generic backend support for arbitrary exact raw output is unknown.",
    "No generic neutral-5/non-center support claim without source-backed evidence."
  ],
  "diagnostics_expected": [
    "EVIDENCE_MISSING_REF",
    "TABLE9_UNSUPPORTED",
    "NEUTRAL5_UNKNOWN",
    "NONCENTER_UNKNOWN",
    "EXPORT_UNSUPPORTED",
    "PUSH_UNSUPPORTED"
  ]
}
```

### 3) `mock_mode_specific_only_backend`

```json
{
  "fixture_id": "mock_mode_specific_only_backend",
  "backend_id": "mock.backend.mode.specific.only.v1",
  "fixture_kind": "MOCK_BACKEND_CAPABILITY",
  "scope": "MODE_SPECIFIC",
  "claim_status": {
    "vocabulary": [
      "SOURCE_BACKED",
      "INFERRED",
      "UNKNOWN",
      "UNSUPPORTED_BY_CURRENT_SOURCE"
    ]
  },
  "source_refs": [
    {
      "path": "docs/project/G2_CONTROLLER_CAPABILITY_SURFACE_EXTRACTION.md",
      "note": "Mode-specific caveat pattern"
    }
  ],
  "capabilities": {
    "exact_raw_left_stick_output": "SOURCE_BACKED",
    "full_9way_directional_modifier_table": "UNKNOWN",
    "neutral_direction_5_support": "UNKNOWN",
    "noncenter_neutral_support": "UNKNOWN",
    "selected_runtime_only_support": "SOURCE_BACKED",
    "export_support": "UNSUPPORTED_BY_CURRENT_SOURCE",
    "push_to_device_support": "UNSUPPORTED_BY_CURRENT_SOURCE"
  },
  "notes": [
    "Mode-specific support is source-backed only for selected runtime scope.",
    "Cannot satisfy a generic backend requirement by itself."
  ],
  "unknowns": [
    "Generic backend equivalence remains unknown without generic source-backed claims."
  ],
  "diagnostics_expected": [
    "SCOPE_MODE_SPECIFIC_ONLY",
    "MODE_SCOPE_MISMATCH"
  ]
}
```

## Same-effective dependency example

Same-effective is external-dataset-dependent and must not be derived implicitly.

```json
{
  "comparison": {
    "desired_raw": { "x": 95, "y": 128 },
    "realized_raw": { "x": 90, "y": 128 }
  },
  "equivalence_dataset": {
    "dataset_id": "senscope_equivalence_v1",
    "provided": true
  },
  "allowed_status_if_mapping_exists": "SAME_EFFECTIVE_OUTPUT"
}
```

No dataset case:

```json
{
  "comparison": {
    "desired_raw": { "x": 95, "y": 128 },
    "realized_raw": { "x": 90, "y": 128 }
  },
  "equivalence_dataset": {
    "dataset_id": null,
    "provided": false
  },
  "required_status": "RAW_MISMATCH or UNKNOWN",
  "forbidden_status": "SAME_EFFECTIVE_OUTPUT"
}
```

## Boundary reminders

1. This draft is docs-only and fixture-shape-only.
2. Fixture examples are synthetic and non-production.
3. No actual Glyph runtime capability is asserted here beyond source-backed references already documented in existing G2/G5/G6/G8 docs.
