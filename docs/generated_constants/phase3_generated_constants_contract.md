# Phase 3 Generated C++ Constants Contract

Status: mixed-phase document with historical docs/tools contract and a current firmware-integration branch.

## Branch split and contract ownership

This document is authoritative for two explicit stages:

- **Phase 3 steps 1-4 branch**: `phase3-generated-constants-contract`
  - docs/tools-only scope
  - preview-only contract and checker preparation
  - no firmware source integration
  - no firmware runtime behavior claims
  - no profile artifact changes

- **Phase 3 Step 6 firmware-integration branch**: `phase3-generated-constants-firmware-integration`
  - behavior-preserving source refactor only
  - firmware source/build-path integration path established for this branch
  - same source-backed values, names, and ordering preserved
  - no runtime-loaded config
  - no WebSerial/device write
  - no protobuf binary write
  - no firmware flashing automation
  - no Senscope schema change
  - no game-semantic source promotion

The preview artifact remains docs-only and is not the active firmware input.

## Purpose and scope

This document defines the Phase 3 generated C++ constants contract for Glyph / HayBox
backend sources.

### Phase 3 steps 1-4

These steps are covered by this contract and are docs/tools-only:

1. define the generated C++ constants target contract;
2. define the source-diff checker contract;
3. implement a read-only checker/tool prototype if repo structure supports it;
4. emit or define a dry-run generated constants preview artifact that is not
   consumed by firmware.

### Phase 3 Step 6 (current branch)

The current approved integration branch:

- does the behavior-preserving firmware refactor from hardcoded table literals to
  generated-like source constants;
- keeps table behavior unchanged;
- requires firmware build and hardware-result gate before merge.

Scope boundaries (current branch):

- behavior-preserving source refactor only;
- no behavior/semantics changes;
- no runtime-loaded config;
- no device write;
- no protobuf binary write;
- no firmware flashing automation;
- no profile artifact changes;
- no Senscope schema changes;
- no game-semantic source authority promotion.

## Non-goals

This contract does not:

- produce profile artifacts;
- add runtime-loaded config;
- add macros, turbo, timing automation, one-shots, or history-dependent logic;
- claim universal official configurator compatibility;
- claim nunchuk validation.

## Source authority requirements

A Phase 3 claim must be backed by one of the following:

- a source file inspected in this repo;
- a documentation file inspected in this repo;
- a fixture or test inspected in this repo;
- an explicit user/domain statement;
- a source-backed hash recorded in the preview artifact.

Primary source authority for this document is limited to:

