# Mk6 beta-readiness audit

**The current host replay attributes almost the entire modeled setup cost to two namespace classifications. A late read-fault test rejects the straightforward shortcut.** The host work did not establish a safe reduction of at least one second in cold boot to validated mode or usable input. The retained Switch image remains the hardware reference. [Source correspondence](TRANSPORTS.md) · [Installation, recovery and physical qualification packet](QUALIFICATION.md) · [Measured results and command ledger](evidence.json)

## Baseline and custody

Live SenatorSSB/glyph-ultimate-expanded-fw `configurator` resolved to `59870835e7cd8e7c52bd3742e4910a7083cd21f5` at intake and closing readback. Its verified ancestry includes baseline `2bcb5104054f64d8b9c1af9dd1be4a974112f8ec`, reviewed GOPT `79475873f2c5f4b84e77bf9f94ab39779ffc69a5`, tested USB source `5dfc4cc26ca27d1de15c80e2a59f9637052f1b5c` and the physical acceptance record `ac3dcde060235ee7ce13d19b0ffaba49e1b04e1b`. Exactly five evidence/documentation files differ between the tested source and canonical integration.

The retained UF2 was rehashed locally to `de793f3469e8d88de31fb6f85d50bacd203b13928f1333ae5b291557c84b1518`. Its acceptance covers normal sticks and gamepad buttons in Ultimate on the owner's original Switch and an exact before/after API-visible comparison of Config and 27 profiles. It also records a GC connection trial. Earlier GOPT GC gameplay belongs to its own source and UF2. [Physical result](../gusb/PHYSICAL_RESULT.json) · [Integration receipt](../gusb/INTEGRATION.md)

## Current startup measurements

Ten fresh host processes independently mounted the same seeded 512 KiB LittleFS image, containing one committed managed package and 26 raw profiles in 32 files. The fixture has a valid compact Config and settled store. The release code for setup, persistence, namespace classification and receipt handling ran through the existing boot-stage probe. The replay added a host clock and CheckedStorage counters at the existing marks. The OLED and backend initializers were stubs. No transport was connected. These are fresh host mounts, with zero physical cold-power or warm-reboot timing trials on the 59870835 line in this audit. The owner described the installed image as feeling very similar to the earlier one and supplied no timed observations. About's older GOPT observations (Store 2416–2418 ms, Backend approximately 525 ms, Ready 5045–5406 ms, Screen approximately 5455 ms) belong to a different image and test conditions. [Historical timings and method](../gopt-qualification/PHYSICAL_CLOSEOUT.md)

| Stage | Current host characterization | What the controller measures or still needs |
| --- | --- | --- |
| Power-on, mount and setup entry | Global Persistence mounts LittleFS before setup with auto-format disabled. Host stage clock starts at Enter, 0 µs. | Power application, pre-setup mount and early TinyUSB attachment precede About's origin. Use external capture for cold boot. |
| Display attempt | Stub returns ready. Entry and return in same host microsecond. | Mk6 scans the button matrix, starts I²C and OLED, handles bootloader hold or transfers splash. Production per-stage OLED redraw is behind the debug flag. |
| Validator preparation | Defaults validator installed and validated by 1 µs median from Enter. | Failure enters recovery before saved data is used. |
| Saved Config load | 41 µs median (39–46), 124 checked reads, 153 simulated NOR read callbacks. | Checked size/CRC, validated protobuf decode and selected current/prior/legacy handling. Recovery dispositions remain distinct. |
| ProfileStore Begin | **2,140 µs median (2,098–2,293)**. 24 complete directory enumerations, 104 read opens, 218 seeks, 1,616 checked reads, 13,438 callbacks. | About Store measures this interval. |
| Compact receipt | **2,128 µs median (2,108–2,300)**. Another 24 enumerations, 104 read opens, 218 seeks, 1,616 checked reads, 13,439 callbacks. | A managed receipt invokes full classification again. About Store excludes this cost. Nonmanaged compact receipts have a different path. |
| Migration and ownership/layout | Both marks reached after receipt. Matched current-format fixture needs no migration, layout rewrite or further storage reads. | Pending/legacy states can import, validate, save or refuse. Normal boot does not imply that every starting state has this cost. |
| Backend initialization | One successful stub call. Physical detection, USB enumeration and GC response are unmeasured. | Ordinary detection waits 500 ms before evaluating USB/NES/SNES evidence. Quiet Joybus probes may then consume receive windows up to 10 × 10 ms for GC and 60 × 20 ms for N64. These budgets apply when those probes are reached. Final Switch-only reattachment adds 10 ms. |
| Normal publication | Ten normal outcomes, zero simulated flash programs/erases, byte-identical media. Setup median **4,308 µs** (4,247–4,635). | Core 0 publishes the terminal outcome before normal mode/report service. Recovery clears routing scratch, records its stage/readiness and publishes a recovery outcome. |
| First mode, dashboard, receiver | Outside the host probe. | Ready is sampled upon a non-null bound mode before SendReport. Core 1 waits for terminal publication in 1 ms polls. Screen is recorded after a completed ordinary dashboard transfer. Neither records the first report reaching a receiver or moving a character. |

