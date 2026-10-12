# Private Default position 2 correction — 2026-10-12

Direct owner authority: the friend corrected the originally supplied Default
position 2 from (-77,0) to (0,-77). The owner requested an updated single UF2,
isolated from the progressed main project, and permits private Git publication.

Base: c247985d3730812faf5c92ee59a51ce9122b31eb, storage-recovery-v2.
The ONLY active firmware change is one raw table point: (51,128) -> (128,51).
All other coordinates, intentional Tilt2 X flip, remaps, modifiers, priorities,
C-stick, defaults, RGB, baked Config, validators and storage recovery are kept.

The table is compiled into the application, not persisted in Config. Keep the
same /friend_ult_20261011_v2.flag and exact payload. A valid existing v2 marker
skips provisioning and preserves later user edits; the new point takes effect
without a Config push, forced re-adoption or filesystem wipe. First installation
still uses the existing validated full-Config/save/equality/verified-marker path.

Unchanged private data-loss policy: after no-autoformat mount failure, successful
setConfig and validated baked defaults permit explicit format/remount. A later
unmountable filesystem may also be erased, restoring baked defaults. Mounted
storage is never formatted. This is not canonical persistence behavior.

Classification: FIRMWARE_SOURCE_ACTIVE_BEHAVIOR, private hardware-test candidate.
No merge into configurator, no main work order, no main checkout edits, no
runtime-loaded architecture, no device writes or flashing by the assistant.
No rebase onto progressed configurator: retain the reviewed friend baseline.
Past package bytes, manifests, hashes and physical evidence are preserved.

Validation: complete actual-source friend/recovery host suite in both enum ABIs,
all existing regressions, a specific valid-v2-marker upgrade/Config-preservation
test, exact single-point source-delta proof, full Config equality/roundtrip,
actual selected LittleFS probe, stack measurements, repository wrapper build,
UF2 inspection, main-work isolation snapshots and one fresh independent review.
Reviewer-only delegation is appropriate: no separable investigation is needed
for this one-point mechanical correction. Root owns source/build/publication.

## Short owner/friend retest

1. Enter RPI-RP2 and drag ONLY this package's updated firmware.uf2.
2. Wait for normal boot. No configurator, Fresh Install or Config push.
3. With no modifier, press physical LF2 (Down): raw target (128,51), straight
   down, not left. Release: (128,128).
4. Check one diagonal and one representative modifier remain unchanged.
5. Power-cycle and repeat Down; confirm normal boot and retained settings.

HARDWARE: NOT_TESTED / PRIVATE_BUILD_READY_FOR_OWNER_TEST for this new artifact.
Do not inherit the previous owner's no-crash observation as acceptance of this
new coordinate fix. Nunchuk remains NOT_TESTED.
