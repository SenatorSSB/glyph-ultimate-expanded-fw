# Complete ProfileStore CREATE path diagnosis — 2026-10-15

Disposition: diagnostic candidate with source-proven repairs; physical root cause
UNPROVEN. No canonical merge, device operation, factory reset, or hardware PASS.
The owner explicitly authorized the complete CREATE path repair on 2026-10-15.
The owner reports no SWD probe. The hardware candidate must therefore provide
USB-readable stage evidence after a diagnostic watchdog reset.

## Historical evidence retained

Canonical live ref is `6b73a7c507f35c111745c6bdd341618b490cbdcd`.
Parent is `83f526b843fbcc61ee7dac6da9df0bc79351c2bf`, tree
`526e8c7707020db70cca2b082450d3f9e499b378`, production repair ancestor
`585d0db1c311a28dc002c7749b98eb40924a1a71`. The parent's exact 941568-byte UF2
`3d47af6bd409825cd6c59b02170b45d375df1d6327a254989190f8980903e303` timed out
on one CREATE after ready/STATUS generation0/LIST empty. No probe, retry, reboot,
read, Config change, or later observation followed that timeout. Its post-timeout
state is UNKNOWN. The old directory callback frame was not a complete explanation.

F4's overlength temporary component was proven and remains repaired. F5's returned
COMMIT_UNKNOWN with ID1/revision1 proves record publication completed; its later
reboot recovered generation0/empty/no token. F6 had no CREATE or GET_DEVICE_INFO
response before reboot, then generation0/empty. F5 does not prove that F6 or the
latest attempt reached the same stage. Different binaries/FS histories can take
different stack and metadata paths. Nothing here asserts that directory temp
write, verification, rename, or response serialization was reached physically.

## Source-proven repairs

* `HandleProfileStore` allocated an entire automatic profile for the unrelated
  SET_MODE_REFERENCE branch. GCC reserved 2384 bytes on every call. Static
  core0-owned read scratch removes it; final instrumented frame is240 bytes.
  The static8192 frame,2264-byte request and2840-byte response were never the
  explanation for the automatic2152-byte profile. Streams/results/scalars/spills
  account for the remaining frame. DUPLICATE's nested profile scratch moves to
  its own static2152-byte object (2216 to64 bytes).
* `setup()` contained an automatic migration Config (~31KB) despite already
  launched core1. Its reservation exceeded both scratch banks even on the
  non-migration/early-return path. The boot-only unpublished candidate is now
  static; measured setup frame is256 bytes. This consumes additional BSS and
  requires final linked RAM evidence. It does not select/mutate a Config except
  in the already authorized migration branch.
* Atomic readback formerly overwrote the expected buffer via `const_cast`,
  accepting a self-consistent stale record with matching identity or a stale
  root with matching generation. Separate bounded4128-byte readback and exact
  byte comparison reject that case before remove/rename. The original bytes
  remain intact. Directory/record CRC and semantic validation remain required.
* The pinned TinyUSB CDC `write` loops while connected and remaining bytes are
  nonzero, without a deadline. A connected non-draining host can stall after
  commit. ProfileStore responses now encode fully into owned scratch, then use
  a fresh COBS writer with a2-second packet deadline. Each Serial write is at
  most available FIFO capacity; single core0 producer and IRQ draining are
  required. Failed TX leaves the committed store intact. The next response
  first emits a delimiter and uses fresh encoder state, including when the
  next request is a legacy command such as GET_DEVICE_INFO. `_out.abort()` is not
  used: its pinned implementation does not reset all leftover state.
* Direct `Create` successful-token replay previously proceeded to allocate a
  second ID because cached success looked like admission success. CREATE now
  returns the cached result before filesystem work. Digest mismatch still
  conflicts. The backend's existing generation fence and QUERY semantics are
  unchanged; this is not a broad redesign of token semantics in other methods.

Persistent format, root alternation, accepted direct decoder, filenames,
READ has_profile, duplicate-next fix, legacy RGB compatibility, RT2 recovery,
and malformed/timeout/cap guards remain. No framework patch or stack enlargement.

## Execution table

All CREATE work below runs synchronously on core0. Core1 runs the Configurator
REMAPPER early-return loop, or the existing transport-recovery refusal loop.
It is not a ProfileStore caller. Frame figures are pinned O3 target `.su` values;
inline routines have no independent live frame to add. No row below implies
physical stage completion. P/E means an arbitrary state-dependent number of
LittleFS program/erase callbacks, each with the documented pause/resume pair.

