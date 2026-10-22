# Bounded source diagnosis of GameCube hardware failure

Exact candidate `4898951994bcabcaef2846145de2922a674656f8`; UF2 `7ab99a2f4461c5002c9f71b29f3b7bfe9c87f404970ecd3048e73f8ed885a81e`. Reviewer /root/selector_source_review. Read-only source/evidence inspection; only this report was written. No build, repository mutation, device I/O, retry, cleanup or flashing.

## Facts and disposition

GC_hardware_failure_01.json records the owner's SEL01 -> SEL20 -> SEL01 sequence, correct reported values, final transition frozen at the intermediate menu view, and recovery after the owner reconnected. Exact timing of the final reported value relative to reconnection is not separately established. Current active identity, postfailure Config and record integrity are unknown. STOP_HARDWARE_FAILURE.json applies. This is a genuine required-route hardware failure; no hardware PASS, merge or automatic cleanup is justified. Root cause remains UNPROVEN.

## Concrete source progress gap

The new request has no bounded opportunity to reach its sole consumer on GameCube. config/glyph/common/src/config.cpp:363 calls service_profile_selection only before the foreground backend SendReport calls. A request arriving after this check can wait while HAL/pico/src/comms/GamecubeBackend.cpp:27-36 stays in its poll-start loop. That loop scans inputs but neither checks pending requests nor returns on a bounded interval.

The exact linked dependency .pio/libdeps/glyph_mk6/joybus-pio/src/GamecubeConsole.cpp:76 calls joybus_receive_bytes(..., receive_timeout_us, false). joybus-pio/src/joybus.c:81-116 applies a timeout only after the first byte or when first_byte_can_timeout is true; the false path reaches pio_sm_get_blocking for that first byte. Without arriving traffic, core0 therefore need never return to the selector consumer. Additional unbounded line-high/send waits exist at joybus.c:65-77. This is an existing backend blocking behavior newly depended upon by the asynchronous selector; it is not a new claim that GC timing or serialization itself should be redesigned.

Meanwhile DefaultConfigMenu.cpp:248-253 deliberately ignores every control while Pending is nonzero. A request stranded behind a blocked GC poll therefore leaves the menu unresponsive indefinitely. This is a concrete liveness defect in the new request integration under a source-supported no-progress condition. It is a plausible explanation of the report, not demonstrated causation: no captured poll state or foreground program counter establishes that GC traffic actually stopped during this failure. A repair proposal must establish a safe bounded consumer opportunity outside an active Joybus command, preserving single core0 persistence ownership, backend protocol/timing and existing authority boundaries. No such repair has been implemented or authorized by this diagnosis.

## Intermediate menu view is explained, but does not locate the failure

SetStoredProfile (DefaultConfigMenu.cpp:288-292) only posts the ID and returns. ConfigMenu.cpp:89-99 then immediately moves to the parent page and resets the highlight. IntegratedDisplay.cpp:42-48 draws before processing controls, so the next display cycle can show that parent while core0 still has not started, is validating, or is saving the request. The old SetDefaultMode instead delays and reboots inside its action. The newly observed brief return-to-menu view thus follows directly from the asynchronous path. It does not prove a crash at that statement, nor distinguish waiting for GC traffic, persistence/flash lockout, or reset initiation.

## Save/reset ownership and remaining hypotheses

service_profile_selection (config.cpp:156-169) keeps the ID occupied through Persist and calls reboot_firmware only after Saved and committed scratch publication. On returned refusal it clears Pending. Persist uses one checked durable generation save, validates the selected body/context, and does not mutate ProfileStore. I found no direct source evidence here of an unconditional precommit reboot, second writer, accidental profile deletion or hot activation.

Other plausible locations require evidence: flash/other-core lockout while core1 continues display/RGB work; a blocked storage operation; or reset initiation after a completed save. GamecubeBackend.cpp:38-71 itself idles and resumes core1 around report construction/transmission, so a static menu also cannot identify which core stopped. Root separately inspects SDK scheduling/flash paths. Existing host selector/service tests do not execute real GameCube polling, physical flash lockout, core1 display/RGB scheduling or actual reset, so their PASS cannot exclude these hypotheses. Resource arithmetic PASS likewise does not prove liveness.

Any further device readback, fixture cleanup, retry, diagnostic firmware or repaired artifact requires its own authorized bounded continuation. Preserve the20 owned fixture bindings and all receipts; do not infer successful restoration from recovery after reconnect.
