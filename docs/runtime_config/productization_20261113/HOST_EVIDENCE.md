# Host verification and dependency record

The source under test for the combined firmware is `84556d904f067bda5a101e6297689239ecd04aae`. Its parent line begins with the accepted configurator snapshot `f4146bedebb50559454954b8e20c9b641aeba616`. The tested display image at `9e69188d857138a3884bcbe243f22188815e9355` remains the historical baseline. The earlier CREATE and dashboard observations have separate scopes. No physical observation belongs to any new candidate.

| Feature | Diagnostic source | Integration |
| --- | --- | --- |
| Startup and presentation | `7d1f6a3ba99627e88dfdaf404e08ff816902ccfc` | Namespace reader, release splash, recovery diagnostics and About timing. Combined borrowed the same timing frame correction. |
| Ordinary profile selection | `f6655e30c6d94b4468711053e5c6c76c00be9cc7` | Dedicated pair, backend-filtered menu, reboot-bound activation, exact ID, physical GameCube idle admission. |
| Package lifecycle | Integrated on top of the accepted CREATE transaction. `9ea1898b` records an intermediate storage design only. | Protocol 4, operations 17 through 20, exact replacement and deletion guards, dense owned-row/RGB compaction, transaction fencing, protected references and retry receipts. |
| Combined | `84556d904f067bda5a101e6297689239ecd04aae` | Forward integration followed by cross-feature fixes, source-bounded stack lifetimes, and GameCube chord admission. |
| Host tooling | Senscope `codex/glyph-productization-20261113` | Explicit target plate in local/portable persistence, native compiler, file preview, finite package codec and offline stored-data verification. |

The first diagnostic builds were `d19c8a00` (startup) and `2d32ea23` (selection). Their artifact directories remain for historical comparison. Use the forward diagnostic revisions listed above for a later test. The combined source contains the same functional fixes, despite the differing Git parents of these isolated branches.

## Production-path checks

| Evidence on the combined source | Result |
| --- | --- |
| Existing production transaction checks using a real LittleFS mount on emulated NOR | 64 regression groups passed. |
| Replacement, rename, reorder and delete | 108 before/after interruption and restart cases over five transactions, including UPDATE with and without RGB. Exact guarded retries, wrong revisions, token conflicts, capacity reclamation, unrelated rows/defaults and native-program preservation passed. |
| Ordinary selection | Two asymmetric packages with separate preprocessing, native programs and plates. Seven per-backend selection/refusal checks, four fresh-process activations, two damaged-pair checks and exact preservation passed. |
| Release boot | 58 fixture routes (nine normal, 49 recovery). Thirty-two storage-fence cases and 25 bounded backend-detection checks passed. |
| Historical storage | Five positive and 17 negative observed Configs and 33 namespace cases passed, including I/O and short-read faults. |
| Physical chord logic in the peripheral simulator | Both compiler enum ABIs. No-console hold/release, queued transmission and partial command, first matching chord, USB admission, live GameCube report and unchanged legacy controls passed. Actual cable and receiver behavior require hardware. |
| Wire upper bounds | Protocol 4 response 241 bytes (244 framed), request 4,580 (4,601 framed). Existing protocol 3 response limit remains 228 bytes. |

The 27-profile healthy startup image is unchanged by classification. Full enumerations fell from 192 to 24, opens from 236 to 104, seeks from 1,026 to 218, checked reads from 6,533 to 1,616, and NOR reads from 78,054 to 13,438. Desktop median was 20.509 ms on the parent and 6.789 ms in the final combined rerun. This interval measures namespace observation. The release path also removes 15 synchronous post-display stage transfers. Power-on to usable GameCube output and to first dashboard remain separate board measurements, with the owner's earlier approximate 1–2 s experience as the target.

## Resource review and repair

A linked review found that the combined lifecycle/selector stack initially exceeded the 2,048-byte core0 reservation. Forward commits split CREATE and lifecycle preparation, released the root intent hash before Config parsing, bounded the DescribeConfig phase, ended the timing helper before storage calls and separated chord scanning from persistence. GameCube managed chord saves then gained the same receiver idle protection as menu selection. Confirm exact resource records against the ELF in each candidate's manifest. Static call-graph bounds are distinct from measured controller stack high-water.

The final combined image uses 198,888 static RAM bytes against the retained 199,632-byte budget. Both stacks reserve 2,048 bytes. The core0 review covers 50 affected paths; the largest new lifecycle path is 2,044 bytes. The inherited legacy SET staging path reaches all 2,048 bytes, leaving zero modeled margin on that path. Core1 is bounded at 1,068 bytes including its interrupt allowance, with 237 reachable functions and zero unresolved edges under the retained model. The startup-only core0 routes peak at 2,044 bytes with the same inherited 2,048-byte staging path. These results make high-water observation and stack re-review important for any subsequent source/toolchain change.

