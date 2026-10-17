# Production reconstruction source audit

Authority: owner attachment e1c7a932-d829-4a8a-ab7d-c42e6144cd0e, read in full. Scope: canonical 6b73a7c507f35c111745c6bdd341618b490cbdcd through cb9a5ab580da8d7aa0a6ab3d5aed9aa7195b82aa. No controller action, build, commit, merge, or RT2 investigation was performed by this specialist. The root later delegated bounded retirement edits; this report is therefore source-authority/implementation evidence, **not** the required fresh independent candidate review.

## Base decision

Construct a new direct child of canonical. Use 4ee63e26c912a0954ab9d7028a70a04ff80ced8d as the reviewed *source reference* for general ProfileStore and the last general USB repair, then explicitly remove acceptance instrumentation and the original manual RT2 entry. Do not merge, cherry-pick wholesale, or call 4ee itself clean production. Its strict flag enables fault injection/resource/trace controls. No source changes after 4ee in the cb9 ancestry independently repair ordinary ProfileStore/transport behavior: the delta is the candidate fault-QUERY route followed by RT2 observers and workarounds. In particular current ProfileStore.cpp is byte-identical between 4ee and cb9 (SHA256 300d568a145baab2203a01906114244f6eed87443fa6241d6e14ad57e21b3c09).

The machine partition records all79 ancestry commits,49 with active firmware/schema/build changes, and382 net changed paths. It classifies actual semantics rather than treating `test:` commit subjects as nonproduction:2c742fdc/48ed606b actually alter staged root/record publication;1bd606a7 tightens production legacy normalization;81d4dcfd mixes real resource/transport hardening with a subsequently removed probe.

## Production retain (A)

- `HAL/pico/src/core/ProfileStore.cpp`, `include/core/ProfileStore.hpp`, `ProfileStoreStorage.hpp`, `ProfileStoreTransaction.hpp`, `Sha256.hpp`: exact serialized formats, redundant roots/control checkpoints, independent publication readback, immutable records, monotonic IDs, transaction identities/receipts, high-water fences, reconciliation, per-record health and protected garbage collection. Preserve actual checked operation/error handling while removing observer calls/state.
- Source anchors at cb9: directory validation/decode lines269–459; Begin/BeginRecovery465–513; control/bootstrap515–737; authoritative root selection739–774; checked publication776–804; reconciliation874–916; records925–1011; activation/health1013–1064; protected roots/capacity/GC1066–1257; replay/admission/commit1272–1327; CRUD1329–1480; authenticated migration1556–1760. These are source mechanisms, not new hardware acceptance.
- `CheckedStorage.cpp/.hpp`, `CheckedStorageFile.hpp`: same existing mounted LittleFS instance, explicit close/sync/readback, uncertain metadata acknowledgements, bounded path names, capacity/enumeration. The lost-open-acknowledgement close and explicit close despite observer failure are real handle-safety fixes. Preserve native handle close on all error paths; strip injectable hook state in production.
- `Persistence.cpp/.hpp`, `CompactConfigRecovery.hpp`, `ConfigWriteCandidate.hpp`: checked Config publication, temporary/prior/current selection, independent deterministic readback, unchanged live Config until durable commit, fencing/reconciliation and authenticated legacy capture. Static whole-Config workspace and streamed migration prevent oversized stack frames; these are resource hardening, separate from resource telemetry.
- `config_validation.cpp/.hpp`, RGB target validation/domain: shared Ultimate profile semantic validation independent of legacy Config envelope; strict current compact validation, narrow predecessor RGB unspecified/zero-color normalization. Retain stable ID and compact marker/reference rules.
- `mode_selection.cpp/.hpp`, `ModeSelectionTransaction.hpp`, `backend_init.cpp`, ordinary config.cpp pieces: checked durable destination before watchdog reboot; one-shot MDST scratch2 target matches durable Config and does not save again; held chord consumed across reset; stable profile activated at boot. MDST is a production namespace and must survive diagnostic scratch retirement.
- Normal Configurator CRUD, payload `has_profile`, complete READ/duplicate, bounded frame receive/response, correct ownership of COBS EOP, reference transaction receipt purity and live/durable reference separation remain production requirements.
- General `LastDiagnostic` checked-storage error labels are retained useful errors; they are distinct from retired candidate trace telemetry.

