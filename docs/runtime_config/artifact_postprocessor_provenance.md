# Artifact Postprocessor Provenance

Status: `observed_only_no_artifact_acceptance`.

This packet records only static facts visible in the current repository. The
CI workflow builds `firmware.uf2`, copies it to a short-SHA-named path such as
`glyph_mk6/Glyph-<short-sha>.uf2`, moves the tracked `glyph_nuker` executable
next to that file, invokes it on the UF2, and uploads the directory as the
`Glyph_FW` artifact. The workflow does not record a full candidate Git SHA,
final artifact SHA-256, or an immutable candidate/artifact-addressed locator.

The tracked `glyph_nuker` file is an x86-64 statically linked stripped ELF with
SHA-256
`8c488005c1ae7676518a0f8e048ff7d2fb51b71b743fdb785aeed3d8cf9f56ae`. This is
file identity evidence only. The repository does not establish its purpose,
the bytes it changes, whether it is reproducible, or whether it is safe to
use for hardware acceptance. Those fields remain `UNKNOWN`; this cycle does
not execute it or inspect a real pre/postprocessed UF2.

## Inert sidecar contract

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

The verifier is
`tools/check_glyph_artifact_postprocessor_provenance.py --check`. It hashes
only the tracked postprocessor for its recorded file identity and synthetic
fixture bytes in a temporary directory. It does not execute `glyph_nuker`,
read a firmware build output, publish or upload an artifact, select a durable
store, flash a device, or claim hardware acceptance. It rejects short or
changed identities, metadata/hash mismatches, and false immutable-locator
claims.

This packet does not create an artifact, sidecar for a real build, release,
CI integration, or candidate. The durable locator remains unresolved, so the
exact-snapshot hardware gate still requires a future externally preserved
candidate/artifact pair.
