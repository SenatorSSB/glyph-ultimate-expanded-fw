# Production reconciliation: current B1–B10 dispositions

## Superseding exact-candidate hardware status — 2026-10-18

The exact `af69dd91e629db852f1d2371e8d8c2d6b624fc54` clean-production hardware
gate has passed. B9 and B10's exact-candidate hardware/correspondence clauses
are closed; their explicitly named power/reserve evidence debt remains
nonblocking and NOT_TESTED/NOT_REACHED as applicable. This does not convert
B7A physical failure-entry cases to PASS or reopen B7B RT2. Details are in the
[hardware acceptance result](profile_store_production_hardware_acceptance_result.md).

Authority: direct owner `e1c7a932-d829-4a8a-ab7d-c42e6144cd0e`, **2026-10-18**.
The [RT2 closure](profile_store_rt2_deferred_closure.md) supersedes the old
blocking manual-RT2 acceptance criterion. The chapter is **NOT DONE**.

This table re-evaluates the original strict review against later hardening,
physical receipts and the owner scope change. “CLOSED” applies to the original
defect; it does not accept a newly reconstructed candidate. Retained evidence
belongs to its exact tested source/artifact. Final clean-source tests, resources,
review and required exact hardware acceptance remain separate gates.

| Blocker | Current disposition | Evidence and remaining boundary |
|---|---|---|
| B1 — measured capacity/admission/reserve/GC | **NON-BLOCKING EVIDENCE DEBT**; original source defect closed | Checked same-mount geometry/admission, protected union, reserve and bounded GC replace count-only arithmetic. Strict pinned-LittleFS tests cover refusal. Physical capacity20 STATUS at generation26 reports total524288, used131072, free393216, protected172032, staging45056 and reserve16384; retained post-reboot LIST/READ payload witnesses exist. GC V/W injected remove failure/lost acknowledgement safely reconciled at166. Physical reserve refusal remains **NOT_TESTED / NOT_REACHED**: the125-update campaign still reported free368640 and mutation_feasible=true. Successful reclamation is not refusal PASS. |
| B2 — checked persistence outcomes | **CLOSED** original source defect | Native same-mount checked open/write/sync/close/remove/rename; independent exact readback; definite/unknown outcomes and fences. Retained54 primitive and37 Config source cases plus unchecked negatives; later4ee record/control/root/Config boundary receipts, including corrected Config P/Q/R1/S1/T0/U0/T1/U1. No electrical power-loss claim. Clean source must preserve this logic. |
| B3 — reboot-bound selection | **NON-BLOCKING EVIDENCE DEBT**; original source defect closed | Actual selection TU/setup-route tests prove checked destination save/reset, failed/unknown refusal, held/same-destination no-op and reject old immediate activation. Exact physical disposition remains `SELECTION_CHORD_PHYSICAL = NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE`. It is neither FAIL nor PASS. Any later safe fixture is separately scoped. |
| B4 — authenticated transactions and reconciliation | **CLOSED** original source defect | Firmware canonical SHA/full token, durable root/Config receipts, monotonic token high-water, replay/change rejection and uncertainty fences. Retained T1 lost-response QUERY/replay receipts cover CREATE/UPDATE/RENAME/REORDER/DUPLICATE/DELETE/reference. Do not claim unbounded receipt history; old tokens may truthfully expire. |
| B5 — stable identity/root recovery | **CLOSED** original source defect | Required roots, checkpoint/intent, independent Config root-format marker and lone-gen1/lost-root/rollback negatives. Exact2e0 root reconciliation physical PASS retained:165→166, actual ID22rev132 and useful IDs1/3/4 unchanged. Invalid earlier4ee fault route is historical test-route invalidity, not a product failure. No exhaustive physical arbitrary-file-loss claim. |
| B6 — authenticated streaming migration | **CLOSED** original source defect | Exact persisted legacy identity, one-profile streaming, authenticated mappings/dependencies/compact binding, capacity/high-water checks and retry/interruption negatives. Original migration/payload equality and strict upgrade readbacks retained. Migration PARTIAL denotes unavailable Runtime-B output discriminator, not failed persistence. No new candidate migration PASS inferred. |
| B7 — old combined recovery requirement | **SUPERSEDED** by B7A/B7B | **B7A remains required:** automatic/normal recovery safety, refusal and read-only initialization; retain source setup/storage tests. Automatic physical failure-entry cases remain NOT_TESTED where no safe preserved scenario exists. **B7B DEFERRED BY OWNER — DESTRUCTIVE ROM BOOTSEL FACTORY RECOVERY ACCEPTED FOR MVP.** Manual RT2 is not PASS. |
| B8 —32-byte metadata/lazy health | **CLOSED** original source defect |33-byte name storage preserves32 accepted UTF-8 bytes; source tests cover lengths/rename/duplicate/reboot and healthy/prior/missing/corrupt/unsupported health, including old truncation negative. Retained N1 metadata and H1/READ receipts corroborate ordinary target rows. Unperformed corrupt/prior health states are host-only. |
| B9 — resource sufficiency | **CLOSED source-level insufficiency**; exact candidate correspondence/hardware gates remain | Preliminary production source measurement RAM187320B/heap arena74628B, backend444B/stream88B, unchanged Config/profile/store ABI; CREATE/READ/RX enumerated bounds within4096B envelope. Static/workspace hardening retained; observers retired. Final exact committed reports and independent review are bound in the [clean production handoff contract](profile_store_production_reconciliation.md), not inherited. Runtime stack/heap peaks on this production image remain NOT_MEASURED; whole IRQ/ROM/indirect maximum not claimed. Prior instrumented receipts remain historical only. |
| B10 — target geometry/interruption | **NON-BLOCKING EVIDENCE DEBT** for unperformed power/reserve subcases; final exact hardware gate remains | Target geometry/capacity, corrected injected record/control/root/Config outcomes,2e0 root unreadability/reconciliation and GC V/W supersede “no target evidence.” `UNCONTROLLED_POWER_CUT = NOT_TESTED`; physical reserve refusal remains NOT_TESTED/NOT_REACHED. Injection is not power removal. Fresh exact clean-candidate hardware PASS is still required before merge. |

