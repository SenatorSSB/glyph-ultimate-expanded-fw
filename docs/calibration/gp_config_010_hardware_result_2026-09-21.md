# GP-CONFIG-010 Hardware Result - 2026-09-21

Result: `INCONCLUSIVE`

The project owner manually updated a standard supplier-purchased Glyph with
candidate `f4771e17430fd1ea3f1e3e5339a83dfe648290a3` using the exact preserved
791040-byte UF2 whose SHA-256 is
`9be230cdce6b6ce0b97941da920ec8f043ff98c174ffb126cfcc654ad599209a`.
Custody was `PRE_HANDOFF_VERIFIED` immediately before the manual update. The
firmware rebooted normally, selected Ultimate automatically, and connected
normally to Nintendo Switch.

Indices 0 Melee, 1 Brawl, and 2 Ultimate passed the supplied menu/operation
checks. At index 3, Split FGC was absent because the owner's persisted
six-profile configuration remained active. The reported active list was
Melee, Brawl, Ultimate, RoA, RoA2, and Gamecube. The candidate was not intended
to replace persisted profile/configuration data, so this is a test-setup gap
and not an observed firmware failure.

Indices 3 through 12 were not completely exercised and the active six-profile
configuration did not cross the historical 10-slot cache boundary. The final
post-matrix power-cycle/reconnect sequence was therefore not executed. The
owner separately reported normal Ultimate values and buttons, miniscreen
behavior, and connection stability. No failure or abnormal behavior was
reported in the executed scope.

The canonical structured record is
`docs/calibration/fixtures/gp_config_010_hardware_evidence_2026-09-21.json`.
It preserves all 13 expected rows, the exact observations, gaps, and required
retest. This result does not authorize merge or `DONE`; GP-CONFIG-010 remains
`LOCAL_ACCEPTANCE_PENDING`. Nunchuk remains `NOT_TESTED`, no rollback was
performed, and the exact candidate remained installed at the end of the
reported session.
