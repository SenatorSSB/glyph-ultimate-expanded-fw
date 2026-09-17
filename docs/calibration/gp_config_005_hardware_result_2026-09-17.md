# GP-CONFIG-005 Hardware Result - 2026-09-17

Status: `HARDWARE_PASS`

## Exact Identity

- Work order: `GP-CONFIG-005`
- Candidate branch: `glyph/gp-config-005-transactional-setconfig`
- Candidate Git SHA: `437f87e8086a50f0dfbd834176b80d245c1ed307`
- Base `configurator` SHA: `9550a1bf1309383e351f4f9e66663562fc9f13ac`
- Tested UF2 SHA-256:
  `650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44`
- Preserved artifact:
  `local_backups/hardware-artifacts/437f87e8086a50f0dfbd834176b80d245c1ed307/650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44/firmware.uf2`
- Protocol: `GP_CONFIG_005_HW_V1`
- Fresh operator package:
  `local_backups/gp-config-005-operator/fresh-run-20260917T224913Z/`
- Structured evidence:
  `fixtures/gp_config_005_hardware_evidence_2026-09-17.json`

The live remote candidate ref still resolved to the exact candidate SHA during
processing. The candidate is a direct child of its recorded base. The
preserved regular read-only UF2 was re-hashed without rebuilding: 792064 bytes
and the exact SHA-256 above. No firmware source or artifact was changed by this
result publication.

## Restored Fresh Baseline

Before the fresh acceptance attempt, the original preserved config artifact
was restored through the existing owner-controlled path. The artifact
re-encoded exactly to 4202 bytes with SHA-256
`26919308427aa081633b0a40c0c83c5762ba9edf35eb912b901e9fa847a4dd84`.
The immediate post-write readback, post-reboot readback, and fresh-run baseline
all matched those exact bytes.

## Rejection Suite

The fresh suite contained the required seven cases in protocol order:

1. malformed decode;
2. invalid default backend;
3. invalid backend default mode;
4. invalid keyboard reference/type;
5. invalid custom reference/type;
6. keyboard index out of range;
7. custom index out of range.

Every case returned the exact expected `CMD_ERROR`; no invalid request returned
`CMD_SUCCESS`. Every row recorded `connected_after: true`, a successful
`CMD_GET_DEVICE_INFO` / `CMD_SET_DEVICE_INFO` follow-up, and
`followup_responsive: true`. The persisted post-rejection payload remained
byte-for-byte equal to the 4202-byte fresh baseline.

That persisted equality is a `config.bin` observation. It is not used to claim
live-RAM byte identity; the reviewed production-path host harness supplies the
byte-level rejection invariant proof.

## Valid Update And Reboot

The benign valid update changed only `rgb_brightness` from `255` to `20`. It
changed no game mode, mapping, backend, or controller-output field. Its exact
payload was 4201 bytes with SHA-256
`f589317b59b3ab7543cad563e2e0877dc5f491227e6e35777bc732d402bb1480`.

The transaction record contains, in order:

`prewrite_read_attempted` -> `prewrite_read_completed` ->
`prewrite_baseline_matched` -> `pre_write` -> `write_attempted` ->
`write_system_call_completed` -> `awaiting_response` -> `response_received` ->
`response_decoded` -> `followup_read_attempted` ->
`followup_read_completed`.

The response was `CMD_SUCCESS`. The immediate persisted `GET_CONFIG` readback
was byte-for-byte the sent payload. After one reboot, the persisted readback
again matched the same 4201 bytes and SHA-256, with `rgb_brightness = 20`.

## Owner-Reported Physical Observations

After the fresh rejection suite, the project owner reported:

- the Ultimate profile operated normally on Switch;
- no rejected value was observed operationally;
- display/menu behavior appeared normal;
- no disconnect or regression was observed.

After the valid update and reboot, the project owner reported:

- controller behavior was normal;
- expected profile/mapping behavior was normal;
- display/menu behavior was normal;
- connection behavior was normal.

These are owner-reported observations. The local operator JSON intentionally
left human observation fields null; this canonical record does not infer human
observations from mechanical output.

## Prior Inconclusive Event

The earlier run remains separate historical evidence in
`gp_config_005_prior_inconclusive_persistence_event_2026-09-17.md` with
classification `INCONCLUSIVE_PERSISTENCE_EVENT`. Its post-drift config was the
exact 3969-byte compiled Glyph default payload with SHA-256
`fb70c955b7e9813cb730a4749bbfc8dfe4fc5fb3b99b7ecacaafc329a1db8855`.
The fresh run supersedes it only as the current acceptance attempt. The prior
event is not reclassified as PASS, combined with the fresh run, or assigned a
proven persistence-failure window.

## Accepted Result

The exact candidate/artifact pair is `HARDWARE_PASS` for the bounded
GP-CONFIG-005 invariant and `GP_CONFIG_005_HW_V1` protocol. This source-free
evidence publication makes the exact tested candidate eligible for the
Implementation Supervisor's publication-recovery checks and exact-candidate
integration. It does not merge or publish candidate runtime source.

## Non-Claims

- No disk rollback guarantee.
- No atomic persistence guarantee.
- No power-loss safety guarantee.
- No recovery guarantee.
- No live-RAM byte identity claim from `GET_CONFIG`.
- No Nunchuk behavior claim; Nunchuk remains `NOT_TESTED`.
- No unrelated firmware path acceptance.
- No low-level root-cause claim.

