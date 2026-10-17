# RT2 deferred closure and production recovery policy

Current owner disposition, **2026-10-18**: **RT2 NON-DESTRUCTIVE RECOVERY IS DEFERRED**.
Authority is the direct owner request `e1c7a932-d829-4a8a-ab7d-c42e6144cd0e`
(`Pasted text.txt`). This changes the MVP acceptance scope; it does not fabricate
RT2 acceptance. The chapter is **NOT DONE**.

`UNDERLYING_RT2_USB_CAUSE = UNRESOLVED`.

## Physical ROM recovery evidence

`GLYPH_MK6_ROM_BOOTSEL_RECOVERY_PHYSICALLY_VERIFIED` records the owner's
physical observation on the test controller:

- A recessed physical hole/button is labelled **BOOTSEL**.
- Holding that internal button while connecting to a Mac exposes **RPI-RP2**.
- The application LEDs and miniscreen do not initialize in this route.

The supported interpretation is an independent RP2040 ROM route below the
application firmware. It does not depend on normal Glyph startup,
ProfileStore/Config validity or firmware RT2, and provides a last-resort UF2
installation route. No additional pin wiring, universal failure immunity or
successful persistent-state erasure was observed. **Ordinary UF2 flashing is
not assumed to erase LittleFS.**

## Product acceptance boundary

**B7A — automatic/normal recovery safety and refusal semantics** remain
production requirements: normal Configurator, checked atomicity and
reconciliation, per-profile corruption isolation, read-only recovery/refusal
policy and other existing non-destructive normal recovery mechanisms.
Preserving these source paths does not establish unperformed physical entry
cases.

**B7B — manual RT2 non-destructive Configurator** is
**DEFERRED BY OWNER — DESTRUCTIVE ROM BOOTSEL FACTORY RECOVERY ACCEPTED FOR MVP**.
It is not PASS. Catastrophic recovery may lose local ProfileStore and Config;
a future verified Fresh/Factory Recovery artifact/process must deliberately
restore defaults. See the single bounded
[factory-recovery follow-up](profile_store_factory_recovery_followup.md).

User-facing tradeoff: a sufficiently severe firmware, application or persistent
state failure may require factory recovery and loss of locally stored profiles,
but the verified ROM installation route provides last-resort recovery below the
application. RT2 remains a future enhancement for preserving or inspecting
state in that severe case.

## Historical physical classifications

These are **separate physical boots**, with their original scopes and caveats.
No row supplies a missing observation in another row. The failed final
workaround does not disprove any earlier positive observation. Historical
contracts, receipts, source audits, artifacts and failed candidates remain
retained as evidence; their hardware packets are not current instructions.

