# Exact failed selector liveness audit

Owner-directed repair; source base4898951994bcabcaef2846145de2922a674656f8,
failed tree7b73fe086fcc6a0c4f5f8010751a64ec2dd07150. Live canonical failure
publication3a7a8174f10dfc11563b4a6a6d2029a4e2acf29f verified2026-10-22.
The complete new owner objective is retained in OWNER_OBJECTIVE.md. It authorizes
this bounded repair after the historical failure stop; no hardware acceptance,
device operation or source integration is authorized. Historical evidence stays
unchanged. Physical root cause remains UNPROVEN; Nunchuk NOT_TESTED.

## Exact ordering and ownership

DefaultConfigMenu.cpp SetStoredProfile posts a nonzero stable ID through
profile_selection::Request. The atomic compare-exchange releases one word;
Pending acquires it. Menu controls refuse all competing actions while occupied.
ConfigMenu's ordinary action return moves to its parent page; IntegratedDisplay
can redraw that parent in loop1. That redraw precedes neither a guaranteed core0
service nor a guaranteed reboot. The intermediate page is consistent with the
asynchronous implementation, not proof of any particular fault mechanism.

config/glyph/common/src/config.cpp loop calls service_profile_selection before
select_mode and all backend SendReport calls. A posted ID before that call is
served immediately. A request after it waits for SendReport, runtime identity,
metrics and optional keyboard report before the next application iteration.
Only core0 executes Persist against existing ConfigWriteCandidate storage;
core1 only reads published directory metadata and produces an ID. Persist loads
checked Config, reads selected body into the unused compact embedded slot,
validates exact native context/backend, clears that slot and makes one checked
generation save. Only Saved writes committed destination scratch registers and
calls reboot_firmware. Refusal completes the mailbox without reboot.

GamecubeBackend.cpp SendReport scans slow/medium then fast inputs and calls
WaitForPollStart repeatedly. After POLL only, it pauses core1, updates outputs,
copies the report fields, receives tail, transmits on non-ERROR and resumes
core1. loop1 otherwise schedules display then RGB; it cannot execute the core0
transaction. Persistence uses existing checked storage and flash critical
sections; no second writer or mutation owner is a repair option. These files
and selection validation/publication/reboot bodies remain out of repair scope.

## Every identified stranding point

1. Request just after service: GamecubeBackend waits before next service.
2. Request while first byte absent: Joybus receive false enters blocking FIFO
   read and has no first-byte timeout.
3. Repeated non-POLL PROBE/ORIGIN commands: backend continues internally rather
   than returning to application service.
4. Partial first byte: PIO autopush needs eight bits. Existing true timeout sees
   empty FIFO even though wire activity may already have begun. It cannot alone
   prove safe idle admission.
5. Active command/tail or transmit: preserve current command completion; no
   transaction may interrupt it. Existing send waits for line high and FIFO
   progress; malformed/stuck active traffic is distinct from absent first byte.
6. Checked storage uncertainty/refusal intentionally releases without reboot;
   it is not idle-poll starvation and must retain all existing semantics.

## Exact dependency and first-byte constraint

platformio.ini pins GregTurbo/joybus-pio f2f59c0; installed clean tracked HEAD is
f2f59c0aee07aea58cdd03616439bc3c6a8cbd8a. GamecubeConsole.cpp71-99 reads one
byte with first-byte timeout false, ignores count, dispatches actual byte.
joybus.c81-114 true timeout checks RX FIFO only. joybus.pio8-15 loops WAIT-low,
IN, WAIT-high, JMP for every bit; autopush threshold8 at55-57. PC==WAIT alone
cannot distinguish a partial byte between bits. GamecubeConsole.cpp102-124
retains50us per-tail-byte timeout and reply deadline;127-134 sends the exact
report structure. joybus.c64-78 queues TX; return is not TX-complete proof.

A naive false->true edit is unsafe: zero count must not dispatch uninitialized
command data, and empty FIFO must not be called idle when a byte is partial.
Independent source specialists confirmed this concrete constraint before edits.

## Bounded repair design under investigation

Use existing receive timeout as a service check; no request leaves receive
running. For pending selection only, qualify a safe idle boundary before
returning to core0. Minimal sticky first-bit PIO instrumentation may be needed:
replace WAIT-low[19] by undelayed WAIT-low plus nonwaiting IRQ[18], retaining
20 total cycles and unchanged IN sampling. Per-SM marker lifecycle must use
existing disabled reset/send boundaries; never erase activity on wait entry.
Atomic idle admission must distinguish marker, PC, GPIO and FIFO states, and
must not pause normal polling without a pending selection. Generated instruction
relocations, flag ownership and24-instruction fit need explicit proof. This is
not yet implementation, resource, build, review or hardware acceptance.
