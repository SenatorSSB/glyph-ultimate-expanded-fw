# GP-BIND-002 hardware-failure repair curation packet

Status: `CURATION_REQUIRED`; non-authorizing repair obligation.

## Exact failed tuple

- Work order: `GP-BIND-002`
- Candidate/ref: `codex/gp-bind-002-carrier-ownership-final-failclosed` /
  `b3d60feb48d637efa8612515d2351a470fe9df0e`
- Tree: `3ab9366225591543da487f0b7d95c820614f70d4`
- Candidate direct parent: `b4ca04d1914c96e2a65e21c1e68099ff5cbef1bb`
- Candidate base: `897356709ea4425eeac0631ca77e44dc68ce780f`
- UF2: `bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921`,
  `988160` bytes
- Controlling corrected identity protocol:
  `GP_BIND_002_HW_V2`, with `GP_BIND_002_HW_V1` otherwise unchanged
- Source-free evidence:
  `repo-json:docs/calibration/fixtures/gp_bind_002_hardware_failure_2026-10-19.json`
- Owner-supplied terminal evidence digest:
  `f44d5f7fd160ecbf95bb98e62f6a8423adca494cf243239c10b5f7685aa961fa`

## Exact result and preserved recovery

H1, H2, and H3 PASS only for the failed exact tuple. H4a FAIL: verified V4
Profile 3 with LT6 as X1 carrier activated X1 while legacy Down+A leaked. H4b,
H4c, and H5 are `NOT_RUN` under the protocol stop rule. No source change,
rebuild, flash, or merge followed the failure.

Deterministic Profile 3 recovery completed without uncertainty. Its payload
equals the ordinary backup and Config bytes are byte-identical; the honest
post-state is generation 172, Profile 3 revision 5, and high-water
`17293822569102712070`. This is ordinary-state restoration only, not H5 PASS
and not transferable acceptance.

## Required Curator question

Determine whether the direct hardware finding supports one further bounded,
generic repair for the post-snapshot carrier-consumption path. Do not authorize
implementation merely by this packet.

Any future proposal must remain inside all of these boundaries:

1. Trace the generic claimed-carrier path after function activation through
   every relevant legacy digital and analogue interpretation; identify the
   exact remaining consumption gap from source.
2. Retain activation from the original physical remap/SOCD snapshot.
3. Ensure the one explicit, valid claimed carrier is consumed generically,
   without LT6 special casing; unclaimed controls must retain legacy behavior.
4. Preserve V1-V3, default LT5 X1, Mode+LT5, and accepted conflict behavior.
5. Require fresh tests for alternate LT6 X1 and Mode+LT6 without Down, A, or
   Down+A leakage, and for unclaimed LT6 legacy Down+A retention. Require both
   digital and analogue coverage, Stage-C/ProfileStore regression, both ABI
   layouts, and negative ownership validation.
6. Do not migrate another function family or redesign Stage A/B/C, ProfileStore,
   persistence, schema/product behavior, device writes, flashing, RT2, or
   hardware protocol scope.

The prior GP-BIND-001 failure, GP-BIND-002 authorization, implementation,
reviews, protocol, artifact custody, and this failure record remain immutable
historical evidence. No prior H1-H3 or recovery result transfers to a future
candidate. A future source candidate needs fresh Curator authority, source
review, validation, build, unique custody, final handoff review, and a wholly
fresh hardware sequence before any merge.
