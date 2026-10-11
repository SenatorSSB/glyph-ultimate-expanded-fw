#!/usr/bin/env python3
"""Versioned repair custody only; preserve the entire physically failed package.
No mounted device paths, flashing, canonical writes or filesystem erases here.
"""
import hashlib, json, pathlib, re, shutil, subprocess
root=pathlib.Path(__file__).resolve().parents[1]; task=root.parent
repair=task/'storage-recovery-v2'; out=repair/'verification'; package=repair/'package'; profile=repair/'profile'
failed_source='8b8d829d79810d5b4597255aabce036c6970d208'
failed_sha='3f7c074bc92e3683af5aa3525b96e8f5dd75296c247b349da4ad6c5384da1bf8'
base='28ba39da5f517baa40f3dee8d868c9bb583dde4a'
def git(*args):return subprocess.check_output(['git',*args],cwd=root).decode().strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify_hashes(directory):
    for line in (directory/'hashes.txt').read_text().splitlines():
        expected,name=line.split('  ',1);assert '/' not in name and '..' not in name
        assert sha(directory/name)==expected,name
verify_hashes(task/'package')
assert sha(task/'package/firmware.uf2')==failed_sha
assert (task/'package/firmware.uf2').stat().st_size==800768
assert (task/'package/hashes.txt').read_bytes()==(out/'FAILED_PACKAGE_ORIGINAL_HASHES.txt').read_bytes()
assert not git('status','--porcelain'),'final committed source must be clean'
commit=git('rev-parse','HEAD');assert commit!=failed_source
source=root/'.pio/build/glyph_mk6/firmware.uf2'; digest=sha(source);assert digest!=failed_sha
binary=(root/'.pio/build/glyph_mk6/firmware.bin').read_bytes()
assert commit[:8].encode() in binary and (commit[:8]+'-DIRTY').encode() not in binary
inspection=json.loads((out/'uf2-inspection-final.json').read_text())[0]
assert inspection['whole_file_sha256']==digest and inspection['uf2_magic_valid'] and not inspection['errors']
assert inspection['family_ids']==['0xe48bff56'] and not inspection['missing_block_numbers'] and not inspection['duplicate_block_numbers']
assert not inspection['overlaps_official_clean_only_high_flash_range'] and not inspection['writes_outside_local_app_like_range']
assert len(inspection['segments'])==1 and int(inspection['segments'][0]['end'],16)<=0x1017f000
review=(out/'INDEPENDENT_REVIEW.md').read_text();assert 'Result: APPROVE' in review
log=(out/'build-final.log').read_text();assert '[SUCCESS]' in log
assert json.loads((out/'ISOLATION_REPORT.json').read_text())['result']=='PASS'
for abi in ['short','ordinary']:
    assert 'TOTAL checks=6106 PASS' in (out/('focused-'+abi+'.log')).read_text()
    assert 'MACRO-OFF CONTROL PASS' in (out/('macro-off-'+abi+'.log')).read_text()
