# Glyph Capability Model Target

This document sketches the target shape for a future Glyph/HayBox-style backend capability model.

It is a design target, not a claim that all fields are currently supported.

## Purpose

A capability model should describe what the backend can represent and what Senscope can safely evaluate.

## Target concepts

### Backend identity

```ts
type BackendIdentity = {
  backend_id: string;
  label: string;
  version?: string;
  source_refs: string[];
};
```

### Input capability

```ts
type BackendInputCapability = {
  input_id: string;
  role: "DIRECTION" | "MODIFIER" | "MODE" | "ACTION" | "OTHER";
  label: string;
  source_refs: string[];
};
```

### Output capability

```ts
type BackendOutputCapability = {
  output_space: "RAW_GC_LEFT_STICK" | "UNKNOWN";
  raw_x_range?: [number, number];
  raw_y_range?: [number, number];
  supports_neutral_output: boolean | "UNKNOWN";
  supports_9_way_directional_outputs: boolean | "UNKNOWN";
  source_refs: string[];
};
```

### Modifier capability

```ts
type BackendModifierCapability = {
  modifier_id: string;
  supports_directional_outputs: boolean | "UNKNOWN";
  supported_directions?: Array<1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9>;
  source_refs: string[];
};
```

### Evaluation status

```ts
type BackendRealizationStatus =
  | "EXACT_RAW_MATCH"
  | "SAME_EFFECTIVE_OUTPUT"
  | "RAW_MISMATCH"
  | "UNSUPPORTED"
  | "UNKNOWN";
```

### Diagnostic

```ts
type BackendRealizationDiagnostic = {
  severity: "info" | "warning" | "error";
  code: string;
  message: string;
  source_refs: string[];
};
```

## Source references

Every capability should have `source_refs`.

A source ref may point to:

- code file;
- doc file;
- test file;
- fixture;
- user-confirmed note.

Capabilities without source refs should be marked `UNKNOWN`.

## Non-goals

- final package location;
- final JSON schema;
- final export format;
- push-to-device behavior;
- complete inverse realization solver.

## Stop condition

Before implementing this as runtime code, complete and review:

- G1 repo inventory;
- G2 capability surface extraction;
- G3 neutral profile integration boundary design.
