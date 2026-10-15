# Strict B3/B7 selection and recovery regression

Run `python3 tools/check_glyph_profile_store_selection_recovery.py`.
The checker generates the current Nanopb Config ABI, compiles the actual
`src/core/mode_selection.cpp` with inert mode/hardware doubles, and runs
ASAN/UBSAN. It also executes the same destination transaction, one-shot boot
consumer and recovery initialization helpers used by production startup.

The persistence double deliberately commits bytes and returns UnknownOutcome
for the lost acknowledgement case. The selection loop must leave runtime
activation and reset untouched even when durable state changed. Repeating the
held chord must not write again. After a release, the helper re-reads durable
state and recognizes an unchanged destination.

The explicit old-behavior controls restore the former immediate set_mode loop
and remove BeginRecovery from the recovery initializer. Both must fail their
runtime behavioral assertions; a compile failure does not count as detection.
Hardware/display/USB timing and physical storage are not modeled here.

## Required exact-candidate target checks

These checks belong in the owner's final hardware packet and are NOT performed
by this checker. First back up the exact Config and each listed stable record,
record the candidate Git SHA and UF2 SHA-256, and retain the pre-test selection.
No profile CREATE/UPDATE/DELETE or uncontrolled power cut is needed for these
selection/recovery rows. Stop immediately on an unexpected stable ID, revision,
store incarnation, Config field change, repeated reset, or gameplay output in
recovery. Restore the original durable selectors with the ordinary separately
approved Config transaction and verify them after the restoration reboot.

1. From an ordinary compact Ultimate destination, hold its own chord. Confirm
   no reset and unchanged Config generation. Then choose a different compact
   Ultimate row with a different stable reference. Confirm a single reset,
   saved backend/mode destination, unchanged references, and activation on the
   subsequent boot. Keep the chord held through that boot; confirm no further
   reset until full release. Repeat with a non-Ultimate row and a GameCube
   destination where the owner's available backend permits it.
2. Use only the candidate-scoped checked-persistence fault hook in the final
   packet to inject definite failed and lost-acknowledgement Config publication.
   Confirm the command does not reset or switch the active runtime profile.
   Reconnect/reboot separately to inspect which durable result actually won;
   do not label unknown publication as clean failure. Remove the fault-enabled
   candidate before final production acceptance according to that packet.
3. Enter manual RT2 with a usable filesystem and disconnected/failed display.
   STATUS must identify recovery, LIST must inspect the existing store rather
   than claim it is empty, READ/health must work on existing records, and all
   mutations must be refused without Config/store generation changes. Confirm
   bounded transport responsiveness and absence of gameplay reports.
4. Exercise automatic Config-rejection entry through the bounded final packet's
   fault/backup procedure. Confirm STATUS says Config invalid, existing store
   remains inspectable, GET_CONFIG and writes are refused, no defaults are
   saved, and no normal mode/backend/menu output begins. A storage-unavailable
   injected case must report the narrower filesystem health and reject all
   storage-dependent commands; diagnostic/device-info/reboot remain available.
5. Hold MB1 and RT2 together. Confirm bootloader/update priority, with no Config
   load/store inspection or automatic formatting. Verify both recovery routes
   also remain headless and make no filesystem writes.

Record corruption, root corruption, migration fencing, unknown transaction and
read-only recovery health observations are supplied by the companion store and
protocol regressions plus their exact-candidate target packet. This fixture
does not claim physical PASS or cover a particular game's output semantics.
