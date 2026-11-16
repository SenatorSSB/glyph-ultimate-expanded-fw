# Glyph Mk6 USB qualification and beta update

The initial Switch USB failure is repaired within the owner's tested scope. The owner authorized and performed one installation, tested sticks and gamepad buttons in Ultimate on original Nintendo Switch, then returned the controller to Mac Configurator Mode.

**Tested candidate.** Source `5dfc4cc26ca27d1de15c80e2a59f9637052f1b5c`, program-only UF2 `de793f3469e8d88de31fb6f85d50bacd203b13928f1333ae5b291557c84b1518`, 1,325,568 bytes. Configurator reports `5dfc4cc2`. After the owner's GameCube connection trial and return to Switch USB, all 27 profiles plus the complete Config remain byte-identical to the immediate preinstall snapshot. The procedure below is retained for additional setups. Further installation or saved-state mutation requires its own authorized scope. [Physical result](PHYSICAL_RESULT.json) · [Candidate qualification and custody](QUALIFICATION.md)

## Console check on the installed image

1. Record the console family and model (Switch, OLED, Lite or Switch 2), system version, dock or host accessory, dock power, USB port, cable and any intervening adapter. Use a cable known to transfer data. When available, verify the same host port with a working **wired** controller. Record which parts of the path that control actually tests.
2. Disconnect GameCube and other Glyph leads. Boot normally with controls released. Record About's firmware version and the **dashboard** backend and profile label. A previous installation receipt can identify an image if custody is continuous. A short version alone cannot identify an exact UF2. If an approved Config backup exists for this state, resolve the saved USB destination from its one-based backend index and that backend's default mode row. Mark missing identity or saved state unknown. Keep serial numbers, profile contents and USB location IDs private.
3. Test the intended route when the running dashboard says **Switch**. Return from the configuration menu to the ordinary dashboard before testing (menu entry can suspend the primary game mode). Press and release one mapped face button and one direction. Record local changes, then use a second controller to reach HOME → Controllers. Record the new controller's icon/player assignment or its absence. Open **Change Grip/Order** if needed and follow the on-screen join prompt. In the console button test, record which Glyph button appears, then enter Ultimate and verify movement, a mapped action and release with other controllers untouched. Repeat after one normal cold reconnect if included in the approved observation. Record first input time separately from About's local Ready time.
4. If recognition fails, record the initial result before changing the setup. On original Switch/OLED, inspect **System Settings → Controllers and Sensors → Pro Controller Wired Communication**. On Switch 2 use **Controllers & Accessories → Nintendo Switch Pro Controller Wired Communication**. If the owner chooses an On trial, record initial/final setting and restore the original afterward. Nintendo documents this for its Pro Controller. Its relevance to the Glyph's Pokkén-style HID identity is a diagnostic question. Lite needs a suitable USB host accessory. [Nintendo wired setup](https://en-americas-support.nintendo.com/app/answers/detail/a_id/49387) · [Nintendo model-specific guidance](https://en-americas-support.nintendo.com/app/answers/detail/a_id/26315)
5. HORI's wired-controller controls include checking console/software versions and dock seating, a full console shutdown, reconnecting the cable, powering on, and checking Change Grip/Order. Apply to the actual dock/model, recording any variable changed and the result. These instructions cover HORI's named products. A system update or HORI firmware updater is outside this diagnostic. [HORI Switch](https://stores.horiusa.com/nintendo-switch-controller-troubleshoot/) · [HORI Switch 2](https://stores.horiusa.com/nintendo-switch-2-controllers-troubleshooting/)

**Record each result separately.** Power / saved destination / dashboard backend / local response / console player registration / console button event / Ultimate action and release / reconnect. Use observed, absent or unknown. Target-console qualification requires registration and actual input on the named setup and image.

## Optional Mac enumeration observation

With permission for a Mac connection, run this before and after connecting the same released-controls Glyph directly by the data cable. The command reads the macOS registry. It prints USB vendor/product numbers and interface numbers/classes only. Compare the added device and any matching HID interface (class 03). For the Switch route the intended pair is 0f0d:0092. An unexpected new pair, a missing HID class or no added device is worth recording. This observation alone cannot determine the bytes sent or the console's response.

```sh
/usr/sbin/ioreg -a -r -c IOUSBHostDevice | python3 -c '
import plistlib, sys
def walk(node, device=None):
    if "idVendor" in node and "idProduct" in node:
        device = (node["idVendor"], node["idProduct"])
        print("device %04x:%04x" % device)
    if device and "bInterfaceNumber" in node and "bInterfaceClass" in node:
        print("interface %04x:%04x number %d class %02x" %
              (*device, node["bInterfaceNumber"], node["bInterfaceClass"]))
    for child in node.get("IORegistryEntryChildren", []):
        walk(child, device)
for root in plistlib.loads(sys.stdin.buffer.read()):
    walk(root)
' | sort -u
```

If an identical model is already attached, compare with it disconnected before interpreting the result. Retain only the added device's rows. For stage localization, record HID descriptor availability, OS configuration and received interrupt reports only when actually measured. Internal scan, output, readiness and submission can remain unknown in the physical record.

## Saved mode and preservation

If Switch is already executing, the console trial needs no USB-mode save. If another backend is executing, pause at the current state. **Menu → USB Mode → Switch** can save the one-based Switch backend index to `Config.default_usb_backend_config` **and** the current eligible row to that backend's `default_mode_config`, then reboot. The protocol enum is 7. Its value is not the saved array index. A managed selection requires matching context and an eligible existing profile. Check the before values, desired after values and final restoration path before asking approval for the named selection. Switching back can leave a changed default on the Switch row. If ordinary return cannot restore every specified field, hold the write. [USB selection](../../../HAL/pico/src/display/DefaultConfigMenu.cpp) · [Managed persistence](../../../include/core/ProfileSelection.hpp) · [Boot selection](../../../HAL/pico/src/comms/backend_init.cpp)

For an approved preservation-oriented test, privately identify the unit and capture the original Config bytes, store status/guards, incarnation, generation, transaction high-water, ordered directory with IDs and revisions, and every readable wrapper. Record the executing backend, row, profile ID, revision, schema and digest on a supported identity route. Configurator Mode provides the full saved inventory. Capture original normal-mode identity separately. Use the existing serial Config reader, production STATUS/LIST/READ and runtime identity tools under the approved read scope. Stop on ambiguity, incomplete reads, unexpected recovery/fencing or unexplained content changes. These API-visible backups cannot re-create raw flash, allocator/root history or arbitrary prior firmware. [Accepted GOPT preservation](../gopt-qualification/PHYSICAL_CLOSEOUT.md)

## Manual install and recovery boundaries

| Starting condition | Operator disposition |
| --- | --- |
| Known Mk6 and existing library | Qualify **one named starting version → one exact candidate**. Before approval, bind candidate SHA/tree, retained UF2 SHA-256/size, current source identity, complete backup, intended cases, final backend/profile and privately identified board. Verify UF2 program-block addresses against the current partition layout. |
| New, genuinely blank Mk6 | Fresh installation remains unqualified for public users. A separately approved clean-unit trial should use the same exact program-only UF2 and confirm first startup, expected Config/defaults, store status and normal input. An unknown or unreadable library is outside this case. |
| Existing unreadable store, failed install or recovery screen | Record the last completed step, screen, ROM/normal enumeration and copy result, then stop. If the application is unavailable, physical recessed BOOTSEL is the documented independent ROM entry. Its availability does not restore profiles. A separately reviewed recovery decision needs the exact last image, custody, storage compatibility and retained backup. |
| Downgrade or destructive factory reset | Outside the proposed beta support scope. A verified destructive factory artifact and procedure are still outstanding. The October image is historical evidence only. [Factory recovery status](../../runtime_config/profile_store_factory_recovery_followup.md) |

Only after exact installation approval, rehash the immutable custody file using the repository's pre-handoff verifier. The owner uses the known recessed BOOTSEL procedure, checks that the intended Mk6 is the unique RPI-RP2 target, and copies that exact regular UF2 **once**. Allow normal reboot with buttons released. No erase, drive formatting, second copy, automatic recovery, downgrade or profile modification is part of this installation. If identity is uncertain or boot fails, preserve the result before deciding recovery. [Custody verifier and path](../../agent_framework/HARDWARE_ARTIFACT_CUSTODY.md) · [Recorded manual method](../../runtime_config/profile_native_ultimate/hardware_installation_qualification_20261022/INSTALL_PACKET.md)

After the approved test, compare Config bytes, all entries/wrappers, defaults, guards and counters to the current preflight, accounting only for explicitly approved intermediate changes. Verify final normal-mode source/backend/profile and local operation after leaving Configurator. Report the exact final state and any residual difference. Keep raw evidence private. A successful manual copy plus advertised source identity provides custody evidence, with installed flash readback still unmeasured.

## First-beta scope recommendation

| Capability | Physical evidence and beta disposition |
| --- | --- |
| GameCube adapter / Ultimate | **Physically accepted in recorded scope** on the GOPT owner setup. Preserve it. Distinguishing output of independently backed profiles remains undemonstrated (53 and 54 have identical wrappers). Profile 27 retains its context hold. Limit adapter/console claims to measured setups. [GOPT closeout](../gopt-qualification/PHYSICAL_CLOSEOUT.md) |
| Switch USB | **Physically accepted in recorded scope** on original Nintendo Switch with the repair candidate. The owner reports normal sticks and gamepad buttons in Ultimate. Postinstall version and complete API-visible preservation pass. Other console/accessory combinations require their own evidence. [Candidate physical result](PHYSICAL_RESULT.json). The October report covers the observed Ultimate profile/menu, reboot and apparently normal controls. Kazuya was unselected and enumeration/receiver data were not captured. Switch 2 requires separate model-specific evidence. [October report](../../runtime_config/character_profile_menu/hardware_20261023/USB_Nintendo_Switch_owner_report.json) |
| XInput | **Partially tested**. GOPT has physical runtime identity and local operation. Qualify a Windows XInput host separately by detecting the controller through XInputGetState and observing button and axis transitions. Native XInput on Switch is **unsupported** in this proposed scope. [Microsoft XInput guidance](https://learn.microsoft.com/en-us/windows/win32/xinput/getting-started-with-xinput) |
| Configurator and managed profiles | **Physically accepted in recorded scopes** for historical readback, preservation, managed CREATE, scoped selection and disposable UPDATE/RENAME/REORDER/DELETE. Keep dedicated Config row plus ProfileStore record, one-to-one ownership, existing eligibility and lifecycle. Separate saved identity from executing identity. Distinguishing receiver output and profile 27 remain held. [Package acceptance](../../runtime_config/package_active_profile_display/integration_20261113/README.md) · [Lifecycle and remaining gaps](../gopt-qualification/BETA_AND_HARDWARE.md) |
| UI, resources and optional routes | Long-name ellipsis is **host validated only**. Physical stack high-water is unmeasured. Nunchuk is **not tested**. Exclude other unqualified routes and accessory combinations from beta v1. [GOPT closeout](../gopt-qualification/PHYSICAL_CLOSEOUT.md) |

Release remains held for disposition of the chosen installation/recovery scope and separate owner release approval. Integration of previously accepted GOPT has its own exact-ref approval.
