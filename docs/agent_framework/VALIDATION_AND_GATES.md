# Validation And Gates

Status label: CURRENT.

Every branch needs a behavior classification before merge recommendation.

## Classifications

`DOCS_CHECKER_ONLY`

- Docs, schemas, examples, or checkers only.
- Active firmware behavior unchanged.
- Firmware build not required unless build/source files were touched
  unexpectedly.
- Hardware not required.

`INACTIVE_GENERATOR_OR_FIXTURE`

- Generator, fixture, or inactive artifact work only.
- Active firmware behavior unchanged.
- Run relevant generator/checker tests.
- Hardware not required unless active behavior changes.

`FIRMWARE_SOURCE_NON_ACTIVE`

- Firmware source was touched, but active behavior is source-backed as
  unchanged.
- Build proof required.
- Hardware may be required if active behavior uncertainty remains.

`FIRMWARE_SOURCE_ACTIVE_BEHAVIOR`

- Active firmware behavior or active RuntimeConfigView selection changed.
- Build proof required.
- Hardware PASS required before merge.

`FORBIDDEN_OR_UNSAFE`

- Runtime-loaded config activation.
- Active `candidate.view` publication.
- Active `active_storage.view` publication.
- Generated active RuntimeConfigView wrapper publication.
- RuntimeConfigView replacement as customization mechanism.
- RAM-backed active table publication.
- WebSerial/device write.
- Protobuf binary write.
- Backend config.pb write.
- Persistent runtime-config storage.
- Flashing automation.
- Source-authority bypass.

Stop and report.

## Glyph Gates

- Active behavior changed -> build proof plus hardware PASS before merge.
- Docs/checker-only with active behavior unchanged -> hardware not required.
- Failed active-source branches are evidence only; do not present them as
  current work.
- No destructive Git commands: no reset, clean, stash, revert, or force-push
  unless explicitly approved.
- Artifact hashes are local observations only and not checker gates.
- Nunchuk remains NOT_TESTED unless the user explicitly reports a test.
- Root cause remains unproven unless direct evidence is found.
- Runtime-loaded config remains not implemented.

## Current Active Path Boundary

The only hardware-proven active path remains source-owned firmware behavior
through the existing active RuntimeConfigView path:

- `GetActiveRuntimeConfigState()`
- `ResolveActiveRuntimeConfig()`
- active publication remains `&kSourceOwnedCurrentBaselineRuntimeConfig`
- active RuntimeConfigView selection remains unchanged
