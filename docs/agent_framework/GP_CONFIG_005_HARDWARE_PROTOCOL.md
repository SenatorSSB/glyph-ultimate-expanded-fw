# GP-CONFIG-005 Hardware Acceptance Protocol

Status: CANDIDATE_IDENTITY_PENDING.

Protocol version: `GP_CONFIG_005_HW_V1`.

This is the candidate-local H2 protocol for the approved live-RAM SetConfig
rejection invariant. It is not evidence that a test occurred. Fill exact
candidate Git SHA, base SHA, artifact SHA-256, preserved local locator,
controller context, observations, tester, and time only after an exact
candidate exists.

## Preconditions

- The exact candidate passed its production-path host transaction tests,
  canonical build, map/RAM review, aggregate gates, and independent review.
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
