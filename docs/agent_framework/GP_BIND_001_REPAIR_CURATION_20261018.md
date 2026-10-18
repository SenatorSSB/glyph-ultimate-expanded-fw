# GP-BIND-001 hardware-failure curation packet

Status: `CURATION_REQUIRED` / `REPAIR_REQUIRED`. This is a source-free,
non-authorizing curation packet. It does not create a READY work order, permit
firmware edits, rebuilds, flashing, merging, device access, or a hardware retest.

## Immutable failed input

- Failed candidate: `32c1bd81910ec5bcea0104fe98b9b37fb267d071`
- Candidate tree: `a9d2fb6dbde1c3853121e111ed2b5025d0280855`
- Direct parent: `ec384b6139e821358fcb919efcc678ce940222dc`
- Adopted authority base: `83bd38ab7e7946562a6e952171d85acbfed7339b`
- Exact failed UF2: 986624 bytes, SHA-256
  `ea261256dc57a0974d4f23b232e8bd43d5cf50d7094661a4c0531f92aad9d1ed`
- Protocol: `GP_BIND_001_HW_V1`
- Failure evidence: `repo-json:docs/calibration/fixtures/gp_bind_001_hardware_failure_2026-10-18.json`

H1 ordinary LT5/X1, H2 Mode+LT5, and H3 required conflicts passed only for this
failed candidate/artifact pair. H4 failed: LT6 activated X1 but legacy forced
Down+A also occurred. H5 was not run. Profile 3 was deterministically restored
to the preserved ordinary payload, but that recovery is not H5 PASS and does
not transfer acceptance to any source or artifact.

## Curation case and proposed work-order identity

- Curation case: `GP-BIND-001-REPAIR-20261018`
- Proposed, non-authorizing repair work-order ID: `GP-BIND-002`
- Required disposition before any implementation: an independent post-opening
  Curator receipt covering the exact failed candidate and this pending failure
  event. The earlier GP-BIND-001 READY receipt predates the failure and cannot
  resolve it.

## Owner-authorized bounded repair contract for Curator adjudication

Any later READY repair must be limited to all of the following:

1. Add an explicit, unambiguous generic function-carrier ownership
   representation.
2. Evaluate function activation from the original physical remap/SOCD snapshot.
3. Consume a claimed carrier from every legacy digital and analogue
   interpretation.
4. Preserve legacy behavior for every unclaimed carrier.
5. Preserve V1-V3, ordinary/default LT5 X1, Mode+LT5, and the established X1
   conflict behavior.
6. Prove alternate LT6 X1 and Mode+LT6 have no Down, A, or Down+A leakage.
7. Prove LT6 retains legacy Down+A when LT5, rather than LT6, is the X1 carrier.
8. Do not migrate any other function family or redesign Stage or ProfileStore.

## Required evidence before a later hardware handoff

A repair candidate must receive new, candidate-specific proof. At minimum the
Curator must require focused host/fixture coverage for original-snapshot
activation, digital and analogue carrier consumption, unclaimed legacy
behavior, V1-V3 invariance, LT5 X1/Mode+LT5/conflict preservation, alternate
LT6 X1/Mode+LT6 no-leakage, and LT5-carrier LT6 legacy Down+A retention. It
must also require exact candidate/source review, canonical Mk6 build and exact
artifact custody, then complete candidate-specific `GP_BIND_001_HW_V1`
acceptance. The H1-H3 observations above are retained failure evidence and may
not satisfy any repair candidate row.

## Next permissible action

An independent Curator may review this post-opening packet and either decline
the repair or publish a bounded new READY work order with its immutable receipt.
Until then the only current action is curation; implementation, build, flash,
merge, device access, and hardware retest remain unauthorized.