The instrument is host-only. To reproduce, use Arduino-Pico 3.6.3, the Mk6 PlatformIO dependencies, a Python with the repository's protobuf/nanopb host dependencies and the Senscope package corpus at dcc1c9992531adbde2f793a30f575005b25b8d05. Run the script in this directory with a clean canonical checkout, the corpus directory and a new output directory. It instruments a disposable fixture copy and checks all ten healthy boots and the two read-fault controls. The source-header and firmware paths in the supplied checkout remain inputs. [Stage replay](replay_boot.py) · [Stage observer](observe_boot.inc) · [Actual setup and core loops](../../../config/glyph/common/src/config.cpp) · [Boot diagnostics](../../../include/core/BootDiagnostics.hpp) · [Timing definitions](../../../include/core/BootTiming.hpp)

```sh
python3 replay_boot.py --repo "$GLYPH_CHECKOUT" --corpus "$SENSCOPE_CHECKOUT/contracts/glyph-package-v1" --out "$NEW_OUTPUT_DIR"
```

## What can safely be removed

The eight-entry reader page refills through a complete checked directory traversal. The classifier reads all bytes, including unrelated files, before interpreting versions, root/control agreement, package records, Config projections and ownership. Begin decodes the selected directory under the classifier lease. On a managed store, receipt handling acquires a new lease, checks a fresh namespace, requires a committed supported state, matches the directory generation/incarnation and compares the loaded Config digest to the observed current Config. No write occurred between these calls on the healthy fixture. [Classifier](../../../src/core/PackageNamespaceClassifier.cpp) · [Directory reader](../../../HAL/pico/src/core/GlyphPackageSourceReader.cpp) · [Store and receipt checks](../../../HAL/pico/src/core/ProfileStorePackage.inc)

**Reusing the first success loses a demonstrated refusal.** A persistent read failure on `/ultimate-00000002-00000001.bin` starting at StoreBegin prevented StoreReady. Moving the same fault to ReceiptBegin allowed StoreReady, then produced Recovery Configurator with zero gameplay-backend initializations. Both runs had one terminal publication, no flash mutation and byte-identical media. The latter failure would be invisible to a boot path relying only on the earlier classification and an in-memory Config hash. A fresh content/namespace check or an equivalent fault-detecting design is essential.

