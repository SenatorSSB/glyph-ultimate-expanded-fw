#!/usr/bin/env python3
"""Private v3 custody using the existing read-only main snapshot helpers."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
from default2_release import ROOT, TASK, git, sha, dump, snapshot

PREVIOUS='375c486de48ddb39814914754952b18be46cafe2'
BASE='28ba39da5f517baa40f3dee8d868c9bb583dde4a'
RELEASE=TASK/'config-refresh-v3-20261012'
OUT=RELEASE/'verification'

def current_snapshot():
    result=snapshot()  # Includes original failed package and storage-recovery-v2.
    directory=TASK/'default2-fix-20261012'/'package'
    for line in (directory/'hashes.txt').read_text().splitlines():
        expected,name=line.split('  ',1)
        assert Path(name).name==name and name not in {'.','..'}
        assert sha(directory/name)==expected, name
    result['coordinate_update_package']={p.name:sha(p) for p in sorted(directory.iterdir()) if p.is_file()}
    return result

def isolation():
    before=json.loads((OUT/'ISOLATION_BEFORE.json').read_text())
    after=current_snapshot()
    assert before==after, 'main/local/live configurator or previous package changed; inspect, never undo external work'
    report={'result':'PASS','main_head':after['head'],'main_branch':after['branch'],
            'main_status_unchanged':after['status'],'local_configurator':after['local_configurator'],
            'live_configurator':after['live_configurator'],'main_files_checked':len(after['files']),
            'all_main_files_and_index_unchanged':True,'all_three_previous_packages_unchanged':True,
            'hardware_flashing_performed':False}
    dump(OUT/'ISOLATION_REPORT.json',report)
    return report

def package():
    assert not git(ROOT,'status','--porcelain'),'clean committed source required'
    commit=git(ROOT,'rev-parse','HEAD'); assert commit!=PREVIOUS
    current_snapshot()
    isolated=json.loads((OUT/'ISOLATION_REPORT.json').read_text()); assert isolated['result']=='PASS'
    assert 'Result: APPROVE' in (OUT/'INDEPENDENT_REVIEW.md').read_text()
    counts=[]
    for abi in ['short','ordinary']:
        log=(OUT/('focused-'+abi+'.log')).read_text()
        counts.append(int(re.search(r'TOTAL checks=(\d+) PASS',log).group(1)))
        assert counts[-1]>6127 and 'V3 REFRESH PASS' in log and 'DEFAULT2 UPGRADE PASS' in log
        assert 'MACRO-OFF CONTROL PASS' in (OUT/('macro-off-'+abi+'.log')).read_text()
        assert (OUT/('baked-'+abi+'.pb')).read_bytes()==(TASK/'default2-fix-20261012/verification'/('baked-'+abi+'.pb')).read_bytes()
    assert counts[0]==counts[1]
    assert 'checks=24 PASS' in (OUT/'actual-littlefs.log').read_text()
    assert 'REFERENCE PASS' in (OUT/'reference-checks.log').read_text()
    assert 'sole runtime change is the marker path/payload v2 -> v3' in (OUT/'source-checks.log').read_text()
    build=(OUT/'build-final.log').read_text()
    duration=re.search(r'\[SUCCESS\] Took ([\d.]+) seconds',build).group(1)
    firmware=ROOT/'.pio/build/glyph_mk6/firmware.uf2'; digest=sha(firmware)
    assert digest!='d602a8ab0947592b57d0a49e0cf155d0d0ebdaf80e59a3a60a198773cf74f213'
    binary=(ROOT/'.pio/build/glyph_mk6/firmware.bin').read_bytes()
    assert commit[:8].encode() in binary and (commit[:8]+'-DIRTY').encode() not in binary
    inspection=json.loads((OUT/'uf2-inspection-final.json').read_text())[0]
    assert inspection['whole_file_sha256']==digest and inspection['uf2_magic_valid'] and not inspection['errors']
    assert inspection['family_ids']==['0xe48bff56'] and not inspection['missing_block_numbers'] and not inspection['duplicate_block_numbers']
    assert not inspection['overlaps_official_clean_only_high_flash_range'] and not inspection['writes_outside_local_app_like_range']
    assert len(inspection['segments'])==1 and int(inspection['segments'][0]['end'],16)<=0x1017f000
    out=RELEASE/'package'; out.mkdir(exist_ok=False)
    shutil.copy2(firmware,out/'firmware.uf2')
    for name in ['friend-config.json','friend_profile_normalized.json','FRIEND_PROFILE_NORMALIZED.md']:
        shutil.copy2(RELEASE/'profile'/name,out/name)
    for name in ['README_INSTALL.md','CONFIG_REFRESH_V3.md','OWNER_FIRST_BOOT_TEST.md']:
        shutil.copy2(ROOT/'friend'/name,out/name)
    shutil.copy2(TASK/'default2-fix-20261012/verification/OWNER_REPORTED_REFUSAL.md',out/'PREVIOUS_REFUSAL_REPORT.md')
    for name in ['build-final.log','uf2-inspection-final.json','INDEPENDENT_REVIEW.md','ISOLATION_REPORT.json',
                 'focused-short.log','focused-ordinary.log','macro-off-short.log','macro-off-ordinary.log',
                 'actual-littlefs.log','reference-checks.log','source-checks.log','stack-usage.log']:
        shutil.copy2(OUT/name,out/name)
    for name,base in [('source.patch',BASE),('config-refresh.patch',PREVIOUS)]:
        (out/name).write_bytes(subprocess.check_output(['git','diff','--binary',base,commit],cwd=ROOT))
    manifest=f'''# Private friend full-Config refresh v3 — 2026-10-12

INSTALLATION_MODE: RPI_RP2_SINGLE_UF2
SEPARATE_CONFIG_PUSH_REQUIRED: NO
HARDWARE: NOT_TESTED / PRIVATE_REPAIR_READY_FOR_OWNER_TEST
Owner will test on their Glyph FIRST, before friend delivery.

Owner explicitly approved replacing the full saved Config after the friend's
Stored Config rejected / Recovery required / Operation refused report. Previous
v2 reportedly booted normally on that controller. Exact device cause remains
UNPROVEN. PREVIOUS_REFUSAL_REPORT.md retains scope/identity caveats. All three
previous packages, including rejected/failed evidence, remain byte-identical.

Only active change from {PREVIOUS}: marker path/payload v2 -> v3.
Marker /friend_ult_20261012_v3.flag (27-byte basename).
Payload friend_ultimate_20261012_applied_v3 plus newline (36 bytes).
Absent/invalid v3 marker triggers exactly one full baked Config replacement,
including if a valid v2 marker and rejected Config coexist. All user settings
are replaced at this adoption, as authorized. No weakened validation. Full save,
checked readback/production validation/exact encoded equality precede checked
marker write/flush/close/reopen verification. Subsequent valid v3 boots preserve
later legitimate edits and still reject invalid stored Config rather than
silently repeating reset. All coordinates/routing/chords/RGB/defaults unchanged,
including corrected Default2 offset(0,-77)/raw(128,51). Config3779 bytes unchanged.

IMPORTANT DATA LOSS: mounted storage is NEVER formatted. Existing private
recovery can format/remount the linked LittleFS partition after initial mount
failure with successful setConfig and baked validation. Future unmountable
storage can also be erased, losing all files/settings. This is unchanged and
private-only. This UF2 is NOT a Clean/Fresh flashing-time wipe image.

Private commit: {commit}
Private tree: {git(ROOT,'rev-parse','HEAD^{tree}')}
Private branch: {git(ROOT,'branch','--show-current')}
Same worktree: {ROOT}
Original source base: {BASE}
Live configurator unchanged during repair: {isolated['live_configurator']}
No rebase/merge/main edit, new work order or runtime-loaded architecture.

Build PASS / exit0 / {duration} sec: ./scripts/build-glyph-mk6-quiet.sh
Underlying ./scripts/pio-local.sh run -e glyph_mk6; PlatformIO6.2.0,
raspberrypi1.14.0, ArduinoPico1.30603.0+sha.32e74d0, ARM GCC12.3.0.
Existing isolated environment; no new global installation.
UF2 size: {firmware.stat().st_size} bytes
UF2 SHA-256: {digest}
Valid RP2040 family0xe48bff56, one app/update-style segment
{inspection['segments'][0]['range']} (end exclusive). No Clean/Fresh high-flash
or linked filesystem [0x1017f000,0x101ff000) overlap, no flashing-time wipe.

Host validation PASS: {counts[0]} per ABI / {sum(counts)} total, sanitizers;
complete prior friend/recovery suite plus v2->v3 full refresh of valid edited,
invalid USB/RGB, bad CRC, truncated/malformed protobuf and header-size mismatch
Config; install failure matrix; exact
v3 adoption/readback/marker and later-edit preservation/later-corruption refusal.
Production validator, full Config equality/roundtrip PASS, both macro-off controls
PASS,24 selected-LittleFS host checks PASS. Source proof only marker constants
changed. Stack in stack-usage.log, static Config/buffer retained, no relevant
regression. One independent reviewer APPROVE. No hardware test by assistant.
Main index/all tracked/untracked file bytes unchanged; previous packages intact.

Retest on owner's Glyph: flash only this UF2 (full Config replacement), no Config
push, normal boot/Ultimate, LF2 Down=(128,51), RT1/A, representative modifier,
power-cycle and persistence. Then report exact artifact/results before sending
to friend. Nunchuk NOT_TESTED; no inherited hardware PASS.
'''
    (out/'BUILD_MANIFEST.md').write_text(manifest)
    (out/'hashes.txt').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.is_file() and p.name!='hashes.txt'))
    assert (out/'firmware.uf2').read_bytes()==firmware.read_bytes()
    print(json.dumps({'package':str(out),'commit':commit,'uf2_size':firmware.stat().st_size,'uf2_sha256':digest,'inventory':sorted(p.name for p in out.iterdir())},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['baseline','isolation','package'])
    args=parser.parse_args(); OUT.mkdir(parents=True,exist_ok=True)
    if args.command=='baseline':
        assert not (OUT/'ISOLATION_BEFORE.json').exists(),'preserve original baseline'
        dump(OUT/'ISOLATION_BEFORE.json',current_snapshot()); print('BASELINE PASS: main/live configurator and all three previous packages recorded')
    elif args.command=='isolation': print(json.dumps(isolation(),indent=2))
    else: package()
