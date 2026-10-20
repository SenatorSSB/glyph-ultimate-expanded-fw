# Profile-native resource / storage / attestation inventory (M0/M1 research)

Frozen source baseline: `976ba2195b72046b32f7ecdd41063e7bad791ded`, `/private/tmp/glyph-profile-native-20261020`. No tracked firmware/schema/options/source edited by this worker. Main writer's untracked research docs may appear. Owner directive read in full from attachment `85b013f3-4d2b-4605-9e99-00561c84d96f/pasted-text-1.txt`. This is bounded research, not design freeze, implementation authorization, hardware evidence, or a claim that the native architecture already exists.

## Baseline build and measurement status

`pio run -e glyph_mk6` attempted exactly: shell exit127, `pio` not on PATH. Approved repository fallback `./scripts/build-glyph-mk6-quiet.sh` found installed Python PlatformIO, began canonical pinned platform installation, failed DNS contacting github.com before compile. Logs `/private/tmp/glyph-native-baseline-build.log`, `/private/tmp/glyph-native-baseline-fallback.log`. Parent confirmed permitted network capability; exact fallback retried with `sandbox_permissions=require_escalated`, session38262, output `/private/tmp/glyph-native-baseline-network-enabled.log`, detailed live log `$TMPDIR/glyph_mk6_build.log`. Dependency resolution currently running; no broad install retry or credential mutation. Fresh exact Mk6 RAM/flash/build result still pending; historical187344 RAM and477452 flash for GP-BIND-003 are NOT silently current measurements.

Fresh isolated ARM Cortex-M0+ production struct probes use freshly generated bindings from current tracked schema/options, installed main-workspace Nanopb0.4.91 (its `.piopm` records version), and installed ARM toolchain5.120300.240127. The probes do not reuse generated `.pio` schemas or a prior firmware image. Generator/runtime/compiler/schema/options/generated hashes are in `/private/tmp/glyph-native-resource-probes/abi.json`; source, objects and raw nm output are retained there. These are exact target ABI structure measurements, not an exact firmware rebuild or stack proof. The ARM toolchain defaults to short enums: an initial unflagged-vs-short comparison was not two ABIs. Corrected probes explicitly use `-fshort-enums` and `-fno-short-enums` and retain all raw output. Host Config figures are120bytes greater (31432/56272): fifteen CommunicationBackendConfig callback fields each have two8-byte host pointers versus two4-byte ARM pointers. Use ARM values for target budgets; the host harness is source-faithful but not target pointer ABI. PB_FIELD_32BIT optional probes are retained separately and are not labeled production without build flags.

| Type | ARM short enum bytes | ARM no-short enum bytes |
|---|---:|---:|
| Config |31312|56152|
| GameModeConfig |220|764|
| UltimateProfile |2152|2344|
| UltimateProfileTable |22|22|
| UltimateProfileCondition |22|22|
| UltimateProfileRole |24|24|
| UltimateProfileRoutingSlot |2|2|
| UltimateProfileTableRule |26|26|
| UltimateProfileOutputProgram |436|628|
| UltimateProfileOutputEffect |36|52|
| ProfileStore |4352|4736|
| ProfileStoreRequest |2304|2496|
| ProfileStoreResponse |3024|3216|

Fresh descriptors: UltimateProfile maximum encoded bound5740, request5919,response6756. This generated bound exceeds actual store admission4096 and is not a promise of persistence for every syntactically populated legacy message. Fresh Python encoding from exact tracked schema and accepted Stage fixtures: v1 profiles1960/1960 bytes, v2 profile2677 bytes, v3 complete profiles3042/3047 bytes. Their Config envelopes4064/4781/6248 bytes respectively. Raw fixtures and results `/private/tmp/glyph-native-resource-probes/{v1,v2,v3}-*.pb`, `encoded-capacity.json`.

## Existing storage and lifetime mechanisms

REUSE_AS_IS: stable nonzero uint32 IDs, incarnation, immutable revisions, checked writes/readback/sync/close/rename/publication/reconciliation, redundant directory roots and corruption isolation in `HAL/pico/src/core/ProfileStore.cpp` and `CheckedStorage.cpp`; 64 entries,16384 recovery reserve,512KiB configured FS (`platformio.ini`); actual geometry comes from mounted LittleFS config (`CheckedStorage::Capacity`) rather than the nominal limit. `ProfileStore.hpp::kMinimumAdmissionProfiles=20` is a target/static directory invariant, not proof every payload set fits.

