# RT2 E5 investigation and raw diagnostic candidate result

Disposition: `MULTI_PROFILE_STORE_RT2_DCD_DIAGNOSTIC_READY`, subject to the final exact committed build/custody handoff. E5 status: `E5_DEFERRED_GPIO15_TIMING_UNBOUNDED`. The hypothesis is unresolved, not rejected. No exact alternative reset-to-SETUP defect or root cause is proven. No controller action or canonical merge was performed by source diagnosis.

## Findings

The b075 purple/violet observation is consistent with MAGENTA and supports `RT2_DCD_BUS_RESET_RECEIVED_NO_SETUP_OBSERVED`. Its independent reset-progress assignment does not prove pull-up was sampled ON; the separately observed normal-mode pull-up does not fill that RT2 evidence gap. [Physical adjudication](profile_store_rt2_e5_physical_adjudication.json) retains the original evidence and source correction.

SDK1.5.1 chip version1 means B0/B1 (E5 affected), version2 means B2 (E5 fixed); ROM versions1/2/3 distinguish B0/B1/B2. Actual chip revision remains UNKNOWN until next normal control. The candidate reports these values plus independently encoded eligible/enabled/would-execute bits. Enabled and would-execute remain false.

The official asynchronous workaround can force GPIO15's matrix input high during a scan and suppress MB1/LF3/LF4/LT5. MB1 priority can therefore be corrupted even though RT2 is another column. It also has unbounded SE0/CONNECTED waits and singleton saved-register state without reentry protection. A late RT2 gate misses possible pre-setup resets. The [source audit](profile_store_rt2_e5_source_audit.md) answers all eight GPIO questions, alarm/IRQ behavior, exact restoration scope, timing, silicon applicability and DCD prerequisites.

The [diagnostic contract](profile_store_rt2_e5_diagnostic_contract.md) defines raw SETUP (BLUE), DCD event (CYAN), attributable USB-task control progress (GREEN), and configured/inspection (WHITE). New DCD resets begin fresh sticky episodes, so old queued requests cannot hide the next failure. All MMIO samples are reads. No GPIO15 borrowing, USB control writes, new IRQ masking, timer callback, startup delay, continuous LED refresh, vendor-source patch or persistence semantic change is added.

## Validation completed before final exact-artifact freeze

- Actual pinned DCD/USBD/CDC/backend host model:28 cases PASS under ASan/UBSan, plus removed reset-hook negative detected. This covers raw SETUP with NVIC/INTE/PRIMASK delivery blocked; task-deferred SETUP; simultaneous SETUP+RESET ordering; old queued SETUP; reset interrupting foreground read or real control transfer; queue-full dropped reset; reset-stage markers; chip eligibility; replug epoch change; no continuous refresh; and unchanged storage.
- Full USB-startup/normal Configurator host regression PASS. The actual startup path, descriptors, USBD, CDC and backend remain exercised with explicit physical/NVIC/MMIO limits.
- Selection/recovery host regression PASS after adding the newly required diagnostic header to its extracted-setup fixture. No production behavior was changed for this fixture repair.
- Development `glyph_mk6` build PASS: RAM187724 bytes (+176 from b075); flash485060 bytes (+1704). These are development measurements, not final artifact custody or hardware resource measurements.
- Fresh independent source/design review APPROVED, with independent28-case and startup reruns PASS. [Review](profile_store_rt2_e5_independent_review.md) records the separate exact-artifact gate.
- Broader retained regression: all21 checks PASS after the documented fixture-include repair; the initial20/21 run and corrected selection run are retained separately. Pinned large-request RX, large-response TX and root-reconciliation regressions PASS.
- Root supervisor owns the final committed build, exact firmware identity, critical-input hashes, wrapper/ELF binding, target definitions, resource proof and immutable UF2 handoff. These must be checked in the final receipt rather than inferred from this pre-freeze report.

The development invocation automatically updated PlatformIO's build orchestrator `tool-scons` from4.40801.0 to4.41101.0. This was tooling orchestration, not a firmware SDK/source update. Do not claim identical SCons provenance to b075; preserve the actual final compiler/framework/library hashes and build log. No installed framework source was edited.

## Exactness and hardware boundary

Parent/input candidate: `b07502866c56a1c7e1e217132aea30366e234461`, tree `f6274649de4a7e620b19be795d16f95e53550683`, its parent `466f91ed867884640375627734d3473e9fb22c32`. Canonical base remains `6b73a7c507f35c111745c6bdd341618b490cbdcd`. This result intentionally avoids a self-referential candidate SHA; the later final receipt/HANDOFF binds the committed candidate SHA/tree and exact preserved UF2 SHA-256/size.

First complete the [b075 normal-boot read-only adjudication](profile_store_rt2_e5_device_adjudication.md). Only then use the [one-attempt hardware packet](profile_store_rt2_e5_hardware_packet.md) against the final exact artifact. Normal candidate Configurator enumeration, useful Config/profile correspondence, matrix sanity, actual silicon readback and candidate RT2 outcome are all hardware NOT_TESTED. No E5 fix executes in this artifact even if affected silicon is found. No exact-snapshot H2/H3 acceptance or merge is claimed.

Retained prior evidence: exact466 application phase11, late-CDC explanation rejected by pinned startup source, exact5913 identity control physically insufficient, separate root-reconciliation and GC V/W PASS. Selection remains NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE. Nunchuk NOT_TESTED. Root cause UNPROVEN.
