#!/usr/bin/env python3
"""Assemble only a reviewed clean-commit private artifact; never touches devices.
Run after final clean wrapper build and read-only inspection are complete.
"""
import hashlib, json, pathlib, shutil, subprocess, sys
raise SystemExit('The v1 package physically FAILED and is immutable evidence. Use friend/assemble_storage_recovery_package.py for the separately versioned repair.')
root=pathlib.Path(__file__).resolve().parents[1]; task=root.parent
package=task/'package'; verification=task/'verification'; profile=task/'profile'
def git(*args): return subprocess.check_output(['git',*args],cwd=root).decode().strip()
assert not git('status','--porcelain'), 'source snapshot must be clean'
commit=git('rev-parse','HEAD'); base='28ba39da5f517baa40f3dee8d868c9bb583dde4a'
source=root/'.pio/build/glyph_mk6/firmware.uf2'
data=source.read_bytes(); sha=hashlib.sha256(data).hexdigest()
assert sha!='92708652b354eb4d3bf3ccd28586e78d062988b00c6d2dc96dd7758db0c5d4de'
inspection=json.loads((verification/'uf2-inspection-final.json').read_text())[0]
assert inspection['whole_file_sha256']==sha and inspection['uf2_magic_valid']
assert not inspection['overlaps_official_clean_only_high_flash_range']
assert not inspection['writes_outside_local_app_like_range']
assert len(inspection['segments'])==1 and int(inspection['segments'][0]['end'],16)<=0x1017f000
review=(verification/'INDEPENDENT_REVIEW.md').read_text()
assert 'APPROVE' in review
log=(verification/'build-final.log').read_text()
assert '[SUCCESS]' in log and 'stack usage is 26992' not in log
binary=(root/'.pio/build/glyph_mk6/firmware.bin').read_bytes()
assert commit[:8].encode() in binary, 'firmware must identify exact committed source'
assert (commit[:8]+'-DIRTY').encode() not in binary, 'dirty build is not deliverable'
package.mkdir(exist_ok=True)
shutil.copy2(source,package/'firmware.uf2')
for name in ['friend-config.json','friend_profile_normalized.json','FRIEND_PROFILE_NORMALIZED.md']:
    shutil.copy2(profile/name,package/name)
for name in ['README_INSTALL.md','OWNER_FIRST_BOOT_TEST.md','VALIDATION_REPORT.md']:
    shutil.copy2(root/'friend'/name,package/name)
