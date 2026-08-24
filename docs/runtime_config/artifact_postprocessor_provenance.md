# Artifact Postprocessor Provenance

Status: `observed_only_no_artifact_acceptance`.

This packet records only static facts visible in the current repository. The
CI workflow builds `firmware.uf2`, copies it to a short-SHA-named path such as
`glyph_mk6/Glyph-<short-sha>.uf2`, moves the tracked `glyph_nuker` executable
next to that file, invokes it on the UF2, and uploads the directory as the
`Glyph_FW` artifact. Before the bounded observed-only sidecar integration, the
workflow did not record a full candidate Git SHA, final artifact SHA-256, or an
immutable candidate/artifact-addressed locator. The current sidecar records the
first two for observed correspondence; it still does not establish the third.

The tracked `glyph_nuker` file is an x86-64 statically linked stripped ELF with
SHA-256
`8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae`. This is
file identity evidence only. The repository does not establish its purpose,
the bytes it changes, whether it is reproducible, or whether it is safe to
use for hardware acceptance. Those fields remain `UNKNOWN`; this cycle does
not execute it or inspect a real pre/postprocessed UF2.

## Observed-only sidecar contract

`docs/runtime_config/fixtures/artifact_postprocessor_provenance.json` defines
the synthetic-only sidecar shape. A complete record carries:

- the full 40-character candidate Git SHA;
- final artifact filename, size, and SHA-256;
- tracked postprocessor path and SHA-256;
- `purpose: UNKNOWN` and `byte_transformation: UNKNOWN`;
- `observed_only` source classification; and
- `immutable_locator: null` until an approved durable store exists.

The synthetic sidecar pins its candidate Git SHA to the observed live
`configurator` snapshot `7688ee287491ff05898038045f5c1918be09f675`; this is a
source-observation identity, not a firmware candidate or hardware acceptance
record.

The synthetic verifier is
`tools/check_glyph_artifact_postprocessor_provenance.py --check`. The same
tool's CI-only `--verify-checkout` mode requires full lowercase `GITHUB_SHA` to
equal checked-out `git rev-parse HEAD` and verifies the tracked postprocessor
hash before the existing workflow step. After that step, `--write-sidecar`
and `--verify-sidecar` bind the final UF2's filename, size, and SHA-256 to the
same source identity and observed-only fields before upload. The static
ordering checker is
`tools/check_glyph_artifact_postprocessor_workflow.py`.

These commands do not execute `glyph_nuker` in tests, select a durable store,
flash a device, or claim hardware acceptance. The workflow sidecar is
correspondence metadata only; it does not establish artifact acceptance,
reproducibility, postprocessor purpose/effect, retention, or an immutable
locator.

This packet does not create a real build artifact or release in repository
tests. The bounded `build.yml` CI integration emits the sidecar during a real
workflow run, but the durable locator remains unresolved, so the exact-
snapshot hardware gate still requires a future externally preserved
candidate/artifact pair.
