# X1 Offset-41 Hardware Result - 2026-09-02

Status: `HARDWARE_PASS`

## Exact Identity

- Work order: `GP-X1-001`
- Candidate branch: `runtime-config-x1-offset41-hardware-candidate`
- Candidate Git SHA: `74ae24364b84520d4e0e39240beb9867653cc7b9`
- Base `configurator` SHA: `045bca0d1450c261c3c60ccf5ef86f7302bd3dbc`
- Tested UF2 SHA-256:
  `5fadd3d7e82e629fbccd41fac868312b07b01e39d2ef0a0a98a06d649ae28254`
- Protocol: `GLYPH_X1_OFFSET41_MANUAL_PROTOCOL_V1`
- Structured evidence:
  `fixtures/x1_offset41_hardware_evidence_2026-09-02.json`

## Human Report

The project owner reported:

> Everything confirmed working, outputs are as expected and the controller
> isn't disconnecting at any point.

After receiving the regenerated prior `configurator` UF2, the project owner
then reported:

> worked, now proceed with the real results

## Accepted Result

- All nine exact neutral/cardinal/diagonal X1 output expectations: PASS.
- Continuous connection during the reported candidate test: PASS.
- Restoration of the prior working firmware: PASS as rollback evidence.
- Anomalies reported by the tester: none.
- Nunchuk: `NOT_TESTED`.
- Low-level root cause: unproven.

The report applies only to the existing sole/non-mode X1 path selecting
`kX1Table`. The unchanged mode+X1 `kMX1Table` path is not claimed as part of
this test.

## Artifact Reconciliation

The UF2 was SHA-256 verified before the manual handoff from the normal local
build path. After the test, the still-present bytes were re-hashed and copied
unchanged to the candidate-SHA/artifact-SHA-addressed local backup recorded in
the structured evidence. This post-test preservation is explicitly recorded
as an anomaly because it was not an approved external immutable artifact-store
handoff before flashing. The original task expressly allowed reconciliation
after this exploratory test when exact tested source and artifact identity was
preserved sufficiently; no upload or release was authorized.

The exact candidate branch is pinned remotely. This result does not claim UF2
reproducibility across rebuilds.

## Non-Claims

- No other source-owned table or routing behavior was tested or accepted.
- Runtime-loaded configuration, persistence, WebSerial/device write,
  protobuf write, and flashing automation remain unimplemented.
- Nunchuk remains `NOT_TESTED`.
- Root cause remains unproven.