shutil.copy2(verification/'INDEPENDENT_REVIEW.md',package/'INDEPENDENT_REVIEW.md')
shutil.copy2(verification/'uf2-inspection-final.json',package/'UF2_INSPECTION.json')
shutil.copy2(verification/'build-final.log',package/'BUILD_LOG.txt')
shutil.copy2(verification/'ISOLATION_REPORT.json',package/'ISOLATION_REPORT.json')
(package/'source.patch').write_bytes(subprocess.check_output(['git','diff','--binary',base,commit],cwd=root))
(package/'SOURCE_COMMIT.txt').write_text('base='+base+'\nbranch='+git('branch','--show-current')+'\ncommit='+commit+'\ntree='+git('rev-parse','HEAD^{tree}')+'\n')
import re
duration=re.search(r'\[SUCCESS\] Took ([\d.]+) seconds',log).group(1)
manifest=f'''# Friend single-UF2 build manifest

INSTALLATION_MODE: RPI_RP2_SINGLE_UF2
SEPARATE_CONFIG_PUSH_REQUIRED: NO
HARDWARE: NOT_TESTED / PRIVATE_BUILD_READY_FOR_OWNER_TEST

Base/live configurator: {base}
Private branch: {git('branch','--show-current')}
Private commit: {commit}
Private tree: {git('rev-parse','HEAD^{tree}')}
Private worktree: {root}
Final package: {package}

Exact clean committed source build: PASS, exit 0, {duration} seconds.
Command: ./scripts/build-glyph-mk6-quiet.sh
Underlying command: ./scripts/pio-local.sh run -e glyph_mk6
PlatformIO 6.2.0 through /usr/local/bin/python3 -m platformio (Python 3.14).
PLATFORMIO_CORE_DIR: private worktree/.platformio-home
No Python/PlatformIO installation or canonical script changes in this repair.
Earlier missing global pio/platformio names are immaterial to the wrapper.
Prior banner-only output was not authoritative; completed exit status/full log
confirm builds. A narrower historical original-startup cause is not recoverable
from retained evidence and is not claimed here.

Platform: raspberrypi 1.14.0, 5e87ae34ca025274df25b3303e9e9cb6c120123c
framework-arduinopico: 1.30603.0+sha.32e74d0
toolchain-rp2040-earlephilhower: 5.120300.240127, ARM GCC 12.3.0
Schema/nanopb: build-selected config.pb and nanopb 0.4.9.2

UF2 size: {len(data)} bytes
UF2 SHA-256: {sha}
Original output: {source}
Wrapper full log: /var/folders/_f/25t1m0794kb7ms1vx8tdwgr00000gp/T/glyph_mk6_build.log
Preserved exact final log: BUILD_LOG.txt
App segment: {inspection['segments'][0]['range']} (end exclusive)
Family: RP2040 0xe48bff56; valid blocks: {inspection['magic_valid_blocks']}
Classification: application/update-style, no Clean/Fresh high-flash write.
Linked filesystem [0x1017f000,0x101ff000): NO UF2 overlap.
First boot writes complete Config and private marker normally; no FS format.

Stack: old ~26992-byte helper removed. Exact ARM/O3 compiler measurement:
helper/equality inlined into setup frame440 bytes; marker56, comparator16,
production checked-load implementation224, Ultimate analog112. Static readback
Config resets each attempt; bounded static16KiB encoding buffer. These are
frame sizes, not a hardware/cumulative-stack claim. No private high-stack
warning. Unchanged LittleFS directory-method unbounded warnings and unrelated
prototype self-test1240 remain outside installer path.

Validation: 6051 assertions per short/ordinary enum ABI (12102 total), ASan/UBSan;
all owner bindings/tables/priorities, production Config validator, real CRC /
nanopb save/load, complete serialized equality3779 bytes each, A-J fault matrix,
source safety and binary/JSON/binary roundtrip PASS. See VALIDATION_REPORT.md.
Repaired-scope independent review: APPROVE (Luna/medium).

Marker: /friend_ultimate_20261011_applied.flag
Exact payload: friend_ultimate_20261011_applied_v1 followed by newline (36 bytes).
Save + validated exact readback precede marker; write/flush/close/reopen exact
marker verification precedes installer success. Valid marker avoids overwrite
and retains normal checked Config load. Malformed marker never counts applied.

Earlier799744-byte SHA92708652b354eb4d3bf3ccd28586e78d062988b00c6d2dc96dd7758db0c5d4de
is REJECTED / SUPERSEDED and is NOT in this delivery package. It is retained
only outside package under verification/REJECTED-92708652-firmware.uf2.
No hardware flash, canonical modification, merge or publication occurred.
'''
(package/'BUILD_MANIFEST.md').write_text(manifest)
inventory=sorted(p.name for p in package.iterdir() if p.is_file() and p.name!='hashes.txt')
(package/'hashes.txt').write_text(''.join(hashlib.sha256((package/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in inventory))
for line in (package/'hashes.txt').read_text().splitlines():
    digest,name=line.split('  ',1); assert hashlib.sha256((package/name).read_bytes()).hexdigest()==digest
assert (package/'firmware.uf2').read_bytes()==data
print(json.dumps({'package':str(package),'commit':commit,'uf2_size':len(data),'uf2_sha256':sha,'inventory':sorted(p.name for p in package.iterdir() if p.is_file()),'hashes':'PASS'},indent=2))