| Retained classification | Bounded physical scope |
|---|---|
| `MULTI_PROFILE_STORE_466` application-phase evidence | Normal control PASS; manual RT2 reached application phase11/repeated-loop sampling after inspection, Serial, backend, read-only installation and publication. No enumeration or private-DCD progression established. The phase11 MB1 yellow observation alone does not encode every upper phase bit. |
| `MULTI_PROFILE_STORE_5913` identity A/B transport unavailable | Normal control PASS; one bootstrap-identity-retention RT2 attempt exposed no matching USB device or serial. Retaining the identity was insufficient in that boot. Coarse RED does not prove a SendReport hang. |
| `RT2_DCD_BUS_RESET_RECEIVED_NO_SETUP_OBSERVED` | Exact b075 purple/violet was interpreted as frozen MAGENTA, conditional on color interpretation and indicator delivery: DCD bus-reset milestone, no later milestone, black display/no endpoint. MAGENTA does not require a prior pull-up-ON sample; no physical packet history or cause proved. |
| `E5_PHYSICALLY_INAPPLICABLE_ON_TEST_CONTROLLER` | Exact 88ab normal chip-version2/ROM3 identifies B2; E5 is disabled/inapplicable on this controller. This does not identify the RT2 cause. |
| `MULTI_PROFILE_STORE_88AB_RT2_RAW_SETUP_DIAGNOSTIC_TRANSPORT_UNAVAILABLE` | Its one RED/black/no USB/no endpoint attempt supports `REPEATED_RECOVERY_LOOP_OBSERVATION_NOT_ESTABLISHED`. Bus reset and task entry/return in that boot remain UNKNOWN; b075 observations are not imported. |
| `MULTI_PROFILE_STORE_3761_RT2_COMPREHENSIVE_TRANSPORT_UNAVAILABLE` | Its single settled panel/black/no USB/no endpoint attempt established one reset emission; consumed reset completed CDC/MIDI/control reset and reached the next queue read. No queue drop or downstream progression established. |
| `RAW_SETUP_OBSERVED_NO_DCD_SETUP_EVENT` | Exact 3761 aggregate raw SIE/INTR/INTS SETUP evidence was positive; its exact layer was not distinguished. Pull-up register sampled ON is not electrical proof of host recognition. |
| `MB1_PAIR_ROLE_DECODING = PHYSICALLY_UNRELIABLE` | Exact 3761 MB1 pair cannot attribute task invocation/return/reset. Reliable main-button evidence retains its separate scope. |
| `MULTI_PROFILE_STORE_0F22_RT2_SETUP_IRQ_TRANSPORT_UNAVAILABLE` | Exact 0f22 normal control PASS; one WHITE/YELLOW/OFF attempt, black display/no USB/no serial. |
| `SETUP_INTERRUPT_STATUS_OBSERVED_NO_DCD_SETUP_EVENT` | Exact 0f22 sticky positive SIE/INTR/INTS samples are historical sequential positives, **not proven simultaneous**. No stronger sampled gate/trampoline or downstream condition. Neither IRQ non-entry nor panic was proved. |
| `MULTI_PROFILE_STORE_88A36E_RT2_PRE_SETUP_TRANSPORT_UNAVAILABLE` | One GREEN/OFF/OFF attempt; latest observed handler returned, no specific pre-SETUP/panic/downstream marker. Raw SETUP reproduction in this boot UNKNOWN. Earlier 3761/0f22 positives remain intact. |
| `MULTI_PROFILE_STORE_RT2_SETUP_NOT_SNAPSHOTTED_BY_DCD` | Exact d30e one CYAN/OFF/OFF attempt: private initial S0 snapshots occurred and none contained SETUP; historical raw positive. S0/S1 ordering was not observed by this candidate. Not a SETUP-branch failure. |
| `MULTI_PROFILE_STORE_RT2_SOFTWARE_OBSERVABILITY_LIMIT_REACHED` | Exact 60313 one CYAN/OFF/OFF/black/no USB/no endpoint attempt under minimal S0/S1 instrumentation. Sampling does not observe electrical traffic or actual EXC_RETURN, or prove a silicon/NVIC cause. Private timing/late-return caveats remain. |
| `MULTI_PROFILE_STORE_RT2_RECOVERY_USB_REINITIALIZATION_TRANSPORT_FAIL` | Exact e6de normal control PASS; one failed manual warm-reinitialization attempt, black/no USB/no endpoint, ancillary LF4 CYAN. Earlier boots remain separate. |
| `MULTI_PROFILE_STORE_RT2_TWO_STAGE_COLD_RECOVERY_TRANSPORT_FAIL` | Exact cb9 normal control is corroborated by firmware cb9a5ab5, incarnation1/generation166, Config1182731055 and accepted payload hashes. One RT2 authorization, buttons released, black/off/no USB/no endpoint, ancillary LF4 CYAN. Operator records `BOOT_A_AUTOMATIC_REBOOT: UNKNOWN`; no physical Boot A reset or Boot B phase is inferred. |

Exact diagnostic descendant
`cb9a5ab580da8d7aa0a6ab3d5aed9aa7195b82aa` is not the production base and must
not be promoted as production. Its old source handoff's hardware-NOT_TESTED
snapshot is chronologically superseded by the later owner-reported failed
attempt, within the scope above. No root cause is claimed.

Historical authorities include the individual `profile_store_rt2_*` physical
adjudication documents, the owner's prior result attachments, and retained
`local_backups/hardware-tests/multi-profile-store-strict-hardening-20261016/`
operator receipts. Some older identity snapshots contain stale expected-candidate
template fields; those fields do not bind a physical candidate. Actual device
information, exact owner identification and artifact custody supply the bounded
binding, as the corresponding adjudications explain.

## Production continuation

The new production branch starts directly from canonical
`6b73a7c507f35c111745c6bdd341618b490cbdcd`, using semantic reconstruction rather
than promotion of the RT2 descendant. Retain independently justified
ProfileStore/Config repairs and ordinary d596 coordination, 895 TX progress and
4ee RX progress corrections. Retire RT2 phase/color/panel/raw-SETUP/IRQ/panic/S0/S1
observers, instrumented private DCD replacement, warm/cold experiments and
candidate-only fault hooks from compiled production. Preserve useful test
fixtures and historical evidence outside that path.

Exact new candidate SHA/tree/parent, committed build, resources, independent
review and custody are **PENDING** at this documentation snapshot and must be
recorded in its final handoff. Historical hardware PASS does not accept the new
binary. The [fresh blocker table](profile_store_production_reconciliation_blockers.md)
sets the continuation boundary. No controller action or canonical merge is
part of this source reconciliation.

Ordinary supervisor workflow resumes with bounded implementation, review, exact
candidate, genuinely required exact hardware acceptance and only then authorized
canonical integration. RT2 is not the default next task; reopening requires
explicit owner direction or genuinely new evidence modality, such as an external
USB analyzer.
