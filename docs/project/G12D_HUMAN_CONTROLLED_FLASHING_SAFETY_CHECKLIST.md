# G12d Human-Controlled Flashing Safety Checklist

Status: future human checklist only. This is not an agent instruction to flash and not authorization to perform hardware flashing.

## Core Rule

Agent must not flash hardware, write firmware artifacts to mounted devices, run upload commands, add upload scripts, or operate a connected controller as a firmware target.

## Preconditions Before Any First Custom Firmware Flash

A human reviewer should confirm all of the following before any first custom firmware flash:

1. Official firmware file is available locally from a trusted official source.
2. Recovery path is documented and understood before custom firmware is attempted.
3. Custom artifact format is confirmed from local build output and official updater/bootloader expectations.
4. `glyph_mk6` build passed on the intended branch/commit.
5. Custom mode remains unreachable by default unless intentionally testing a selected debug path approved for that specific test.
6. No config/protobuf/default activation changes are present unless explicitly approved.
7. No Force Up-B, digital output, right-stick, or C-stick expansion is present unless explicitly approved.
8. Test on a spare device if available.
9. Do not use a tournament/main controller first if avoidable.

## Human Review Before Flash Decision

Record before proceeding:

- branch and commit;
- working tree clean/dirty state;
- artifact path, name, hash, and size;
- artifact format evidence;
- official firmware restore file path/source;
- recovery procedure evidence;
- whether user config preservation is known or unknown;
- whether the device is spare/test hardware or a main controller.

## Stop If Uncertain

Stop if any of these are true:

- artifact format is unknown;
- official updater/connect-mode expectations are unknown;
- official rollback path is unknown or untested;
- official firmware file is unavailable;
- a spare device is unavailable and the only device is important for tournament/main use;
- source/header/config/protobuf/default activation changes are unexpected;
- Force Up-B, digital output, right-stick, or C-stick behavior changed unexpectedly;
- `SenscopePrototype` became reachable by default unexpectedly;
- USB enumeration is unstable;
- the human cannot explain how to recover official firmware;
- any step would depend on undocumented backend behavior as fact.

## Explicit Non-Commands

This checklist intentionally provides no commands that write to a device. Any future hardware procedure must be separately approved, human-controlled, and based on verified official recovery evidence.
