# Exact private RP2040 DCD RT2 diagnostic contract

Latest direct owner correction52ec706f-e12c-4b47-9aa1-92678981065d rejects hardware
readiness of7e9e2ea0e3ac8c018dfa3088ef65af6b6c8cc820 (tree
9749862621c12d6c6459cdf2441120f7385fcf98, parent
88a36e67bcdf4acc447707da42687501afcd4d13). Its source/build/custody architecture
is accepted; its90 intentional instructions/36DMB before local INTS read are not.
This timing correction is a direct child of7e9e2e, with final identity in sealed
HANDOFF. Original private-observer authority184ed11d remains bounded by this
newer correction. Old7e9e2e UF2 is NOT authorized for installation.
Canonical6b73a7c507f35c111745c6bdd341618b490cbdcd unchanged. This is observation only:
no controller action, installed framework edit, TinyUSB upgrade, USB/endpoint repair,
manual SETUP service, IRQ force/rescan/retry, gate/branch/clear/reset/descriptor
change, workarounds, delays, persistence or mutation semantics, or canonical merge.

## Physical authority and variability

See profile_store_rt2_private_physical_adjudication.json. Exact88a36e normal control
owner-reported PASS: generation166, useful profiles/Config preserved, core0/1
min-free1856/3716, heap10716/capacity72156. Its ONE RT2 LF4GREEN/LF3OFF/LF5OFF,
black/no matching USB identity/no serial means latest observed handler returned,
no pre-SETUP/intercepted-panic/externalSETUP/downstream marker. Raw SETUP reproduction
in THIS boot UNKNOWN. MULTI_PROFILE_STORE_88A36E_RT2_PRE_SETUP_TRANSPORT_UNAVAILABLE.
No subsequent device action. Do not infer prebranch nonreturn/panic from this boot.

3761 separately established RAW_SETUP_OBSERVED_NO_DCD_SETUP_EVENT, one reset emitted,
processing completed/next queue read, no drop, pullupON.0f22 separately established
SETUP_INTERRUPT_STATUS_OBSERVED_NO_DCD_SETUP_EVENT, historical SIE/INTR/INTS positives
not necessarily simultaneous, no stronger sampled gate/trampoline/no downstream.
Do not combine milestones across boots. Variability retained. MB1 role decoding
PHYSICALLY_UNRELIABLE, B2/E5 physical inapplicability and historical V/W PASS remain
separate. Selection/Nunchuk NOT_TESTED. Root cause UNPROVEN.

## Exact source, insertion and source selection

Active pinned Arduino-Pico3.6.3/Adafruit2.3.0/TinyUSB0.16/SDK1.5.1 source:
/Users/rasmus.pekkarinen/.platformio/packages/framework-arduinopico/libraries/Adafruit_TinyUSB_Arduino/src/portable/raspberrypi/rp2040/dcd_rp2040.c
SHA25692a74cc04eef498a9523b3980c4b6b704990bff40531e23bb7ca490dd3358b12.
Repository pristine vendor/diagnostics/tinyusb-0.16.0/rp2040/dcd_rp2040.c preserves
exact18095 CRLF bytes, copyright/license and same hash. tools/rt2_private_dcd.py
verifies installed and pristine hashes, creates .pio/rt2-private-dcd/dcd_rp2040.c
with only one marker header include and12 post-read call insertions. Removing those added
lines must recover exact pristine hash. Patched hash and compile provenance are
recorded in final build/assembly receipts; no mutable installed-package patch.

Strict-only pre:builder_scripts/rt2_private_dcd.py routes the original exact source
node to one candidate object with cloned library environment and original header
parent. Original source is excluded, not compiled alongside it. Prelink requires
one replacement. Final ELF/map/compile-command and original/patched disassembly
prove single DCD implementation/candidate-owned source and actual status dataflow.
No E5/E15/E16 option changes. All18 existing external wrappers retain real-call
semantics and remain separately proved in final ELF. The registration wrapper
forwards the ORIGINAL private callback exactly once, same priority; there is no
per-invocation diagnostic trampoline or observer-enabled check before the private
INTS read. Registration metadata is recorded only during registration. Legacy
setup_irq/pre_setup IRQ pre/post/entry/return/age fields are unsupported zero in
response version2. Do not substitute post-read evidence for those pre-read fields. Private history records from the FIRST DCD call, including normal and early USB
initialization before BeginRecovery. Enable gates snapshot validity/publication
only and does not reset history. All boot paths incur bounded diagnostic stores;
old external observers still enable only in recovery. No disabled-hook fast-path
claim. Constant-initialized atomic BSS requires no dynamic bank constructor.

## Marker ABI and exact control flow

