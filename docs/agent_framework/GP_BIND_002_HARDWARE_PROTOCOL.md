# GP-BIND-002 carrier-ownership hardware protocol

Protocol version: `GP_BIND_002_HW_V1`  
Status: `HARDWARE_TEST_REQUIRED`; this is a source-free terminal-agent packet.
It records no controller observation and authorizes neither a firmware merge nor
an automatic update.

This is a new immutable packet for the GP-BIND-002 repair.  It does not amend,
replace, or transfer any row from `GP_BIND_001_HW_V1`.  In particular, the
earlier candidate's H1--H3 PASS, H4 FAIL, H5 NOT_RUN, and deterministic
Profile 3 recovery are historical evidence only.

## Exact candidate and custody tuple

| Field | Exact value |
| --- | --- |
| Candidate branch | `codex/gp-bind-002-carrier-ownership` |
| Candidate Git SHA | `b3d60feb48d637efa8612515d2351a470fe9df0e` |
| Candidate tree | `3ab9366225591543da487f0b7d95c820614f70d4` |
| Candidate direct parent | `b4ca04d1914c96e2a65e21c1e68099ff5cbef1bb` |
| Canonical base | `897356709ea4425eeac0631ca77e44dc68ce780f` |
| Preserved UF2 locator | `local_backups/hardware-artifacts/b3d60feb48d637efa8612515d2351a470fe9df0e/bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921/firmware.uf2` |
| UF2 SHA-256 | `bc82db6f7e334c598ef8eca4f7bcb4aa53964cfc1dfdba202e90b1fbecf1d921` |
| UF2 byte size | `988160` |
| Mk6 RAM | `179280 / 262144` bytes (`68.4%`) |
| Mk6 flash | `493940 / 1568768` bytes (`31.5%`) |

The terminal agent must freshly verify candidate ref, tree, parent, base,
regular-file custody path, exact byte count, and SHA-256 immediately before
the update.  A missing, unreadable, symlinked, size-mismatched, or
hash-mismatched artifact is an identity failure: stop without update, rebuild,
or result inference.  A rebuild is not a substitute for these preserved bytes;
if a rebuild is separately authorized later, it has a new artifact identity.

## Roles and boundaries

The terminal agent performs all local repository, artifact, host, serial,
Configurator, ProfileStore, backup, update, readback, journal, and evidence
operations.  The owner performs only one requested physical controller action
at a time and reports the observable result.  The chapter daemon does not
access local devices, `/private/tmp`, custody media, or serial endpoints.

Use only the ordinary approved manual UF2 update route and the approved
ProfileStore production tool/read-only Config route already used for this
chapter.  No automatic flash, reset, retry-after-ambiguous-write, schema
change, full Config write, or source change is authorized.  The terminal agent
must preserve request/response receipts and exclusive journals for every
ProfileStore operation.

## Required host preflight and recovery route

Before update, the terminal agent must:

1. Capture the controller model/revision as owner supplied, host/backend,
   endpoint, current selected profile/state, time, and exact candidate tuple.
2. Make a fresh read-only ordinary-state backup: raw Config bytes and
   SHA-256/size, ProfileStore status, and every profile/configuration record
   needed to restore the ordinary active state.  Record its generation,
   incarnation, profile revisions, transaction high-water, and all backup
   file hashes.
3. Record the approved deterministic restoration request for the saved
   ordinary ProfileStore state.  It must use current readback identities and a
   fresh token above the observed high-water; it must never roll transaction
   metadata backwards.  If the safe route is unavailable or a proposed write
   is uncertain, stop before update.
4. Verify that the prepared V4 alternate-binding profile is exact and
   admissible before it is loaded: its single X1 `STICK_TABLE_MODIFIER`
   binding has carrier LT6, retains the reviewed bounded table IDs/priorities,
   and does not add another function family.  Preserve its encoded payload and
   pre-load readback evidence.

If any H4 mutation or restoration has an ambiguous request, response, status,
or readback, stop immediately.  Do not retry the write.  Restore only when
the approved tool's exact preconditions and response are conclusive.  A
successful deterministic restoration is recovery evidence, never H5 PASS.

## Physical acceptance sequence

The terminal agent gives the owner one physical action at a time, captures the
answer verbatim, then supplies the next action.  For every row record active
profile/state, physical controls, representative directions, backend/host,
actual observable controller/input-viewer result, anomalies, and PASS/FAIL/
PARTIAL/INCONCLUSIVE.  No row may be inferred from host tests or prior
candidate evidence.

