# GP-BIND-002 active-runtime identity diagnosis

Status: `DIAGNOSIS_ONLY`; source-free; no repair authority.

## Scope and boundary

This record examines only immutable repository objects and the source-free
GP-BIND-002 failure record.  It did not inspect a controller, USB/serial
endpoint, Configurator, ProfileStore, local artifact custody, or terminal-held
hardware evidence.  It does not claim current device state or authorize a
source change, build, artifact, flash, recovery, retest, successor, or merge.

## Exact evidence set

| Object | Git object | SHA-256 of bytes |
| --- | --- | --- |
| Failure fixture at `cd0c805b805750182af7404f2b57c823494a95c4` | `0b11664416e7428ea30ba40f103841f57c6c7d88` | `ae9edf6e814478ad3da5ac6dd9945907832d8525ae1c2c3a820e73b49af19d41` |
| Hardware protocol V1 at `111e5780632283cec6a690610c140f9464292348` | `49c5ede3c070331fd04c90d60be225c5033efe2c` | `ba92ef30b1cfed98e2d8dde033c79b18bc7debcd0d1f5b1fbdf8ce9a20069c1c` |
| Hardware identity addendum V2 at `111e5780632283cec6a690610c140f9464292348` | `58a2409ead57e153737bcacbb024d9db8bacee37` | `1f14197ec4ad96e1fb0e0b4615d5e4b425fda066dea0ae590a240d716453d1aa` |
| Diagnosis-only Curator receipt at `fae53744ed1a1c0a085a571841c69577adc8ae8b` | `e4b545d19e800a4ff62dd2f42303cfafdbb53e32` | `cd5a41f142ab7e44fe7e0e2a1c6beff0beebc255d7da96e4f6a8dc40e37ff1f9` |

The fixed failed tuple remains candidate
`b3d60feb48d637efa8612515d2351a470fe9df0e`, tree
`3ab9366225591543da487f0b7d95c820614f70d4`, and UF2
`bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921` /
`988160` bytes.  This diagnosis does not alter that tuple.

## What the preserved record establishes

These are historical terminal/owner claims, not a live device read:

- H4a used a *verified V4 Profile 3* whose sole claimed X1 carrier was LT6;
  it activated X1 and leaked legacy Down+A.
- H1--H3 passed only for the failed tuple.  H4b, H4c, and H5 were not run.
- Recovery reported ordinary Profile 3 restored, Config byte-identical, store
  generation `172`, Profile 3 revision `5`, and transaction high-water
  `17293822569102712070`.

The recovery statement neither proves the pre-failure active profile nor makes
any assertion about present controller state.

## Result: H4 active runtime identity is unreconstructible

The preserved source-free evidence does **not** contain the following H4-time
values:

| Required runtime fact | Repository evidence result |
| --- | --- |
| Active backend / host | Unrecorded |
| Selected `GameModeConfig` index, ID, and decoded row | Unrecorded |
| Selected row's `ultimate_profile_id` | Unrecorded |
| ProfileStore active ID, activation status, and active revision | Unrecorded |
| H4-time raw Config bytes / hash and decoded Config | Unrecorded |
| Full H4 Profile 3 protobuf/decoded record, routing slots, roles, output program, and their hash | Unrecorded |
| Generated nanopb descriptor object or hash used by the exact Mk6 build | Unrecorded |

Accordingly, the fact that a stored Profile 3 record was verified does **not**
prove that Profile 3 was the runtime `_profile` during H4.  No repair may infer
an active routing map, output effect, or carrier-domain mapping from this gap.

## Source basis for the non-inference

The failed candidate's `set_mode` resolves a ProfileStore record only while
initializing the selected `GameModeConfig`: for an Ultimate row and compact
store, it calls `profile_store.Activate(mode_config.ultimate_profile_id, ...)`
and passes the result to `ultimate_mode.SetConfig`.  Therefore the selected
Config row and activation status are necessary facts.  The relevant candidate
source objects are:

| Path at candidate `b3d60feb…` | Git object | SHA-256 |
| --- | --- | --- |
| `src/core/mode_selection.cpp` | `cbae52f6ae93e7a16362c9e873dffa1744420616` | `857d2a147ae45908a13cdf7dc7f3892dfdfc9322f23d692156a1508b70bcb872` |
| `include/core/state.hpp` | `ff3aa94df61fd6a41448799fa1d6f508c41ecd0f` | `c46eb5347843ac4574dcffb28faeace608f029c27b94690c02ce06981cc4e6a3` |
| `include/modes/UltimateProfileEvaluator.hpp` | `2a416f86c4753c2f38c3619319e29321544b52a3` | `3ac311b07b9b4aa81454a7d27ef2d53864cac30a66c439b005ff327ed0fd03fb` |
| `src/modes/Ultimate.cpp` | `c7f2eab04f011c69058dbb7bfedbdd451dafef70` | `47e440a63489d207f8e56c0954bcccfd3ac7feb2e32d672e8a8dd4fd181dc3e9` |
| `schema/haybox/config.proto` | `6ed09823ddcde478cf9a082ed647576a0ec8425c` | `38646eed763a98ead43760eb9cc29ce0bab9fd73a956be057b44235bcc9fa232` |

The candidate source shows that `InputState.buttons` and named members such as
`lt6` share a union, and that both digital and analogue Ultimate paths mask
`inputs.buttons` before logical routing.  Those source facts motivate the
ongoing path diagnosis, but cannot reconstruct the absent H4-time active
configuration or prove a hardware cause.

## Protocol capture gap

V1 required the terminal agent, before update, to capture host/backend and
current selected profile/state, raw Config, ProfileStore status, every needed
profile/configuration record, and the exact alternate profile payload/readback.
It also required each row to record active profile/state and backend/host.  The
source-free result fixture summarizes the verified alternate record and outcome
but does not preserve those captures or their hashes.  This is an evidence
retention gap; it does not invalidate the reported H4 failure.

## Minimum bounded future evidence

Before any future hardware row, the terminal agent should retain immutable
copies and SHA-256s of: raw Config; decoded selected `GameModeConfig` index/ID
and `ultimate_profile_id`; backend/host identity; ProfileStore status and the
exact selected profile readback including revision; the prepared alternate
profile payload; and the exact generated nanopb descriptor/build manifest used
for the candidate.  A source-faithful host fixture must explicitly construct
that selected row and profile rather than equating a stored record with an
active runtime profile.

Definitive proof of the in-memory `ProfileStore::ActiveId()` / Ultimate
`_profile` pointer would require a separately authorized read-only runtime
diagnostic surface, because the preserved protocol/result lacks it and this
diagnosis does not add one.
