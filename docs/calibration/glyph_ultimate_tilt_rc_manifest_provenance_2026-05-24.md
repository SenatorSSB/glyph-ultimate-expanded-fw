# Glyph Ultimate Tilt RC Manifest Provenance Semantics (2026-05-24)

## Scope

This note defines provenance semantics for:

- `tools/write_glyph_ultimate_tilt_rc_manifest.py`
- `tools/check_glyph_ultimate_tilt_rc_manifest.py`
- `docs/calibration/glyph_ultimate_tilt_rc_manifest.md`

It does not change runtime firmware behavior, flashing behavior, SOCD behavior, remapping semantics, or profile/schema behavior.

## Why The Manifest Cannot Self-Reference Its Final Commit SHA

The manifest file is generated from the current worktree state before the manifest commit exists.  
If the manifest tried to contain the SHA of the commit that introduces the manifest itself, writing that SHA would change the manifest content and therefore change the commit SHA again. That becomes a self-referential amend loop.

For this reason, provenance records:

- `firmware_source_commit_sha`: the current `HEAD` commit used as the firmware source baseline at generation time
- `manifest_generated_from_branch`: the branch where generation ran

## Provenance Identity Layers

These fields represent different evidence types and must not be conflated:

- Firmware source commit:
  - The commit whose source tree the firmware candidate came from (`firmware_source_commit_sha`).
- Manifest commit:
  - The later commit that stores the generated manifest markdown file.
- Artifact checksum:
  - SHA-256 of candidate build artifacts (`artifact_N_sha256` fields).
- Hardware test result:
  - Human-recorded manual device test evidence in the hardware result file (still not claimed until manual testing happens).

## Dirty State Semantics

The manifest records full worktree state and split classifications:

- `git_dirty_state`
- `firmware_relevant_dirty_state`
- `firmware_relevant_dirty_entries`
- `non_firmware_dirty_entries`
- `git_status_short`

`git_dirty_state` reports overall repository dirtiness.  
`firmware_relevant_dirty_state` only reports dirty entries that touch firmware-relevant paths:

- `src/`
- `include/`
- `HAL/`
- `config/`
- `platformio.ini`
- build scripts
- proto/schema/configurator/backend/persistence paths

Docs/tools-only changes remain visible in `git_status_short` and `non_firmware_dirty_entries`, but are not firmware-relevant by themselves.

## Required Clean State Before Manual Flash

Before manual hardware use, require all of the following:

- `firmware_relevant_dirty_state: CLEAN`
- build succeeds and artifact identity is recorded
- artifact checksum(s) are recorded and stable for the candidate build
- hardware result is still treated as `NOT_TESTED` until a real manual test result file is produced

`git_dirty_state` may be `DIRTY` when only docs/tools are in-flight, but firmware-relevant paths must be clean before manual flash approval.
