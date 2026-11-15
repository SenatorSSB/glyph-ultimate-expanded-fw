# Glyph Mk6 optimization qualification

**GLYPH OPTIMIZATION CANDIDATE READY for host-to-hardware handoff. Physical status is HARDWARE_TEST_REQUIRED. Hold public open beta.** The primary qualification target is Super Smash Bros. Ultimate through the GameCube adapter on an identified Glyph Mk6. The result covers one host-built candidate with three reviewed changes.

## Exact admission and source

| Record | Git identity |
| --- | --- |
| Live canonical starting point, configurator | `2bcb5104054f64d8b9c1af9dd1be4a974112f8ec` |
| Owner-approved proposal | `9db7e3f301d5b006cdbdd598353429b2286de0ed` |
| Independent proposal review | `a3db3d224a5db934166b7cb6d5cdada92ea26f5a` |
| Direct GOPT-0 through GOPT-4 admission | `2ff7dd72a43e1023023087b408eab630233d2cb3` |
| Recorded group scopes and controls | `835d1822ef1ab0a2fa34905288ddb623702e1a42` |
| Input loop | `7877e68aaf365a31abdbb55a89837b18a4da992d` |
| Dashboard | `5e3d0e380a078f6e4f3fa3fca64d8efa2e5e83f9` |
| Saved Config | `127d7131cbb75f92d550a398fcbd350b9e56a528` |
| Dashboard review correction and terminal-state controls | `a313afd454d420e10cedd71c36ad3a7c24874e56` |
| Final source and CRC stack-lifetime correction, codex/gopt-host-stabilization | `55739675e5706ea8799265c4221724ac4f2dce9b` |
| Candidate Git tree | `87ad82c2302353d50325ff3b8445464b62fc92e9` |
| Independent final review, codex/gopt-host-review | `399e06f099a96a4e903cb349fcc7ee03e9d749b2` |

The existing owner chat admitted one integrated noncanonical host candidate and up to three improvement groups and three concurrent specialists. The publisher reused the accepted GOPT-0 baseline, assigned bounded investigations and a fresh independent engineering review, and recorded ordinary corrections under the same admission. There were no new Planner or Curator cycles, canonical publications, physical operations or physical results. Token expenditure was not measured. The evidence branch descends from the admitted scope before the firmware edits. It carries reports and host proof materials. [Admission ledger](../GOPT_ADMISSION.md) · [Baseline, timings, priorities and source paths](../GOPT_BASELINE.md) · [Independent final review](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/blob/399e06f099a96a4e903cb349fcc7ee03e9d749b2/docs/planning/GOPT_CANDIDATE_REVIEW.md)

## Startup and steady-state results

| Group | Baseline → candidate on matched inputs | Controls and limits |
| --- | --- | --- |
| GOPT-1, H3 saved Config CRC | Initial Config validation/load on the 27-profile, 32-file LittleFS fixture used 330 → 124 checked reads, down 206 (62.4%). Simulated NOR callbacks stayed at 153. | A bounded 32-byte buffer batches exactly the remaining checked bytes. The CRC and independent protobuf decode still run. All 124 injected read errors refused publication. Of 124 displaced-cursor short-read controls, 121 failed closed and three already-consumed terminal positions correctly loaded. Positive-length partial chunks at the first, middle and final positions failed closed. Caller sentinel, unchanged medium, size/CRC/truncation and 6,966 independent equivalence cases passed. |
| GOPT-1, H2 report loop | Each stable Normal iteration takes one boot-state mutex acquire/release pair, down from two. | Pending retains the second observation. Selection gating, mode/chord service, report order, ready mark, identity and keyboard were traced. Baseline-overhead and removed-second-read mutations were rejected. Both GameCube idle admission outcomes were exercised. |
| GOPT-2, H2 dashboard | A supported long executing name previously entered the adjacent analog readout. The renderer now fits printable glyphs and an overflow ellipsis within x=12–77. The readout begins at x=78. | Short and exact-fit names kept their pixels. The label source, profile/plate/backend identity, frame cadence and controls are preserved. Independent actual-font tests covered 31,350 cases. Both enum ABIs passed first-frame, menu action/return, hold/release, cooldown and transfer sequencing using host render doubles. An early-order mutant failed. |

The first-ranked namespace hypothesis failed. A larger 16-entry directory page violated owner-overlap bounds, and a rearranged nine-entry page did the same work as baseline. A variable-length experiment took 15,556 NOR callbacks versus the 15,000 ceiling. The candidate keeps the original reader. Its separate ProfileStore::Begin phase still uses 24 full enumerations, 104 opens, 218 seeks, 1,616 checked reads and 13,438 simulated NOR callbacks. Fixture SHA-256 is `251a9a7cc1c1c3242be170605e651074e198e12d9c02a9ca5da3336d53a99580`. No activation, report latency, OLED latency or cold-boot speedup in milliseconds was measured on the device.

## GOPT-3 reliability and resources