## Evidence authority and limits

The historical [strict review](profile_store_strict_done_review.md) correctly
blocked f7ba82d4 against its then-current requirements/source. The later
[strict-hardening result](profile_store_strict_hardening_result.md),
[checked-storage proof](profile_store_checked_storage_source_proof.md),
[transaction contract](profile_store_protocol_hardening.md), root-reconciliation
result and exact hardware receipts provide subsequent evidence. Earlier negative
F1–F6 and594/d596/895 candidate classifications remain unchanged. Target injected
fault tests and ordinary successful reboots are not uncontrolled power-cut tests.
The rebuilt production candidate receives no inherited physical acceptance.

Runtime-B remains **NOT_TESTED — PHYSICAL_RUNTIME_OBSERVER_UNAVAILABLE** and
non-blocking observer debt under the strict-review decision. Selection remains
**NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE**. Nunchuk remains **NOT_TESTED**.
No gameplay, unrelated backend, public-release or whole-program stability claim
is added. `UNDERLYING_RT2_USB_CAUSE = UNRESOLVED`.

## Smallest executable continuation

Finish the owner-authorized semantic clean-source reconstruction, retire
candidate-only behavior, run directly affected production host regressions,
build exact Glyph Mk6, review resources and obtain fresh independent review.
This is the current source task; final identity/results must be bound by the final exact-candidate handoff;
source-level closure never substitutes for that correspondence or hardware gate.

If that source gate passes, the next ordinary task is bounded **exact clean
production candidate normal Configurator/persistence/affected-transport hardware
acceptance**, with the existing useful state read-only adjudicated and preserved.
No RT2 attempt, cleanup, arbitrary fixture write or uncontrolled interruption is
implied. No hardware action is authorized during this reconciliation, and no
canonical merge occurs. The supervisor should record hardware wait and consume
actual exact evidence before proposing integration; if a concrete source blocker
remains, issue only that bounded implementation task.

The single [factory recovery item](profile_store_factory_recovery_followup.md)
is a separate safety deliverable. It does not block ordinary implementation
resume, but a verified destructive recovery process is needed before relying on
it for public shipping. A safe selection fixture is separate evidence work,
with no general Config-writer authority inferred.