`ProfileStore.cpp` maximum payload4096 and record4128 bytes (32header). Current record kind16-bit at offset6 is1; envelope format at4 is1. Header binds incarnation/id/revision/length and separate header/payload CRC. ReadProfile requires both1 and only payload schema1..3. Create/Update/Read/Write/Activate all currently take by-value-layout legacy UltimateProfile types and descriptors. Directory Entry stores payload_version, not runtime object or engine identity. A different payload kind/version is explicitly anticipated by `multi_profile_persistent_ultimate_profile_store_design.md:82-88`; native must not reinterpret failed V4.

REUSE_VIA_ADAPTER: payload-kind/version admission, decoding/validation, candidate publication, READ/CREATE/UPDATE host envelope and current status reporting. Native data can share record identity, transaction path and protection policy. Changing record payload dispatch is integration, not a new store/root layout. Unsupported native data must fail closed; source currently permits legacy fallback after selected activation failure (`mode_selection.cpp:128-135`), which must be specialized for a selected native identity so it cannot silently regain physical-slot meanings.

`ProfileStore::Activate` reads selected current into `_candidate_profile`, optionally exact previous revision, then copies into `_active_profile`, latches activeID/revision. Update does not mutate activecopy. Selection is `GameModeConfig.ultimate_profile_id`; SET_MODE_REFERENCE performs checked Config update; `set_mode` at backend initialization resolves selected record and passes pointer to Ultimate. Keep reference→checked commit→reboot/reinitialize→activation; inactive records are never cached in RAM.

RAM is count-independent: store has two2152-byte profile bodies, three fixed Directory workspaces (3848bytes each, Entry56bytes, freshly probed from exact extracted production declaration;11544total), fixed wire buffers. `Config` statically embeds two UltimateProfiles even compact persistent Config has no authoritative embedded body. Whole Config copies: global `config/glyph/common/src/config.cpp::config`, `Persistence::LoadConfigChecked::candidate`, shared `ConfigWriteCandidate::candidate` total93936 bytes. Request and response each embed another UltimateProfile; active/candidate add two more. Thus a naive Δ bytes appended to UltimateProfile generally expands six embedded instances across3 Config copies +2 store +1request +1response ≈10Δ static bytes, before new evaluator/cache/stack. Avoid this route.

## Twenty-profile capacity, with revisions/staging/reserve

Actual production FileCharge(n,b) is roundUp(n+4*(ceil(n/b)+1),b), not payload-only arithmetic. With b4096,32-byte header means payload<=4056 charges4096;4057..4096 charges8192. This cliff is stricter than just4096 admission.

Conservative source-derived model:20 profiles×3 protected revisions=60 records;3 roots/control3924 bytes,2 retained old directory files2620; four conservatively maximum8200-byte Config/source copies; metadata8blocks+2*roundUp((files+12)*128); staging one maximal4128 record+two3924 root files+8200 Config+4blocks; reserve16384. This uses current Capacity accounting, including its conservative retained old root/config allowance:

| component | payload<=4056 | payload4057..4096 |
|---|---:|---:|
|60 revision records|245760|491520|
|fixed root/Config copies|69632|69632|
|metadata|57344|57344|
|transaction staging|45056|45056|
|recovery reserve|16384|16384|
|total|434176|679936|
|vs524288|fits,90112 spare|fails,155648 excess|

An additional latched-active revision and2 legacy-migration dependencies conservatively raise the first total to446464, still fits; capacity depends on actual fixed files/geometry and cannot be claimed as physical PASS from arithmetic. Existing `Capacity().admissible_profiles` hardcodes representative v3 record3079; native adapter must use a truthful representative complete native envelope rather than retaining this claim unchanged. Directory64 is unaffected.

This is a genuine conflict only if complete accepted native representative cannot encode<=4056 under unchanged semantics.4096 payload admission alone does not prove20×3 maximum records. A cap at4056 for complete representative native profiles or a more compact equivalent encoding avoids budget increase; do not weaken reserve/revision recovery or increase FS to make arithmetic pass. Maximum syntactic legacy/native cardinality need not equal the representative capacity promise, but representative must populate every native function/table family independently as owner requires.

## Feasible compact representation witness (not proposed frozen architecture)