| Stage / call | Own stack bytes | Owned static/storage | Flash, waits, return and observability |
|---|---:|---|---|
| main → loop → SendReport |48+16+104|backend instance|USB read dispatch; no FS; unsupported/error path|
| ReadPacket |72|frame8192|PacketIO/COBS;5s inactivity/cap8192; timeout/resync; before probe arm|
| request decode, HandleProfileStore |240 + recursive Nanopb|request2264|bounded schema/decode; version rejection; marker1 after complete decode|
| Create / validation / ID selection |192|current directory; separate static next|bounded semantic loops; invalid/full/fence/replay returns; no flash|
| WriteProfile, size pass and encode |336 + Nanopb|record4128; request profile referenced|CRC/encode failure → IO_FAILURE; marker2|
| record ReplaceVerifiedFile |inlined in WriteProfile|readback4128 separate from expected|markers17,3,4,18,19,5 bracket publication|
| adapter Write/open |72 + FS open48 + LittleFS open56|heap File impl +256-byte caches|w+ create/truncate/sync; P/E; open failure → record.temp_open_write;20→21|
| record data write/close |adapter frame + wrapper/lfs|file/cache|allocation, program, metadata sync P/E;22→23; count failure; ignored wrapper close status caught by readback|
| record temporary read/verify |Read64 + wrappers/lfs; verifier inlined|readback distinct; expected identity12 bytes|read/size/byte/CRC failure; markers4→18; no publish|
| record destination handling/rename |adapter8/16 + wrappers/lfs|paths64+64 within WriteProfile|Exists; Remove only if existing; metadata P/E;19→5; IO_FAILURE on false|
| construct next Directory |within Create192|next2616 distinct from current|copy existing, fill entry, increment generation/token; record orphan possible on later failure|
| PublishDirectory / EncodeDirectory |160 incl inlining|wire2620, verified2616|encode rejection; marker6|
| directory ReplaceInactiveRoot |inlined in PublishDirectory|same sequential readback4128|marker7 before Write; no overlap with record operation|
| directory open/write/close |same adapter/wrappers|new File/cache|24→25→26→27→8; P/E; COMMIT_UNKNOWN with specific boolean failure diagnostic|
| directory readback |Read64 + lfs|readback|marker9; exact bytes compared before semantic decoder|
| DecodeDirectoryCommit / DecodeDirectory |inline callback /32|parsed2616 then verified|length/magic/version/count/CRC/IDs validation; marker10|
| inactive destination Exists/Remove |adapter8/16 + lfs|inactive root only|P/E on Remove; active root retained on failure; marker11|
| inactive-root rename |adapter8 + FS8 + lfs rename240 + descendants|verified temp|P/E; marker12; false → COMMIT_UNKNOWN|
| update _directory / result return |Publish160 / Create192|current=next; TransactionResult16|generation guard; marker13; FS frames unwind before response|
| populate response |Handle240|response2840|bounded fields/diagnostic copy; no FS/Config writes|
| Nanopb response encode |Handle240 + encoder|frame8192 reused after complete request decode|marker14→15; no TX during serialization; error exits and disarms probe|
| WriteProfilePacket / COBS / CDC |336 + writer32/COBS24–32 + CDC|local COBS255; TinyUSB FIFO|2s whole-packet deadline; calls admitted to FIFO; USB task/mutex internals remain framework dependencies|
| response end |same TX chain|queued host bytes|marker16 only if COBS end succeeds; not host acknowledgment; probe disarmed on every normal completion/failure|

Pico flash callbacks themselves use24 bytes before SDK/ROM. Interrupt state,
mutex/FIFO loops, core1 handler ownership, normal Config persistence comparison,
source hashes and conditional P/E accounting are detailed in
[the independent flash analysis](profile_store_create_flash_analysis.md).

## Cumulative stack evidence and limits

`tools/check_glyph_profile_store_create_stack.py` recompiles actual production
translation units from PlatformIO's compilation database with `-fstack-usage`
and call-graph dumps. It gates Handle<=512, WriteProfile<=512, Create<=256,
Publish<=256, Duplicate<=128, setup<=512, and bounded TX helper<=512.
The old callback checker now calls2048 a minimum reservation, not the whole
available stack. It still rejects reintroduction of the large callback copy.

