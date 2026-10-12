# Private full friend-Config refresh v3 — 2026-10-12

Owner relayed the friend's screen: Stored Config rejected / Recovery required /
Operation refused, and confirmed the previous v2 booted normally on that Glyph.
The exact failed device bytes and CRC/decoding/semantic reason are unmeasured.
ROOT CAUSE remains UNPROVEN. The original coordinate-only package is retained
as refused-test evidence, not accepted hardware firmware.

Owner explicitly approved reapplying the FULL baked friend Config, replacing
later saved settings: "yes, it's better to have a full clean thing here. I'll
try it on my Glyph this time first". This authorizes one Config refresh, not a
Clean/Fresh UF2 wipe, weakened validation, main-source change or hardware flash
by the assistant. No main work order, rebase or merge is created.

Base: 375c486de48ddb39814914754952b18be46cafe2.
Only active source delta: versioned marker path and payload change from v2 to v3.
New marker: /friend_ult_20261012_v3.flag (27-byte basename).
Exact payload: friend_ultimate_20261012_applied_v3 followed by newline (36 bytes).
All tables, corrected Default2 offset(0,-77)/raw(128,51), intentional Tilt2 flip,
buttons/chords/priorities, RGB, backends and full baked Config are unchanged.

Old v2 marker cannot suppress new adoption. On mounted storage, absent/invalid
v3 marker -> validate baked Config -> save complete Config -> checked readback
and production validation -> exact full encoded equality -> checked marker
write/flush/close/reopen/length/content/EOF. Only verified v3 completes adoption.
Failures do not accept the marker. Invalid old Config does not need to decode
before this explicitly authorized replacement. Mounted storage is NEVER formatted.
Valid v3 marker on subsequent boots -> no repeated overwrite, ordinary checked
stored load; later valid user edits survive, later invalid Config is still refused.
No new large automatic Config/buffer, no heap Config, no reentrant installer.

Existing mount-recovery/data-loss policy is unchanged: if initial no-autoformat
mount fails but setConfig succeeded and baked Config validates, private recovery
may format/remount the linked LittleFS partition, even on a later corrupted-FS
boot. This may erase all persisted files/settings. It is private-only, explicit
firmware behavior, not a flashing-time high-flash/filesystem wipe.

Host proof includes valid v2 marker + valid edited Config / invalid USB reference /
invalid RGB target / bad CRC / truncated Config / malformed protobuf with valid
CRC / header-size mismatch -> exact fresh baked adoption
once, zero formats on mounted storage. Save/readback/mismatch/partial-marker/
marker-readback faults with old v2 marker refuse. Later v3 user edits persist;
later corrupt Config is NOT silently reset. All prior friend/recovery tests,
production validation/full roundtrip, stack/build/UF2/isolation and one fresh
independent review remain required. Root owns changes/build/publication;
reviewer-only delegation avoids unrelated investigation for this constant change.

## Owner's Glyph first — short test

WARNING: your saved controller Config will be replaced with the full friend Config.
Retain the archived owner firmware/Config pair for later restoration.

1. Enter RPI-RP2. Drag ONLY this package's firmware.uf2; wait for reboot.
2. No Fresh Install, web configurator or second Config push.
3. Confirm normal boot, no refusal, and Ultimate active.
4. No modifier: LF2 Down must be straight down, raw(128,51); release(128,128).
5. Check RT1/A and one representative modifier.
6. Power-cycle; confirm normal boot/profile persistence and Down again.
7. Report this exact artifact hash and observed results. Only then send to friend.

HARDWARE: NOT_TESTED / PRIVATE_REPAIR_READY_FOR_OWNER_TEST.
No physical PASS is inferred from host/build/review or earlier no-crash evidence.
