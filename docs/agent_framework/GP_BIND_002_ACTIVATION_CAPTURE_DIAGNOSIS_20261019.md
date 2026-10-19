# GP-BIND-002 activation-capture diagnosis

Status: `DIAGNOSIS_ONLY`; source-free record of terminal-supplied read-only
evidence.  No repair authority.

## Scope

This record binds the terminal result returned after
`GP_BIND_002_ACTIVATION_OBSERVATION_DIAGNOSTIC_V1`.  It records no local
device operation: the terminal result was supplied to the chapter daemon.
It does not authorize a profile mutation, recovery, reset, flash, firmware
edit, build, candidate, hardware row, acceptance, or merge.

The fixed failed tuple remains GP-BIND-002 candidate
`b3d60feb48d637efa8612515d2351a470fe9df0e`, tree
`3ab9366225591543da487f0b7d95c820614f70d4`, and UF2
`bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921`
(`988160` bytes).  H4a remains `FAIL`; H1--H3 do not transfer and H4b,
H4c, and H5 remain `NOT_RUN`.

## Immutable terminal observation

The returned read-only packet has SHA-256
`9d9c959130edaec5b14d8a827d9fa7bf122d3d139d927e30b67a55db121fe51a`.
The terminal reported the following without a Config write, ProfileStore
mutation, firmware change, build, flash, or physical controller test:

| Observation | Result |
| --- | --- |
| Endpoint continuity | It re-enumerated from `usbmodem1102` to `usbmodem1101` before opening; the packet used `usbmodem1101`. This is historical terminal evidence, not a current endpoint claim. |
| ProfileStore STATUS | Healthy; generation `172`; token high-water `17293822569102712070`. |
| Decoded XInput default row | The observed stored default selected an Ultimate row referencing Profile 4, not Profile 3. |
| Selected-profile readback | Profile 4 read successfully at revision `1`. |
| Alternate payload | The prepared LT6-carrier V4 Profile 3 payload was retained but was not the profile referenced by that inspected XInput default row. |

This proves only the observable stored configuration at capture time.  It
does not prove the historic H4a runtime selection, a present `ActiveId`, or
the Ultimate instance's `_profile` pointer.  In particular, “Profile 3 was
not selected by the observed XInput default row” is not equivalent to
“Profile 3 was unloaded from runtime memory.”

## Source-grounded activation semantics

At the failed candidate, `set_mode(CommunicationBackend *, GameModeConfig &,
Config &)` selects an Ultimate `GameModeConfig` and calls
`profile_store.Activate(mode_config.ultimate_profile_id, &status)`, then
passes that returned profile pointer into `ultimate_mode.SetConfig`.
`Ultimate::SetConfig` stores the pointer in `_profile`.  `ProfileStore::Activate`
copies the selected record into `_active_profile` and tracks `_active_id` and
`_active_revision`.

Consequently, a stored record readback is not itself an active-runtime
attestation.  A selected row provides an observable intended activation
input; it cannot prove when, whether, or with what status activation happened
for a particular backend/Ultimate instance.

Source references at candidate `b3d60feb48d637efa8612515d2351a470fe9df0e`:

- `src/core/mode_selection.cpp`: selected-row `ProfileStore::Activate` and
  `ultimate_mode.SetConfig` path;
- `HAL/pico/src/core/ProfileStore.cpp`: `Activate`, `ActiveProfile`, and
  `ActiveId` implementation;
- `include/core/ProfileStore.hpp`: in-process `ActiveId`/`ActiveProfile`
  declarations and active state fields;
- `src/modes/Ultimate.cpp`: `_profile` storage and the digital/analogue
  carrier-consumption path.

The approved production ProfileStore tool exposes only `status`, `list`,
`read`, `create`, and `update`; the read-only actions do not expose
`ProfileStore::ActiveId`, `_active_revision`, backend-local selection, or the
Ultimate `_profile` pointer.  The serial Config route supplies stored Config
bytes, not an active Ultimate instance.  Therefore the exact current approved
read-only API result is:

`ACTIVE_RUNTIME_IDENTITY_UNAVAILABLE_WITH_CURRENT_APPROVED_READ_ONLY_SURFACES`.

## Why the existing host proof was a false pass

The GP-BIND-002 host carrier test directly constructed/selected the profile
under test and drove the evaluator with that constructed profile.  It did not
construct the exact observed XInput default `GameModeConfig` row, invoke the
mode-selection/`ProfileStore::Activate` boundary, and bind the resulting
selected profile to the Ultimate instance.  It therefore proved carrier
consumption inside the evaluator path, but not that the same profile was
selected at a controller H4 row.  That omitted activation-state boundary is
the exact fixture gap; it does not establish a new firmware defect.

## Smallest allowed host-fixture improvement

The smallest source-faithful fixture is host-only and must:

1. build a compact-store Config with the actual selected Ultimate
   `GameModeConfig` row and a distinct stored Profile 3 / Profile 4 pair;
2. invoke the same `set_mode`/`ProfileStore::Activate` selection boundary;
3. assert the selected profile ID and revision as observed by in-process test
   hooks, then exercise the resulting Ultimate instance; and
4. demonstrate that Profile 3 carrier consumption cannot be attributed to a
   Profile 4 selection, without adding a runtime protocol or changing
   production APIs.

This fixture is diagnosis/validation design only.  It requires separate
Curator work-order authority before implementation because it changes test
coverage and may expose a concrete repair boundary.

## Deliberately deferred live attestation

An on-device query of `ProfileStore::ActiveId`, active revision, selected
backend row, or Ultimate `_profile` would require a new read-only runtime
diagnostic surface.  That is outside the existing approved read-only
Config/ProfileStore routes and is not implemented or authorized by this
record.  No conclusion about a live runtime identity may be inferred until
such a separately authorized interface exists and is independently reviewed.

## Next permissible action

Use this record only for source-faithful diagnosis and adversarial review.
Any test implementation, production repair, ProfileStore/runtime diagnostic
surface, build, candidate, or H4 execution needs its own completed authority.