The exact baseline ELF has core0 top0x20042000/bottom0x20041800 and core1
top0x20041000/bottom0x20040800. Each reservation is0x800. ScratchY starts
0x20041000; scratchX starts0x20040000; both scratch data sections are empty.
Ordinary core stacks can grow through their4KB banks before crossing other
storage; that is distinct from the2KB reserved minimum. No guard proves safety.

A reachable record-open path with orphan cleanup is:
48 main +16 loop +104 SendReport +240 Handle +192 Create +336 WriteProfile
+72 adapter +48 FS open +56 LittleFS open +1320 LittleFS call chain
+24 flash callback = **2456 bytes** before SDK/ROM/interrupt additions.
With the original2384-byte handler,328-byte WriteProfile and64-byte adapter,
the comparable chain is **4568 bytes**, already beyond4KB without an IRQ.
This is a reachable state-dependent chain, not an assertion the device took it.
Directory publication replaces336 with160 and has its own metadata branch.
The record and directory publication frames do not coexist with one another;
ReadPacket/decode and response encoding also do not coexist with FS leaf frames.

The four-level request decoder's deliberately conservative enumerated C upper
bound is **1944 bytes** including main/loop/dispatch/handler and overcounted
substream helpers. Nested arrays iterate rather than increasing message depth.
Complete CREATE record encoding has only three message levels; CREATE response
has no profile payload and no FS frames live. The response host stress tests
exercise the full profile response separately.

**Whole-target upper bound remains UNKNOWN.** SDK/ROM flash internals, all
indirect library paths, IRQ entry/handler nesting and device-dependent metadata
recovery are not certified by `.su`.2456 is not a claim of a2456-byte global
maximum or a guarantee to fit2048. The diagnostic candidate reduces known unsafe
frames; it does not manufacture a whole-program or physical stack PASS.

## Ownership, aliasing and filesystem state

The static request owns all decoded fields (generated fixed arrays, no input
pointer callbacks). Reusing frame for response cannot overwrite request/profile.
Record expected bytes, directory expected bytes, readback, decoded parsed,
verified, current and next objects are distinct. Record and directory use the
shared readback sequentially; validators do not recurse into mutations. No core1
store calls or nested event callback into CREATE were found. Profile activation
continues to copy candidate into separate active storage. Multiple concurrent
ProfileStore instances/reentrant calls are not supported by these existing
static ownership contracts.

The representative Stage-B fixture encodes3042/3047-byte profiles, hence3074/3079
byte records; maximum envelope4128. Directory is always2620. Both representative
files exceed the pinned256-byte inline threshold and fit one4096 data block;
maximum record crosses it. Thus 'directory larger than record' is not a supported
explanation for this fixture; exact physical payload/allocator state is unknown.
Temporary record component remains30 characters. Root temp names remain valid.

Existing .tmp is truncated by w+; orphan immutable destinations may be replaced
for a non-authoritative failed first CREATE; existing inactive roots can be
removed before rename while the active root survives. Exact readback rejects
stale internally valid content. Tests cover16 stale combinations, root A/B
rotation, failures on the next inactive slot after valid generations, and retry
without factory reset. Raw physical files were not inspected. Old revisions
accumulate; the logical20-profile capacity calculation is not an FS free-space
or indefinite-update guarantee.

## Counter-hypotheses

| Hypothesis | Evidence / disposition |
|---|---|
| A cumulative stack |Proven source budget defect; repaired large frames. Physical causality unresolved.|
| B idleOtherCore wait |Unbounded in pinned source. No source-proven CREATE-specific fault; retained probe brackets FS stage.|
| C core1 cannot acknowledge |Registered before setup1; no persistent Configurator IRQ disable found. Cannot guarantee all physical execution states.|
| D repeated pause/resume |Sequential paired source paths; no missing resume/early exit found. No physical repeated-cycle proof.|
| E allocation threshold |Both representative record/directory outlined; real pinned lfs RAM test passes. Target timing/flash unknown.|
| F stale files |Host production and pinned lfs tests pass; stale-valid verification gap repaired. Physical remnants unknown.|
| G metadata remove/rename |Real lfs tests pass, deep stack and unbounded flash wait remain candidates. Separate stage markers distinguish them.|
| H alias/corruption |Expected/readback alias removed; sanitizers pass. Physical corruption is not excluded.|
| I post-commit response |Unbounded CDC loop proven and bounded for ProfileStore; dropped response controls preserve/query committed result.|
| J other wait |FS allocator scans return NOSPC; SDK ROM, mutex, flash and IRQ execution still require hardware evidence.|

