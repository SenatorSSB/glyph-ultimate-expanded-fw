# GP-BIND-001 X1 Hardware Protocol

Protocol version: `GP_BIND_001_HW_V1`  
Status: `HARDWARE_TEST_REQUIRED`; no physical observation is recorded here.

## Exact identity

- Candidate branch/SHA: `codex/gp-bind-001-profile-defined-x1` / `32c1bd81910ec5bcea0104fe98b9b37fb267d071`
- Candidate tree: `a9d2fb6dbde1c3853121e111ed2b5025d0280855`
- Canonical base: `83bd38ab7e7946562a6e952171d85acbfed7339b`
- UF2: `local_backups/hardware-artifacts/32c1bd81910ec5bcea0104fe98b9b37fb267d071/ea261256dc57a0974d4f23b232e8bd43d5cf50d7094661a4c0531f92aad9d1ed/firmware.uf2`
- UF2 SHA-256/size: `ea261256dc57a0974d4f23b232e8bd43d5cf50d7094661a4c0531f92aad9d1ed` / `986624` bytes

Rehash those preserved bytes immediately before update. Any identity mismatch stops: do not flash, infer a result, or substitute a rebuild.

## Preconditions

1. Record controller model/revision, host/backend and active profile identity; preserve the ordinary profile/configuration state and a recoverable backup before changing anything.
2. Confirm the candidate SHA, UF2 SHA-256 and byte count above. Use the existing approved manual update route only.
3. This packet claims only the X1 slice. Do not test, alter, or claim X2, Y1, Y2, Tilt, RT2, Nunchuk, factory recovery, Senscope, macros, timing, or unrelated modifiers.

## Human observations

For every row, record the actual controller/input-viewer or game-observable result, backend/host, and any anomaly. A row is PASS only when it matches the established ordinary X1 behavior on the selected profile; unknown or incomplete observations are `PARTIAL`/`INCONCLUSIVE`.

| Row | Physical action | Expected bounded fact |
| --- | --- | --- |
| H1 | On the ordinary/default profile, actuate the current X1 control alone through neutral and representative directions. | The accepted default X1 table behavior remains unchanged. |
| H2 | Hold Mode with that same X1 control and repeat representative directions. | The accepted Mode+X1 table behavior remains unchanged. |
| H3 | Repeat X1 with each relevant accepted conflict control represented by the X1 fixture exclusions, beginning with LT4/X2; include Mode+X1+LT4. | X1 precedence/conflict behavior matches the accepted ordinary profile: no unexpected X1/MX1 selection overrides the established competing/default result. |
| H4 | Load the deliberately prepared V4 profile whose single `STICK_TABLE_MODIFIER`/`X1` binding uses a different physical input, while retaining the same bounded table IDs/priorities. Actuate that alternate input alone and with Mode. | The same X1 and Mode+X1 behavior is selected from the alternate physical input; the legacy LT5/slot is not required for X1 meaning in that profile. |
| H5 | Return to the ordinary/default profile/state and repeat H1. | Ordinary/default X1 behavior remains correct after the alternate-binding check. |

## Result and recovery

Record `PASS`, `FAIL`, `PARTIAL`, or `INCONCLUSIVE` with exact row observations, anomalies, pre/post update hashes, and recovery/rollback performed in a hardware evidence record conforming to `HARDWARE_EVIDENCE.md`. Restore the preserved ordinary profile/configuration after testing. No source integration follows anything except complete exact PASS with empty evidence gaps.
