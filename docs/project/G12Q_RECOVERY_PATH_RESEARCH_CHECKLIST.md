# G12q Recovery Path Research Checklist

Status: recovery research checklist only. No flashing, mounted-device writes, upload commands, or hardware actions are authorized.

## Purpose

Define the evidence needed before trusting any custom firmware recovery path. This checklist is intended to guide future human-controlled spare-device testing and to prevent treating source plausibility as hardware proof.

## Evidence Split

### Source-Backed Repo Behavior

- `config/glyph/common/src/config.cpp` reads matrix input early in `setup()`.
- If `inputs.mb1` is true, the repo source shows the update bitmap, lights bootloader RGB, and calls `reboot_bootloader()`.
- `HAL/pico/src/reboot.cpp` implements `reboot_bootloader()` as `rp2040.rebootToBootloader()`.
- `HAL/pico/src/display/DefaultConfigMenu.cpp` exposes a `Manual FW.Update` menu item that calls `reboot_bootloader()`.
- `HAL/pico/src/core/Persistence.cpp` stores config through LittleFS.
- `platformio.ini` sets `board = pico` and `board_build.filesystem_size = 0.5m`.

### Official Glyph Procedure

- Limit Labs documents Update and Fresh Install firmware options.
- Limit Labs documents connecting while holding the illuminated Menu button.
- Limit Labs documents the `RPI-RP2` drive and `.uf2` drag/drop update.
- The Glyph manual documents Manual FW Update and indicates a physical BOOTSEL button exists under the top plate/artwork sheet.

### Inferred RP2040 Behavior

- `RPI-RP2`, family ID `0xe48bff56`, `board = pico`, and Raspberry Pi docs strongly support RP2040 UF2 bootloader behavior.
- Raspberry Pi docs say BOOTSEL mode is ROM-resident and cannot be rewritten.
- This improves recovery confidence only if BOOTSEL remains accessible on the actual Glyph hardware.

### Unknowns

- Whether the official Menu-hold path is hardware-wired BOOTSEL, firmware-mediated reboot, or both.
- Whether `inputs.mb1` is definitively the illuminated Menu button named in official docs.
- Whether the physical BOOTSEL button is safely accessible for all Glyph hardware revisions.
- Whether custom firmware preserves Menu-hold and Manual FW Update paths until tested.
- Whether official Update restore after custom firmware has been observed on spare hardware.

## Checklist Before Trusting Custom Firmware Recovery

- [ ] Official Update UF2 is archived, hash-recorded, and role-confirmed.
- [ ] Official Clean/Fresh Install UF2 is archived, hash-recorded, and reserved for intentional profile wipe only.
- [ ] Current official Limit Labs firmware page date, version, release commit string, and links are captured.
- [ ] Official Update is recorded as profile-preserving per official page.
- [ ] Official Clean/Fresh Install is recorded as profile-resetting per official page.
- [ ] Generated custom UF2 is parsed read-only and confirmed Update-style/app-only.
- [ ] Generated custom UF2 does not write `0x1017f000..0x101ff000`.
- [ ] Generated custom UF2 does not write at or beyond `0x101ff000`.
- [ ] Repo source still contains early `inputs.mb1 -> reboot_bootloader()` path.
- [ ] Repo source still contains `Manual FW.Update -> reboot_bootloader()` path.
- [ ] `reboot_bootloader()` still maps to `rp2040.rebootToBootloader()`.
- [ ] No unexpected display/menu/config/persistence/backend/default-mode files changed.
- [ ] Custom mode remains default-unreachable unless explicitly approved.
- [ ] Menu-hold update entry has been observed on stock official firmware.
- [ ] Manual FW Update has been observed on stock official firmware.
- [ ] Physical BOOTSEL fallback has been identified from official/manual/PCB evidence.
- [ ] Physical BOOTSEL fallback is not relied upon until access is understood.
- [ ] Spare-device custom flash is used before main-device use.
- [ ] After custom flash on spare hardware, Menu-hold update entry still works or a physical fallback is confirmed.
- [ ] After custom flash on spare hardware, Manual FW Update still works or is not required as the only fallback.
- [ ] Official Update restore is observed after custom firmware.
- [ ] After restore, normal enumeration, menu access, profiles, and configurator behavior are checked.

## Risk Matrix

| Risk | Severity | Evidence | Control |
| --- | --- | --- | --- |
| Custom firmware breaks firmware-mediated Menu-hold update path | High | Menu path exists in app source | Verify on spare device before main device |
| Manual FW Update unavailable after bad app | High | Menu action lives in app source | Do not rely on it as sole recovery |
| Physical BOOTSEL inaccessible or misunderstood | High | RP2040 docs prove ROM BOOTSEL, not Glyph access | Confirm official/manual/PCB procedure |
| Accidental profile wipe | Medium-high | Clean UF2 zeroes high-flash filesystem-sized region | First custom artifact must be app-only |
| Invalid UF2 partly writes or fails unclearly | Medium | RP2040 datasheet warns invalid UF2 may fail partially | Parse UF2 before any device write |
| Official restore assumptions wrong | High | Restore after custom not yet observed | Require spare-device rollback evidence |
| Hidden downstream differences from official firmware | Medium | Full release-source equivalence unknown | Treat custom builds as untrusted until tested |

## Recovery Trust Levels

| Level | Meaning |
| --- | --- |
| `NOT_TRUSTED` | Recovery evidence is incomplete; no custom flash should occur. |
| `SOURCE_PLAUSIBLE` | Repo and official docs suggest recovery paths, but no spare-device custom rollback has been observed. |
| `SPARE_DEVICE_OBSERVED` | A spare Glyph has completed custom flash, recovery entry, official restore, and post-restore checks. |
| `MAIN_DEVICE_APPROVED` | Spare-device evidence is accepted, risks are reviewed, and a human explicitly approves main-device use. |

Current status: `SOURCE_PLAUSIBLE`, not flash-approved.

## Stop Conditions

Stop before hardware action if:

- official restore cannot be completed;
- profile state changes unexpectedly;
- USB enumeration is unstable;
- update mode is unreachable;
- physical BOOTSEL fallback is unknown and firmware-mediated paths fail;
- generated artifact writes filesystem/EEPROM regions unexpectedly;
- any step depends on undocumented Glyph behavior as fact.