## Retained candidates

| Candidate | Exact source | UF2 bytes | UF2 SHA-256 |
| --- | --- | ---: | --- |
| [Combined](candidates/combined/manifest.json) | `84556d904f067bda5a101e6297689239ecd04aae` | 1,326,592 | `6b3fd3e2f71b839e7448ab6b0daa54e5d4f1d6473d0df917849413e3f4227ddb` |
| [Isolated startup](candidates/startup-7d1f6a3b/manifest.json) | `7d1f6a3ba99627e88dfdaf404e08ff816902ccfc` | 1,300,480 | `46bf9d701376dba8b0d013efd8429b15ee36fde0fbf0964a2f9cc5866bcc3a57` |
| [Isolated selection](candidates/selection-f6655e30/manifest.json) | `f6655e30c6d94b4468711053e5c6c76c00be9cc7` | 1,299,968 | `9d348290512fffa77b817b2a0c88aaa2a5b7aee522b6b02c0d1033c1903fe502` |

Each manifest binds ELF, BIN, UF2 and MAP to the source named in the table. Reproduce the conditional stack calculations with the scripts and hashes in [resources](resources/REPORT.md). The candidate images differ when compiled from another source commit, including CI verification merges with a different embedded build version. Use the reviewed UF2 listed above for the proposed controller session.

The final selector-only build uses 198,864 static RAM bytes. Its highest affected core0 path is 2,036 bytes and core1 is 1,060 bytes. The inherited legacy Config staging route is still 2,048 bytes. Its mandatory host tests checked the GameCube idle gate in both enum configurations and all persistence/recovery routes. Firmware and hardware acceptance remain separate from canonical CI maintenance.

## Hosted CI and source correspondence

Canonical CI maintenance is `486aaecfd67c2f3b9731e3a3abcbb59a40cdf633` on `configurator`. Its 24 changed files are CI tooling, workflow and supporting contract records. The strict comparison against the accepted package snapshot found identical inputs outside those files. Census discovery and its retained inventory both found 263 checkers. The host tests cover current runtime, compiler, configuration and real LittleFS behavior. Historical C023 replay uses its recorded immutable source. The pre-publication run passed all 25 aggregate checks and built Mk6. After publication, the canonical branch passed host tests, all 25 aggregate checks, actual Mk6 compilation, postprocessing, provenance verification and artifact upload. The canonical GitHub archive is 14053614356 with SHA-256 a971307ed98e7d2b9cdfb0523542c7ceb2ab45fd5947ccd72c617092debfdda7. A separate prose-only push passed validation and skipped the Mk6 build. [Canonical run](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/actions/runs/43455266594) · [Pre-publication run](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/actions/runs/43448793374) · [Prose-only run](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/actions/runs/43447535125)

The hosted combined verification commit `f0df0ac4658d70f3837b6e5d5c69347b6269d839` applies those CI checks to combined firmware `84556d904f067bda5a101e6297689239ecd04aae`. Firmware inputs match the handoff source across src, include, lib, HAL, config, schema, platformio.ini and builder_scripts. The host job, 25 aggregate checks and actual Mk6 build/upload all passed. The source-scope checker reported 46 changed paths outside CI maintenance and recorded hardware acceptance as pending. The three source-bound UF2s listed above are the artifacts retained for the controller session. [Combined verification run](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/actions/runs/43448890812)

## Retained-library replay

The Senscope read-only operator checked all four original LIST pages and 27 READ replies from the earlier accepted display session. Each emitted request matched the original transmitted bytes. Each profile wrapper matched both its original bytes and its SHA-256. The earlier library includes a valid legacy record with directory metadata version 1 and actual wrapper schema 3. Both facts are recorded; native entries require a native wrapper. Synthetic tests covered the reverse legacy pair, interrupted snapshots, unsupported families and diagnostic/recovery responses. New hardware evidence was not collected during replay.

The companion setup CLI exercised two separately approved CREATE operations against the production command handler and LittleFS on emulated NOR. It verified the full expected Config and defaults, the returned row and assigned ID, existing directory order and wrappers, and new native bytes. It also exercised a stale preview, duplicate name, queued data before write, missing acknowledgement and failure to close the port after a receipt. No subsequent create can inherit a hardware result from these host fixtures.