Historical helper nuance: `ProfileStoreAtomicCommit.hpp` and `ProfileStoreCapacity.hpp` remain useful test primitives, but the current checked `Publish` and mounted capacity calculation supersede their old active invocation. Their frozen512KiB capacity calculation is not current physical filesystem proof. The CREATE scratch probe introduced81d4/4ac was removed08296b0e; do not resurrect its deleted header or test as active firmware.

## General USB repairs (A) and limitations

`CoordinatedCdcStream.hpp`, `ConfiguratorBackend.cpp/.hpp` from4ee retain three independently justified mechanisms:

1. **d596 coordination:** shared `__usb_mutex` outer try-lock precedes native CDC FIFO/endpoint locks. `Guard` never spans task servicing, waiting, delay, or yielding. The USB task IRQ can defer while foreground holds it. This removes the source-supported lock inversion. Historical d596 full campaign failed; source reproduction does not locate the physical blocked PC.
2. **895 large TX:** service `TinyUSB_Device_Task` outside Guard, then flush under Guard. `ProfilePacketWriter` services after admitted writes and during wait; `finish` shares the original2s whole-packet deadline and drains the final short tail/COBS delimiter into the endpoint. Failure preserves delimiter resynchronization before a subsequent ProfileStore or legacy frame. Empty TX FIFO proves endpoint submission, not final host acknowledgement. Do not replace with bare `yield`, whose pinned FlushCDC lacks the outer mutex. Separate895 READ gate PASS must remain separate from895 full-campaign failure.
3. **4ee large RX:**64-byte native read cache amortizes locking. Explicit task passes before and after guarded reads service deferred completion/OUT rearm after releasing the mutex. `_rx_pos/_rx_end` cache survives COBS `next()`; only PacketIO consumes frame delimiters. Keep the5s receive deadline, oversize refusal and exactly one advance after EOP. RX diagnostic counters do not participate in any of these decisions and can compile out.

Relevant retained checkers: USBcoordination, CDCprogress, CDCrxprogress, timeout/resynchronization/strictprotocol, rxhost, readstorage and livenesshost. Their explicit frozen negative controls exercise lock ordering, missing deferred task passes, missing tail servicing, partial packets and ticket inertness. Their historical PASS is regression evidence; reconstructed exact source must rerun directly affected checks. No blanket whole-lineage hardware PASS is inferred from normal controls or a partial gate.

## Test/hardware harness only (B)

`ProfileStoreFaultControls.hpp`: volatile pending/armed rule, bounded skip/path-class mapping, ticket activation and `EndMutation` removal. It is acceptance-only, including the later2e0 narrow root-reconcile QUERY route. General `ProfileStore::QueryTransaction/ReconcileTransaction` is A; injected QUERY interception is B.

`ProfileStoreReadTrace.hpp`: callback may emit USB frames and can make READ fail when that observer fails; it cannot remain mutable active production state. Production definitions now make `Mark` constexpr true and `Failed` constexpr false, with no callback/state/Scope. STRICT host acceptance retains the original callback.

`ProfileStoreRxDiagnostics.hpp` and stream RX counters: candidate phase/count/timing observation; no transport authority. Backend members/sampling/population now compile only with STRICT. Stream counters/accessors compile only with STRICT or `GLYPH_CDC_COORDINATION_TEST`; the64-byte cache remains always functional on RP2040.

`ResourceDiagnostics.cpp/.hpp`, `StackWatermark.hpp`, `_sbrk` interposition and resource sampling calls: acceptance instrumentation. Crucial coupling: RESOURCE=1 with STRICT=0 is explicitly rejected by the header; leaving STRICT=1 merely to retain watermarks would re-enable fault controls. Ordinary production disables both flags and `_sbrk` wrapping. Preserve static workspace/frame/heap safety fixes and external resource measurement checkers independently.

CheckedStorage's hook pointer, hook setter and before/after injected returns now compile only for STRICT or explicit `GLYPH_CHECKED_STORAGE_TEST_MOUNT`. Production executes genuine checked operations and genuine errors without an activation pointer. Host test doubles may keep the test setter.

