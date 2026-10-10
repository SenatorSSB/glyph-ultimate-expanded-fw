# Private friend profile focused validation

Baseline: configurator `28ba39da5f517baa40f3dee8d868c9bb583dde4a`.
No hardware acceptance is claimed. No flashing or device interaction was used.

## Actual-source host tests

`python3 friend/run_checks.py`: PASS, 6,051 assertions per ABI, 12,102 total.
Apple clang, ASan/UBSan with fail-on-first-error, short and ordinary enum ABIs.
Uses the exact build-generated Config schema, build-selected nanopb sources,
actual Ultimate/ControllerMode/InputMode/SOCD, actual production validators,
and actual Persistence save/readback/CRC/decoder. Only platform/filesystem I/O
are host doubles. Raw output logs and compile commands are retained in private
`../verification/`. The harness is private, not canonical product infrastructure.

Checks cover all 9 entries of every requested modifier/table across both
physical Left sources and all three Up sources on XInput/DInput/Switch/GC;
128 physical modifier subsets verify all priority interactions. All 34 physical
button digital bindings and requested triggers/chords are checked. Blank buttons
are inert with every modifier/direction. RF8 enters LF3's SOCD pair before
effective-direction/table selection. Second-input-priority reactivation and
initially simultaneous opposition neutrality are exercised as frame sequences.
Intentional Tilt2 flip and unusual Default direction 2 remain owner-exact.

C-stick tests press the physical IDs: RT3 Left=(39,128), RT5 Right=(217,128),
RT2 Down=(128,1), RT4 Up=(128,255), every diagonal and neutral, with each modifier
on all four backends. Digital and analog routing agree. No legacy diagonal
override remains active. Requested RGB reference 3 is STATIC/empty (off).

## Production Config and one-shot installer

Complete baked Config passes current production `validate_glyph_config` through
Persistence's installed validator. Real SaveConfig/LoadConfigChecked roundtrip
and full deterministic nanopb encoded equality: expected=3,779 bytes,
readback=3,779 bytes, exact bytes/length PASS. Same-length changes outside
Ultimate are rejected by full Config comparison. Binary/JSON/binary roundtrip
also passes with the exact selected schema and identical short/ordinary bytes.

Failure matrix A-J passes: invalid baked (no save), failed SaveConfig, failed
readback, structurally valid but different full Config, empty/partial failed
marker write, preexisting empty/old/truncated/trailing markers, correct marker
skipping overwrite, successful first adoption/reboot, later legitimate user
change preserved. Additional cases: invalid readback after prior successful use,
marker open/reopen failure, config write I/O failure, short Config read. Failure
never creates a valid applied marker. A short/failed marker write removes its
entry; even if an entry survives, exact payload recognition rejects it.

Marker path: `/friend_ultimate_20261011_applied.flag`.
Exact ASCII payload: `friend_ultimate_20261011_applied_v1\n` (36 bytes, including
newline). Validation -> SaveConfig -> checked readback -> readback validation ->
full encoded equality -> checked marker write -> flush/close -> reopen and
exact size/content/EOF verification. Valid marker skips the installer only;
ordinary production stored-Config load/validation still runs. No exists-only
acceptance, raw Config memcmp, heap Config, or stack encoding buffer is used.

## Source safety and stack

`python3 friend/verify_source.py`: PASS. C021/C022/C023/C024-era validators,
Persistence, backend initialization/selection, and ConfiguratorBackend are
byte-identical to baseline. Boot source differs only by the private include and
four-line safe-refusal hook; validator installation and default validation
precede provisioning, normal checked load precedes normal boot publication,
and original core1 refusal gates remain intact. Twelve unrelated profiles and
RGB configurations remain unchanged.

`friend/measure_stack.py` uses exact PIO ARM GCC 12.3/O3 flags plus
`-fstack-usage`, compiling separate verification objects. Previous reported
installer frame ~26,992 bytes is removed. Installer/equality are inlined into
the complete `setup()` frame of 440 bytes; marker_valid=56, comparator=16,
production checked-load implementation=224, Ultimate analog=112 bytes.
These are compiler frame measurements, not cumulative dynamic stack or hardware
measurements. Readback Config is function-static and reset before every use;
expected encoding is bounded static 16 KiB. Boot-only, core0-before-core1-release;
valid-marker later boots bypass readback/encoding. No large automatic Config
remains on the installer path. Build emits no private installer stack warning.
Unchanged library LittleFS directory helpers warn about potentially unbounded
stack; unrelated SenscopePrototypeSelfTest warns 1,240 bytes. Neither directory
helper nor prototype self-test is called by the one-shot installer.

## Build/UF2 candidate before final custody build

Repository wrapper PASS, exit 0, 43.891 seconds. PlatformIO 6.2.0.
Candidate UF2 800,768 bytes, SHA-256
`16db5ed2d4c268b40597437aae4056413e895ed351e0d3e9e17c268da85cb160`.
This is pre-commit evidence; final package manifest identifies the clean committed
rebuild. Inspector PASS: valid 1,564-block RP2040 UF2 (family 0xe48bff56), one
contiguous app segment `[0x10000000,0x10061c00)`. No block overlaps linked
filesystem `[0x1017f000,0x101ff000)` or Clean/Fresh high-flash wipe range.

Earlier 799,744-byte `92708652...` UF2 is rejected/superseded and excluded from
the final delivery package. It is retained only under verification as REJECTED.
Hardware remains NOT_TESTED / PRIVATE_BUILD_READY_FOR_OWNER_TEST.
