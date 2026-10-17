<!-- Owner e1c7a932 production-reconciliation supersession — 2026-10-18 -->
> **Current owner scope supersedes the historical acceptance wording below.**
> RT2 non-destructive emergency Configurator is **DEFERRED BY OWNER**, not PASS.
> Physical BOOTSEL/RPI-RP2 recovery is owner-verified; ordinary UF2 erasure of
> LittleFS is not established. B7A automatic/normal safety remains required;
> B7B accepts destructive ROM factory recovery for this MVP. The chapter is
> **NOT DONE**. A clean production patchset is reconstructed directly from
> canonical6b73a7c; RT2 descendants and candidate fault hooks are not promoted.
> Exact new candidate/build/resource/review identities are bound by the final handoff.
> See [current closure](./profile_store_rt2_deferred_closure.md),
> [fresh B1–B10 table](./profile_store_production_reconciliation_blockers.md),
> and [nonexecuting factory follow-up](./profile_store_factory_recovery_followup.md).
> Historical evidence and separate-boot classifications remain unchanged;
> underlying RT2 cause remains **UNRESOLVED**. No controller action or canonical
> merge is part of this reconciliation; RT2 is not the default next task.

# Strict hardening source and hardware handoff

This is a new hardware candidate based on reconciliation
`04d7521fbdaeb313c1fe768a992a6c35847b68bf`. It is not a canonical integration or
a claim that f7ba82d4 hardware tests accept changed behavior. The external
content-addressed custody manifest binds the final candidate SHA/tree/parent,
base/merge-base, remote branch, exact committed build, final ELF/map/resource
report and UF2 bytes/hash. This document intentionally does not embed its own
future commit hash.

## Original strict matrix

| Blocker | Old defect | Repair and decisive regression | Source disposition / physical remainder |
|---|---|---|---|
| B1 | Count-only admission, no measured protected/reserve/GC model | Actual same-mounted geometry and block usage; protected two-root/prior/migration/active union;16KiB reserve and bounded GC. Pinned LittleFS real-adapter20-profile test; near-reserve CREATE/UPDATE/DUP refusal,64 ceiling,12 destructive GC boundaries/retry; frozen count-only negative. | Source closed; exact target capacity/refusal rows remain in packet. |
| B2 | Arduino void close could not prove checked persistence outcomes | Native same-mount checked open/write/sync/close/remove/rename, exact independent readback, definite/unknown outcomes and fences.54 injected primitive cases and4 old unchecked controls, including actual native sync error;37 Config cases. | Source closed; physical checked-boundary behavior remains in packet. |
| B3 | Ordinary chord path immediately activated a different profile | Durable destination save then reset; same destination/held chord no-op, failed/unknown saves no switch/reset. Actual selection TU and setup-route tests plus immediate-activation negative. | Source closed; chord/reset/held-through-boot target rows pending. |
| B4 | Caller digest, partial replay, unqueryable reference result | Firmware canonical SHA-256/full token; durable root and Config receipts; protocol2 monotonic token high water; exact replay before fences; accepted abort identity retained; uncertain reconciliation. All mutation/ref replay, changed fields, lost response, reset, interposed tokens, aborted-token and caller-digest negatives. | Source closed; exact target response-loss and injected rows pending. |
| B5 | Lone gen1 could reuse lost ID2; missing roots ambiguous | Two required roots, authenticated control checkpoint/intent and independent Config root-format marker. Exact lone-gen1/gen2 loss, both-root loss, older-pair rollback, all-v2-file loss with retainedv1, restart and non-reuse regressions; frozen ID2-reuse negative. | Source closed; non-destructive target root-read failure/reconcile row pending. |
| B6 | Native Config CRC receipt, weak retry/dependencies and unbounded import assumptions | Immutable exact persisted source SHA, one-profile streaming, mapping/dependency/compact hashes, count/high-water/reserve preflight. Exact A/B, changed source, missing/corrupt deps,63/64,overflow, import/completion boundary/reset cases, short-read rejection and mismatched-retry negative. | Source closed; upgrade and applicable target migration observations pending. |
| B7 | Manual recovery skipped store; rejected Config could dead-end | Shared validator/storage inspection in manual/automatic headless recovery, explicit health, read-only commands, MB1 priority. Actual extracted setup routes and old skipped-store/dead-refusal negatives. | Source closed; manual target route pending; automatic physical entry honestly NOT_TESTED if no preserved disposable scenario. |
| B8 |17-character truncation and no complete lazy health |33-byte name storage preserving32 UTF-8 bytes; explicit healthy/prior/missing/corrupt/unsupported inspection. All accepted lengths/rename/duplicate/reboot/upgrade and frozen truncation negative. | Source closed; target metadata/inspection rows pending. |
| B9 | Build-fit only; incomplete heap/whole-stack evidence | Actual ARM ABI/map/frame/call analysis, shared scratch, in-place directory reset, explicitly marked candidate heap/stack high-water instrumentation. F6 and aggregate-temporary negative controls retained. | Source-analysis/instrumentation closed; exact committed resource report in custody, physical peak/margin rows pending. No whole-target formal bound claimed. |
| B10 | No final target geometry/interruption acceptance | Bounded owner packet, explicit candidate-only one-shot fault controls, saved exact request/replay client and backup/identity-preservation stop rules. Disabled-hook and armed/triggered/clear/invalid controls tested. | Physical acceptance remains open; packet is prepared. No power-cut evidence invented. |

