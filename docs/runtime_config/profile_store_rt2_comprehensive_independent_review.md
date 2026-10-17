# Fresh independent comprehensive RT2 source review

Reviewer: fresh_comprehensive_review,2026-10-17. Scope is the direct3b5c descendant in `/private/tmp/glyph-profile-store-rt2-comprehensive`, under owner request1ff9ec44. No controller operation, vendor edit, Git mutation or canonical merge was performed by this reviewer.

Result: **PASS_SOURCE_WITH_RESIDUALS; exact final artifact review pending**. No blocking source defect found in the reviewed hashes below. This is candidate preparation review, not physical USB acceptance and not root-cause proof.

## Findings and source boundaries

- All fourteen wrappers call their real function once with original arguments and preserve returned values. The queue wrappers identify `_usbd_qdef.ff` directly; they do not change FIFO contents, send results, queue order, capacity or task drain policy. The exact Pico OSAL source holds its existing queue critical section across `tu_fifo_write/read`; queue acceptance and failed RESET/SETUP are observed before leaving that lock. IRQ callback emission is recorded separately after that boundary, so emission is not treated as acceptance. The local XInput reset has no safe external relocation; its empty body remains unmodified. Final ELF proof must verify all fourteen bindings, builtin class function-pointer relocations, and `_usbd_qdef` identity.
- Foreground entry requires core0, exception0 and the post-loop arm. Calls are serialized by the existing outer USB mutex. Entry/return IDs have explicit atomic publication points. DCD reset attribution reads the active ID at emission, separately preserving pre-first, first, current and post-first counts. The old first-return flag cannot conceal a later active ID. Sequence banks reject an in-progress or changed publication with one bounded attempt; core1 retries on a later ordinary loop. Producer observations remain inside the existing masked queue critical section. No observer RMW, allocation, mutex, busy polling or new USB policy was found.
- The task bank has serialized USB-task ownership. Class wrappers are task-context boundaries; the inspection flag has its own foreground atomic, avoiding nested writers to the task sequence bank. Queue-consumed RESET clears the configuration shadow before class callbacks. Consequently green enumeration is the last completed configuration boundary with no later observed consumed-reset/deconfiguration, not an atomic direct read of TinyUSB mounted state.
- Core1 reads only non-destructive USB SIE/INTR/INTS and pullup registers plus bounded atomic banks. No TinyUSB call, outer mutex, Configurator, persistence, inputs, normal display or gameplay initialization was added. Existing boot-state acquire/release and core1 recovery/refused/normal guards remain unchanged from3b5c. A core0 task which does not return cannot prevent the core1 publication branch.
- Mk6 source maps pixels0/1=MB1,2/3=LF4,4/5=LF3,6/7=LF5 on GPIO11. Source proves association/order, not the human orientation or optical separability of the two pixels within each button. Disjoint role palettes within each pair avoid requiring orientation. A photograph/observation must still resolve both colors; an unresolved/blended pair remains unknown.
- The dedicated PIO program emits24bits per word at800kHz. Joined TX FIFO holds all eight words while its SM is disabled; eight nonblocking puts cannot need a CPU refill. Transmission takes240us, so the inherited200us busy interval returns before the last bits finish. This is safe for the frozen single panel because hardware finishes independently and stalls low after the final word, with no subsequent frame. No system clock or USB timing change was added. The panel waits for a valid atomic sample after the10-second threshold and then never refreshes, including while further DCD IRQs continue.

## Explicit limits required in the handoff

1. A frozen active task color is a finite observation, never proof of infinite non-return. Later WHITE requires the same active ID observed for at least1s; recent later activity is YELLOW. First ORANGE alone means first ID active at freeze and may have entered late. The serial age field carries the measured age; an absent endpoint cannot supply it.
2. The static panel separately represents total and current-invocation reset count. It cannot distinguish all pre-first versus post-first versus prior-invocation histories after a task returned; those are telemetry counters. The last reset-stage pixel distinguishes CDC/MIDI and completion/continuation. Narrower MSC/HID entry/return masks are telemetry only. These are explicit panel-resolution residuals when the serial endpoint is absent.
3. Core1 raw SETUP sampling may miss a brief hardware latch cleared between samples; DCD emission remains an independent later fact. No raw observation plus no event is not proof that no electrical SETUP existed. Host never sending versus PHY never latching remains HOST_PHY_SETUP_RESIDUAL; external host trace/protocol analysis is the next evidence source.
4. Added observation work is bounded but not timing-neutral. Queue wrappers lengthen existing IRQ-masked critical sections by atomics and count sampling; no negligible-perturbation or causal-exoneration claim is supported without target timing/physical comparison. This does not introduce a task budget or change drain semantics.
5. Across distinct single-writer banks a snapshot represents compatible published boundaries, not a globally atomic hardware instant. Queue acceptance can momentarily precede the subsequent DCD hook flag. Saturation and mixed/odd snapshots must remain honest invalid/finite observations.

## Validation inspected and independently performed

The comprehensive harness receipt reports55 source-faithful ASan/UBSan scenarios, seven required removal-negative controls detected, and bounded publication-interruption tests PASS. Current reviewed firmware/header hashes match its `source_hashes`. The harness keeps pinned USBD/CDC/MSC/HID/MIDI bodies and extracted XInput reset bodies, with explicit host scheduling/stall/MMIO/lock/packet-completion models. It is not macOS USB or physical causality proof. Host-only exceptions simulate a paused foreground owner without invoking target changes.