assert 'OLD MARKER PROVEN DEFECT' in (out/'actual-littlefs.log').read_text()
package.mkdir(parents=True,exist_ok=True)
def copy(src,name):shutil.copy2(src,package/name)
copy(source,'firmware.uf2')
for name in ['friend-config.json','friend_profile_normalized.json','FRIEND_PROFILE_NORMALIZED.md']:copy(profile/name,name)
for name in ['README_INSTALL.md','OWNER_STORAGE_RETEST.md','OWNER_FIRST_BOOT_TEST.md','PHYSICAL_FAILURE.md','STORAGE_RECOVERY_REPORT.md']:copy(root/'friend'/name,name)
copy(root/'friend/STORAGE_RECOVERY_REPORT.md','VALIDATION_REPORT.md')
for original,name in [('build-final.log','BUILD_LOG.txt'),('uf2-inspection-final.json','UF2_INSPECTION.json'),('INDEPENDENT_REVIEW.md','INDEPENDENT_REVIEW.md'),('ISOLATION_REPORT.json','ISOLATION_REPORT.json'),('focused-short.log','FOCUSED_TESTS_SHORT.log'),('focused-ordinary.log','FOCUSED_TESTS_ORDINARY.log'),('macro-off-short.log','MACRO_OFF_SHORT.log'),('macro-off-ordinary.log','MACRO_OFF_ORDINARY.log'),('actual-littlefs.log','ACTUAL_LITTLEFS_PROBE.log'),('stack-usage.log','STACK_USAGE.txt'),('source-checks.log','SOURCE_CHECKS.txt'),('reference-checks.log','ROUNDTRIP_CHECKS.txt'),('historical-Persistence.cpp','HISTORICAL_PERSISTENCE.cpp'),('FAILED_PACKAGE_ORIGINAL_HASHES.txt','FAILED_PACKAGE_ORIGINAL_HASHES.txt')]:copy(out/original,name)
(package/'source.patch').write_bytes(subprocess.check_output(['git','diff','--binary',base,commit],cwd=root))
(package/'storage-repair.patch').write_bytes(subprocess.check_output(['git','diff','--binary',failed_source,commit],cwd=root))
(package/'SOURCE_COMMIT.txt').write_text('base='+base+'\nfailed_source='+failed_source+'\nbranch='+git('branch','--show-current')+'\ncommit='+commit+'\ntree='+git('rev-parse','HEAD^{tree}')+'\n')
duration=re.search(r'\[SUCCESS\] Took ([\d.]+) seconds',log).group(1)
manifest=f'''# Private storage-recovery-v2 build manifest

FRIEND_STORAGE_RECOVERY_REPAIR_READY
INSTALLATION_MODE: RPI_RP2_SINGLE_UF2
SEPARATE_CONFIG_PUSH_REQUIRED: NO
HARDWARE: NOT_TESTED / PRIVATE_REPAIR_READY_FOR_OWNER_TEST

## Preserved physical failure

FRIEND_SINGLE_UF2_PROVISIONING: FAIL
Observed first boot: "Config storage failure" (direct owner report).
Failed source: {failed_source}
Failed UF2: 800768 bytes / SHA-256 {failed_sha}
Failed package retained unchanged: {task/'package'}
Do not distribute that artifact as accepted. Original READY text is superseded
by PHYSICAL_FAILURE.md; every original package checksum is verified unchanged.

## Baseline, source and build

Live/local configurator: {base}
Same private branch: {git('branch','--show-current')}
New private commit: {commit}
New private tree: {git('rev-parse','HEAD^{tree}')}
Same isolated worktree: {root}
New versioned package: {package}
Build PASS, exit0, {duration} seconds; exact clean committed source.
Command: ./scripts/build-glyph-mk6-quiet.sh
Underlying command: ./scripts/pio-local.sh run -e glyph_mk6
PlatformIO6.2.0 / /usr/local/bin/python3 -m platformio; private PLATFORMIO_CORE_DIR.
Platform raspberrypi1.14.0 / 5e87ae34ca025274df25b3303e9e9cb6c120123c
ArduinoPico1.30603.0+sha.32e74d0 / ARM GCC12.3.0
Nanopb0.4.9.2 / exact build-selected Config schema.
No new PlatformIO install, canonical script change, merge or publication.
Full wrapper log preserved in BUILD_LOG.txt; original log path:
/var/folders/_f/25t1m0794kb7ms1vx8tdwgr00000gp/T/glyph_mk6_build.log

## Repair policy and data-loss warning

ROOT CAUSE of the exact device failing stage: UNPROVEN; no device FS/stage log.
PROVEN defect: v1 marker basename37 rejected by selected wrapper (<32 bytes)
and actual littlefs returns NAMETOOLONG(-36). The previous host double missed
this limit. Strong separate hypothesis: no-autoformat constructor left an
uninitialized/unmountable filesystem unavailable with no repair path.
Historical friend85794b24ad236471f1d072fe3d76678976f042a4 used begin() defaults
permitting auto-format. See STORAGE_RECOVERY_REPORT.md for exact boot routes.

Option B: canonical no-autoformat initialization FIRST. Validated baked defaults
may authorize one explicit format/remount ONLY if setConfig succeeded but the
constructor mount failed. Recovery updates that Persistence object's cached
mount result. Mounted storage NEVER formats, even on later Config/marker I/O
failure. Configuration/format/remount/provisioning failures remain fail-closed.
Private guard GLYPH_PRIVATE_FRIEND_STORAGE_RECOVERY is enabled only in this
private glyph_mk6 environment. Macro-off controls retain canonical behavior.

DATA LOSS: this private policy also formats a later unmountable filesystem.
First-install failure and later corruption cannot be distinguished using a
marker inside that filesystem. All persisted files/settings may be lost and
baked defaults restored. Normally mounted storage with a valid v2 marker
preserves legitimate later user edits. No extra persistent mechanism was added.

Marker: /friend_ult_20261011_v2.flag (27-byte basename)
Payload: friend_ultimate_20261011_applied_v2 plus newline (36 bytes).
Old v1/partial markers do not suppress v2 adoption. Checked save + persisted
validation + exact full Config encoded equality (3779/3779 bytes) precede
checked marker write/flush/close/reopen/exact size/content/EOF verification.
No large automatic Config: static reset readback and static16KiB encoding buffer.

## Validation, stack and inspection

6106 assertions per short/ordinary enum ABI (12212 total), ASan/UBSan PASS;
all previous friend assertions retained plus constructor-aware R1-R10 recovery
matrix and failed-v1 states. Macro-off controls PASS both ABIs. Production
validator, actual CRC/nanopb SaveConfig/load/equality and JSON roundtrip PASS.
24-check actual selected LittleFS probe PASS on simulated512KiB flash: erased
mount failure, explicit format/remount, old-name rejection, new Config+marker
exact persistence across remount. Not Pico hardware acceptance.
Gameplay/routing/tables/defaults/RGB source byte-identical to failed snapshot.
Stack: complete setup frame440; recovery method16; marker56; comparator16 bytes
under exact ARM/O3 flags. No private large-stack regression; frame measurements
are not cumulative/hardware stack proof. Existing unrelated prototype1240 and
LittleFS directory-method unbounded warnings remain outside this path.
Independent Luna/medium review: APPROVE, one layer.

New UF2: {source.stat().st_size} bytes
New full SHA-256: {digest}
Output: {source}
RP2040 family0xe48bff56; valid blocks={inspection['magic_valid_blocks']}.
App/update-style segment: {inspection['segments'][0]['range']} (end exclusive).
NO official Clean/Fresh high-flash overlap; NO linked filesystem
[0x1017f000,0x101ff000) overlap; NO flashing-time filesystem wipe.
Any authorized formatting happens explicitly at firmware boot through LittleFS.

Canonical/main dirty files and queue/ROADMAP/CURRENT_STATE untouched;
ISOLATION_REPORT.json records hashes and fresh live SHA. No hardware flash by
assistant. First action: OWNER_STORAGE_RETEST.md (one UF2, no Config push).
'''
(package/'BUILD_MANIFEST.md').write_text(manifest)
inventory=sorted(p.name for p in package.iterdir() if p.is_file() and p.name!='hashes.txt')
(package/'hashes.txt').write_text(''.join(sha(package/name)+'  '+name+'\n' for name in inventory))
verify_hashes(package);verify_hashes(task/'package')
assert (package/'firmware.uf2').read_bytes()==source.read_bytes()
print(json.dumps({'result':'FRIEND_STORAGE_RECOVERY_REPAIR_READY','commit':commit,'package':str(package),'uf2_size':source.stat().st_size,'uf2_sha256':digest,'failed_package_unchanged':True,'inventory':inventory+['hashes.txt']},indent=2))
