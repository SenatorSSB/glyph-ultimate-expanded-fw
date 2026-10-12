#!/usr/bin/env python3
"""Private correction custody/isolation, not firmware flashing or product tooling."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT.parent
MAIN = ROOT.parents[3]
RELEASE = TASK / 'default2-fix-20261012'
OUT = RELEASE / 'verification'
PREVIOUS = 'c247985d3730812faf5c92ee59a51ce9122b31eb'
ORIGINAL_BASE = '28ba39da5f517baa40f3dee8d868c9bb583dde4a'

def git(directory, *args):
    return subprocess.check_output(['git', *args], cwd=directory).decode().rstrip('\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')

def packages():
    result = {}
    for directory in [TASK/'package', TASK/'storage-recovery-v2'/'package']:
        for line in (directory/'hashes.txt').read_text().splitlines():
            expected, name = line.split('  ', 1)
            assert Path(name).name == name and name not in {'.', '..'}
            assert sha(directory/name) == expected, str(directory/name)
        result[str(directory)] = {p.name: sha(p) for p in sorted(directory.iterdir()) if p.is_file()}
    return result

def snapshot():
    paths = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'], cwd=MAIN).split(b'\0')
    contents = {}
    for value in paths:
        if not value: continue
        name = os.fsdecode(value)
        path = MAIN/name
        if path.is_symlink(): data = os.readlink(path).encode()
        elif path.is_file(): data = path.read_bytes()
        elif not path.exists(): data = b'<absent>'
        else: raise RuntimeError('unexpected non-file in main tracked inventory: '+name)
        contents[name] = hashlib.sha256(data).hexdigest()
    return {
        'main': str(MAIN), 'head': git(MAIN,'rev-parse','HEAD'),
        'branch': git(MAIN,'branch','--show-current'),
        'status': git(MAIN,'status','--porcelain=v1'),
        'index': git(MAIN,'ls-files','--stage'), 'files': contents,
        'local_configurator': git(MAIN,'rev-parse','configurator'),
        'live_configurator': git(MAIN,'ls-remote','origin','refs/heads/configurator').split()[0],
        'preserved_packages': packages(),
    }

def check_isolation():
    before = json.loads((OUT/'ISOLATION_BEFORE.json').read_text())
    after = snapshot()
    assert before == after, 'main/local/live configurator or prior-package snapshot changed; inspect before continuing'
    report = {'result':'PASS', 'main_head':after['head'], 'main_branch':after['branch'],
              'main_status_unchanged':after['status'], 'local_configurator':after['local_configurator'],
              'live_configurator':after['live_configurator'], 'main_files_checked':len(after['files']),
              'all_main_tracked_and_untracked_bytes_and_index_unchanged':True,
              'previous_packages_hashes_unchanged':True, 'hardware_flashing_performed':False}
    dump(OUT/'ISOLATION_REPORT.json', report)
    return report

def package():
    assert not git(ROOT,'status','--porcelain'), 'source must be committed and clean'
    commit = git(ROOT,'rev-parse','HEAD')
    assert commit != PREVIOUS
    isolation = json.loads((OUT/'ISOLATION_REPORT.json').read_text())
    assert isolation['result'] == 'PASS'
    packages()
    assert 'Result: APPROVE' in (OUT/'INDEPENDENT_REVIEW.md').read_text()
    counts = []
    for abi in ['short','ordinary']:
        log = (OUT/('focused-'+abi+'.log')).read_text()
        counts.append(int(re.search(r'TOTAL checks=(\d+) PASS',log).group(1)))
        assert counts[-1] > 6106 and 'DEFAULT2 UPGRADE PASS' in log
        assert 'MACRO-OFF CONTROL PASS' in (OUT/('macro-off-'+abi+'.log')).read_text()
        assert (OUT/('baked-'+abi+'.pb')).read_bytes() == (TASK/'storage-recovery-v2'/'verification'/('baked-'+abi+'.pb')).read_bytes()
    assert counts[0] == counts[1]
    assert 'checks=24 PASS' in (OUT/'actual-littlefs.log').read_text()
    assert 'REFERENCE PASS' in (OUT/'reference-checks.log').read_text()
    assert 'sole runtime change' in (OUT/'source-checks.log').read_text()
    build = (OUT/'build-final.log').read_text()
    duration = re.search(r'\[SUCCESS\] Took ([\d.]+) seconds',build).group(1)
    source = ROOT/'.pio/build/glyph_mk6/firmware.uf2'
    digest = sha(source)
    assert digest != '8029b594cb20fd3ef541bb7d04b423f25ec8925b1323870730714003d4656a11'
    binary = (ROOT/'.pio/build/glyph_mk6/firmware.bin').read_bytes()
    assert commit[:8].encode() in binary and (commit[:8]+'-DIRTY').encode() not in binary
    inspection = json.loads((OUT/'uf2-inspection-final.json').read_text())[0]
    assert inspection['whole_file_sha256'] == digest and inspection['uf2_magic_valid'] and not inspection['errors']
    assert inspection['family_ids'] == ['0xe48bff56']
    assert not inspection['missing_block_numbers'] and not inspection['duplicate_block_numbers']
    assert not inspection['overlaps_official_clean_only_high_flash_range'] and not inspection['writes_outside_local_app_like_range']
    assert len(inspection['segments']) == 1 and int(inspection['segments'][0]['end'],16) <= 0x1017f000
    out = RELEASE/'package'
    out.mkdir(exist_ok=False)
    shutil.copy2(source, out/'firmware.uf2')
    for name in ['friend-config.json','friend_profile_normalized.json','FRIEND_PROFILE_NORMALIZED.md']:
        shutil.copy2(RELEASE/'profile'/name, out/name)
    for name in ['README_INSTALL.md','DEFAULT2_UPDATE.md','OWNER_FIRST_BOOT_TEST.md','PHYSICAL_FAILURE.md','STORAGE_RECOVERY_REPORT.md']:
        shutil.copy2(ROOT/'friend'/name, out/name)
    for name in ['build-final.log','uf2-inspection-final.json','INDEPENDENT_REVIEW.md','ISOLATION_REPORT.json',
                 'focused-short.log','focused-ordinary.log','macro-off-short.log','macro-off-ordinary.log',
                 'actual-littlefs.log','reference-checks.log','source-checks.log','stack-usage.log']:
        shutil.copy2(OUT/name, out/name)
    for name, base in [('source.patch',ORIGINAL_BASE),('default2-update.patch',PREVIOUS)]:
        (out/name).write_bytes(subprocess.check_output(['git','diff','--binary',base,commit],cwd=ROOT))
    manifest = f'''# Friend Default position 2 update — 2026-10-12

INSTALLATION_MODE: RPI_RP2_SINGLE_UF2
SEPARATE_CONFIG_PUSH_REQUIRED: NO
HARDWARE: NOT_TESTED / PRIVATE_BUILD_READY_FOR_OWNER_TEST

Only runtime delta from storage-recovery-v2: Default direction 2 offset
(-77,0) -> (0,-77), raw (51,128) -> (128,51). Physical LF2 Down.
All other table points/routing/modifiers/chords/defaults/RGB are unchanged.
Coordinates are compiled into firmware. Full Config bytes are unchanged
(3779 bytes); the same valid v2 marker skips provisioning and preserves user
edits. No new marker, Config push, forced overwrite or flashing-time wipe.

Private source baseline: {PREVIOUS}
Original configurator source base: {ORIGINAL_BASE}
Live configurator checked unchanged during this update: {isolation['live_configurator']}
Private branch: {git(ROOT,'branch','--show-current')}
New committed source: {commit}
New source tree: {git(ROOT,'rev-parse','HEAD^{tree}')}
Same isolated worktree: {ROOT}

Build: PASS / exit0 / {duration} seconds.
Command: ./scripts/build-glyph-mk6-quiet.sh
Underlying command: ./scripts/pio-local.sh run -e glyph_mk6
PlatformIO6.2.0; raspberrypi1.14.0 / ArduinoPico1.30603.0+sha.32e74d0;
ARM GCC12.3.0. Existing isolated packages/tooling; no new global installs.
UF2 size: {source.stat().st_size} bytes
UF2 full SHA-256: {digest}
UF2: valid RP2040 family0xe48bff56, single application/update-style segment
{inspection['segments'][0]['range']} (end exclusive). No Clean/Fresh high-flash
overlap and no linked filesystem [0x1017f000,0x101ff000) overlap/wipe.

Validation: {counts[0]} assertions per ABI / {sum(counts)} total under sanitizers;
all original friend and recovery checks plus explicit existing-v2-marker upgrade
and full user-Config preservation test. Production validator/full encoded equality
and binary/JSON/binary roundtrip PASS. Macro-off controls bothABIs PASS. Selected
LittleFS actual-source host flash probe24checks PASS. Sole-point source proof PASS.
Stack measurements are in stack-usage.log; no large automatic Config introduced.
One fresh independent review: APPROVE. Main index/all tracked and untracked file
bytes unchanged; local/live configurator unchanged by this task. No merge/rebase.
Past packages preserved byte-for-byte; no assistant device access/flashing.

UNCHANGED DATA-LOSS WARNING: this private firmware can explicitly format LittleFS
after initial no-autoformat mount failure if setConfig and baked validation pass.
A later unmountable/corrupted filesystem can also be erased and settings lost.
Normally mounted storage is NEVER formatted; valid v2 marker preserves user edits.
See README_INSTALL.md and DEFAULT2_UPDATE.md. Existing storage report is historical
v2 diagnosis/regression evidence, not a claim that the new artifact was tested.

Retest: flash this UF2 only, normal boot, unmodified LF2 Down=(128,51), release
neutral=(128,128), representative diagonal/modifier, power-cycle/persistence.
No hardware PASS is claimed; Nunchuk remains NOT_TESTED.
'''
    (out/'BUILD_MANIFEST.md').write_text(manifest)
    (out/'hashes.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.is_file() and p.name!='hashes.txt'))
    assert (out/'firmware.uf2').read_bytes() == source.read_bytes()
    print(json.dumps({'package':str(out),'commit':commit,'uf2_size':source.stat().st_size,'uf2_sha256':digest,'inventory':sorted(p.name for p in out.iterdir())},indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['baseline','isolation','package'])
    args = parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    if args.command == 'baseline':
        assert not (OUT/'ISOLATION_BEFORE.json').exists(), 'preserve the original snapshot'
        dump(OUT/'ISOLATION_BEFORE.json',snapshot())
        print('Baseline recorded: main index/files/refs, live configurator and both prior packages')
    elif args.command == 'isolation': print(json.dumps(check_isolation(),indent=2))
    else: package()