C-safe RecoveryPrivateDcdMarkers.h declares dedicated
GlyphDcdPrivateStatus(status), then GlyphDcdPrivateMarker(marker,value) for later
boundaries. The original INTS read is the first private source statement. No H0
callback, diagnostic statement, barrier, load, store or helper precedes it.
Only actual private handler calls it. Status/test arguments use the private local
variable, never an extra MMIO read. Each marker closes a single-writer aligned32
atomic bank BEFORE original vendor work resumes, so later nonreturn does not strand
an open sequence. No RMW/lock/alloc/log/Serial/TinyUSB/PIO/wait/recovery/MMIO writes
from hooks. The sole non-reentrant core0 USBCTRL writer uses aligned32 atomic payload
words: relaxed odd sequence store, release fence, relaxed data operations, release
even sequence store. One bounded core1 read uses initial acquire sequence, relaxed
data, acquire fence, final relaxed sequence; only matching even values are valid.
Initial acquire excludes older payload; reading any newer writer payload bridges
the release/acquire fences, forcing the final sequence beyond the old even value
by atomic coherence. Both fences and initial acquire/final release are required;
a release odd store alone is insufficient. Enabled is separately release/acquire.
No seq wrap during a bounded read is assumed; this is not an unbounded ABA proof.
State::Marker is inlined into each noinline C ABI, with no nested hook layer.
Added post-read calls/stores/barriers still perturb IRQ latency. Instruction/barrier inventories
are not cycle bounds or a negligible-perturbation claim.

| ID/bit | Boundary | Value |
|---|---|---|
|0 obsolete|NO target callback; bit0 means merged post-read entry|not called|
|1 H1|one dedicated publication after original sole INTS read; entry/ID/status/enable-window fact|actual local status|
|2 H2 SOF|after dcd_event_sof returns, only when SOF branch ran|0|
|3 H2 BUFF|after hw_handle_buff_status returns, only when branch ran|0|
|4 H3|after prebranches, immediately before original SETUP if|actual boolean status&SETUP|
|5 H4|first SETUP branch statement|0|
|6 H5 pointer|after DPRAM setup pointer acquisition|0|
|7 H5 PID|after reset_ep0_pid completes|0|
|8 H6|immediately before original dcd_event_setup_received|0|
|9 H7|immediately after call returns|0|
|10 H8 before|immediately before original SETUP_REC clear|0|
|11 H8 after|immediately after clear|0|
|12 H9|after original unhandled-IRQ check before normal return|0|

Marker bit13 records actual H3 FALSE, bit14 TRUE. Bit4 proves test reached.
Pointer acquisition is only address formation; the inline event helper performs
DPRAM request copy later. H6/H7 enclose that inline construction/copy/external call.
H7 does not prove queue accepted. Marker11 proves original clear store was executed,
not an electrical/latch-state guarantee. Marker12 means normal return boundary reached;
it is not proof of the completed machine return; the external trampoline was
removed to protect read timing. Earlier SOF/BUFF may be nonreturning
even if local SETUP was captured; H1 without H4 alone is not a surprising C-test
failure. H3/H2 and final assembly are needed before that inference.

## Fixed boot-lifetime selected history

Snapshot96B/24uint32: valid, entries, returns, setup_status_count, reset_status_count,
buff_status_count, multi_status_count, ever_status, latest_id, latest_status,
latest_markers, active, first_setup_id/status/markers, latest_setup_id/status/markers,
setup_test_false_count, marker_calls, enabled_setup_count, first_enabled_setup_id,
first_enabled_setup_status, first_enabled_setup_markers. Enabled means flag sampled
TRUE at exact H1/STATUS; core0 recovery enable cannot interleave an active core0 IRQ.
First-enabled markers update only that exact ID. Enable/BUS_RESET never erase history.
Latest invocation record plus first and latest
SETUP-containing selected records; no dynamic ring/flash persistence. Counts/IDs
saturate UINT32_MAX, a theoretical history-identity limit far outside one10s attempt;
not an unlimited unique-ID promise. FirstSETUP markers update only for that exactID.
LatestSETUP markers belong to latestSETUPid, latest invocation may be nonSETUP.
Relevant flags retain full local status incl SOF/BUFF/SETUP/reset/suspend/resume and
other bits; multi means any2bits in localstatus. Exact pinned bits checked by tests.

Core1 reads task/setup/prebranch/private caches without USB calls/locks, Config,
profile, input or display work. At>=10s valid bounded samples freeze under the SAME
single release publication and static whole-panel frame. No spin on invalid sample;
retry on next ordinary loop. Existing8word joined PIO FIFO emits one immutable
frame, no refresh/refill/DMA. Task age127 and prebranch age182 remain their own
meaning. Response-only183–208 version2 exposes private history via caller-owned
static96B backend cache sharing existing captured/live decision. Retain old raw
SIE/INTR/INTS sticky bits and individual response fields; never claim simultaneous.
Scratch3 v9 namespace525c retains525b/525a/5259/older acceptance; selectors0–2/SDK4–7
unchanged. No Config/Profile/Request/persisted-schema changes.

## Whole large-main-button panel

