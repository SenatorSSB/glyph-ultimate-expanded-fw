# Mk6 optimization baseline and qualification gaps

Inventory taken on November 15, 2026. Live `configurator` and the clean measurement checkout both resolved to `2bcb5104054f64d8b9c1af9dd1be4a974112f8ec`. The current-host, validation and Mk6 UF2 build jobs all passed. The firmware source, HAL, config, include, schema, platformio.ini, libraries and builder scripts compared equal to physically tested source `0b9ef3afd1834ac7832871bca0651b67147840a2`. The canonical tip changes one generated checker census from its integration parent. [Canonical CI run](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/actions/runs/43649031926)

## Startup, activation and first report

On Mk6 the package backend is enabled. Core 0 initializes the OLED and splash, validates defaults, loads and validates saved Config, classifies the package namespace, checks receipts/migration/layout and initializes eligible backends before publishing the normal boot state. Failure can enter the recovery configurator. Core 1 waits for terminal publication before setting up menus and LEDs. The normal report loop services selection/chords and eligible backends, then identity and keyboard. Profile activation and backend selection are separate from namespace classification. A saved row can exist without an executing mode. Inspect `config/glyph/common/src/config.cpp`, `HAL/pico/src/core/ProfileStorePackage.inc`, `HAL/pico/src/core/ProfileStore.cpp` and `tools/fixtures/glyph_package_v1/transaction/managed_selection.py`.