EXTEND_EXISTING separate native payload kind + distinct schema5 (leave failed experimental4 unsupported); do not append large fields to UltimateProfile. An explicit fixed-width versioned native message/body can preserve current finite condition operators and compact tables, with decode/validation/compilation outside polling. A temp-only layout feasibility witness (`compact-layout.cpp`, `compact-layout-nm.txt`) measures3416 bytes ARM for:64-byte header,28×18 raw table bytes,8×16-bit direction references,64×34-byte conditions (15domain-qualified16-bit tokens +3 counts +flags),22role records×2,19rules×4,32digital bindings×4,12effects×34 (including18 inline coords and masks). This demonstrates storage/RAM room, NOT that these exact counts cover every migration case or that a3416-byte native-struct memcpy is portable wire encoding. Serialize explicit widths/endian/order; never native padding. Full counts and full-coordinate values must be encoded in a converter specimen and source-faithful decoder proof before M1 freeze. Existing evaluator condition/role/table helpers should be adapted to access this layout, not duplicated.

A3416-byte complete wire body fits one4096 storage charge and gives~640bytes below4056 for explicit counts/checks/identity. If independent arbitrary native condition demand exceeds64, deduplicate identical conditions or use variable-length finite records; prove complete legacy conversion first. Do not silently shrink ordinary modifier/output coverage to meet the witness. Both default/short ABI measurements are needed for final actual schema structs; the temp layout has no enums so is ABI-stable.

Smallest ownership plan: one immutable active native program, one bounded candidate/compiler workspace; reuse existing4096 record scratch for native decode with explicit synchronous lifetime; neither Config, request nor response gets by-value copies of big native tables. A discriminated payload adapter can retain legacy UltimateProfile storage and separate native workspace or use one tagged union per active/candidate (careful with all legacy call sites). ProfileStore request/response need bounded native-body streaming/callback handling or a dedicated admitted payload field without large Config embedding. The source's fixed COBS8192 transfer bound can accommodate a~3.5KiB native body; actual protobuf envelope and max framing remain measurable. A wire extension affects directly involved ProfileStore tools and negotiation only; unrelated firmware transports remain unchanged.

Compiled active program must own all table/condition/effect bytes; no pointers into decode/request/transaction scratch. Publish only after complete validate/compile. Generation and payload identity must latch with program; candidate failure leaves previous immutable active program or explicit unavailable native state, never legacy reinterpretation. This layout needs exact build/RAM/stack proof before budget acceptance; old arithmetic headroom74800 against historical187344 is not current usable stack/heap headroom.

## Attestation and failed-history constraints

REUSE_VIA_ADAPTER: `RuntimeIdentity.hpp::Observe` currently proves actual primary mode is exact Ultimate object, selected Config pointer belongs to current row, selected profile pointer equals store.ActiveProfile, ready/nonrecovery state, latched activeID/revision; then streams deterministic `UltimateProfile_fields` payload digest and rechecks mode/profile. Latched revision rather than latest stored revision is essential. Digest domain `Glyph.RuntimeIdentity.UltimateProfile.v1\0`; excludes record/native padding/Config. Service core0 after complete SendReport; fixed72-byte current wire includes schema and profile digest but NO independent engine/program generation/digest field. Native program correspondence therefore requires explicit identity extension or a proven native schema→engine identity contract plus exact source-build identity, and observer must compare actual active engine/program identity to activated payload. Merely hashing newly stored native bytes is insufficient. Do not call the existing wire proof a compiled-program attestation.

GP-BIND-003 exact307d7234 / UF2 83aa255a... /979456 has owner A1-A5 PASS in `gp_bind_003_partial_evidence_2026-10-19.json`. XInput persistedID4/revision1 digest readback,90s capture2exactresponses/295viewerrecords, post ordinary unplug/replug identity observed; Configurator remains neutral. Queue is HARDWARE_VALIDATED at exact baseline, and parent owns independent strict integration/DONE chain verification. Current docs front matter contains older pending narratives; immutable newer hardware fixture wins only its bounded scope. Do not transplant GP-BIND-003 acceptance to native source or GameCube. Target query timing/peak stack remain NOT_MEASURED.

GP-BIND-00132c1bd81 / UF2ea261256... H1-H3 passed,H4 LT6-X1 also Down+A failed,H5notrun. GP-BIND-002b3d60feb /UF2bc82db6f... same H4failure,H4b/H4c/H5notrun. Stored V4record correctness did not identify H4active runtime: backend/selected Config row/activeID/revision/fullpayload/descriptor captures absent; rootcause UNPROVEN. Full native composed path must independently prove engine actual active identity and complete reports; do not import failed V4 source semantics or conclude bit-layout defect was physical rootcause.

