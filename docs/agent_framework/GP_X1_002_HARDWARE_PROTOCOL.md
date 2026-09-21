# GP-X1-002 hardware protocol

Protocol version: `GP_X1_002_HW_V1`

This packet applies only to the exact candidate Git SHA and preserved UF2 named
by the canonical queue. Re-hash that preserved artifact before update; a
rebuild is not a substitute.

The existing source route is the Ultimate sole/non-Mode X1 path where source
sets `x1_active` from logical input `LT5`. LT5's physical location must be
owner-confirmed or authoritatively source-resolved before testing; this
protocol does not invent a physical button location. Mode+X1/`kMX1Table` is
outside scope.

Immediately before the coordinate test, show the operator this complete table:

| Direction | Numpad meaning | Raw X | Raw Y | Miniscreen X | Miniscreen Y |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | down-left | 93 | 51 | -35 | -77 |
| 2 | down | 128 | 51 | 0 | -77 |
| 3 | down-right | 163 | 51 | +35 | -77 |
| 4 | left | 93 | 128 | -35 | 0 |
| 5 | neutral | 128 | 128 | 0 | 0 |
| 6 | right | 163 | 128 | +35 | 0 |
| 7 | up-left | 93 | 205 | -35 | +77 |
| 8 | up | 128 | 205 | 0 | +77 |
| 9 | up-right | 163 | 205 | +35 | +77 |

The miniscreen conversion is `display = raw - 128` only. It is not an angle or
radius claim.

Required acceptance, one operator action at a time:

1. Record candidate/base SHA, preserved artifact path/hash, controller model as
   owner supplied, operator, time, active profile, and update context.
2. Update using the ordinary accepted manual procedure and the preserved UF2.
3. Connect normally with the owner's expected Ultimate profile active.
4. Activate only the unchanged sole/non-Mode X1 path. Observe and record all
   nine rows, including neutral/release behavior.
5. Verify representative unrelated normal inputs, miniscreen/menu sanity, and
   continuous connection. Record anomalies without expanding acceptance.
6. Disconnect ordinarily, power-cycle/reconnect, verify automatic expected
   profile selection, connection stability, and one representative X1 row.
7. Record PASS, FAIL, PARTIAL, or INCONCLUSIVE, anomalies and rollback. PASS
   requires every row and regression check above to pass.

Do not claim Mode+X1, another modifier, gameplay semantics, persistence,
runtime-loaded configuration, device-write behavior, Nunchuk, or root cause.
The supervisor stops before merge until exact-snapshot physical PASS is
processed under the Revision-2 evidence contract.
