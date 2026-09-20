# GP-CONFIG-010 hardware protocol

Protocol version: `GP_CONFIG_010_HW_V1`

This packet is for the exact candidate Git SHA and preserved UF2 named by the
canonical queue. Test only after the candidate/artifact custody gate passes.

1. Record candidate Git SHA, base configurator SHA, preserved UF2 path, and
   artifact SHA-256 before updating the controller.
2. Re-hash the preserved UF2 immediately before update and require an exact
   match with the recorded artifact hash.
3. Update the owner-held controller using the ordinary accepted firmware update
   procedure. Record controller model/revision and host context without adding
   unrelated hardware identifiers.
4. Exercise every current default mode entry in order (indices 0 through 12),
   including each activation binding, and record the observed backend/mode
   result for every row.
5. Exercise ordinary reconnect/power-cycle and regression checks required by
   the owner's normal controller procedure. Do not claim Nunchuk coverage
   unless its rows are actually executed.
6. Record `PASS`, `FAIL`, `PARTIAL`, or `INCONCLUSIVE` with exact observations,
   anomalies, rollback, tester, and time. A successful build is not a hardware
   result; a rebuilt UF2 is not a substitute for the preserved artifact.

The implementation supervisor stops at the hardware gate. No merge or DONE
publication is authorized until exact-snapshot physical PASS is recorded.