The [fresh independent review](profile_store_strict_hardening_independent_review.md)
records CLOSED/STILL BLOCKED against each original blocker, with physical-only
remainders distinguished from source defects. The historical SetConfig
aggregate checker still fails its frozen-scope guard (`C024 post-integration
change outside validation/evidence paths`); it is not reported as an aggregate
PASS. Direct affected production-unit checks are separate evidence.

## Format, capacity and resources

See [format/upgrade design](profile_store_strict_hardening_design.md),
[checked persistence proof](profile_store_checked_storage_source_proof.md) and
[protocol/transaction contract](profile_store_protocol_hardening.md).
The existing f7ba82d4 state upgrades without factory reset: incarnation,
generation8, high-water4/deletedID2, ID1rev2/ID3rev1/ID4rev1 and mode1→3/mode2→4
remain intact. V1 roots remain explicit read-only compatibility evidence; v2
publication never authorizes writable downgrade. New Config root-format2 marker
prevents resurrecting retained v1 roots after loss of all v2 files.

The real production adapter on pinned LittleFS RAM flash admits20 representative
profiles with total524288, used110592, free413696, protected143360, staging45056
and reserve16384 bytes; derived conservative representative admission32. These
are host measurements on target geometry, not actual device readings. Actual
free capacity and worst-case requested staging gate every admitted write.

Earlier84.4% RAM usage remains historical. The third preliminary integrated
build used187320/262144 bytes (71.5%) and474084/1568768 flash bytes (30.2%). Those
uncommitted preliminary values are not final artifact identity; the final
committed build/resource report in custody supersedes them. See
[resource method and limits](profile_store_strict_resource_diagnostics.md).
The final physical packet records boot/runtime/Configurator/recovery high-water
rows, including both4KiB scratch banks and heap arena peak. The SDK0x800
reservation is never equated to the whole-runtime stack limit.

## Acceptance boundary

Follow the [owner hardware packet](profile_store_strict_hardening_hardware_packet.md)
using only the exact custody artifact. No device action, factory reset, new
power-cut evidence or canonical merge occurred in this source-hardening run.
Candidate-only diagnostics/fault controls are conspicuous and must be removed
or explicitly accepted in a separately reviewed final production snapshot.
Existing hardware receipts, F1–F6, Nunchuk NOT_TESTED and non-blocking Runtime-B
physical observer debt remain unchanged.

## Later physical adjudication — 2026-10-16

Exact594066d9 / UF2fb8f005995b6feef33a196f1c3d8dbc6985350ca3d4bc40d22a03cf1724c4413
is permanently HARDWARE_FAIL — CONFIGURATOR_LIVENESS_FAILURE_DURING_FAULT_CAMPAIGN.
Earlier PASS rows remain scoped evidence; record/write injection was not executed.
See [liveness diagnosis](profile_store_fault_liveness_result.md) for retained
ARM_TRANSMISSION_UNPROVEN adjudication and the separately reviewed next candidate.
The source/build handoff above is historical and does not claim hardware acceptance.
