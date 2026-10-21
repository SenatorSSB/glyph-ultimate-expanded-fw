# GP_NATIVE_001_CONFIGURATOR_BACKUP_ENTRY_V1

Status: proposed narrow extension to the approved Mac preflight. No entry or CDC lookup has been executed. This packet requires a separate explicit owner approval because Menu → Configurator restarts the firmware, whereas the earlier approval covered already reachable sessions and excluded restart operations.

## Exact scope

1. The owner uses the known menu item “Connect to Configurator” / “Configurator Mode” exactly once on the currently connected intended Mk6. Select only that item; release all controls after selection. This explicitly permits the menu action’s USB disconnect, watchdog-scratch selection and firmware restart. It permits no boot/recovery chord, other backend/default/settings selection, Manual FW Update or RPI-RP2 action. If the ordinary Configurator display does not appear, stop without another entry attempt.
2. After the owner confirms that display, run the pinned `configurator_port_lookup.py` exactly once. It uses installed pySerial’s normal OS serial-registry metadata enumeration and retains only VID2E8A/PID1092 candidates. pySerial internally examines serial-service metadata; it opens no serial port or USB/HID user client. Unrelated serial metadata is not retained. Require exactly one matching `/dev/cu.usbmodem…` port for the owner-identified unit; ambiguity, no match, access error or another device stops the step. No retry or alternate discovery method.
3. On that positively identified ordinary Configurator session, perform only the existing read requests already approved under GP_NATIVE_001_MAC_PREFLIGHT_V1: one fixed current-Configurator identity query, one GET_CONFIG backup, one explicit STATUS, complete bounded LIST and READ of available original IDs. Use115200 baud and new host output/journal files. Require current identity status `configurator` and normal STATUS; recovery/unsupported/error/timeout is a stop. No host reset,1200-baud operation or Config/ProfileStore mutation.
4. Preserve exact command/stdout/stderr/session evidence, backup JSON and decoded raw payload SHA256/length, available store directory/records and their checksums. The existing backup key is `rawConfigPayloadBase64`. Validate completeness, decode and custody before any later mutation. Leave the controller in Configurator after these reads; no further mode action is included.

The original session's bounds do not reset: at most one Config backup, one current-Configurator identity query, at most8 LIST calls at page size8,64 original-ID READ calls, and73 STATUS queries including each existing LIST/READ preflight. All of these counters are currently zero. The failed XInput capture remains stopped; this packet permits no XInput retry. WUP is unavailable on this Mac; no WUP inspection/capture/0x13 occurred or is requested here. Switch capture is unattempted and is not requested by this extension.

## Source-backed preservation qualification

Exact source is F334fbd06e4541c120b0db423e5be7e112eb1f6f6. The entire menu file is unchanged from accepted307d72347653c079ec8ec6e9b6ecae3c30ae536c and baseline976ba2195b72046b32f7ecdd41063e7bad791ded. The specific Configurator watchdog branch skips the backend SaveConfig path. The selector can change the live RAM USB default, but GET_CONFIG streams the saved file payload rather than that temporary RAM Config. This is independently source-qualified in CONFIGURATOR_ENTRY_QUALIFICATION.md; generic warnings about other watchdog backend changes do not mean this branch necessarily saves its temporary selection.

Installed firmware remains UNKNOWN. Existing startup/recovery/migration/bookkeeping can still occur; this packet does not promise byte-identical persistent state across restart or a pristine filesystem history. GET_CONFIG may select an existing current/prior/legacy source; actual backup/status must establish normal compact-v2/store eligibility. An unavailable, recovery, unsupported or incomplete backup is an engineering stop. Public backup is not a raw filesystem image and cannot preserve unrelated directory/orphan/history/journal bytes. Existing supported filesystem states and all resource/storage limits remain unchanged.

## Exact host operations after approval and confirmed entry

```sh
python3 /private/tmp/glyph-native-configurator-entry-backup-20261022/configurator_port_lookup.py --output '<new-configurator-port.json>'
GP_NATIVE_F='/private/tmp/glyph-profile-native-20261020'
python3 "$GP_NATIVE_F/tools/glyph_runtime_identity_tool.py" --port '<single-confirmed-CDC>' --context configurator --token '<fresh-nonzero-token>' --session '<actual-Configurator-boot-session>'
python3 "$GP_NATIVE_F/tools/glyph_serial_config_tool.py" --read --port '<same-CDC>' --backup-out '<new-original-backup.json>'
python3 "$GP_NATIVE_F/tools/glyph_profile_store_production_tool.py" --port '<same-CDC>' --journal-out '<new-status.jsonl>' status --output '<new-status.json>'
python3 "$GP_NATIVE_F/tools/glyph_profile_store_production_tool.py" --port '<same-CDC>' --journal-out '<new-list-page.jsonl>' list --page '<actual-cursor>' --page-size 8 --output '<new-list-page.json>'
python3 "$GP_NATIVE_F/tools/glyph_profile_store_production_tool.py" --port '<same-CDC>' --journal-out '<new-read-ID.jsonl>' read --profile-id '<actual-original-ID>' --output '<new-read-ID.json>'
```

The identity tool has no raw-output-file option; retain its actual JSON stdout. Existing dependencies were checked offline without a device open. `source_pins.json` binds exact F/menu/backend/transport/schema sources, the host lookup, installed pySerial implementation and owner entry description. The separate focused ACK binds final packet and lookup hashes. Root reserves each attempt durably before launching it. No command may run from this document alone without the new owner approval.

## Separate future candidate gate

This step does not install or test candidate334f. Its retained instrumented UF2 remains1041408 bytes, SHA25641305f260d42e8206bf4a2fb06c88912416e49cd8a68bc13ce3d3c7605306982; ELF SHAa42bd2bf6ab1efd3cac565b27d9e236c0128da3be84a5977e5c739db2697c15d. It grants no flashing, native profile/Config mutation, H1–H12 campaign, RPI-RP2, restoration/recovery experiment, driver/privilege/OS-settings workaround or controller reset command. The one menu-triggered firmware restart above is the entire new controller action.

Actual backup/eligibility and usable observers precede the separate exact-candidate installation/physical-test packet. Manual GameCube-adapter-to-Switch tests are relevant; raw WUP on Mac is not mandatory equipment. Missing required L/R/Z/analog or other observations remain explicit until a demonstrated observer or an explicit evidence-standard decision resolves them. Source/host evidence never becomes physical PASS. Hardware/Nunchuk NOT_TESTED, timing/highwater NOT_MEASURED, RT2 deferred, root cause UNPROVEN and all existing acceptance gates remain.