MB1 pixels0/1 DARK. LF4 pixels2/3; LF3 pixels4/5; LF5 pixels6/7. Both LEDs per button
SAME color. No MB/menu, orientation, transient/video or within-button roles.
RAW means ANY historical SIE/INTR/INTS SETUP-positive observation from retained
banks, not all3, current assertion, a packet count or one simultaneous snapshot.

| Button | Uniform settled colors |
|---|---|
|LF4 private status/raw|GREEN valid frozen/no private entry/no RAW; MAGENTA no entry/RAW; BLUE entries/no LOCAL SETUP/no RAW; CYAN entries/no LOCAL SETUP/RAW; ORANGE boot LOCAL SETUP exists only before enable; YELLOW any enabled LOCAL SETUP; RED intercepted USBCTRL panic overrides|
|LF3 first enabled LOCAL SETUP, else first boot record|OFF none; RED localSETUP/no branch entry (prebranch residual); ORANGE branch/pointer reached; YELLOW PID complete; CYAN H6; GREEN H7; WHITE clear-after or normal-return reached|
|LF5 downstream|OFF none; ORANGE externalSETUP entry; MAGENTA old hook; CYAN accepted; YELLOW consumed; BLUE control began; GREEN descriptor/address; WHITE configured-current/inspection; RED SETUP drop|

All-dark/unclear remains UNKNOWN, not noentry evidence. LF4GREEN/BLUE is positive
ready/no RAW-observed evidence, not proof SETUP never existed. LF4CYAN/MAGENTA
supports CASE A raw positive without private SETUP history. LF4YELLOW supersedes RAW encoding when an enabled local SETUP exists. LF4ORANGE
explicitly identifies solely pre-enable private SETUP: its LF3 first-boot progress
cannot be compared to the recovery-only external event bank as an event mismatch.
Individual raw values remain telemetry. LF3 selects FIRST ENABLED SETUP record when
available, otherwise FIRST BOOT SETUP record; never joins different invocations;
LF5 is retained downstream history. RED panic masks LF4status/raw; telemetry or
later separate evidence needed, never infer hidden panel facts.

## Cases and post-hardware classifications

A: RAWpositive, no boot-lifetime localSETUP snapshots -> MULTI_PROFILE_STORE_RT2_SETUP_NOT_SNAPSHOTTED_BY_DCD.
This narrows dispatch/scheduling/timing/hardware residual, not branch failure.
B: localSETUP, no branchentry -> examine prebranch completion/H3/assembly/corruption/
instrumentation before any claim. It can still be prebranch nonreturn.
C: localSETUP/entry but noH6 -> MULTI_PROFILE_STORE_RT2_EARLY_SETUP_BRANCH_PHYSICALLY_NARROWED.
D: ENABLED-record H6/externalboundaryabsent -> inspect exact inline event construction/DPRAM copy/
call assembly and instrumentation; do not invent endpoint repair.
E: ENABLED-record H7 -> classify queue/downstream; old noevent boundary did not reproduce.
Pre-enable-only SETUP (LF4ORANGE) remains historical private evidence; it does not
prove event/queue loss after recovery enable. Treat that observation window honestly.
F: no boot-lifetime localSETUP/noRAW -> MULTI_PROFILE_STORE_RT2_PRIVATE_HANDLER_ATTEMPT_NONDIAGNOSTIC.
No unseen-sample/never-occurred claim. Root cause UNPROVEN in all source results.

## Hardware stop and proof

Separate profile_store_rt2_private_device_adjudication.md: exactly one ordinary
normal88a36e boot/read-only Configurator/deviceinfo/PULSE/STATUS/allLIST/READ1/3/4/22/
GET_CONFIG, expected incarnation1/store166, useful bytes unchanged, Config1182731055/
exact252bytes, no uncertainty/unresolvedreceipt/pendingarmedfault/resources, STOP.
Any failure blocks replacement. No QUERYrepair/cleanup/RT2retry.
After PASS only: exact new manualinstall, normalcontrol/authority/resources,
ONE RT2/wait10s/maincolors/display/USB/serial, noendpoint STOPINPLACE, endpoint
boundedread-onlythenSTOP. No sourceagent deviceactions, no secondattempt/video/GC/
selection/cleanup. Full packet profile_store_rt2_private_hardware_packet.md.

Final source/harness/integration/assembly/resource/custody and fresh independent
review receipts bind exact candidate SHA/tree/parent/UF2 in sealed HANDOFF.
Host stop throws model nonreturn without hanging process and never change target
panic. Marker-removal negatives and actual patched-source branches required.
The source and assembly gates reject any pre-read diagnostic, DMB, helper,
atomic store, second INTS read, reread argument, moved STATUS marker, reordered
boundary, and wrong saved-value dataflow. Final disassembly separately reports
compiler prologue differences and intentional post-read costs. Zero intentional
pre-read instructions/barriers does not mean identical whole-handler timing or
zero observer perturbation. No whole-target stack/cycle bound or new physical acceptance claimed. Framework
aggregate NOT_RUN/NOT_CLAIMED; prior debt remains. Hardware NOT_TESTED.