## Probe and minimal next hardware packet

This is intentionally a **diagnostic** build. Only a decoded CREATE arms the
watchdog. Stage IDs1–16 cover every requested high-level boundary;17–27 split
record write/verify/destination and both files' open/data-write/close.28 indicates
an ordinary failed encode/TX path before disarm. `ProfileStoreCreateProbe.hpp` is
the authoritative numeric list. A marker is the last reached boundary, not proof
of the next operation. Eight seconds is a diagnostic deadline, not measured FS WCET.

On stall, the watchdog resets hardware, retains scratch2/3 and boots directly
into transport-only recovery before filesystem/config/display initialization.
STATUS returns IO_FAILURE with `create.hang.stage=N`; generation0 in that response
is an uninitialized transport default, **not a disk observation**. CREATE and
other mutations, GET_CONFIG and reboot commands are refused. Do not interpret
recovery IO_FAILURE as an additional storage failure. Core1 does no display/RGB
work in this recovery route. Normal successful responses disarm and clear the
marker; power loss destroys evidence. Watchdog writes MMIO only and preserves
LittleFS flash IRQ/FIFO sequencing; it intentionally changes a stall to reset.
Reset can interrupt an in-progress flash operation: no atomicity acceptance is
claimed until hardware evidence is processed.

1. Owner verifies exact committed candidate/UF2 custody, then performs the
   separately authorized manual update. This agent performs no flash operation.
2. On ready normal Configurator, one STATUS and LIST establish starting state.
   Stop if unexpected; do not infer pristine raw storage or erase anything.
3. Send exactly one authorized CREATE with recorded token/profile bytes. Bound
   host wait to30 seconds. Record full response or disconnect/timeout and elapsed
   time. No retry and no GET_DEVICE_INFO liveness probing.
4. If a watchdog reset re-enumerates USB, reconnect once and issue only STATUS
   to retrieve `create.hang.stage=N`. Save response verbatim and stop. No LIST,
   READ, Config write, further CREATE, reboot or unplug before capturing stage.
   If recovery fails to enumerate, stop and report that narrower failure; no
   stage is invented. A failure before probe arm may still yield no retained marker.
5. If CREATE returns success, record token/ID/revision/generation; the owner may
   perform the agreed read-only LIST/READ and one approved reboot/reconstruction
   check as a separate acceptance packet. No automatic CRUD campaign. No merge
   before exact human hardware PASS and independent evidence processing.

## Validation and review records

Relevant atomic/decoder/migration/real4201-predecessor/Stage A/B/C checks passed.
Expanded production backend tests use real Nanopb/PacketIO/ProfileStore with
ASAN/UBSAN, including all CRUD, three LISTs, duplicate-next negative control,
malformed COBS,5s timeout/nonmutation/resync and8192 cap. Added512 CREATE cycles,
old-valid-byte controls,2s TX drop/no-space/short-write recovery and watchdog
read-only recovery controls. Fake-MMIO watchdog tests validate control flow,
not physical reset. Pinned LittleFS C engine runs under ASAN/UBSAN against a
512KiB RAM NOR model at2620/4128 bytes with128 replacements and128 negatives;
Arduino wrappers, multicore and real flash are excluded. No usable configured
RP2040 physical/emulator execution harness was found; no physical equivalence.

Historical `check_glyph_configurator_setconfig_transaction.py` fails before its
harness with 'C024 post-integration change outside validation/evidence paths'.
Its frozen old-campaign correspondence is not amended or reported PASS. Normal
HandleSetConfig body remains byte-identical to parent. This is carried framework
scope debt; current recovery refusal has separate actual-backend coverage.
Independent review found and closed legacy-command delimiter recovery after
partial ProfileStore TX; the retained-backend GET_DEVICE_INFO control now covers
it. The fake watchdog now models SDK scratch4 modification explicitly.
Initial test compilation during fixture editing and the first stack-report
parser run failed; repaired repeat results, not those attempts, establish PASS.
No full aggregate PASS is claimed. Final exact review/build/custody is recorded
beside the content-addressed UF2 in its handoff manifest after the source commit.

Delegation: repository SUBAGENT_CONTRACTS applies; native collaboration discovered.
Read-only flash/multicore specialist and isolated test-file specialist used;
required fresh independent final review is a separate role. No Planner/Curator,
new full user chat, canonical publication, device action, or hardware claim.
