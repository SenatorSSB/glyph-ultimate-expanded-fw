# Private storage-recovery-v2 diagnosis, policy and validation

## Physical evidence and root-cause status

FRIEND_SINGLE_UF2_PROVISIONING: FAIL.
Owner reports exact v1 source `8b8d829d79810d5b4597255aabce036c6970d208`,
800,768-byte UF2 SHA-256
`3f7c074bc92e3683af5aa3525b96e8f5dd75296c247b349da4ad6c5384da1bf8`,
flashed manually through RPI-RP2; first boot displayed "Config storage failure".
Original package and original verification evidence remain unchanged outside
the repair directory. PHYSICAL_FAILURE.md supersedes their historical READY text.

ROOT CAUSE of the exact device failing stage: UNPROVEN (no stage telemetry or
filesystem dump). Two source-backed failure routes are identified, not conflated:

1. Strong mount hypothesis: current constructor sets LittleFSConfig(false),
   records setConfig and begin results, and never retries. Historical friend
   branch `glyph/friend-fw-final-faifra-layout` at
   `85794b24ad236471f1d072fe3d76678976f042a4` calls only LittleFS.begin(). The
   selected library's default LittleFSConfig permits auto-format; begin attempts
   mount, then format/remount only if auto-format is enabled. Thus uninitialized
   or incompatible/unmountable storage can work historically yet fail now.
2. PROVEN independent v1 defect: its marker basename is 37 bytes; selected
   Arduino-Pico LittleFS compiles LFS_NAME_MAX=32, and wrapper pathValid rejects
   any component >=32 bytes. LittleFSImpl::open returns an invalid File before
   opening the old marker. Even with mounted storage and valid Config adoption,
   v1 cannot complete marker creation. Exact selected littlefs C source on
   simulated flash reproduces LFS_ERR_NAMETOOLONG (-36); literal wrapper
   pathValid rejects the old name. This is a proven source/library defect and a
   sufficient explanation for refusal, but does not prove how far the device
   progressed before refusal. The old host File double missed filename limits;
   that validation gap is corrected, not hidden.

## Failed v1 boot order and all relevant refusal routes

1. Global `config = glyph_default_config()` initializes the full baked Config;
   global Persistence construction initializes storage before Arduino setup.
   Their relative cross-translation-unit construction order is not required by
   the helper; both are complete before setup, and Config construction uses no FS.
2. Persistence constructor calls `LittleFS.setConfig(LittleFSConfig(false))`;
   false leaves configuration false/mount false and does not call begin.
3. If configuration succeeds, begin attempts no-autoformat mount; false is
   cached as `_mounted=false`. `IsAvailable()` requires both cached flags.
4. setup honors the unchanged manual bootloader entry path, then installs the
   production validator and validates baked Config. A failure here shows
   "Config defaults rejected", not the observed storage text.
5. v1 provision_once checks IsAvailable before marker access. If false it returns
   false immediately; no marker/save/readback occurs. It has no mount repair API.
   SaveConfig itself would also immediately return false on unavailable storage
   before opening/writing config.bin (mechanically tested with the real constructor).
6. On available storage, v1 checks exact marker contents; invalid/missing/open
   failure leads to validating and saving the baked Config.
7. Failed SaveConfig returns false. Successful save proceeds to static/reset
   checked readback, production validation and full nanopb equality; any failure
   returns false. A valid but different full Config also refuses.
8. Only after equal readback does v1 try opening its marker for writing; that
   overlong name is rejected by the selected wrapper. Open/write/reopen-verification
   failures all return false. Mere partial marker existence never counted valid.
9. Any helper false maps directly to `refuse_boot(BootOutcome::StorageFailure)`
   and the observed text. No normal boot publication/backend gameplay follows.
10. Helper true permits ordinary LoadConfigChecked(config). Rejected maps to
    "Stored Config rejected"; non-Loaded storage failure maps to the observed
    "Config storage failure". Normal checked load and startup-index validation
    precede publishing Normal. Existing core1 refusal gates remain unchanged.

The screen alone therefore cannot prove mount, SaveConfig, readback, equality,
marker or ordinary-load stage. No physical recovery PASS is claimed.

## Exact private repair policy

