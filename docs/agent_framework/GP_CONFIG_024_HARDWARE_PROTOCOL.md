# GP-CONFIG-024 hardware protocol

Protocol version: `GP_CONFIG_024_HW_V1`

Status: `HARDWARE_TEST_REQUIRED`. No physical row has been run. The owner has
not supplied the current Config identity, a concrete distinguishable profile
pair, or the established update and restoration route. Do not begin a device
action until those exact prerequisites are recorded. No Config write, device
write, or flash action has been performed by this task.

## Exact candidate and build

- Candidate branch: `codex/gp-config-024-usb-profile-identity`
- Candidate Git SHA: `8ab1173b0690f5ed3e994f95af797c9e9a265525`
- Candidate tree: `15ed2d35d561d6b1709499fe42083ca4d789e920`
- Sole parent / base: `b404453ef22cc994eec54338b8a23c3ba61df808`
- Build: `pio run -e glyph_mk6`, PASS, PlatformIO Core 6.1.19;
  ArduinoPico framework `1.30603.0+sha.32e74d0`
- RAM: `105784 / 262144` bytes (40.4%)
- Flash: `389808 / 1568768` bytes (24.8%)
- UF2: `.pio/build/glyph_mk6/firmware.uf2`, 803840 bytes
- UF2 SHA-256: `95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6`
- Preserved locator:
  `local_backups/hardware-artifacts/8ab1173b0690f5ed3e994f95af797c9e9a265525/95de108f23b0d7219caa38a1f85c4dec1691f087061b29787d07b83dab0ba0e6/firmware.uf2`
- Custody: `ALREADY_PRESENT_VERIFIED`; pre-handoff rehash PASS.
- Independent source/build/artifact review: APPROVED for the exact candidate
  and artifact. No device action or hardware acceptance is claimed.
- Accepted rollback: GP-CONFIG-017 candidate
  `5994f1657e45e0883c6c75468a19be7e3b49a72c`, UF2 SHA-256
  `e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5`,
  796672 bytes, at
  `local_backups/hardware-artifacts/5994f1657e45e0883c6c75468a19be7e3b49a72c/e68105ff1fa033308ec9761d87260908a1cd145068e73eb2df516e34ee2e0fe5/firmware.uf2`.

The build required the existing PlatformIO installation and a network-enabled
dependency fetch. The exact candidate checkout remained clean. The preserved
artifact is content-addressed and read-only. Rehash it immediately before any
later manual update; never substitute a rebuild.

## Required setup before physical testing

1. The owner identifies the controller, current firmware, host/adapter, and
   tested backend. Confirm the owner's established manual update, recovery, and
   Config read/restore routes. Record an independently verified accepted
   rollback artifact and rehash it before use.
2. Through the owner's existing read-only route, preserve the complete current
   raw Config and record byte count, SHA-256, and decoded profile rows. Do not
   change it. Record exact row indices and names for a later duplicate-name or
   empty-name pair, plus a safe observable difference between the rows, such
   as a known button mapping. The owner must confirm that the expected
   controller/host output can distinguish those rows.
3. If the current Config has no suitable pair, or the rows cannot be safely
   distinguished without changing Config, stop. This order does not authorize
   editing Config to create a fixture. Report the exact missing profile or
   observation route for separate owner direction.
4. Do not begin until the owner explicitly reports that the setup and recovery
   route are ready. Give one manual action at a time and wait for its report.
   No executor or reviewer writes Config, updates a device, or automates
   flashing.

## Test rows

Keep every row `NOT_TESTED` until the owner reports the exact observation.
For each executed row, record candidate SHA, UF2 SHA-256, controller, host,
adapter, backend, Config hash, profile index, stimulus, expected and observed
output, result, and anomalies.

| ID | Procedure and expected observation |
| --- | --- |
| `valid_startup` | With the preserved valid Config, observe ordinary startup and input release on each supported test route: XInput, DInput, and Switch USB; record GameCube/Ultimate/X1 sanity where supported. Do not infer coverage for an untested route. |
| `duplicate_or_empty_profile_selection` | Using only the owner-identified existing pair, select the later row in the ordinary menu, choose the supported USB backend, and follow the existing reboot flow. Confirm the selected backend and the row-specific observable mapping after reboot. Repeat with the other row if the owner confirms it is safe. |
| `keyboard_dinput` | `NOT_TESTED / DEFERRED_POST_FIRST_PUBLIC_BETA`; nonblocking for the current first-beta scope. Do not perform Keyboard physical testing now. Preserve raw Keyboard semantics; this deferral authorizes no behavior removal, disabling, or output transformation. |
| `reconnect_reboot` | Reconnect and reboot using the same valid stored Config. Confirm the expected backend/profile output and clean input release; read back Config only through the established read-only route and compare exact bytes. |
| `restoration` | Restore no data unless the owner has separately changed it. Re-read the original Config and confirm exact byte equality. If any approved change occurred outside this order, use only the owner's already established restoration route and report each step. |
| `rollback` | If recovery is needed, use only the exact accepted rollback artifact recorded before action. Rehash it immediately before manual use and report the resulting firmware identity. |
| `safe_stop_and_anomalies` | Record unavailable routes, unexpected output, disconnects, stuck input, Config mismatch, or recovery anomalies. Stop on any identity mismatch or unsafe/unavailable recovery path. |

The selector's source-proven successful order is disconnect, 500 ms delay,
one-based profile/backend scratch writes, 30 ms delay, then reboot. A returned
reboot causes an immediate return. Physical acceptance must observe the actual
selected row through an owner-confirmed distinguishing output; the host proof
does not establish physical selection, controller behavior, or persistence.

## Acceptance

The required physical rows and any required gaps are reviewed by the Hardware
Evidence Processor under `docs/agent_framework/HARDWARE_EVIDENCE.md`. A build,
host proof, or this protocol alone is not controller acceptance. Keep C024
unmerged until an exact-candidate and exact-artifact human HEP `PASS` has no
required evidence gaps, followed by exact source integration review and
separate strict DONE. Nunchuk remains `NOT_TESTED`; root cause remains
`UNPROVEN`; public release remains human-owned.