- `src/modes/Ultimate.cpp`
- `src/modes/UltimateIdentityRuntimeTables.hpp`
- `tools/extract_glyph_identity_runtime_tables.py`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`
- `docs/calibration/glyph_identity_runtime_hardware_validation_and_rollback_plan_2026-05-28.md`
- `docs/calibration/glyph_identity_runtime_smashbox_hardware_result_2026-05-28.md`

Unknowns must be labeled `unknown`. Inferred behavior must be labeled
`inferred`.

External-remapper material remains quarantined unless independently source-backed.

## Generated artifact ownership boundaries

The following are the preview/docs artifacts for this contract:

- the Phase 3 contract document;
- the dry-run preview artifact under `docs/generated_constants/preview/`;
- the read-only checker under `tools/`.

The following were historical preview targets only and are not active inputs in the
current branch by themselves:

- `docs/generated_constants/phase3_generated_constants_contract.md` as contract text;
- `docs/generated_constants/preview/gfw3_generated_constants_preview.json`;
- `tools/check_glyph_phase3_generated_constants_preview.py`;
- any future candidate generated files.

## Generated C++ constants target shape

The current source-backed target shape is the current 27-table
`StickPoint[9]` family used in `src/modes/Ultimate.cpp`.

For this integration branch, the firmware-facing generated-like source path is:

- `src/modes/UltimateIdentityRuntimeTables.hpp`

The above path is used as a generated-like firmware include, while the preview
artifact stays docs-only. `Ultimate.cpp` includes this header after the
`StickPoint` definition.

Target shape requirements:

- preserve the current source-backed table names and ordering;
- preserve the current `StickPoint[9]` table cardinality;
- preserve current source-backed point counts and current baseline values;
- keep the target as pure data, not runtime logic;
- keep the generated-like target free of runtime-loaded config and device-write semantics.

### Current branch integration record

- branch: `phase3-generated-constants-firmware-integration`
- approved scope: behavior-preserving source refactor only
- actual firmware-facing generated-like path: `src/modes/UltimateIdentityRuntimeTables.hpp`
- `Ultimate.cpp` includes this generated-like header after `StickPoint` is defined
- no runtime-loaded config
- no WebSerial/device write
- no protobuf binary write
- no firmware flashing automation
- no profile artifact change
- no intentional controller behavior change
- build gate required
- hardware test/result gate required before merge
- nunchuk status: `NOT_TESTED` unless separately tested and recorded

## Required metadata and provenance fields

Every Phase 3 preview artifact must carry, at minimum:

- `artifact_id`
- `artifact_kind` with the value `DRY_RUN_PREVIEW`
- `generated_for_phase` with the value `3`
- `consumed_by_firmware` with the value `false`
- `source_authority.classification`
- `source_authority.references`
- `source_authority.unknowns`
- `target_file_classes`
- `constants_preview.table_family`
- `constants_preview.table_count`
- `constants_preview.point_count_per_table`
- `comparison_contract.source_diff_mode`
- `comparison_contract.required_pass_conditions`
- `comparison_contract.forbidden_diffs`
- `comparison_contract.allowed_preview_only_diffs`
- SHA-256 hashes for the referenced source-backed files or fixtures

The preview may use source-backed summary metadata rather than raw table values,
but it must state that choice explicitly.

## Allowed data categories

- source-backed current-baseline table names;
- source-backed point counts;
- source file references;
- fixture references;
- SHA-256 hashes for the referenced source-backed files or fixtures;
- preview-only provisional target file names;
- caveats and unknowns;
- deterministic PASS/FAIL checker output.

## Forbidden data categories

- runtime-loaded config claims;
- device-write claims;
- protobuf binary write claims;
- firmware flashing claims;
- active profile artifact changes;
- Senscope schema changes;
- universal compatibility claims;
- macros, turbo, timing automation, one-shots, or hidden history-dependent
  automation;
- unlabelled inferred behavior.

## Review gates

### Step 6 (current branch)

- product approval gate before firmware source integration;
- source-authority review gate;
- source-diff checker review gate;
- build gate;
- hardware test gate;
- hardware result gating;
- rollback gate before merge.

### Phase 3 steps 1-4 (preview)

- docs/tools review gate;
- source-authority review gate;
- preview artifact review gate;
- source-diff checker review gate;
- product approval gate before firmware source integration;
- build gate for any later firmware-integration branch;
- hardware test gate for any later firmware-integration branch;
- rollback gate before merge of any later firmware-integration branch.

## Source-diff checker contract

### Inputs

The checker must read:

- the Phase 3 preview artifact;
- this contract document;
- the current source-backed table extractor;
- the current `src/modes/Ultimate.cpp` table source;
- `src/modes/UltimateIdentityRuntimeTables.hpp` (current branch reference);
- the current committed baseline fixtures named in the preview artifact.

### Outputs

The checker must emit:

- a stable identifier line;
- PASS or FAIL status;
- the number of checked source-backed tables;
- the comparison mode;
- a non-zero exit code on failure.

### Deterministic behavior

The checker must be read-only, stdlib-only, and deterministic. It must not:

- modify files;
- read hardware or device state;
- invoke firmware builds;
- rely on network access;
- rely on environment-specific mutable state.

### Expected pass conditions

The checker must pass only when all of the following are true:

- the preview artifact declares itself as `DRY_RUN_PREVIEW`;
- `generated_for_phase` is `3`;
- `consumed_by_firmware` is `false`;
- the source authority classification is source-backed and preview-only;
- referenced source-backed file hashes match the current files;
- table names match the current source extractor output;
- point counts match the source-backed baseline shape;
- the preview artifact clearly states any summary-only representation;
- required caveats are present;
- required future target file classes are present and marked as provisional or
  docs-only, not active build inputs.

### Forbidden diffs

The checker must fail on any preview claim or diff that implies:

- firmware source integration in this docs/tools-only phase;
- runtime-loaded config;
- device write;
- protobuf binary write;
- firmware flashing automation;
- profile schema changes;
- universal compatibility claims;
- nunchuk validation claims;
- macros, turbo, timing automation, or hidden automation;
- source authority that is missing, ambiguous, or only inferred without label.

### Allowed preview-only diffs

The checker may accept:

- docs/tools-only artifact paths;
- provisional future target file names marked as not active;
- source-backed summary-only table representation;
- source hashes and provenance hashes;
- explicit unknowns and caveats.

### Source-backed comparison requirements

The checker must compare the preview artifact against source-backed expectations, not
against guessed behavior. If the preview artifact omits raw table values, the
omission must be explicit and the checker must still verify the source-backed table
names, point counts, and provenance hashes.

### Metadata and hash requirements

The checker must require SHA-256 hashes for every referenced source-backed file
or fixture listed in the preview artifact. If a hash field is missing, or if the
computed hash does not match, the checker must fail closed.

### Missing or inferred authority handling

If source authority is missing, inconsistent, or only inferred without being
marked as inferred, the checker must fail.

### Future firmware-integration branch proof before merge

Any later firmware-integration branch that turns this preview into build inputs must
prove all of the following before merge:

- explicit product approval for firmware source edits;
- an exact source diff that preserves the source-backed baseline or otherwise
  explains the approved change;
- a passing firmware build on the approved branch;
- a separate hardware test plan and a recorded hardware result for the stated
  scope;
- a rollback path through normal Git history;
- no unauthorized profile/schema, runtime-loaded config, or device-write
  expansion.

## Rollback and caveat policy

- If the preview artifact or checker drifts, fix the docs/tools artifact first.
- If a future approved firmware branch fails, roll back through normal Git
  history to the current hardcoded baseline.
- Preserve unknowns as unknowns and inferred items as inferred items.
- Do not promote preview-only review text into firmware authority.
- nunchuk remains `NOT_TESTED` unless specifically validated.
