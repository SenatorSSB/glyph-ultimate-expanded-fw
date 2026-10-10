# Friend Ultimate private build — installation

INSTALLATION_MODE: RPI_RP2_SINGLE_UF2

SEPARATE_CONFIG_PUSH_REQUIRED: NO

Hardware status: NOT_TESTED / PRIVATE_BUILD_READY_FOR_OWNER_TEST.

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
Reflashing the same build over a valid marker does not force a fresh adoption.

The UF2 is application/update-style and contains no Clean/Fresh or filesystem
wipe range. First-boot Config/marker writes are intentional; a filesystem format
is not. If storage cannot mount, save or verify, normal operation is refused;
this package does not automatically erase/repair the filesystem. If the screen
shows a recovery/refusal message, stop and report it to the owner. Do not try a
Clean/Fresh wipe or a second Config push as an undocumented installation step.

This remains an untested private firmware fork, not canonical configurator or
product acceptance. Run OWNER_FIRST_BOOT_TEST.md before giving it normal use.
