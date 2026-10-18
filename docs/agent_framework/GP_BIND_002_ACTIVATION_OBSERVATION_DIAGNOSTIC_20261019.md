# GP-BIND-002 activation-observation diagnostic

Protocol version: `GP_BIND_002_ACTIVATION_OBSERVATION_DIAGNOSTIC_V1`  
Status: `READ_ONLY_DIAGNOSTIC_ONLY`; source-free terminal-agent packet.

## Purpose and authority

The reviewed diagnosis at
`dab2b29f515142d022cf240cf6a87a8afd56f26e` establishes that the exact
GP-BIND-002 H4a failure is preserved, but the H4a-time selected runtime
profile is not reconstructible from the retained record.  This bounded packet
authorizes a terminal agent to capture the missing **observable** activation
facts before any future H4 row.  It neither changes the failed result nor
explains its cause.

It is authorized by the post-opening Curator resolution receipt
`docs/agent_framework/curation_receipts/gp_bind_002_activation_observation_20261019.json`.
The fixed failed tuple remains:

| Field | Value |
| --- | --- |
| Candidate | `b3d60feb48d637efa8612515d2351a470fe9df0e` |
| Tree | `3ab9366225591543da487f0b7d95c820614f70d4` |
| UF2 SHA-256 | `bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921` |
| UF2 bytes | `988160` |
| Failure | H4a LT6 activated X1 while legacy Down+A leaked |

H1--H3 remain PASS only for that failed tuple. H4b, H4c, and H5 remain
`NOT_RUN`. The historical Profile 3 recovery is recovery only, not
acceptance.

## Terminal-agent capture scope

The terminal agent may use the already approved **read-only** Config and
ProfileStore routes to create immutable local copies and SHA-256 digests.  It
must capture all of the following immediately before any future H4 profile
mutation or physical H4 action:

1. The raw current Config blob, byte size, SHA-256, and its decoding method.
2. The observable active backend and host context, including how each was
   observed and any value that is unavailable.
3. The selected `GameModeConfig` index and ID, the complete decoded selected
   row, and that row's decoded `ultimate_profile_id`.
4. ProfileStore `STATUS`, including store incarnation, generation, and token
   high-water as returned by the read-only operation.
5. Readback of the selected profile referenced by the decoded selected row:
   profile ID, revision, full immutable payload, byte size, and SHA-256.
6. The prepared alternate V4 payload before it is ever loaded: intended
   profile ID, full immutable payload, byte size, SHA-256, and a comparison
   against its readback **only when a later separately authorized operation
   performs that readback**.
7. The exact files, command/tool version identities, timestamps, and SHA-256
   digests needed to bind the above observations together without recording
   credentials or unnecessary personal device identifiers.

The returned evidence must state separately whether an actual
`ProfileStore::ActiveId()` or Ultimate in-memory `_profile` pointer is exposed
by an existing approved read-only surface. If no such surface exists, record
`UNAVAILABLE_WITH_CURRENT_APPROVED_READ_ONLY_SURFACES`; do not infer it from a
stored record, a selected row, or a prior readback.

## Explicit prohibitions

This packet authorizes **no**:

- Config write, ProfileStore create/update/mutation, recovery/restore, reset,
  re-enumeration intended to change state, or retry after an uncertain result;
- firmware source edit, repair candidate, work-order allocation, source review,
  build, artifact production/custody, UF2 installation, flash, or merge;
- H1--H5 physical acceptance action, PASS/FAIL classification, or acceptance
  transfer; or
- X2, Y1, Y2, Tilt, Stage A/B/C, ProfileStore/persistence, schema/product,
  game-semantic, macro/timing, RT2, factory-recovery, Nunchuk, or Senscope
  scope.

The owner performs no physical controller action for this diagnostic. If a
required fact is not observable through the approved read-only surfaces, stop
and return that absence with the exact capture files; do not invent a runtime
diagnostic, mutate state, or widen the scope.

## Outcome and next boundary

This diagnostic supplies retained observational evidence only. It does not
authorize a repair or any future H4 execution. A future source repair remains
subject to a separate source-grounded Curator decision and a new exact
candidate/build/custody/review/hardware lifecycle.