| Linked Mk6 measure | Baseline | Candidate |
| --- | ---: | ---: |
| Flash use, bytes | 651,292 | 650,484 |
| Static RAM, bytes | 198,888 | 198,888 |
| Linked heap capacity, bytes | 63,060 | 63,060 |
| Core 0 modeled maximum / reservation, bytes | 2,048 / 2,048 | 2,048 / 2,048 |
| Modeled lifecycle path, bytes | 2,044 | 2,044 |
| Core 1 modeled bound / retained budget, bytes | 1,068 / 1,152 | 1,068 / 1,152 |

The final CRC helper returns before sibling decode, write, rename and hash paths reuse stack. All 50 retained core 0 paths and 42 current CRC paths passed, with a 1,556-byte maximum for the CRC paths. Of 3,301 linked functions, 3,295 retained their call/frame shape. The six differences were explained. Static headroom under the cap remains 744 bytes, ruling out the proposed 1,024-byte frame cache. Both cores retain 2,048-byte reservations. The legacy path has zero modeled margin and lifecycle has four bytes. The independent resource review passed the accepted baseline control and rejected seven deliberately broken graphs. A separate storage/transaction refactor lacked a demonstrated fault and sufficient safety evidence. Physical stack high-water and peak heap use remain unmeasured. [Resource equations, assumptions and reproduction](resource/README.md)

## GOPT-4 software and artifact qualification

The exact candidate passed all 20 recorded host commands, the eight-command LittleFS build/test sequence and two additional boot/bounds checks. Tests covered both enum ABIs, 1,222,420 native evaluation vectors per ABI, protected report output, keyboard controls, 108 lifecycle cut/restart cases, 58 normal/recovery boot cases, 64 production transaction checks, 32 storage-fence cases, seven backend selection/refusal cases and four fresh activations. Historical Config coverage included five positives, 17 negatives and 33 namespace cases. Build-input inventory, 263-entry checker census and five build cache manifest checks passed. [Commands, log digests and workload counts](host-validation.json) · [Independent file identities](reviewed-identities.json) · [Portable dashboard transition check](display_transitions.py)

Clean `pio run -e glyph_mk6` completed for the committed final source using PlatformIO 6.1.19, Arduino-Pico 3.6.3 and GCC 12.3.0. Earlier input-only and input-plus-dashboard committed builds also passed. Relative to the canonical build inputs, only the three intended production source files changed. Of 545 dependency files compared, 542 were byte-identical and the three generated Nanopb Python bytecode files contained matching code after checkout-filename normalization. The final binary embeds the candidate source identity. Independent ELF-to-BIN conversion matched and all 2,588 ordered RP2040 UF2 blocks reconstructed the expected image. [Build inputs and toolchain](source-correspondence.json) · [Artifact digests and custody](artifacts.json)

| Product | Bytes | SHA-256 |
| --- | ---: | --- |
| Mk6 UF2 | 1,325,056 | `63cb30b4fc905fdd34421051cb373c1e98040b631934587b8b466a09b11848a4` |
| ELF | 5,763,656 | `53b53879b203ca2ef77de346352d1763cb89970560577fd3074a743a9eecfb0b` |
| BIN | 662,516 | `69a4ebc1f6ad941a0e5247dd9571e365a7b8c33512996735952a9d3c700fa2d7` |
| Linker map | 3,927,334 | `b53db2eeb9235f3930b3807ffc560b889f4c605ed5aaa86e7b1c88afece845ff` |

The public repository's push workflow uploads compiled firmware on a build-eligible push. The candidate was published with the skip directive and built locally. A separate Markdown-only review commit with the same firmware, tests, metadata and workflow triggered the ordinary hosted regression and validation jobs. Locally the first aggregate run refused a nested checkout in the existing build directory. In a clean isolated exact-source clone the source proof matched and eleven checks passed before the adversarial aggregate self-test reached its configured 120-second limit. That local aggregate result is FAIL. [Local aggregate receipts](local-aggregate.json) · [Hosted workflow](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/actions/runs/43696030677)

Hosted run 43696030677 completed successfully. Current host passed in 3m17s. All 25 scheduled aggregate checks passed with matching source proof, including the adversarial self-test in 53.035 seconds. GitHub skipped the build job and reported zero artifacts. The review delta from candidate is exactly one Markdown file. The local timeout remains recorded separately. [Hosted validation receipt](hosted-validation.json)

## Hardware and beta decision

The earlier 27-profile preservation, lifecycle and local transport observations belong to their historical builds. They remain the baseline for the proposed physical comparison. Every changed firmware group awaits exact-candidate hardware acceptance. The next owner decision is whether to authorize the scoped manual packet for the candidate SHA and UF2 digest above on a named Mk6 and GameCube adapter. It covers preservation across the manual update, startup, executing identity, menu return and receiver-observed Ultimate gameplay. XInput may be tested first. Downgrade, general recovery, compatibility expansion, canonical integration and release retain separate gates. [Beta matrix and proposed physical packet](BETA_AND_HARDWARE.md)