Use the accepted fixture's representative directions: neutral/release, down,
left, right, up, and at least one diagonal.  Where the existing fixture exposes
the established X1 table's complete nine-coordinate grid, record all nine
rows; otherwise a missing requested row is `PARTIAL`, not PASS.

| Row | Active profile/state | Owner action, one at a time | Required observable result |
| --- | --- | --- | --- |
| H1 | Ordinary/default V4 state, whose X1 carrier is LT5 | Press and release LT5 alone; repeat through the representative directions. | The established ordinary X1 output/table behavior occurs exactly; no regression or unexpected legacy output is observed. |
| H2 | Same ordinary/default state | Hold Mode plus LT5; repeat the representative directions. | The established Mode+X1 output/table behavior occurs exactly. |
| H3 | Same ordinary/default state | Exercise LT5 with each accepted X1 conflict fixture, including LT4/X2 and Mode+LT5+LT4; use the fixture's representative directions. | Existing X1/Mode+X1 conflict/precedence behavior remains unchanged. |
| H4a | Prepared exact alternate V4 profile: LT6 is the sole claimed X1 carrier | Press and release LT6 alone; repeat neutral/release and representative directions. | X1 table behavior occurs from LT6, with no Down, A, or Down+A leakage and no other legacy digital or analogue interpretation of the claimed carrier. |
| H4b | Same prepared alternate V4 profile | Hold Mode plus LT6; repeat neutral/release and representative directions. | Mode+X1 behavior occurs from LT6, with no Down, A, or Down+A leakage and no other legacy digital or analogue interpretation of the claimed carrier. |
| H4c | Ordinary/default V4 state, LT5 remains the claimed carrier and LT6 is unclaimed | Actuate LT6 alone and with the representative directions. | Legacy LT6 behavior, including its established Down+A behavior, is retained. |
| H5 | Restored ordinary/default state using the captured approved recovery route | Confirm exact readback/Config preservation, then repeat H1 (LT5 alone through representative directions). | The pre-test ordinary state is restored and H1 behavior is again correct.  This is a fresh candidate-specific row, not a transferred GP-BIND-001 result. |

H4 validates the bounded ownership repair only: function activation observes
the original physical remap/SOCD snapshot while the exact claimed carrier is
removed from every legacy digital and analogue interpretation.  It does not
claim any X2, Y1, Y2, Tilt, RT2, macro, timing, game semantic, Stage A/B/C, or
ProfileStore redesign behavior.

## Fail-safe result handling

- Any H1--H3 discrepancy, H4 legacy leakage, identity mismatch, or uncertain
  mutation is `FAIL` or `INCONCLUSIVE` as applicable.  Stop dependent rows
  where continuing could compromise recovery, preserve raw evidence, and run
  the approved deterministic recovery only when it is conclusively safe.
- A specific H4 failure requires immediate stop before H5 acceptance.  If
  recovery completes, record it as recovery only, with exact request/response,
  journals, post-readback, and byte-identical Config comparison.  Open the
  `HARDWARE_FAILED` / `REPAIR_REQUIRED` evidence path under
  `HARDWARE_EVIDENCE.md`; do not merge or re-use any row.
- `PASS` requires every H1, H2, H3, H4a, H4b, H4c, and H5 criterion to be
  complete and exact, all identity/custody checks to pass, and empty evidence
  gaps.  Partial, unknown, missing, or contradictory observation remains
  non-merge-eligible.
- Submit the resulting exact human observations and local evidence packet to
  the daemon for independent HEP processing.  HEP alone records the
  source-free result state; no source integration or canonical merge follows
  without its exact PASS and the subsequent prescribed review/publication
  gates.

## Evidence packet required from the terminal agent

Return: exact candidate/tree/parent/base/ref verification; artifact locator,
regular-file result, pre-update hash/size; build resource tuple; backup and
restore file paths plus hashes; endpoint/host/backend/profile identities;
every request/response/journal/readback; exact update method; one-at-a-time
owner observations for H1--H5; outcome classification; anomalies; recovery
state; and references sufficient for an immutable `HARDWARE_EVIDENCE.md`
record.  Do not include credentials or irrelevant hardware identifiers.
