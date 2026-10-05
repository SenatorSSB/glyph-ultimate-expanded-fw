# GP-CONFIG-017 hardware protocol

Protocol version: `GP_CONFIG_017_HW_V1`

This tests the exact committed and built candidate recorded in the queue. The
repair moves the existing null RGB guard before the speed read. The host tests
cover injected null states. Physical null reachability remains UNKNOWN.

## Identity and recovery prerequisites

Before a firmware update, verify the full candidate Git SHA, its direct build
parent and tree, the UF2 SHA-256 and size, and the content-addressed preserved
locator in the reviewed handoff. Re-hash that preserved file immediately before
the manual update. A rebuild is a different artifact.

Record the controller revision, host and adapter, backend, current firmware,
selected profile and ordinary RGB behavior. Preserve the owner's current Config
as exact bytes with size and SHA-256, and establish the supported restoration
route. Keep the exact accepted rollback UF2 available. Missing identity,
Config custody or a safe recovery route stops the update.

The owner performs each physical action through the existing supported manual
workflow. Give one dependent action at a time and wait for its observation.
No automated device or Config write is part of this protocol.

## Required observations

For every row, record the selected configuration, expected behavior, observed
behavior, PASS/FAIL/PARTIAL and any anomaly. Choose valid profiles through the
source-supported operator route after their RGB settings are established.

| Row | Action | Required observation |
| --- | --- | --- |
| identity | Open About after the exact manual update | Build identity matches the expected candidate; record displayed text or explicit confirmation |
| static RGB | Select a valid ordinary static RGB profile and exercise mapped controls | Existing mapped colors and brightness continue; controls remain usable without unexpected blanking or disconnect |
| dynamic RGB | Select valid ordinary rainbow profiles and observe multiple updates | Existing supported animation and brightness continue; use both SHIFT and XWAVE when safely available through the established route |
| mode changes | Switch between the established valid static and dynamic profiles | The selected profile's ordinary RGB behavior appears and controls remain usable |
| reconnect and reboot | Reconnect, then use the established normal reboot route | Controller reconnects and the selected ordinary RGB behavior remains available |
| Ultimate and X1 | Exercise accepted Ultimate controls and the established X1 observation | Accepted controller output is preserved on the recorded host/backend |
| owner Config restoration | Restore the preserved original Config through its supported manual route; verify bytes immediately and after reboot | Exact original size and SHA-256 are restored; selected ordinary profile is usable |

The reviewed handoff must turn these rows into concrete configurations and
expectations before a Config change. A profile unavailable through a safe,
source-supported route remains a gap; do not invent or force an operator path.

## Null reachability and anomalies

Record any naturally observed null transition separately with its exact steps.
Do not force an undocumented state to reach the guard. Host null PASS does not
establish a physical crash, its root cause, or physical null reachability.
Nunchuk remains NOT_TESTED unless the owner explicitly tests it.

On a required-row failure, stop the test and use the established manual
rollback and Config restoration route. Preserve the observation, candidate and
artifact identity, and rollback result. The independent Hardware Evidence
Processor determines acceptance from exact identities and actual owner reports.
