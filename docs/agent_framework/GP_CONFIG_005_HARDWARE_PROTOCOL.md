# GP-CONFIG-005 Hardware Acceptance Protocol

Status: HARDWARE_TEST_REQUIRED.

Protocol version: `GP_CONFIG_005_HW_V1`.

This is the candidate-local H2 protocol for the approved live-RAM SetConfig
rejection invariant. It is not evidence that a test occurred. The exact
candidate and preserved artifact are:

The bounded project-owner CLI and runbook for executing this protocol are in
`tools/gp_config_005_hw_test.py` and
`docs/agent_framework/GP_CONFIG_005_HARDWARE_OPERATOR.md`.

- Candidate branch: `glyph/gp-config-005-transactional-setconfig`
- Candidate Git SHA: `437f87e8086a50f0dfbd834176b80d245c1ed307`
- Base `configurator` SHA: `9550a1bf1309383e351f4f9e66663562fc9f13ac`
- Build output: `.pio/build/glyph_mk6/firmware.uf2`
- Artifact SHA-256: `650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44`
- Preserved locator: `local_backups/hardware-artifacts/437f87e8086a50f0dfbd834176b80d245c1ed307/650b90961e170e6d88221ffe610545f43d880c9334c4d28ab613ad380418af44/firmware.uf2`
- Hardware result: `null`

The tester must record controller context, observations, tester identity, and
time in a Revision-2 evidence record after the physical test.

## Preconditions

- The exact candidate passed its production-path host transaction tests,
  build, map/RAM review, applicable focused/content gates, and independent
  review. The full aggregate remains fail-closed in preflight solely on the
  owner-deferred GP-VAL-011 ignored nested `.pio` repository isolation defect;
  it is not represented as a candidate product failure or a passing aggregate.
- The candidate ref is pinned to the full built Git SHA.
- The exact UF2 is preserved and readback-verified under
  `GLYPH_HARDWARE_ARTIFACT_CUSTODY_V1`; repeat `--pre-handoff-verify`
  immediately before manual update.
- Preserve the current accepted config payload and the exact prior accepted
  firmware artifact for manual rollback. Use only the existing custom
  Glyph/HayBox backend. Do not use or claim official-configurator compatibility.
- Prepare malformed and bounded-invalid payloads from the current protobuf
  schema without adding a runtime fault-injection command. A valid success
  payload starts from the preserved accepted config and changes only a benign,
  explicitly recorded non-game-semantic field for this operational check.

## Steps And Expected Observations

1. Manually update the controller with the exact verified candidate artifact.
   Expected: the device reconnects and the custom backend remains responsive.
2. Send a malformed protobuf SetConfig request. Expected: the existing decode
   `CMD_ERROR`, no disconnect, and continued backend responsiveness.
3. Exercise each existing bounded rejection family: default backend index,
   backend default-mode index, keyboard reference/type, custom reference/type,
   keyboard index bound, and custom index bound. Expected for each: the same
   pre-candidate `CMD_ERROR` text/class, no success response, no disconnect,
   and continued responsiveness.
4. After the rejection series, exercise normal reports and the currently
   active controller/display path. Expected: no rejected candidate value is
   operationally observed and ordinary behavior remains responsive. This is
   regression evidence; source/host tests, not GET_CONFIG, prove byte-level live
   RAM equality because GET_CONFIG reads `config.bin`.
5. Send the prepared valid SetConfig request. Expected: one `CMD_SUCCESS`, no
   disconnect, and continued responsiveness. Reboot once and confirm the
   accepted config is available under existing behavior.
6. Run ordinary controller and display smoke observations relevant to the
   pre-test configuration. Expected: no new regression. Nunchuk remains
   `NOT_TESTED` unless explicitly exercised and recorded.

Do not force a real-device `SaveConfig` failure: destructive storage fault
injection is outside this work order. The production-path host test must cover
`SaveConfig == false` and prove prior live RAM remains unchanged. Hardware
testing covers transport, memory/resource, reboot, controller, and display
regressions; it does not prove disk rollback, atomic persistence, or power-loss
safety.

## Result And Rollback

Record every step as observed `PASS`, `FAIL`, `PARTIAL`, or `INCONCLUSIVE` under
`HARDWARE_EVIDENCE.md`. Any disconnect, wrong response, resource instability,
unexpected live behavior, identity mismatch, or incomplete row prevents merge.
On anomaly, manually restore the exact prior accepted firmware and preserved
config through the existing owner-controlled recovery path, then record the
rollback observation. No flashing automation is authorized.
