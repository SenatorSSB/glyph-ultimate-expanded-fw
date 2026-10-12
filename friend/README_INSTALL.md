# Friend Ultimate private build — installation

INSTALLATION_MODE: RPI_RP2_SINGLE_UF2

SEPARATE_CONFIG_PUSH_REQUIRED: NO

Hardware status: NOT_TESTED / PRIVATE_REPAIR_READY_FOR_OWNER_TEST.
This is the 2026-10-12 v3 full-Config refresh, retaining the corrected Default2.

Only Default position 2 changes: offset (0,-77), raw (128,51), replacing
(-77,0), raw (51,128). All other profile behavior is unchanged. This v3 refresh
deliberately reinstalls the FULL friend Config once, ignoring the old v2 marker.
Existing saved settings will be replaced; the owner authorized this replacement.
No separate Config push is needed. It is not an official Clean/Fresh wipe image.

1. Enter RPI-RP2 bootloader mode.
2. Drag **firmware.uf2** to RPI-RP2.
3. Wait for the controller to reboot.
4. Use the controller (Ultimate is the default on GameCube and all supported USB gamepad backends).

No official configurator webapp, second Config push, or additional installation
file is required. JSON files are reference artifacts, not files to drag onto
RPI-RP2. Do not flash a rejected/superseded artifact from the verification folder.

On its first normal boot this private firmware replaces the complete stored
Config with the validated baked friend Config. Existing device Config changes
will be replaced at that first adoption. It then reads the saved Config back,
validates and compares every encoded byte, and writes/verifies its versioned
marker. A valid marker prevents subsequent automatic overwrite and preserves
later legitimate user Config changes. Empty/partial/old markers do not count.
Reflashing this same build over a valid v3 marker does not force another adoption.

The UF2 is application/update-style and contains no Clean/Fresh or filesystem
wipe range. HOWEVER, this private firmware can format the linked LittleFS
partition at boot: it first attempts current no-autoformat initialization; only
if that mount fails, setConfig succeeded, and baked Config validates, it explicitly
formats/remounts, then provisions and verifies the complete Config and v3 marker.
Mounted filesystems are never formatted, even if a Config or marker read/write
fails. Format/remount/save/readback/marker failure refuses normal operation.

DATA-LOSS WARNING: this policy also applies if storage becomes unmountable on a
later boot. The marker is in that same filesystem, so first-install absence and
later corruption cannot be distinguished. Recovery may erase every persisted
setting/file and restore baked friend defaults. With normally mounted storage
and a valid v3 marker, later user changes are preserved without format/overwrite.
There is no invisible marker outside LittleFS and no new persistence architecture.

The v3 marker is `/friend_ult_20261012_v3.flag`, exact payload
`friend_ultimate_20261012_applied_v3\n`. Its 27-byte basename fits the selected
LittleFS wrapper's <32-byte limit; failed v1 used an invalid 37-byte basename.
Old/partial v1 or v2 state cannot suppress v3 adoption. Old markers need not be
deleted. No official Fresh Install,
web configurator or Config push is a prerequisite. If the screen still shows
recovery/refusal, stop and report it; do not perform undocumented extra steps.

This remains an untested private firmware fork, not canonical configurator or
product acceptance. The owner will test on their Glyph first. Start with
CONFIG_REFRESH_V3.md. Only after the short recovery test passes should the wider
OWNER_FIRST_BOOT_TEST.md matrix be run. A new marker does not establish the
root cause of the friend's earlier rejection; that exact cause is UNPROVEN.
