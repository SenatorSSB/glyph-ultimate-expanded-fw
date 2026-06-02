# Glyph Preimplementation Go/No-Go Index - 2026-05-28

## Purpose and scope

This document is the docs/tools-only preimplementation gate index for generated
constants, runtime-loaded config, device write/transport, hardware validation,
nunchuk validation, and Senscope export boundaries.

Scope boundaries:

- This is docs/tools-only.
- This does not change firmware runtime behavior.
- This does not implement generated constants.
- This does not implement runtime-loaded config.
- This does not implement serial/device write behavior.
- This does not validate hardware.
- This does not validate nunchuk hardware behavior.
- This does not touch Senscope browser app code.

## Current status summary

The current source-backed chain remains hardcoded firmware behavior in
`src/modes/Ultimate.cpp`, docs/tools generated-config review artifacts,
docs/tools export contract drafts, and docs/tools runtime-loaded config design
contracts. None of those artifacts approve firmware source changes, runtime
config loading, device transport, or hardware-validation claims.

## Source authority

Primary source authority for this index is limited to current repository
sources:

- `src/modes/Ultimate.cpp`
- `docs/calibration/glyph_identity_runtime_role_map_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_role_map_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_behavior_cases_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_behavior_cases_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_prototype_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_prototype_2026-05-28.json`
- `docs/calibration/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.md`
- `docs/calibration/fixtures/glyph_identity_runtime_generated_config_contract_v0_2026-05-28.json`
- `docs/calibration/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.md`
- `docs/calibration/fixtures/glyph_senscope_to_glyph_export_contract_draft_2026-05-28.json`
- `docs/calibration/glyph_runtime_loaded_config_design_v0_2026-05-28.md`
- `docs/calibration/fixtures/glyph_runtime_loaded_config_design_v0_2026-05-28.json`
- `docs/calibration/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.md`
- `docs/calibration/fixtures/glyph_runtime_loaded_config_validation_contract_v0_2026-05-28.json`
- current checkers in `tools/`

Unknown backend behavior remains unknown. Inferred behavior must be marked as
inferred before it is used in future planning.

## GO / NO-GO table

| Work class | Gate | Notes |
| --- | --- | --- |
| More docs/checkers for source-backed artifacts | GO | Allowed when source authority remains explicit. |
| Generated config prototype/checker maintenance | GO | Docs/tools-only maintenance is allowed. |
| Behavior-case/evaluator/tooling maintenance | GO | Allowed when it preserves current source-backed behavior. |
| Generated C++ review artifact maintenance | GO | Allowed as review artifact maintenance outside firmware source. |
| Generated constants firmware refactor | BLOCKED_EXPLICIT_APPROVAL | Requires explicit user approval before firmware source changes. |
| Runtime-loaded config interpreter/storage | BLOCKED_EXPLICIT_APPROVAL | Requires explicit user approval and resolved design blockers. |
| Device write / serial transport | BLOCKED_SOURCE_AUTHORITY_AND_APPROVAL | Requires source authority and explicit approval. |
| Official configurator integration | BLOCKED_SOURCE_AUTHORITY | Source authority is not established by this index. |
| Nunchuk hardware-validation claims | BLOCKED_HARDWARE | Requires actual nunchuk hardware validation evidence. |
| New runtime behavior change | BLOCKED_EXPLICIT_APPROVAL_AND_HARDWARE_TEST | Requires explicit approval and hardware test plan/execution. |
| Senscope browser-app export implementation | OUT_OF_SCOPE_FOR_REPO | This repo must not touch Senscope browser app code. |
| Senscope export contract drafting/checkers | GO_DOCS_ONLY | Drafting/checkers are allowed as Glyph-side docs/tools boundaries. |

## Allowed docs/tools work

Allowed work includes source-backed docs, fixtures, checkers, generated-config
prototype maintenance, behavior-case/evaluator tooling maintenance, generated
C++ review artifact maintenance, and roadmap/index updates.

Allowed work must not edit firmware runtime source, place generated files under
firmware/build paths, or claim hardware validation.

## Generated constants refactor gate

Generated constants firmware refactor work is
`BLOCKED_EXPLICIT_APPROVAL`. The generated-config prototype and generated C++
review artifact do not approve firmware source edits.

## Runtime-loaded config implementation gate

Runtime-loaded config interpreter/storage work is
`BLOCKED_EXPLICIT_APPROVAL`. The runtime-loaded config design and validation
contract remain design-only and not implemented.

## Device write / transport gate

Device write, serial transport, USB/configurator transport, and push-to-device
workflow implementation are `BLOCKED_SOURCE_AUTHORITY_AND_APPROVAL`.

## Hardware-validation gate

Hardware-validation claims require a separate hardware test plan, execution,
and result artifact. This index is not a hardware result.

## Nunchuk-validation gate

Nunchuk behavior remains preserved in the source-backed model but is not
hardware-validated here. Nunchuk hardware-validation claims are
`BLOCKED_HARDWARE`.

## Senscope export gate

Senscope export contract drafting and checkers are `GO_DOCS_ONLY` in this repo.
Senscope browser-app export implementation is `OUT_OF_SCOPE_FOR_REPO`.

## Required approvals

The following work requires explicit user approval before implementation:

- generated constants firmware refactor;
- runtime-loaded config interpreter/storage;
- device write / serial transport;
- new runtime behavior changes.

## Required preconditions before firmware source changes

- explicit user approval;
- source-backed implementation plan;
- current checkers passing;
- no forbidden artifacts;
- hardware test plan;
- rollback plan;
- no unsupported behavior claims.

## Required preconditions before runtime-loaded config implementation

- explicit user approval;
- storage/representation design;
- validator design;
- fallback policy;
- version migration policy;
- latency/performance measurement plan;
- hardware validation plan;
- source authority for any transport/storage assumptions.

## Required preconditions before device write/transport implementation

- explicit user approval;
- source authority for transport and storage behavior;
- write-path threat and rollback plan;
- validator boundary before any write;
- no push-to-device assumptions beyond source-backed support;
- no hardware-validation claim without hardware evidence.

## Checker ownership

`tools/check_glyph_preimplementation_go_nogo_index.py` owns the machine-readable
fixture checks and required caveat phrase checks for this index and the paired
readiness packets.

## Open blockers

- Explicit user approval for any firmware source change.
- Source-backed implementation plan for any generated constants refactor.
- Runtime-loaded config storage/representation design.
- Runtime-loaded config validator design.
- Runtime-loaded config fallback and migration policy.
- Source authority for any transport/storage assumptions.
- Hardware validation plan for any runtime behavior change.
- Nunchuk hardware validation evidence before nunchuk validation claims.
