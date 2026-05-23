# G12f First Hardware Test Protocol Draft

Status: future protocol draft only. This is not authorization to flash hardware and does not include flashing commands.

## Purpose

Define a cautious phase sequence for a future human-controlled first custom firmware test after source/build, artifact, recovery, and explicit approval gates are complete.

## Phase Sequence

### 1. Source/Build Verification

Confirm:

- intended branch and commit;
- working tree state;
- no unexpected source/header/config/protobuf/default activation changes;
- no unintended runtime/default reachability changes;
- no Force Up-B, digital output, right-stick, or C-stick expansion unless separately approved;
- `glyph_mk6` build passed.

### 2. Artifact Identification

Record:

- artifact path;
- artifact name;
- artifact hash;
- artifact size;
- artifact file type;
- artifact format conclusion and evidence;
- whether artifact format matches verified official updater/bootloader expectations.

### 3. Recovery Verification

Confirm before any custom flash:

- official firmware file available locally;
- official restore path documented;
- whether official restore has been tested or not tested;
- physical fallback path documented or marked unknown;
- config preservation/reset expectations documented or marked unknown.

### 4. Optional Spare-Device Flash

Only a human may perform this phase, only after explicit approval, and preferably on a spare device.

This protocol draft intentionally provides no flashing commands and no mounted-device write commands.

### 5. Connection Sanity Check

After a human-controlled flash, observe without game involvement:

- device enumerates or does not enumerate;
- USB identity/host-visible behavior;
- whether configurator communication is available, if expected;
- whether any unexpected mode selection occurs;
- whether official recovery path remains accessible.

### 6. No-Game Basic Input Sanity

Before any console/game test, observe basic defaults in a non-game context where possible:

- controller outputs normal defaults;
- no unexpected digital outputs;
- right-stick/C-stick remain unchanged from intended default behavior;
- triggers/default output behavior remain unchanged unless separately approved;
- `SenscopePrototype` is reachable or not reachable as expected for the specific test build.

### 7. Controlled Switch/GC-Adapter Sanity

Only after the device is recovered/revertible, stable, and human-approved:

- perform minimal connection sanity through Switch/GC-adapter path;
- record enumeration and default output behavior;
- stop at first unexpected behavior.

No gameplay semantic labels, thresholds, or Super Smash Bros. Ultimate behavior claims are part of this protocol.

## Observations To Record

- branch and commit;
- working tree clean/dirty state;
- artifact name/hash/size;
- artifact local path;
- artifact type/format evidence;
- official firmware restore tested/not tested;
- official firmware file name/hash/size/source;
- device enumerates/not;
- host-visible USB identity;
- controller outputs normal defaults;
- any unexpected mode selection;
- whether `SenscopePrototype` is reachable or not;
- whether config appears preserved, reset, or unknown;
- whether official recovery succeeded if attempted;
- any unexpected backend, USB, or persistence behavior.

## Hard Stop Conditions

Stop immediately if:

- build failed;
- artifact format is unknown;
- no official rollback path is documented;
- official firmware file is unavailable;
- unexpected source/config/protobuf/runtime changes are present;
- custom mode reachability changed unexpectedly;
- Force Up-B, digital output, right-stick, or C-stick behavior changed unexpectedly;
- USB enumeration is unstable;
- official firmware cannot be restored;
- config preservation is required but unknown;
- any step would require agent-run device writes;
- any conclusion would depend on undocumented backend behavior as fact.