## Cost / missing evidence

Measured: ARM structs both ABIs; exact accepted fixture encoding; source capacity formula;3416-byte compact layout witness. Fresh target build pending.

Source-bounded: activation one selected body (+at most retained prior), fixed count-independent workspace; role/rule/effect loops bounded by64/22/19/32/12 candidate design, not controller count; no heap/filesystem/parse/write in polling. `Begin`/Capacity/recovery may inspect directory/protected record metadata and bodies for migration; do not claim boot globally O(1) profiles. Existing directory scans/GC are bounded64/128, outside polling.

NOT_MEASURED: native polling time, boot/activation latency, native compile peak stack, production peak stack/heap, interrupt-composed stack, fresh target firmware RAM/flash until build completes. Obtain actual compiler stack-usage probes from fresh compileDB; those alone are per-function frames, not hardware whole-program peaks. Runtime timing and physical switch/reboot/attestation require concrete approved device packet and exact candidate/UF2, not this research.


## Worker final handoff (primary daemon continues exact build)

Finite resource research complete. Exact network-enabled fallback build remains running, session `38262`; no final build/firmware-resource result yet. Detailed log absolute path `/private/var/folders/_f/25t1m0794kb7ms1vx8tdwgr00000gp/T/glyph_mk6_build.log` (equivalent `/var/folders/...` TMPDIR spelling). Outer result log `/private/tmp/glyph-native-baseline-network-enabled.log` receives fallback summary on completion. Last observed stage: pinned Arduino-Pico framework3.6.3 recursive dependency installation; all displayed submodules checked out through tools/pyserial, `.platformio-home/packages/framework-arduinopico` now present; no tracked source compile witnessed yet. Snapshot preserved in `build-dependencies-at-worker-handoff.log`. Primary can poll `tools.write_stdin` session38262, then copy detailed log, inspect exact generated descriptors/compiler flags and source-fingerprint, record exact fresh RAM/flash/UF2 SHA. Do not claim historical187344 as the current build result. No second installation attempt or source mutation started by worker after this handoff.

Source identity for this worker: baseline HEAD976ba2195b72046b32f7ecdd41063e7bad791ded; `git status --porcelain=v1 --untracked-files=no` empty when last checked. Main writer research docs are untracked and independent of frozen active source. Probe generation and compile commands are retained in `PROBE_COMMANDS.txt`; exact source input hashes in `abi.json`. Directory probe extracts the exact current `ProfileStore::Directory` declaration before compiling; it does not edit production source. Additional PB_FIELD_32BIT variants are explicitly exploratory, not current production. No controller action, canonical publication, or firmware source implementation occurred.


## Mechanical build-resume correction — 2026-10-20T09:04Z

The former session38262 is now unavailable in both the primary and original worker contexts (`write_stdin: Unknown process id38262`). A permitted read-only process inspection confirms no PlatformIO, pio-local, build-glyph-mk6, package-installing-m1usjg8d, or chapter-build process remains (only the inspection command itself matched). Detailed log remains34176bytes,lastmodified12:01:07Europe/Helsinki; outer result log0bytes. No firmware.elf or firmware.uf2 exists in this chapter build directory. Last recorded stage remains framework recursive dependency checkout, ending tools/pyserial. There is no final exit status, source compile, current RAM/flash measurement, or artifact. Therefore the exact baseline attempt is INCOMPLETE / LOST_RUNTIME_PROCESS, not a firmware/source FAIL and not PASS. Termination mechanism is unknown; do not infer source or dependency fault from missing session. The prior 'still running' handoff is superseded by this verified process absence. No second installer/build was launched during this mechanical resume. The primary daemon must decide the owner-authorized persistent-terminal build fallback or a separately authorized exact environment continuation; historical187344 remains historical.


## Final M1 proposed ABI batch

See `/private/tmp/glyph-native-proposed-abi.md` and `/private/tmp/glyph-native-proposed-abi/report.json` for fresh temp-only callbacktag8/engine205 actual Nanopb generation and target bothABI measurements. Known static wrapper overhead464bytes ARMshort/440bytes ARMno-short; generated profile/request/response size macros disappear and existing digest consumer needs a reviewed explicit bounded replacement. No new build or installation attempt.
