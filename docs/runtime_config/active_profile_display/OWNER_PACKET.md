# Bounded owner display validation — unexecuted

Separate owner approval is required before any device/flash action. Do not use a
rebuild: first bind the exact candidate SHA/tree and preserved UF2 SHA-256/bytes
from [exact candidate evidence](CANDIDATE.json), verify those preserved bytes, and STOP if any
identity/custody/resource/review gate is absent or fails. The baseline firmware's
hardware acceptance does not transfer to this new display code.

1. On the currently accepted firmware, take a fresh read-only inventory with the
   existing approved production inspection route. Seal all records (IDs, names,
   ranks, revisions and payload hashes), store incarnation/generation and health;
   confirm ID27 Pikachu and ID51 Kazuya, compact format1/root format2, no
   migration/recovery/uncertain state, ID27 active.
   Preserve Config separately so ordinary selection/reboot persistence can be
   distinguished from forbidden profile-record changes. Abort on any mismatch.
2. After explicit owner approval, install only the exact retained candidate using
   the existing accepted manual route. No flashing automation. No ProfileStore
   CREATE/UPDATE/RENAME/REORDER/DELETE, migration or recovery operation is allowed.
3. Menu controls from the current source: MB1 opens menu/back, MB2 moves up,
   MB3 moves down, MB4 enters. Use `.Profile` for ordinary stored-profile
   selection and allow its normal reboot; use `Input.Viewer` to open the viewer.
   On each existing accepted route — XInput, GameCube (ordinary accepted adapter/
   console route), USB Nintendo Switch — select/boot Pikachu normally. Dashboard
   must show Pikachu, the expected backend, no Ultimate Runtime, no Unknown Plate
   for the unspecified context. Open Input Viewer and confirm Pikachu too.
4. On each route select Kazuya normally; dashboard and viewer must show Kazuya
   with correct backend and the same plate semantics. This tests identity only;
   no Kazuya gameplay retest or new gameplay acceptance is requested. Return to
   Pikachu normally; verify refreshed identity, normal reboot/reconnect and menu.
   Existing selection may save Config; it must not mutate ProfileStore records.
5. End on Pikachu ID27. Repeat the complete read-only inventory and compare with
   step1: ID27/ID51 and every other record byte/hash/metadata unchanged; store
   generation/incarnation unchanged; no recovery/uncertain state. Confirm current
   ID27 using the existing accepted identity/read-only route. Stop on any drift.

Report exact candidate SHA + tested UF2 SHA-256 and per-route Pikachu/dashboard,
Pikachu/viewer, Kazuya/dashboard, Kazuya/viewer, return-Pikachu/reboot, backend and
preservation PASS/FAIL/NOT_TESTED. Record omissions honestly. If display fails,
retain evidence and use the existing exact accepted rollback artifact manually;
do not repair store contents. No candidate merge before exact hardware PASS.

This packet is prepared only. No device operation has been executed by this run.
