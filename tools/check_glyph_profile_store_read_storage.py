#!/usr/bin/env python3
"""No-device actual LittleFS long-history READ/real nanopb encoding controls."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from check_glyph_stage_b_ultimate_profiles import NANOPB, ROOT, make_v3_artifact
from check_glyph_profile_store_littlefs_host import FRAMEWORK
from check_glyph_profile_store_liveness_host import run, SOURCES

FROZEN = 'd59684b9368be61183881bdfc82adc774ad5f0ba'
HOST = ROOT / 'tools/fixtures/profile_store_read_storage'
HISTORY = ROOT / 'tools/fixtures/profile_store_liveness_host/liveness_harness.cpp'
DEFAULT_EVIDENCE = Path('/Users/rasmus.pekkarinen/Personal code/glyph-ultimate-expanded-fw/local_backups/hardware-tests/multi-profile-store-strict-hardening-20261016/responses')


def maximum_profile(message):
    """Maximize all admitted variable-width bytes within the fixed Stage-C shape."""
    p = message.ultimate_profiles[0]
    for table in p.tables:
        for c in table.coordinates: c.x = c.y = 255
    tokens = [s.slot_id for s in p.routing_slots][:15]
    for item in [*p.roles, *p.table_rules]:
        for name, values in [('all_tokens', tokens[:2]), ('any_tokens', tokens[2:6]), ('none_tokens', tokens[6:])]:
            getattr(item.condition, name)[:] = values
    p.default_table_id = 27
    for i, rule in enumerate(p.table_rules): rule.priority = 255 - i; rule.table_id = 27
    for effect in p.output_program.effects:
        effect.gate_token = 1; effect.gate_inverted = True
        if effect.phase == 1:
            effect.digital_set_mask = 2048; effect.digital_clear_mask = 2047
        elif effect.phase == 9:
            effect.value = 255; effect.suppress = True
        else:
            effect.coordinate_mode = 4; effect.table_id = effect.mode_table_id = 0
            effect.fixed_x = effect.fixed_y = 0
            effect.coordinates[:] = [255] * 18
            effect.suppress = True
            if effect.phase == 10: effect.value = 7
    return p


def instrument(source):
    """Only host-copy insertions, after successful production operations."""
    begin = source.index('bool ProfileStore::ReadProfile(')
    end = source.index('ProfileStore::Status ProfileStore::Read(', begin)
    body = source[begin:end]
    # Read/close, integrity, decode and validation anchors are deliberately exact.
    replacements = [
        ('    if (Get32(wire) != kRecordMagic', '    ReadStoragePhase(0);\n    if (Get32(wire) != kRecordMagic'),
        ('    if (Get16(wire + 4) != 1', '    ReadStoragePhase(1);\n    if (Get16(wire + 4) != 1'),
        ('    if (out.schema_version < 1', '    ReadStoragePhase(2);\n    if (out.schema_version < 1'),
        ('    return ValidateProfile(out);', '    const bool valid = ValidateProfile(out);\n    if (valid) ReadStoragePhase(3);\n    return valid;'),
    ]
    if 'const bool valid = ValidateProfile(out);' in body:
        replacements[-1] = ('    const bool valid = ValidateProfile(out);', '    const bool valid = ValidateProfile(out);\n    if (valid) ReadStoragePhase(3);')
    for old, new in replacements:
        if body.count(old) != 1: raise RuntimeError('READ host instrumentation anchor changed: '+old)
        body = body.replace(old, new)
    return 'extern void ReadStoragePhase(unsigned);\n'+source[:begin]+body+source[end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, help='optional retained hardware responses directory; defaults to exact checked-in evidence copy')
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {'frozen_candidate': FROZEN, 'physical_device_actions': 0, 'runs': {}, 'source_sha256': {}}
    try:
        if json.loads((FRAMEWORK/'package.json').read_text())['version'] != '1.30603.0':
            raise RuntimeError('expected pinned Arduino-Pico 3.6.3')
        import glyph_serial_config_tool as writer
        pb, jf, _ = writer.load_runtime_proto_modules(ROOT)
        message, _ = writer.encode_artifact_payload(make_v3_artifact(), pb, jf)
        retained = (args.evidence_dir/'post-reset-adjudication-read-id1.json') if args.evidence_dir else HOST/'physical_id1_response.json'
        physical = jf.ParseDict(json.loads(retained.read_text())['response'], pb.ProfileStoreResponse())
        actual_file = args.output_dir/'physical-id1-response.pb'
        actual_file.write_bytes(physical.SerializeToString(deterministic=True))
        retained_additional = []
        report['retained_additional_responses'] = []
        for profile_id in (3, 4, 22):
            evidence = (args.evidence_dir/f'post-reset-adjudication-read-id{profile_id}.json') if args.evidence_dir else HOST/f'physical_id{profile_id}_response.json'
            response = jf.ParseDict(json.loads(evidence.read_text())['response'], pb.ProfileStoreResponse())
            if response.profile_id != profile_id or response.store_generation != 160:
                raise RuntimeError('retained response identity/generation mismatch')
            binary = args.output_dir/f'physical-id{profile_id}-response.pb'
            binary.write_bytes(response.SerializeToString(deterministic=True))
            retained_additional.append(binary)
            report['retained_additional_responses'].append({'id': profile_id,
                'evidence_path': str(evidence), 'evidence_sha256': hashlib.sha256(evidence.read_bytes()).hexdigest(),
                'profile_bytes': len(response.profile.SerializeToString()), 'response_bytes': binary.stat().st_size,
                'response_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
                'generation': response.store_generation, 'revision': response.profile_revision,
                'provenance': 'canonical protobuf reconstruction from retained physical decoded response JSON; not original raw USB bytes'})
        maximum = pb.Config(); maximum.CopyFrom(message)
        maximal = maximum_profile(maximum)
        maximal_file = args.output_dir/'maximum-stage-c-profile.pb'
        maximal_file.write_bytes(maximal.SerializeToString(deterministic=True))
        maximum_response = pb.ProfileStoreResponse(protocol_version=1, profile_id=1, profile_revision=130, store_generation=160)
        maximum_response.profile.CopyFrom(maximal)
        (args.output_dir/'maximum-stage-c-response.pb').write_bytes(maximum_response.SerializeToString(deterministic=True))
        # Physical ID1 is v1. Preserve its bytes in ID1; retain v3 in ID3/later records.
        message.ultimate_profiles[1].CopyFrom(physical.profile)
        fixture = args.output_dir/'history-config.pb'; fixture.write_bytes(message.SerializeToString())
        report['retained_evidence'] = {'path': str(retained), 'sha256': hashlib.sha256(retained.read_bytes()).hexdigest(),
            'profile_bytes': len(physical.profile.SerializeToString()), 'full_response_bytes': actual_file.stat().st_size}
        report['maximum_stage_c_profile_bytes'] = maximal_file.stat().st_size
        flags = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g', '-O1']
        with tempfile.TemporaryDirectory(prefix='glyph-read-storage-') as directory:
            temp = Path(directory); generated = temp/'generated'; generated.mkdir()
            nanopb = Path(os.environ.get('GLYPH_PROFILE_STORE_NANOPB', str(NANOPB)))
            schema = ROOT/'schema/haybox'
            run([sys.executable,nanopb/'generator/nanopb_generator.py','-I',schema,'-f',schema/'config.options','--error-on-unmatched','--no-timestamp','-D',generated,schema/'config.proto'])
            library = FRAMEWORK/'libraries/LittleFS'
            inc = [x for p in [generated,nanopb,ROOT/'include',ROOT/'HAL/pico/include', ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',library/'lib/littlefs'] for x in ['-I',p]]
            objects=[]
            for source in [nanopb/'pb_common.c',nanopb/'pb_decode.c',nanopb/'pb_encode.c',generated/'config.pb.c',library/'src/lfs.c',library/'src/lfs_util.c']:
                obj=temp/(source.stem+'.o')
                alloc=['-include',ROOT/'tools/fixtures/profile_store_liveness_host/lfs_alloc.h','-Dmalloc=liveness_lfs_malloc','-Dfree=liveness_lfs_free'] if source.stem.startswith('lfs') else []
                run(['cc','-std=c11',*flags,'-fshort-enums','-DLFS_NAME_MAX=32',*alloc,*inc,'-c',source,'-o',obj]); objects.append(obj)
                report['source_sha256'][str(source)]=hashlib.sha256(source.read_bytes()).hexdigest()
            history=HISTORY.read_text()
            history=history.replace('#include "../profile_store_strict_host/strict_harness.cpp"', '#include '+json.dumps(str(ROOT/'tools/fixtures/profile_store_strict_host/strict_harness.cpp')))
            history=history.replace('int main(int argc, char **argv) {', '#include '+json.dumps(str(HOST/'read_observer.inc'))+'\nint main(int argc, char **argv) {')
            history=history.replace('require(argc == 2, "fixture argument");','require(argc == 7, "fixture arguments");')
            history=history[:history.index('        for (unsigned cycle = 0; cycle < 2048; ++cycle) {')]+(HOST/'read_tail.inc').read_text()
            harness=temp/'read_harness.cpp'; harness.write_text(history)
            frozen=temp/'frozen'
            for relative in SOURCES:
                content=subprocess.run(['git','show',FROZEN+':'+relative],cwd=ROOT,capture_output=True,check=True).stdout
                target=frozen/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
            validation=[ROOT/p for p in ['src/modes/UltimateNativeProfile.cpp','src/core/config_validation.cpp','src/core/config_button_validation.cpp','src/core/config_usb_default_validation.cpp','src/core/config_rgb_target_validation.cpp','config/glyph/common/src/glyph_config_validation.cpp']]
            for label,source_root in [('frozen_d596',frozen),('current_candidate',ROOT)]:
                source=(source_root/SOURCES[0]).read_text()
                probe=temp/(label+'.cpp')
                probe.write_text(instrument(source)+'\nbool GlyphMountedReadRangeProbe(const char *p,size_t o,uint8_t *b,size_t n){MountedStorage s;return s.ReadRange(p,o,b,n);}\n')
                exe=temp/label
                command=['c++','-std=c++17',*flags,'-fshort-enums','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-unused-variable','-DLFS_NAME_MAX=32','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1','-DGLYPH_STRICT_HARDENING_CANDIDATE=1', '-DREAD_PRODUCTION_TRACE='+('1' if label == 'current_candidate' else '0'),'-I',source_root/'include',*inc,harness,probe,source_root/SOURCES[1],*validation,*objects,'-o',exe]
                run(command)
                output=run([exe,fixture,maximal_file,actual_file,*retained_additional])
                (args.output_dir/(label+'.log')).write_text(output)
                report['runs'][label]={'result':'PASS','output':output,'source_sha256':hashlib.sha256(source.encode()).hexdigest()}
                print(label+':\n'+output,flush=True)
        for p in [Path(__file__),HISTORY,*HOST.glob('*.inc'),*HOST.glob('physical_id*_response.json'),ROOT/'include/core/ProfileStoreReadTrace.hpp',*(ROOT/s for s in SOURCES),ROOT/'src/modes/UltimateNativeProfile.cpp',ROOT/'src/core/config_validation.cpp',ROOT/'schema/haybox/config.options']:
            report['source_sha256'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
        report['result']='PASS'
        (args.output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print('glyph_profile_store_read_storage: PASS; storage/encode controls only, no physical causality claim')
        return 0
    except Exception as error:
        print('glyph_profile_store_read_storage: FAIL: '+str(error)); return 1

if __name__=='__main__':raise SystemExit(main())
