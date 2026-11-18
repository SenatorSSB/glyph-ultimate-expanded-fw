# Hardware evidence contract

## Purpose and scope

This current engineering contract defines artifact-custody and hardware-evidence
invariants. It does not itself authorize a device action or establish a candidate
PASS. Actual accepted results and their limits belong in
[hardware acceptance](../history/HARDWARE_ACCEPTANCE.md).

## Build proof versus hardware acceptance

Build proof establishes compilation from known source. Build proof is not
hardware acceptance. Physical acceptance requires the exact candidate Git SHA,
exact tested artifact SHA-256 and recorded human test scope.

A later source commit or later rebuild does not inherit PASS. Byte-identical
rebuilt bytes may establish the same artifact hash only after independent hashing;
matching bytes do not invent missing human observations. Different rebuild bytes
are a new artifact requiring new hardware evidence. Source similarity alone
cannot establish acceptance.

## Exact artifact custody

The current host-file tool is
[tools/glyph_hardware_artifact_custody.py](../../tools/glyph_hardware_artifact_custody.py).
The owner-held, content-addressed locator is:

```text
local_backups/hardware-artifacts/
  <candidate_git_sha>/
    <artifact_sha256>/
      firmware.uf2
```

Candidate identities are full 40-character lowercase hexadecimal Git commit SHAs;
artifact identities are full 64-character lowercase hexadecimal SHA-256 values.
The ignored local root holds bytes; evidence records identify those bytes.

From the clean committed candidate checkout after its build:

```bash
python3 tools/glyph_hardware_artifact_custody.py \
  --preserve .pio/build/glyph_mk6/firmware.uf2 \
  --candidate-sha <full-candidate-sha>
```

The command verifies candidate correspondence to checkout HEAD and clean tracked
inputs, hashes a stable regular source file, copies through a temporary file,
and installs without replacement. It makes the preserved file read-only,
reopens it and re-hashes the preserved bytes. Custody is write-once: identical
re-preservation verifies the existing file; occupied identities are never silently
replaced. Different bytes receive a different hash directory.

Preserve the tested UF2 before handoff; mutable build output is not durable custody.
Before every handoff or acceptance run, verify the recorded identity:

```bash
python3 tools/glyph_hardware_artifact_custody.py \
  --pre-handoff-verify \
  --candidate-sha <full-candidate-sha> \
  --artifact-sha256 <full-artifact-sha256>
```

Verification re-reads and re-hashes preserved bytes. Missing files, malformed
identities, symlinks, path escapes, non-regular files and hash mismatches fail
closed. The command performs no automatic device operation.

Retain artifacts supporting evidence as long as that evidence remains in project
history. Lost bytes remain unavailable; historical records do not recreate them.
The tool supplies no power-loss durability, reproducible-build guarantee,
external backup or automatic cloud retention.

## Hardware evidence

A hardware acceptance record must identify at minimum:

- Exact candidate Git SHA.
- Exact tested artifact SHA-256 and preserved locator/readback verification.
- Test context needed for the claim, such as controller, host, profile, protocol,
  preconditions and relevant reconnect or power-cycle scope.
- Human observations and results, with expected and observed behavior.
- Gaps, anomalies, recovery and retest needs where relevant.

Use PASS, FAIL, PARTIAL or INCONCLUSIVE for executed scope. NOT_TESTED is not FAIL;
N/A is not PASS. A build cannot substitute for human physical execution.
Physical observations must never be fabricated. Incomplete or mismatched evidence
cannot establish complete acceptance. Historical records missing exact identities
cannot supply acceptance for a new candidate or rebuild.

## Device-operation boundary

Preservation and verification are host-file operations. Flashing, firmware updates
and controller writes are separate device actions. This document supplies no
flashing or device-write authority. Specific device actions require explicit user
authorization; documentation and build permission do not supply that authority.

## Privacy and publication

Raw controller captures and private receipts may remain owner-private. Sanitized
public evidence may record bounded reviewed conclusions. Public claims cannot
exceed the public evidence record. Do not publish private locators merely for
completeness. A generic custody template is not a private receipt location.

## Historical provenance

This contract extracts durable engineering content from the original framework
records at commit `367785cfe02d883c185327cfface06c37307f2b3`:

```text
docs/agent_framework/HARDWARE_ARTIFACT_CUSTODY.md
d2e9ce8f2f7e0e7efa7f68a9af7f51c3261c0d59

docs/agent_framework/HARDWARE_EVIDENCE.md
9846a17d13929f4ad53e12fdc882be5dfcfd22e4
```

The originals retain campaign and agent lifecycle history and remain untouched.
This public contract supersedes them only as the CURRENT product-engineering
dependency. It does not authorize deletion of the historical records.

## Machine-readable invariants

The closed structured contract below protects safety semantics while allowing
editorial improvements to the prose.

<!-- hardware-evidence-contract-v1:start -->
```json
{
  "schema_name": "glyph_public_hardware_evidence_contract",
  "schema_version": 1,
  "contract_id": "GLYPH_PUBLIC_HARDWARE_EVIDENCE_V1",
  "custody": {
    "locator_template": "local_backups/hardware-artifacts/<candidate_git_sha>/<artifact_sha256>/firmware.uf2",
    "write_once": true,
    "pre_handoff_rehash_required": true,
    "reject_symlink_or_nonregular": true,
    "different_rebuild_bytes_are_new_artifact": true
  },
  "acceptance": {
    "build_is_hardware_acceptance": false,
    "requires_exact_candidate_git_sha": true,
    "requires_exact_artifact_sha256": true,
    "requires_human_observed_scope": true,
    "acceptance_transfers_to_rebuild": false,
    "results": [
      "PASS",
      "FAIL",
      "PARTIAL",
      "INCONCLUSIVE"
    ]
  },
  "device_operation": {
    "document_authorizes_flashing": false,
    "document_authorizes_device_write": false,
    "specific_user_authorization_required": true
  },
  "privacy": {
    "raw_private_evidence_may_remain_private": true,
    "public_claims_bounded_by_public_record": true
  },
  "provenance": {
    "extracted_from_commit": "367785cfe02d883c185327cfface06c37307f2b3",
    "historical_sources": [
      {
        "path": "docs/agent_framework/HARDWARE_ARTIFACT_CUSTODY.md",
        "blob": "d2e9ce8f2f7e0e7efa7f68a9af7f51c3261c0d59"
      },
      {
        "path": "docs/agent_framework/HARDWARE_EVIDENCE.md",
        "blob": "9846a17d13929f4ad53e12fdc882be5dfcfd22e4"
      }
    ]
  }
}
```
<!-- hardware-evidence-contract-v1:end -->
