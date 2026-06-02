# Glyph Generated Constants Refactor Execution Packet - 2026-05-28

## Purpose and scope

This execution packet defines the exact review boundary for a possible future
generated constants firmware refactor. It is intended to make the future
implementation scope bounded before any firmware source is touched.

Scope boundaries:

- This is docs/tools-only.
- This does not edit firmware source.
- This does not implement generated constants.
- This does not change table values.
- This does not change firmware runtime behavior.
- This does not change profile artifacts.
- This does not implement runtime-loaded config.
- This does not implement serial/device write behavior.
- This does not validate hardware.

## Status

Blocked until explicit user approval. This packet is not approval to edit
firmware source, move constants, add generated firmware inputs, change runtime
behavior, or claim hardware validation.

Hardware status: not a new hardware result.

## Source authority

Primary source authority is limited to current repository sources:

- `src/modes/Ultimate.cpp`
- generated-config prototype docs/fixtures
- generated C++ diff artifact docs/fixtures
- generated constants readiness packet
- generated constants implementation plan
- hardware validation and rollback plan
- preimplementation go/no-go index
- current identity-runtime checkers in `tools/`

Unknown backend behavior remains unknown. Inferred behavior must be marked as
inferred before it can be used in a later implementation branch.

## Required approval before use

A future implementation branch must not start until explicit user approval is
given.

That approval must specifically authorize touching firmware source for a
generated constants refactor.

Approval for generated constants refactor does not approve runtime-loaded
config, serial/device write behavior, profile schema changes, profile artifact
changes, or behavior changes.

## Candidate future implementation objective

If later approved, the candidate objective is:

- Replace or isolate the current 25 identity-runtime `constexpr StickPoint`
  table constants with generated or generated-like constants.
- Preserve exact current table values.
- Preserve current evaluator phase order and behavior.
- Preserve current role bindings and hard overrides.
- Preserve current generated-config and generated-C++ review artifacts.
- Do not introduce runtime-loaded config.

## Allowed file touch set if later approved

If a future prompt explicitly approves firmware source edits, the allowed file
touch set is limited to:

- `src/modes/Ultimate.cpp`
- optionally one generated constants file under an explicitly approved path,
  such as `include/` or `src/`, but only if the future prompt explicitly permits it;
- relevant tools/checkers/docs;
- no profile artifacts unless a future prompt explicitly approves them.

## Forbidden file touch set

The future implementation must not touch:

- `.pio`
- `.uf2`
- `.bin`
- `.elf`
- `.map`
- local backups
- `__pycache__`
- `.pyc`
- profile artifacts unless explicitly approved
- serial writer behavior
- profile/config/protobuf schema files
- HAL/device transport paths
- any generated file under build-output directories

## Required behavior invariants

The future implementation must preserve:

- all 25 source-parsed tables unchanged;
- generated C++ review artifact still matches generated output;
- generated-config prototype still matches source tables;
- behavior evaluator still passes current cases;
- identity runtime source checker still passes;
- no forbidden artifacts checker still passes;
- no profile artifacts changed;
- no serial/device write behavior changed;
- no runtime-loaded config added;
- no hardware validation claim without result doc.

## Required pre-edit checks

Before any later firmware source edit:

- confirm explicit user approval for generated constants firmware source touch;
- confirm the future branch starts from current `origin/configurator`;
- confirm no local or remote target implementation branch already exists;
- run table source sync;
- run generated-config prototype checks;
- run generated C++ diff artifact checks;
- run behavior-case checks;
- run behavior evaluator;
- run preimplementation go/no-go and implementation planning packet checks;
- run no forbidden artifacts checker.

## Required post-edit checks

After any later approved source edit:

- re-run generated-config prototype generation and checks;
- re-run generated-config evaluator-input checks;
- re-run generated C++ diff artifact checks;
- re-run table source sync;
- re-run identity runtime behavior cases;
- re-run behavior evaluator;
- re-run runtime source and binding checks;
- re-run no forbidden artifacts checker;
- confirm no profile artifacts changed;
- confirm no serial/device write behavior changed;
- confirm no runtime-loaded config was added.

## Required build checks

Because this branch is docs/tools-only, no firmware build is required here.

If a later approved implementation branch touches firmware source, it must run
the repo-approved firmware build command before review. If build output is
needed, it must not be committed and must not be represented as hardware
validation.

## Required hardware test gate

A future generated constants firmware refactor must not be merged until:

- the generated constants refactor hardware test matrix has been executed;
- a separate hardware result doc is recorded for the future implementation
  branch;
- failures trigger rollback handling before merge.

This packet does not execute the hardware matrix and is not a hardware result.

## Required rollback plan

Before future firmware source edits:

- identify the rollback branch or commit;
- preserve a normal Git-history path back to the current hardcoded constants;
- restore any previous firmware artifact only if a later branch intentionally
  produces an artifact;
- restore any previous profile artifact only if a later branch explicitly
  changes a profile artifact;
- document any checker, build, or hardware failure and the exact affected scope.

## Stop conditions

Stop a future implementation attempt if:

- explicit user approval is missing;
- approval does not specifically authorize generated constants firmware source touch;
- source authority for a claimed behavior is missing or ambiguous;
- implementation would depend on inferred behavior;
- any table value would change;
- any runtime behavior would change;
- profile artifacts would change without explicit approval;
- profile/config/protobuf schema changes become necessary;
- runtime-loaded config becomes part of the branch;
- serial/device write behavior becomes part of the branch;
- HAL/device transport paths become part of the branch;
- hardware validation would be claimed without a separate result doc;
- any execution-packet text is interpreted as implementation approval.

## Future implementation prompt location

The future prompt template is:

- `docs/calibration/glyph_generated_constants_refactor_agent_prompt_2026-05-28.md`

That prompt must not be run without explicit user approval for firmware source
touch.

## Open blockers

- Explicit user approval for generated constants firmware source touch.
- Current checker sequence passing immediately before edits.
- Approved generated constants file path if one is needed.
- Hardware test execution and separate result doc before merge.
- Rollback plan confirmed before source edits.
- No unsupported behavior, profile, serial/device, runtime-loaded config, or
  hardware claims.