On the original combined candidate `84556d904f067bda5a101e6297689239ecd04aae`, three owner-transcribed trials gave the following milliseconds. Two used the GameCube route directly and one included a USB detour. Store and Backend are phase durations. Ready and Screen are elapsed since Arduino setup entry. Ready denotes local report-service entry. External startup was approximately seven seconds, with limited precision. These figures cannot identify the duration of a specific read or justify shortening backend detection. [Stage D and later acceptance reconciliation](https://github.com/SenatorSSB/senscope/blob/cf28ad448aa97c73def42dcb406b3d07d086a9c6/docs/project/research/glyph-productization-integration-20261114/README.md)

| Trial as recorded | Store | Backend | Ready | Screen |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2418 | 525 | 5405 | 5454 |
| 2 | 2416 | 525 | 5045 | 5454 |
| 3 | 2417 | 525 | 5406 | 5456 |

### Fresh offline measurements

The ASan/UBSan host binary used the pinned Arduino-Pico 3.6.3 LittleFS adapter, actual candidate code and boot probe. The frozen synthetic fixture contains 27 profiles in 32 files. Five runs gave identical operation counts. The timer surrounds only `ProfileStore::Begin`, after Config load. On each run the harness asserted healthy classification, zero additional program/erase, unchanged simulated NOR and zero open handles. An activation run, OLED frame and receiver observation each have different boundaries.

| Full enumerations | Read opens | Seeks | Checked reads | Simulated NOR read callbacks | Desktop median |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 24 | 104 | 218 | 1,616 | 13,438 | 6.069 ms |

The fixture SHA-256 was `251a9a7cc1c1c3242be170605e651074e198e12d9c02a9ca5da3336d53a99580`. Host binary SHA-256 was `351108dbae46b43ef7fb1bfeaef7364db14119523d78f7bdb4edc8ecea13af8c`. The build manifest covered 139 inputs with fingerprint `abfae80f00c2ec9d9eed790978e207a65764120e1cdd6185e7dc7e7c51f152cb`. Reproduction uses `tools/fixtures/glyph_package_v1/transaction/build.py --repo . --boot-probe --out <build>`, followed by `startup_work.py --binary <build>/package-fault-harness --corpus <corpus>` from that fixture directory. The corpus is Senscope `contracts/glyph-package-v1` at `dcc1c9992531adbde2f793a30f575005b25b8d05`. Use the same pinned dependencies, a compatible protobuf runtime and the corpus research/proof paths. The earlier eight-entry page and Config projection cache already account for the published 192→24 enumeration improvement. [Existing workload definition](../runtime_config/startup_performance/README.md)

Fresh baseline controls at the canonical SHA:

| Check | Result |
| --- | --- |
| Visible boot | 58 cases passed, 9 normal and 49 recovery |
| Storage fences | 32 cases passed, including 5 normal |
| Historical Config | 5 positive, 17 negative and 33 namespace cases passed, including I/O and short-read faults |
| Switch readiness | Old ready report and old pre-FAST stall negative passed. Current bounded wait, scan order, menu controls and 8-byte reports passed |
| Checker census and CI build inputs | Census passed with 263 entries. Both build-input tests passed |

## Ranked engineering backlog

1. **Reduce verified namespace work during Store.** The physical Store stage is about 2.4 seconds, and the host fixture still incurs 24 complete enumerations. `GlyphPackageSourceReader::ObjectAt` fills an eight-entry page inside an exclusive classifier lease. First trace page refills and checked reads by phase/path. Test whether existing nonoverlapping lease space permits a larger page or fewer repeated lookups. Compare small, page-boundary, above-page, managed, damaged and full directories. Keep complete name observation, independently checked bytes, failure/recovery classification, rechecks before publication and the full accepted namespace domain. Verify both compiled ABIs and existing overlap assertions. A lower count on one fixture alone is insufficient.
2. **Measure initial saved-Config CRC separately.** `Persistence::CheckSavedConfig` makes N single-byte checked reads for N payload bytes before decode. This part of initial Config load is outside the table above. Prototype bounded block reads only after isolating the load cost and proving scratch ownership. Require equivalent bytes, CRC, extent, seek/close and rejection versus storage-failure behavior for truncated, corrupt, interrupted and short reads, plus other callers and the legacy SET bound. Savings in checked calls may differ from savings in NOR callbacks.
3. **Remove a redundant boot-state mutex acquisition in steady input service.** Stable Normal iterations acquire/release the boot-state mutex twice before checking backends. Publication only changes Pending to terminal. One terminal snapshot could remove one pair each normal iteration. Preserve the old second observation on Pending where transition timing matters. Compare service traces for every boot outcome, null backend cases, terminal immutability, Pending publication races and exact scan/report order. Preserve the accepted Switch wait and per-backend readiness behavior.
4. **Miniscreen redraw and feedback.** On an ordinary non-NES display iteration, rendering and a full 128×64 monochrome transfer recur even for identical pixels. An extra framebuffer costs 1,024 bytes, exceeding the 744-byte retained static headroom on its own. Rendering also has menu side effects, and faster loop iterations can change RGB hue accumulation and GameCube/core-1 contention. Defer whole-frame caching. Check first/return-frame traces, stale identity, plate/backend text, clipping and refusal feedback before proposing smaller changes. Require exact rendered controls, frame transitions and relevant timing proof. Relevant source includes `IntegratedDisplay.cpp`, `ConfigMenu.cpp`, `NeoPixelBackend.hpp`, `GamecubeBackend.cpp` and the Glyph display modes.
5. **Increase stack margin where a live frame can be shortened.** Inspect the longest evidenced routes below. Measure before and after with the same ABI, linked call/interrupt/ROM assumptions and complete affected entry paths. Keep the transaction, persistence and recovery boundaries. Avoid moving work to unaccounted static RAM or heap. Retain historical bounds if no improvement can be proven.

## Resources and existing physical evidence

The retained integration comparison at `e07019b59f370e4853f0eac56de97d91bcea430e` gives flash 651,292 bytes, static RAM 198,888, linked heap capacity 63,060 and 2,048 reserved stack bytes per core. Core 0 modeled lifecycle reaches 2,044 bytes, legacy SET reaches 2,048, and the affected core 1 bound is 1,068 against the retained 1,152 budget. These values describe modeled routes on exact linked inputs. Physical high-water marks remain unknown. [Linked comparison](https://github.com/SenatorSSB/senscope/blob/cf28ad448aa97c73def42dcb406b3d07d086a9c6/docs/project/research/glyph-productization-integration-20261114/resource-summary.json)

The historical physical Switch repair UF2 was 1,327,104 bytes, SHA-256 `6eb992cda7392b6fb5a52ab48989ef10c94fc97ec77fd733360a863e55cd8a83`, for source `0b9ef3afd1834ac7832871bca0651b67147840a2`. The integration rebuild of the same size had SHA-256 `adf23568dddb186cabca233cd94986b15f805115dea90479c27c3c5351c08d03`. They have distinct custody and acceptance. GOPT has produced a host benchmark executable only. [Exact repair evidence](https://github.com/SenatorSSB/glyph-ultimate-expanded-fw/blob/4a5fa494194c366f8a78e324fcdfdb560dd454c5/docs/runtime_config/switch_readiness_20261114/README.md)

## Preliminary open-beta assessment

| Status | Capability and scope |
| --- | --- |
| Demonstrated on prior hardware | Combined Mk6 episode covered managed CREATE, local selection/name/plate/persistence with recorded waivers, and disposable UPDATE/RENAME/REORDER/DELETE with final saved-state readback. The repaired image covered owner-observed local Switch-on-Mac control through idle, verified Stage-H Config restoration and preservation of 27 wrappers, and direct XInput profile 53/revision 1 identity. |
| Host only | Real LittleFS fixtures cover interrupted publication, corrupt and refused states, and ABI/report regression controls. Full-storage/capacity-reuse and failure-message UX require route-specific qualification before public support. |
| Hardware pending | On a future exact candidate, establish Mk6 identification, cold startup and first visible/usable response, physical gameplay with distinguishing input/report outcomes for each proposed transport, menu return, executing identity and preservation across the supported manual update. Keep prior explicit waivers attached to their original scope. |
| Outside proposed initial support | Nunchuk, Nintendo Switch console compatibility, arbitrary downgrades, raw-NOR/full-library restoration guarantees, automatic recovery and additional hardware variants. |

Recommend qualifying the Mk6 with USB/XInput first. Add GameCube through the named tested adapter only after the exact candidate's receiver/gameplay rows pass. Limit ordinary profile operations to the exact tested combinations of complete-package creation, selection and lifecycle; qualify recovery and preservation before promising those operations to public users. A manual update proposal must identify the board, source and UF2 digest, capture and compare API-visible Config, directory and wrappers, verify advertised build and separate executing identity, and stop on mismatch. The existing readable backup covers less than physical media restoration. A downgrade path or erase-based recovery requires independent evidence. The retained pre-reboot pause is unexplained. Reduce uncertainty with phase measurements before classifying it as a defect. Defer optional display polish without a reproduced problem. **Hold open beta** pending candidate-specific qualification and a later release decision.
