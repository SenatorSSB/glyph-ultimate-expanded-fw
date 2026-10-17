# RT2 first-task diagnostic result

Intended disposition: `MULTI_PROFILE_STORE_RT2_TASK_DRAIN_DIAGNOSTIC_READY`,
subject to exact committed build, independent final review and preserved custody.
No root-cause repair or hardware PASS is claimed.

Normal88ab physically established B2: E5 is inapplicable on this controller.
Its failed RT2 RED establishes no repeated-loop observation, not reset receipt
or task non-return. Historical b075 MAGENTA remains separate. The new source
permits continued queue replenishment while foreground owns the USB mutex, but
CDC/MIDI reset locks are another possible boundary. Neither is physically proven.

The candidate adds a core1 observer that survives a non-returning core0 task
under the documented scheduling assumptions. Its two existing MB1 pixels retain
first-invocation active/return/reset-count evidence separately from reset/SETUP/
control progress. The first pixel stays GREEN once ID1 returns; a later stall
is explicitly beyond its visible scope. No task drain limit, queue/drop change,
USB detach, persistence change, input change or E5 workaround is added.

Source/host validation:30 pinned sanitizer cases, four mutation controls,
publication-boundary probes and independent100,000-transition state stress PASS.
All21 broader checks, pinned large-request RX/large-response TX and root
reconciliation regressions PASS. Development build PASS RAM187852(+128 versus
88ab), flash487076(+2016); these are not final artifact identity or physical
watermarks. The existing28-case v4 predicate regression plus its negative,
20 startup cases, two normal Configurator controls and two removed-auto-CDC
negatives PASS. The startup suite initially failed its obsolete phase13 assertion;
a revised handoff assertion initially used phase9 instead of the actual phase8.
Independent review caught that fixture error; corrected rerun PASS verifies
core0 does not publish markers/LED frames after handoff. Those failed runs remain
retained alongside the passing report; no production change was needed.

The requested Astra specialist and fresh reviewer completed source work and
independent tests, then hit a runtime usage limit before final written receipts.
Root completed these source documents from the exact source and retained reports.
A replacement independent final review uses Sol/high under the repository model
routing for coupled technical verification; its actual outcome is recorded in
[review](profile_store_rt2_task_independent_review.md) and the final custody receipt.
Requested model identifiers are not independent runtime model telemetry.

Parent88ab0029d464175865e1ce3e9a19b462579ffed4; canonical base6b73a7c507f35c111745c6bdd341618b490cbdcd.
The final HANDOFF binds candidate SHA/tree, compiled identity, source/tool hashes,
resource deltas and exact UF2. [Source audit](profile_store_rt2_task_source_audit.md),
[contract](profile_store_rt2_task_diagnostic_contract.md), [88ab adjudication](profile_store_rt2_task_device_adjudication.md)
and [one-attempt packet](profile_store_rt2_task_hardware_packet.md) define the scope.
No controller action or canonical merge occurred. V/W PASS remains separate;
selection NOT_TESTED — FIXTURE_NOT_SAFELY_CONSTRUCTIBLE; Nunchuk NOT_TESTED.
