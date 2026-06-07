# Phase 3 Generated C++ Constants Contract

Status: docs/tools-only, preview-only, not firmware input.

## Purpose and scope

This document defines the Phase 3 contract for the Glyph / HayBox-side
generated C++ constants path. Phase 3 steps 1-4 are covered here:

1. define the generated C++ constants target contract;
2. define the source-diff checker contract;
3. implement a read-only checker/tool prototype if repo structure supports it;
4. emit or define a dry-run generated constants preview artifact that is not
   consumed by firmware.

This branch prepares the review and tooling path for a future product-approval
gate. It does not integrate generated constants into firmware and it does not
change controller/runtime behavior.

Scope boundaries:

- docs/tools-only;
- no firmware source integration;
- no PlatformIO or build-input wiring;
- no runtime-loaded config;
- no device write;
- no protobuf binary write;
- no firmware flashing automation;
- no hardware validation claim;
- no Senscope schema change;
- no game-semantic source authority promotion.

## Non-goals

This contract does not:

- implement firmware behavior;
- choose a final firmware file path or include path for the future approved
  branch;
- claim universal official configurator compatibility;
- claim nunchuk validation;
- introduce macros, turbo, timing automation, one-shots, or history-dependent
  logic;
- produce an artifact that firmware consumes in this branch.

## Source authority requirements

A Phase 3 claim must be backed by one of the following:

- a source file inspected in this repo;
- a documentation file inspected in this repo;
- a fixture or test inspected in this repo;
- an explicit user/domain statement;
- a source-backed hash recorded in the preview artifact.

Primary source authority for this contract is limited to:

- `src/modes/Ultimate.cpp`
- `tools/extract_glyph_identity_runtime_tables.py`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_cpp_tables_2026-05-28.txt`
- `docs/CURRENT_STATE.md`
- `docs/ROADMAP.md`
- `docs/WORKFLOW.md`

Unknowns must be labeled `unknown`. Inferred behavior must be labeled
`inferred`.

External-remapper material remains quarantined unless independently
source-backed.

## Generated artifact ownership boundaries

The following are owned by this branch only as docs/tools/preview artifacts:

- the Phase 3 contract document;
- the dry-run preview artifact under `docs/generated_constants/preview/`;
- the read-only checker under `tools/`.

The following are future-branch artifacts only and must not be wired into this
branch's firmware build:

- any generated C++ constants header class;
- any generated C++ constants implementation class;
- any generated C++ constants manifest class;
- any firmware include/build-path wiring for generated constants.

If a later approved branch creates firmware-facing generated files, that branch
must re-author and review those files separately.

## Generated C++ constants target shape

The current source-backed target shape is the current 27-table
`StickPoint[9]` family used in `src/modes/Ultimate.cpp`.

Target shape requirements:

- preserve the current source-backed table names and ordering;
- preserve the current `StickPoint[9]` table cardinality;
- preserve current source-backed point counts and current baseline values;
- keep the target as pure data, not runtime logic;
- keep the target out of firmware wiring in this branch;
- keep the target free of runtime-loaded config semantics and device-write
  semantics.

This branch only defines the target contract and the review path. It does not
approve firmware source edits.

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
- firmware source integration claims in this branch;
- active profile artifact changes;
- Senscope schema changes;
- universal compatibility claims;
- macros, turbo, timing automation, one-shots, or hidden history-dependent
  automation;
- unlabelled inferred behavior.

## Review gates

- docs/tools review gate;
- source-authority review gate;
- preview artifact review gate;
- source-diff checker review gate;
- product approval gate before firmware source integration;
- build gate for any later firmware-integration branch;
- hardware test gate for any later firmware-integration branch;
- rollback gate before merge of any later firmware-integration branch.

The build gate and hardware test gate do not apply to this docs/tools-only
branch. They apply only to a future approved branch that changes firmware
source.

## Source-diff checker contract

### Inputs

The checker must read:

- the Phase 3 preview artifact;
- this contract document;
- the current source-backed table extractor;
- the current `src/modes/Ultimate.cpp` table source;
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

- firmware source integration in this branch;
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

The checker must compare the preview artifact against source-backed
expectations, not against guessed behavior. If the preview artifact omits raw
table values, the omission must be explicit and the checker must still verify
the source-backed table names, point counts, and provenance hashes.

### Metadata and hash requirements

The checker must require SHA-256 hashes for every referenced source-backed file
or fixture listed in the preview artifact. If a hash field is missing, or if the
computed hash does not match, the checker must fail closed.

### Missing or inferred authority handling

If source authority is missing, inconsistent, or only inferred without being
marked as inferred, the checker must fail.

### Future firmware-integration branch proof before merge

Any later firmware-integration branch that turns this preview into build inputs
must prove all of the following before merge:

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
- Phase 3 steps 1-4 are not runtime-loaded config and not device write.