All host test fixtures and operator tools remain outside production. Historical evidence must remain identified with its original candidate and physical scope, not treated as current acceptance.

## RT2 retirement (C)

Exclude all `RecoveryStartupDiagnostics`, `RecoveryUsbDiagnostics`, `RecoveryTaskDiagnostics`, `RecoverySetupIrqDiagnostics`, `RecoveryPreSetupDiagnostics`, `RecoveryPrivateDcdDiagnostics`, `RecoveryPrivateDcdMarkers`, `RecoveryUsbReinitialization`, `ColdRecoveryBoot`, `ColdRecoveryIntent`, and cold USB shim files from active firmware. Exclude all RT2 builder scripts and tool-generated private DCD substitutions/wrappers from production link configuration. Preserve their historical source in Git and historical docs/fixtures.

Retire response recovery observer tags58–217 and all private-copy/IRQ/task/panic/endpoint wrappers, S0/S1 sampling, scratch3 diagnostic namespaces, LF/MB panels and timing/color observer work. Retire warm reset and cold reboot intent machinery. Do not remove production MDST scratch2 or ordinary bootloader/mode routing.

Remove the original manual `inputs.rt2 && !inputs.mb1` early setup route. Otherwise it still ships a now-deferred feature despite the absence of newer instrumentation. A held RT2 alone then follows ordinary startup; MB1 retains its existing firmware BOOTSEL request path. Physical recessed ROM BOOTSEL is independently owner-observed and not equivalent to MB1 software behavior.

## Automatic recovery (B7A) retained

`RecoveryInitialization.hpp` is **not an RT2 observer**. Keep it and automatic recovery setup calls. It installs the existing validator, checks availability, loads checked Config into an unpublished candidate before copying live state and calls `BeginRecovery`, never normal `Begin` initialization/migration/publication. Backend `SetRecoveryState` keeps mutation refusals: SET_CONFIG/CRUD/reference mutation are refused; unavailable/invalid Config is not serialized as valid data; useful inspection remains bounded. This is source safety/refusal authority, not a claim that the previously failed severe-state USB transport is now physically repaired. The owner defers B7B and permits catastrophic factory loss; B7A checks remain applicable.

## Wire compatibility and production admission

Keep original production protocol2 IDs/tags. Existing wire fields can remain inert for compatibility and test descriptors, with no persistent Config schema redesign. Production request identity still binds the complete known deterministic request. Do not silently discard nonzero candidate controls and then perform a real mutation.

Production now rejects nonzero `fault_kind/operation/phase/result/path_class/skip/clear/ticket/liveness_trace` before mutation/QUERY reconciliation or either receipt domain's storage work. ARM_STORAGE_FAULT13 and LIVENESS14 without such controls remain UNSUPPORTED. Strict host tests retain acceptance behavior. Root owns targeted actual-backend tests for these controls and zero diagnostic response values.

Retired request fields:14–20,22,23. Retained production request field21 is expected store incarnation. Retired strict response fields:25–30(resource),33–37/39–41(fault),42–57(trace/RX/reconcile-fault). Retained production response31 token high-water,32 mutation protocol version,38 incarnation. RT2-only58–217 must not populate/compile into production response descriptor. Never reuse or renumber retired wire tags. Leaving strict descriptor scalars inert does not itself create fault behavior; link/source tests must prove absence of state/activation.

## Uncertain/review gates (D)

No new substantive product architecture decision is required to retain the general repairs above. Remaining verification is exact reconstructed candidate evidence: production preprocessing/linkage must show no fault state/setter, trace callback/state/producer, RX counters, resource observer, RT2 wrappers/private DCD/cold symbols. Explicit test flags must keep harness behavior isolated. The root's exact build/map/resource check and a separate fresh review must verify these boundaries.

Do not claim chapter DONE, physical acceptance, root cause, factory erasure semantics, or automatic recovery transport repair from this source partition. Fresh hardware acceptance, where required for the resulting exact behavior-changing snapshot, remains a later owner-controlled gate. Ordinary UF2 flashing does not establish LittleFS erasure.
