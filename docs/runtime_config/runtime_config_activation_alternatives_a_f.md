# Runtime Config Activation Alternatives A-F

Status label: DESIGN / DOCS-CHECKER ONLY.

## Purpose

This note compares six activation alternatives for runtime-config handling and
hardened claim language around them. It is documentation and checker material
only. It does not implement runtime-loaded config, storage, WebSerial/device
write, flashing automation, or active firmware behavior changes.

The note is intentionally conservative:

- claims about current behavior must stay source-backed;
- claims about future behavior must be marked inferred or unknown;
- implementation claims must not be upgraded by this note;
- no alternative here is approval to implement any runtime path.

## Current Baseline

The current known-good baseline is the source-owned active path recorded in
`docs/CURRENT_STATE.md` and `docs/runtime_config/IMPLEMENTATION_BOUNDARY.md`.
The active `RuntimeConfigView` selection remains unchanged, and the forbidden
active-publication paths remain forbidden.

This baseline is the comparison anchor for the alternatives below.
The current lane is blocked before active behavior until a selected activation
strategy is implemented and hardware-gated.

## Claim Invariants

Every claim in this note must satisfy all of the following:

- it is explicitly tagged as `source-backed`, `inferred`, or `unknown`;
- it does not claim runtime-loaded config implementation;
- it does not claim device-write or WebSerial implementation;
- it does not claim firmware flashing automation;
- it does not claim hardware validation that has not been recorded;
- it does not claim nunchuk validation;
- it does not reclassify a forbidden path as approved.

Additional hardening rules:

- `source-backed` means the claim is supported by repo source, repo docs,
  repo tests, fixtures, or an explicit user/domain statement.
- `inferred` means the claim is a reasoned interpretation of source-backed
  evidence and must not be presented as direct proof.
- `unknown` means the repo does not currently support the claim.
- no claim in this note may silently upgrade a design alternative into an
  implementation decision.

## Alternatives

### A. Source-Owned Table-Content Replacement Through The Current Baseline Tables

- Classification: `currently hardware-passed`.
- Claim status: `source-backed`.
- Meaning: preserve the existing source-owned active path through the current
  `RuntimeConfigView` selection and current baseline tables.
- Boundary: this is the current known-good baseline, not a new activation
  mechanism.

### B. Source-Owned Generated Table File Replacing Or Aliasing The Baseline Tables

- Classification: `plausible but requires source design + build + hardware`.
- Claim status: `inferred`.
- Meaning: a generated source-owned table file could replace or alias the
  current baseline tables while preserving the existing active
  `RuntimeConfigView` publication path.
- Concrete source-change shape: the generated table file may replace or alias
  the compile-time contents of `src/modes/UltimateIdentityRuntimeTables.hpp`
  before firmware build, but it must keep
  `GetActiveRuntimeConfigState()`, `ResolveActiveRuntimeConfig()`, and
  `&kSourceOwnedCurrentBaselineRuntimeConfig` unchanged at publication time.
- Boundary: this must keep `GetActiveRuntimeConfigState()`,
  `ResolveActiveRuntimeConfig()`, and `&kSourceOwnedCurrentBaselineRuntimeConfig`
  unchanged at publication time until source design, build proof, and hardware
  proof exist.

### C. Generated `RuntimeConfigView` Wrapper Activation

- Classification: `explicitly forbidden under current evidence`.
- Claim status: `source-backed` only for the prior failure evidence.
- Meaning: active publication through a generated `RuntimeConfigView`
  wrapper.
- Boundary: this repeats the generated-wrapper failure class and remains
  forbidden by the current implementation boundary.

### D. Activate Through `candidate.view`

- Classification: `explicitly forbidden under current evidence`.
- Claim status: `source-backed` only for the prior failure evidence.
- Meaning: active publication through `candidate.view`.
- Boundary: this repeats the candidate-backed active publication failure class
  and remains forbidden by the current implementation boundary.

### E. Activate Through `active_storage.view` Or RAM-Backed Active Table Storage

- Classification: `explicitly forbidden under current evidence`.
- Claim status: `source-backed` only for the prior failure evidence.
- Meaning: active publication through dedicated active storage or RAM-backed
  active table publication.
- Boundary: this repeats the active-storage failure class and remains
  forbidden by the current implementation boundary.

### F. Runtime-Loaded Profile Or Config Interpreter

- Classification: `future architecture only`.
- Claim status: `unknown`.
- Meaning: runtime-loaded config, storage load/save, parser materialization,
  activation selection, and any future browser transport or direct
  device-write activation path as a future runtime architecture.
- Boundary: not implemented, not approved, and not implied by this note.

## Comparison Summary

The alternatives split cleanly into four buckets:

- A is the currently hardware-passed source-owned baseline.
- B is the plausible future source-owned table-file candidate that still needs
  source design, build proof, and hardware proof.
- C, D, and E are explicitly forbidden active-publication paths that remain
  archived evidence.
- F is future architecture only and remains blocked by source authority and
  approval gates.

No alternative in this packet changes the active firmware implementation or
approves a new runtime path.

## Checker Gates

This note is gated by the repo-local checker
`tools/check_glyph_runtime_config_activation_alternatives.py`.

The checker must confirm:

- the A-F headings are present;
- the classification labels match this packet;
- claim invariants remain explicit;
- no positive implementation claim sneaks in for runtime-loaded config,
  WebSerial/device write, flashing automation, candidate-backed activation, or
  active-storage activation;
- the stop line keeps future implementation separate from this note.

The broader runtime-config checker surface remains responsible for the existing
non-claims around generated artifact activation, root-cause proof, nunchuk
testing, runtime-loaded config, WebSerial/device write, and generated wrapper
safe claims.

The Alternative B symbol-map checker
`tools/check_glyph_source_owned_table_symbol_map.py` keeps the current
source-owned alias/replacement boundary explicit without approving any new
active publication path.

## Non-Claims

- This note does not implement runtime-loaded config.
- This note does not implement storage.
- This note does not implement WebSerial/device write.
- This note does not implement flashing automation.
- This note does not change firmware runtime behavior.
- This note does not claim hardware validation.
- This note does not claim nunchuk validation.
- This note does not approve generated RuntimeConfigView wrapper activation.
- This note does not approve `candidate.view` active publication.
- This note does not approve `active_storage.view` active publication.
- This note does not approve RAM-backed active table publication.

## Stop Line

Stop before any implementation work that would turn an alternative into an
active firmware path. Future implementation would require separate source
authority, build proof, and hardware proof where applicable.
