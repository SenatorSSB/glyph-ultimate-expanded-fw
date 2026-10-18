# GP-BIND-002 hardware protocol identity addendum

Protocol version: `GP_BIND_002_HW_V2`
Status: `HARDWARE_TEST_REQUIRED`; source-free terminal-agent packet only.

## Purpose and immutable scope

This is an additive, immutable correction to
`docs/agent_framework/GP_BIND_002_HARDWARE_PROTOCOL.md` version
`GP_BIND_002_HW_V1` at commit
`2e14784412f0d26f3ea05e30017db889f680a9da`.

The V1 packet remains preserved historical governance evidence.  It is not
edited, removed, rewritten, or reinterpreted.  This V2 addendum supersedes V1
only for its erroneous **candidate branch identity**.  Every other V1
requirement remains normative and unchanged, including the exact candidate
SHA/tree/parent/base and UF2 custody tuple, ordinary-state backup and recovery
route, one-action-at-a-time terminal-agent/owner boundary, complete H1 through
H5 acceptance sequence, stop conditions, and evidence/HEP/no-merge gates.

No firmware source, build input, candidate object, artifact byte, custody
identity, controller state, ProfileStore state, Configurator state, physical
observation, work-order scope, or acceptance result changes in this addendum.
It authorizes no update, flash, rebuild, source edit, merge, or transfer of
any prior candidate's acceptance.

## Corrected candidate ref binding

The exact GP-BIND-002 candidate is bound to this live remote ref:

| Field | Exact value |
| --- | --- |
| Candidate branch/ref | `codex/gp-bind-002-carrier-ownership-final-failclosed` |
| Candidate Git SHA | `b3d60feb48d637efa8612515d2351a470fe9df0e` |
| Candidate tree | `3ab9366225591543da487f0b7d95c820614f70d4` |
| Candidate direct parent | `b4ca04d1914c96e2a65e21c1e68099ff5cbef1bb` |
| Canonical base | `897356709ea4425eeac0631ca77e44dc68ce780f` |
| Preserved UF2 SHA-256 | `bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921` |
| Preserved UF2 byte size | `988160` |
| Preserved UF2 locator | `local_backups/hardware-artifacts/b3d60feb48d637efa8612515d2351a470fe9df0e/bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921/firmware.uf2` |

The V1 spelling `codex/gp-bind-002-carrier-ownership` is not an acceptable
hardware candidate ref for this packet.  It identifies a different remote
head and must not be substituted, inferred equivalent, or used as a fallback.

## Mandatory corrected preflight

Before any device operation, the terminal agent must perform V1's full
preflight and additionally establish all of the following from a fresh live
remote read:

1. `origin/codex/gp-bind-002-carrier-ownership-final-failclosed` resolves
   exactly to `b3d60feb48d637efa8612515d2351a470fe9df0e`.
2. The resolved commit tree is exactly
   `3ab9366225591543da487f0b7d95c820614f70d4` and its sole direct parent is
   exactly `b4ca04d1914c96e2a65e21c1e68099ff5cbef1bb`.
3. The candidate descends from the stated canonical base
   `897356709ea4425eeac0631ca77e44dc68ce780f`.
4. The local checked-out candidate, reviewed source, Mk6 build provenance,
   regular-file custody artifact, exact UF2 byte count, and SHA-256 all bind
   to that same candidate SHA.

Any failed, missing, stale, ambiguous, different-ref, tree, parent, base,
source, custody, size, or hash result is an identity failure.  Stop before
update, recovery mutation, physical test, result inference, rebuild, or
merge.  Do not fall back to the V1 branch spelling or any local branch name.

## Controlling protocol statement

For hardware execution, read this addendum together with V1.  In a conflict,
this addendum controls only the candidate branch/ref and the corresponding
preflight requirement above.  V1 controls all remaining requirements,
including its H1, H2, H3, H4a, H4b, H4c, and H5 rows unchanged.

The terminal agent must report both protocol identities in the evidence packet:
V1 `GP_BIND_002_HW_V1` and this corrected addendum `GP_BIND_002_HW_V2`, plus
the exact live corrected ref resolution.  Independent HEP must reject any
evidence that cannot prove this exact corrected ref-to-candidate binding.