A smaller host experiment retained both classifications and the authoritative late NoTemps predicate. It timed an additional fresh checked visit at the same point. On 32 files, one complete visit cost 353 callbacks and about 24 µs. Each existing paged check cost four complete visits, 1,412 callbacks and about 92 µs. The projected workload difference over both checks is six visits and 2,118 callbacks (7.8% of this fixture's total), about 136 µs on this host. That arithmetic is not a measured firmware speedup. A production change needs to preserve the reader's sticky error handling, name/count/type checks, visibility of late temp entries, page consistency, and stack bounds on transaction callers as well as boot. Replacing the reader with a second direct filesystem authority would break that contract. Earlier 16-entry, nine-entry and variable-page experiments respectively exceeded the lease, saved no work and exceeded the 15,000-callback budget. [Prior reader experiments](../gopt-qualification/README.md)

Shortening the 500 ms window changes which consoles can be detected. Initializing a provisional USB backend while storage is still under review changes host-visible behavior and backend lifetime. The 10 ms Switch reconnect has a receiver-qualified purpose. Core 1's poll is concurrent with storage, and moving the dashboard alone cannot advance first input. None is a defensible one-second saving on current evidence.

## Host qualification and resource comparison

The canonical clean Mk6 build passed with PlatformIO 6.1.19 and ARM GCC 12.3.0. The original default package cache lacked the matching SCons version; the successful build used the existing matched package cache. Both tested and rebuilt UF2 block tables and the rebuilt BIN payload were checked. The canonical rebuild embeds a different Git identity. Its SHA-256 is `3fb0eb0fab4bc66ebd054b8d334c5b38c3732dfab69355276048396d49e0bef2` (1,325,568 bytes). It was neither installed nor substituted for the tested file.

| Measure | Tested USB source | 59870835 rebuild |
| --- | ---: | ---: |
| Flash | 650,556 B | 650,556 B |
| Static RAM | 198,888 B | 198,888 B |
| Linked heap capacity | 63,060 B | 63,060 B |
| Core 0 / core 1 reserved stacks | 2,048 / 2,048 B | 2,048 / 2,048 B |
| Core 0 maximum / lifecycle model | 2,048 / 2,044 B | 2,048 / 2,044 B |
| Core 1 setup / loop / envelope | 968 / 984 / 1,068 B | 968 / 984 / 1,068 B |

All 3,302 linked function names and their resolved frame, call, tail-call and indirect instruction shapes matched the tested build's graph. Physical stack high-water and runtime peak heap remain unmeasured on these trials. Heap capacity is a linker quantity.

All 22 focused current-host/provenance commands passed, including the 263-entry census, both enum ABIs, native full-output replay, profile selection, backend detection, GC poll bytes/liveness, Switch USB host-stack/control endpoint replay and readiness. All eight LittleFS transaction build/check commands passed, covering 108 lifecycle cut/restart cases, 58 boot cases (49 recovery), current and historical Config, package ownership and 32 storage-fence cases. A separate migration lifecycle run passed 20 profiles, retry without duplicate IDs, compact references, strict first create and corrupt-record isolation. The new host observation replay passed ten healthy cases plus two stage-specific read faults.

The full aggregate at 59870835 passed eleven checks, then timed out after 120.003 s in validation_aggregate_adversarial, with canonical fingerprint MATCH. An earlier baseline-category invocation failed on the same adversarial checker with a different exit and the standalone adversarial checker passed. Keep each result separate. The previous USB aggregate also timed out and exhausted its cleanup/final-proof budget. Neither historical nor current full aggregate has a PASS. [Machine-readable results](evidence.json) · [Prior aggregate and source qualification](../gusb/QUALIFICATION.md)

## Disposition

No behavior-changing candidate or candidate UF2 was produced. The executable queue at intake had zero READY and zero PREAUTHORIZED items. The measured smaller opportunity is a possible bounded work order once reader/fence equivalence and the cost on the release hardware are established. The host audit itself did not change queue or firmware authority.

Beta qualification still needs exact-image input on the scoped routes and installation/preservation on each advertised starting pair. Matched pre/post cold-boot timings are needed for a speedup claim. Destructive recovery needs a physical trial only if it is advertised. A physical phase and final beta decision remain separate. Switch 2 is excluded. [Operator packet and support matrix](QUALIFICATION.md)
