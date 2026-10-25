# Display hardware observations and preservation — 2026-10-25

Exact candidate `e416cabe3e0878e69036d2f75d59eed0d4d05208`, tree
`c071f006e3e21b5e3146a85c8a767264e8822264`; preserved UF2 SHA-256
`cbd5320d84e72d59bcf8618a4714fd7e94f6ec51fcbbc38450f1cffc077c45b3`,
1046528 bytes. [Result](RESULT.json) records bounded dashboard hardware PASS
for XInput, GameCube and USB Nintendo Switch, plus final preservation PASS.
No source integration, global hardware PASS or Input Viewer name PASS is claimed.

The owner authorized the exact write after connecting RPI-RP2. The known physical
unit identity matched privately. Because it was already in bootloader mode, no
fresh preflash logical inventory was available: the operator instead saved all
16MiB flash, verified installed firmware against the accepted menu UF2, inspected
candidate UF2 addresses and reverified custody. Candidate sectors end0x10080000,
below filesystem0x1017f000. One manual picotool load/verify wrote the retained
UF2 without executing it; full-flash readback then verified every candidate block
and every byte outside the firmware sectors, including Config/ProfileStore,
before application reboot. No reusable flashing automation or store/Config
mutation command was introduced or executed. The alternative preflash method
is disclosed rather than represented as the originally planned logical capture.

Postboot read-only XInput identity confirmed ID27/revision1/schema5. The owner
reported Pikachu on the main dashboard, blank plate information and the visible
Pikachu/Kazuya list. When asked to select Kazuya, verify Kazuya on the dashboard
and return to Pikachu, the owner replied "confirmed". The subsequent request
explicitly asked for the same dashboard checks on GameCube and USB Nintendo
Switch, ending on Pikachu; the owner replied "confirmed all, back on configurator".
These are owner-reported display observations, not agent visual inspection or
Kazuya gameplay retesting. A later read-only XInput query independently confirmed
ID27 after the first return; final Configurator references retain ID27.

Input Viewer remains physically UNCONFIRMED: the owner said it has never shown
profile information to their understanding. The source text-print path and host
rendering tests do not prove visible hardware text. The three-route confirmation
answers the dashboard request; it does not retroactively assert a viewer result.
No font/layout repair or new firmware build is performed here.

Final Configurator capture used only identity, Config read and production
STATUS/LIST/READ. The existing offline packet audit passes all24records/2native.
Every ID/name/rank/revision/schema/wrapper/body matches the sealed accepted
post-cleanup inventory. Store incarnation/generation/token high-water remain
unchanged; all capture fences are stable, no recovery flags, native IDs27/51 and
no48–50. Normal owner selection may change Config; native references end on27.
The older sealed logical inventory is an explicit comparison baseline; fresh
write-stage whole-storage byte preservation is separate evidence. Private raw
Config, records, serial, fences, tokens, full flash and journals remain ignored.
Result metadata pins their private manifest and preservation report hashes.

The device is currently in Configurator for that read-only capture; normal
Pikachu return remains a physical owner step. Firmware flashed YES; profile/store
mutations NONE; profiles modified NONE. Pikachu/Kazuya gameplay payload baselines
unchanged. Nunchuk NOT_TESTED; root cause UNPROVEN. Initial chapter candidate and
review files retain their preflash chronology. No canonical firmware merge follows
from this bounded evidence record.