Option B: retain the canonical no-autoformat constructor and all existing
SaveConfig/LoadConfigChecked/validator/refusal bodies. Add only a guarded,
clearly named PrivateFriendRecoverUnmountableStorage method. The compile define
GLYPH_PRIVATE_FRIEND_STORAGE_RECOVERY is enabled only in this private branch's
glyph_mk6 environment. No canonical checkout or branch is changed/merged.

After validator installation, provision_once validates baked Config before
destructive recovery. If IsAvailable is true, no recovery/format occurs. If
setConfig failed, recovery refuses without format. If setConfig succeeded but
the constructor's no-autoformat mount failed, recovery calls LittleFS.end(),
LittleFS.format(), LittleFS.end() again (format may internally mount for timestamps),
then checked LittleFS.begin(), updating the same Persistence object's cached
mount status. Format or remount failure refuses; each installer invocation makes
at most one format attempt. setup invokes it once before core1 normal release.

No manual flash addresses, custom erase code, implicit auto-format setting,
new generic Config mechanism or flashing-time wipe is added. Format uses only
the existing selected library/linked LittleFS partition. A mounted filesystem
with bad Config or marker I/O is never formatted to repair those failures.

LATER-BOOT DATA-LOSS LIMITATION: there is no external adoption marker. An
unmountable later filesystem cannot reveal its prior v2 marker, so it cannot be
distinguished from first install. This explicitly authorized private policy
formats on any such boot mount failure and may erase all settings/files and
restore baked defaults. README/manifest warn the friend. Mounted storage with
a valid marker preserves later legitimate Config changes and never rewrites.

New marker: `/friend_ult_20261011_v2.flag` (27-byte basename, statically checked
against wrapper limit). Exact payload: `friend_ultimate_20261011_applied_v2\n`
(36 bytes). v2 deliberately re-adopts even if raw/empty/partial/old v1 marker
state exists; valid v2 markers prevent future overwrite. Plausible failed v1
states (unmountable FS, absent/partial/valid config.bin, invalid/old marker) are
covered. Old marker is not used as proof or deleted unnecessarily on mounted FS.

Complete adoption proof remains: production baked validation -> successful save
-> checked persisted load -> production readback validation -> exact complete
nanopb byte/length equality -> marker checked write -> flush/close -> reopen
and exact size/content/EOF verification. Failure leaves no valid v2 applied state.
Readback Config resets on every use and remains static; encoding buffer is
bounded static16KiB. No large automatic Config or new heap Config is introduced.

## Focused validation and scope

Actual-source private suite PASS: 6,106 assertions per ABI, 12,212 total, short
and ordinary enums under ASan/UBSan. Retains every previous 6,051 friend-focused
assertion and adds the constructor-aware recovery matrix R1-R10: mounted old
Config/no marker adopts without format; mounted valid marker skips; initial
mount failure -> format/remount -> complete equal Config/marker -> ordinary
checked load; format failure; remount failure; recovered save failure; recovered
valid-but-different readback; marker open/write/readback failures; actual second
constructor boot no format/rewrite; later legitimate Config edit preserved.
Extra negatives cover configuration failure and invalid defaults with no format,
and plausible failed-v1 states. No implicit auto-format is enabled.

Macro-off controls execute the same Persistence source without the private define
and retain canonical no-autoformat/unavailable fail-closed behavior in both ABIs.
Production full Config validator PASS; actual CRC/nanopb SaveConfig/load/equality
PASS, expected/readback 3,779 bytes each. JSON/binary roundtrip remains exact.
All friend gameplay/table/remap/default/RGB source files are byte-identical to
the failed source snapshot: no friend profile semantics were changed.

Actual selected LittleFS probe: 24 checks PASS under sanitizers, simulated erased
512KiB flash, same read/prog256/block4096/block_cycles16/cache256/lookahead256
and NAME_MAX32 as target. Reproduces erased mount failure and old marker rejection;
explicit format/remount writes full Config and v2 marker and preserves exact
bytes across unmount/remount without another format. Wrapper pathValid body is
extracted literally and source hashes recorded. This is host flash simulation,
not Pico hardware or proof that the friend's initial mount actually failed.

Stack usage, candidate/final wrapper logs, UF2 inspections, source/isolation proof
and independent reviewer result are retained with the versioned repair package.
No hardware was flashed by the assistant. Final hardware status remains
NOT_TESTED / PRIVATE_REPAIR_READY_FOR_OWNER_TEST until the short owner retest.
