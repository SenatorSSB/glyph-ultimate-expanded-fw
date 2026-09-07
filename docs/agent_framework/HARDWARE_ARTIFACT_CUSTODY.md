# Local Hardware Artifact Custody

Status label: CURRENT.

Contract version: `GLYPH_HARDWARE_ARTIFACT_CUSTODY_V1`.

This is the approved Revision-2 custody contract for exact H2/H3 Glyph
firmware candidates. It implements user direction `GLYPH-UD-015` without an
external service, upload, release, device write, or flashing automation.

## Identity And Locator

The custodian is `Glyph project owner / user authority`. The canonical
owner-held root and exact locator are:

```text
local_backups/hardware-artifacts/
  <full-candidate-git-sha>/
    <full-artifact-sha256>/
      firmware.uf2
```

Both identities use lowercase full-length hexadecimal. The candidate identity
is a 40-character Git commit SHA and the artifact identity is the SHA-256 of
the exact preserved UF2 bytes. `local_backups/` remains ignored by Git: the
repository records the identity and locator, while the owner holds the bytes.

## Preserve And Verify

From an exact clean committed candidate after its canonical build:

```bash
python3 tools/glyph_hardware_artifact_custody.py \
  --preserve .pio/build/glyph_mk6/firmware.uf2 \
  --candidate-sha <full-candidate-git-sha>
```

The command requires a clean checkout whose `HEAD` is the candidate commit,
hashes a stable regular source file, copies through a temporary file, installs
the artifact without replacement, makes it read-only, then reopens and
re-hashes the preserved bytes. Its output supplies the queue/evidence locator
and SHA-256.

Before every hardware handoff or acceptance run, use the evidence-recorded
identity, not mutable build output:

```bash
python3 tools/glyph_hardware_artifact_custody.py \
  --pre-handoff-verify \
  --candidate-sha <full-candidate-git-sha> \
  --artifact-sha256 <full-artifact-sha256>
```

The command fails on a missing artifact, malformed identity, symlinked custody
path, non-regular file, or byte/hash mismatch. Physical update remains a manual
user action outside this tooling.

## Write Once, Retention, And Loss

Once installed at a candidate/artifact identity, those bytes are immutable.
The tool never overwrites that path. Re-preserving identical bytes is an
idempotent readback verification; different bytes receive a different
artifact-SHA directory.

Retain every artifact supporting accepted, current, or historical H2/H3
evidence for as long as that evidence remains in project history. There is no
automatic garbage collection or destructive cleanup policy. An independent
filesystem/system backup is operationally recommended, but is not required
and no cloud provider or external store is selected.

If required bytes are lost, keep their historical evidence record as
historical information and mark the artifact unavailable when relevant. A
later rebuild inherits nothing: it may substitute only when its bytes
independently hash exactly to the recorded artifact SHA-256. Different bytes
are a new artifact and require new hardware evidence.

## Boundaries

This contract does not establish deterministic/reproducible firmware builds,
disk or power-loss safety, public releases, GitHub Releases, CI retention,
automatic uploads, credentials, external object storage, firmware flashing,
device writes, or controller acceptance. It complements existing artifact
provenance sidecars; it does not change their historical observed-only claims.

The synthetic checker is:

```bash
python3 tools/check_glyph_hardware_artifact_custody.py
```

It covers exact path derivation, readback/hash equality, wrong candidate and
artifact identities, immutable re-preservation, missing and mutated artifacts,
malformed identifiers, symlink/path escape attempts, and a same-candidate
rebuild with different bytes receiving a new identity. It operates only in a
temporary directory and neither creates nor reads a real firmware artifact.
