# Startup performance candidate

Hardware acceptance is pending. The measurements below cover a host build of
the production ProfileStore and checked LittleFS adapter on a synthetic 512 KiB
NOR image. They do not measure the owner's controller, its retained filesystem,
USB enumeration latency, or time to a GameCube poll.

## Read path and integrity

The old reader enumerated the entire directory for every indexed lookup,
opened and sought each 256-byte scan window, and decoded and validated the same
Config for each row/RGB/native projection. The candidate reads the complete
namespace using the already leased 4128-byte record owner. An eight-entry page
in the existing classifier lease makes adjacent lookups share one complete
directory enumeration. Directories of any supported size refill the page on
demand. Every file's extent and bytes still pass their checked observations.

Row, RGB and native projections may reuse the last materialized named Config
only within one exclusive read-only classification. Config requests themselves
always reread the named file. A path change, failed load, historical decode,
or end of classification invalidates the projection. Prepublication callbacks,
final baseline checks and later requests execute outside that interval. This
uses the existing Config, root, record and readback buffers. The static owner
size/overlap checks still apply. No storage format, accepted digest,
transaction ordering, corruption disposition or write grant changes.

## Host results

Both builds executed the same instrumented ProfileStore::Begin against the same
synthetic 27-profile library (26 raw, one managed), with 32 files. The host
harness checks zero program/erase operations, exact unchanged NOR, zero open
handles, and a healthy classification. The namespace fixture SHA-256 is
`251a9a7cc1c1c3242be170605e651074e198e12d9c02a9ca5da3336d53a99580`.

| Operation | Parent f4146bed | Candidate |
| --- | ---: | ---: |
| Full directory enumerations | 192 | 24 |
| Read opens | 236 | 104 |
| Seeks | 1,026 | 218 |
| Checked reads | 6,533 | 1,616 |
| LittleFS NOR read callbacks | 78,054 | 13,438 |
| Desktop median, 5 runs, sanitized binary | 20.509 ms | 7.532 ms |

Reproduce with the existing transaction build.py and boot-probe option, then
run transaction/startup_work.py with its binary and the frozen glyph-package-v1
corpus. The regression gates operation counts. Desktop wall time is informational.
Full cold boot and PACKAGE_STATUS include work outside this measured interval.
A second fixture with two managed packages, G6 changes and a later raw save fell
from 61 to 10 enumerations, 184 to 66 opens and 11,655 to 3,007 NOR reads.

The real-storage host suite passed 64 production regression groups, 58 startup
routes (nine normal, 49 recovery), 32 storage-fence cases, and 25 bounded
detection checks. Historical Config replay passed five positive and 17 negative
observer inputs and 33 namespace cases, with checked faults and short reads.
The historical negative for migration-source corruption now checks the exact
current diagnostic. The parent and candidate returned identical encoded status
for that case. The selector recovery host checker passed.

## Presentation and device observations

Normal boot keeps the splash visible until the dashboard. All 16 scratch-stage
markers and the failure/recovery page remain. To see the original synchronous
stage frames for diagnosis, build with GLYPH_DEBUG_BOOT_DISPLAY=1. Healthy
release startup removes 15 full post-display stage transfers.

About reports four millisecond measurements. Store and Backend cover their
respective stages. Ready is elapsed time from Arduino setup entry to the first
mode-bound report-service entry. Screen is elapsed time to the first completed
ordinary dashboard transfer. A missing milestone shows a dash. Ready proves
readiness to service output locally. A human observation on the connected
receiver is necessary to verify usable output. Screen omits framework startup
before setup, so also time power-on to visible dashboard externally. Record the
profile-library size, board, adapter/receiver, boot type and display result.
Compare healthy boots against the owner's approximate 1–2 s experience, and
report migration/recovery independently.

The pinned 3.6.3 Arduino-Pico main initializes TinyUSB before Arduino setup.
Healthy startup verifies storage before selecting/initializing the backend.
Automatic detection includes a 500 ms USB/console observation window, with
bounded GameCube and N64 probing on the non-USB route. The XInput constructor
starts its interface and CDC before setting 0738:4726. The Switch constructor
sets 0f0d:0092 before its HID begin. The observed 2e8a:000a cannot establish
when the host read descriptors or which backend was executing. Transport order
is unchanged. On hardware verify GameCube through the adapter, separate USB
enumeration observations, and strict runtime identity where supported.
