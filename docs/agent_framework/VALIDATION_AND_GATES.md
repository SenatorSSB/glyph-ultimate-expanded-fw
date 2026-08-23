# Validation And Gates

Status label: CURRENT.

Every branch needs a behavior classification before merge recommendation.
The supervisor must execute the required branch, validation, commit, push, and
merge operations when they are in scope; it must not stop at reporting the
commands.

Work orders also receive behavioral-effect risk `H0`, `H1`, `H2`, or `H3` as
defined in `WORK_ORDER_TEMPLATE.md`. Branch classification and hardware risk
are complementary: risk follows actual effect, not file location.

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

- Fresh live-remote truth -> attempt ordinary/default read-only verification;
  if restricted-sandbox DNS/network access fails, treat it as inconclusive and
  retry through the permitted network-enabled/escalated path. Do not infer auth
  failure, mutate credentials, request re-login, accept stale tracking refs, or
  return `BLOCKED_EXTERNAL` until all permitted network-capable retries fail or
  are unavailable.
- Active behavior changed -> build proof plus hardware PASS before merge.
- H2/H3 -> automated validation, canonical build, fresh independent review,
  exact candidate publication, full Git SHA plus exact artifact SHA-256, and
  physical controller PASS before merge.
- A successful build proves build integrity only. It never proves controller
  acceptance.
- Relevant source change or a different rebuild invalidates affected hardware
  evidence unless the exact tested artifact bytes and snapshot remain the
  candidate being published.
- Failed candidate source must not enter `configurator`; a result/evidence
  branch is not source authority.
- Docs/checker-only with active behavior unchanged -> hardware not required.
- Failed active-source branches are evidence only; do not present them as
  current work.
- No destructive Git commands: no reset, clean, stash, revert, or force-push
  unless explicitly approved.
- Artifact hashes need not be rebuild-stable, but the exact hash is mandatory
  evidence identity for H2/H3 testing. Checkers enforce recorded identity and
  locator invariants; they do not require a separate rebuild to reproduce the
  digest.
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
