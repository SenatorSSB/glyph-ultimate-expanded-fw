# Storage-recovery-v2 short physical retest

NOT_TESTED / PRIVATE_REPAIR_READY_FOR_OWNER_TEST.

The previous 800,768-byte UF2, SHA-256
`3f7c074bc92e3683af5aa3525b96e8f5dd75296c247b349da4ad6c5384da1bf8`,
failed first boot with "Config storage failure". Do not flash that artifact again
as the repair. Record the NEW commit and complete SHA-256 from BUILD_MANIFEST.md.

This owner-authorized private build may erase the LittleFS partition if it is
unmountable, including on a later corrupted-storage boot. Read README_INSTALL
before installing. No assistant has flashed this repair.

1. Enter RPI-RP2.
2. Flash ONLY this versioned package's repaired `firmware.uf2`.
3. Do not push a Config or use a Fresh Install prerequisite.
4. Observe and record the boot screen.
5. Confirm normal boot instead of "Config storage failure".
6. Confirm Ultimate is active on the intended GameCube setup/backend.
7. Test one normal direction (for example LF3 Left).
8. Test one normal face button (RT1 A).
9. Test one representative modifier (RF4 Tilt1 plus Left).
10. Power-cycle.
11. Confirm normal boot and profile persistence again.

Report PASS/FAIL with the exact new artifact SHA-256, private source commit,
backend, controller revision and any refusal text. Stop on failure. Only after
this short recovery PASS run the wider gameplay/layout test matrix. Host
simulation/build/review are not physical acceptance. Nunchuk remains NOT_TESTED.