Reviewer independently compiled and ran an additional ASan/UBSan state-bank check covering pre/first/later reset attribution, completion/continuation, later active-stage isolation, one control-begin per SETUP, simultaneous RESET+SETUP loss classification, configuration retirement and balanced task returns: PASS. Source inspection also verified pinned OSAL critical sections, reset ordering, process-control callback boundary and post-reset task loop. Preliminary target ELF contains all fourteen wrappers and global `_usbd_qdef`; final committed ELF/resource/custody proof remains required.

## Reviewed file hashes

```json
{
  "HAL/pico/src/core/RecoveryUsbDiagnostics.cpp": "dfb463974d0b6a1a18d8909069dada76419afc7e9b749000a8e1b3cfad17b4c2",
  "HAL/pico/src/core/RecoveryStartupDiagnostics.cpp": "58069a22693d2610a6de4aad0c06151e17df9faa23ed54c927851fbf1e903123",
  "include/core/RecoveryTaskDiagnostics.hpp": "d3219c837baca3ca62c56c758bd3dfdf4a9d95c02ca71ba04616e295f16955c6",
  "builder_scripts/rt2_dcd_observer.py": "dc2f9fdfb85c637377bbbb6e43d9c9082beab8862693055e5a86db5ae0964118",
  "HAL/pico/src/comms/ConfiguratorBackend.cpp": "852dddf71d0d91f7ade5d038d8692f98f40777e4760da7141e1cd764fc6c1bc8",
  "schema/haybox/config.proto": "d8aee9a1c929e8234a3e54e456f1faa12d0cd54653763ba3e86be78777706137",
  "tools/check_glyph_rt2_comprehensive.py": "e33ea0abc3c903ff08df0eec7f867f317bccc3e2422f524d3a5743b9a2fa5930",
  "tools/fixtures/rt2_comprehensive_host/cases.inc": "5062e4e54e6ae6cef2faaaee8c9fee1a44411668dd3172431b1601ffa7e9c146",
  "tools/fixtures/rt2_comprehensive_host/checks.inc": "d03536ca49908640c274521f645d6fca6c26074642dc2b572308522822299068",
  "tools/fixtures/rt2_comprehensive_host/publication.cpp": "c1c364bf225b51a53e9ac5ce71576efb05e363e1665036da0bda7e5de92442e9"
}
```

## Capture correspondence follow-up review

The final capture addition writes a180-byte immutable `Snapshot` on core1 before the one release store to `dashboard`. `CapturedTask()` performs an acquire load and returns the copy only after that publication. Subsequent core1 loops never rewrite the copy. This establishes safe publication without a shared mutable copy or another lock. Header/getter copies introduce target stack work that must be included in final core0 and core1 stack reports; host `sizeof(Snapshot)=180`, `sizeof(State)=224`, with target confirmation still required.

One response correspondence race was identified during review: a prepublication fallback task snapshot could be followed by an independently loaded nonzero dashboard. The author corrected this by fixing `captured` from the acquired snapshot decision before fallback, emitting `task.dashboard` and capture times only when that same decision is true. Reviewed correction PASS. A response before publication has dashboard0; a response after publication has the immutable captured task bank and matching dashboard. Old raw USB fields intentionally remain live/asynchronous and must be labeled separately. New readonly response field128 carries the configuration shadow. No persistent schema or USB behavior change was introduced.

The earlier55-case receipt preceded this follow-up; the required final harness rerun must bind these updated hashes before handoff. Final ELF/build/resource/custody review also remains pending.

```json
{
  "HAL/pico/src/core/RecoveryStartupDiagnostics.cpp": "58069a22693d2610a6de4aad0c06151e17df9faa23ed54c927851fbf1e903123",
  "HAL/pico/src/comms/ConfiguratorBackend.cpp": "dd9b78e847bddfeda6ecd03ef84d103048021bc19a0fbed916f8d3ca30811dcc",
  "include/core/RecoveryStartupDiagnostics.hpp": "258bad6ac6bab1f0ca1b4b94f3bf7f150367de595556606a52ec11bc9cdaa4a4",
  "schema/haybox/config.proto": "d8aee9a1c929e8234a3e54e456f1faa12d0cd54653763ba3e86be78777706137"
}
```

## Final precommit source, validation and packet approval

The final comprehensive harness receipt reports **56 scenarios,8 detected removal mutants and publication boundary checks PASS** with ASan/UBSan. Independently checked all28 source-hash bindings in that receipt against current files: **zero mismatches**. This supersedes the earlier pending capture-harness note above. The frozen-capture test includes continued postcapture IRQs and response/panel immutability.

Read in full the new comprehensive contract, A-Q coverage JSON, separate stopped88ab adjudication and one-attempt hardware packet, plus specialist source audit. They preserve the separate466/5913/b075/88ab evidence, physically inapplicable E5, untested3b5c, candidate-only observer scope, no canonical merge, exact artifact gate, one normal88ab adjudication before replacement, accepted useful profile/Config authority, and exactly one later diagnostic RT2 attempt. Endpoint absence stops in place. No packet authorizes source-agent device operations. Residuals are explicit, including panel aggregation, optical component resolution, raw-latch sampling, finite active duration and host/PHY ambiguity; queue acceptance is actually instrumented rather than falsely left unknown. Root cause stays UNPROVEN.

Precommit documentation approval: **PASS_WITH_RESIDUALS**, with one minor stale contract label identified to the author for correction before commit: comprehensive task diagnostic version is5, matching `response.recovery_task_version=5`; startup version6 is correct. This is a prose-version alignment, no source change requested. Final committed target build, all14 incoming call/table wrapper bindings, both-core stack/resources and immutable custody still need the separately requested artifact approval. No final artifact or hardware PASS is implied by this source review.

Final harness report SHA-256: `dc01ae6b4af0f5c11075d1ac6249ca4aa347abe5dd70933cc98a76b3b5488f39`.
