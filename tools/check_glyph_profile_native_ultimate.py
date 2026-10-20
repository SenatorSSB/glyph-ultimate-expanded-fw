#!/usr/bin/env python3
"""Production native codec/evaluator versus independent frozen legacy evidence."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
from check_glyph_stage_b_ultimate_profiles import ROOT,NANOPB,run,require,make_v3_artifact
from convert_glyph_native_ultimate_profile import convert
HOST=ROOT/'tools/fixtures/profile_native_ultimate'


def compile_runner(temp,default=False):
    gen=temp/'generated';gen.mkdir();schema=ROOT/'schema/haybox'
    run([sys.executable,str(NANOPB/'generator/nanopb_generator.py'),'-I',str(schema),'-f',str(schema/'config.options'),'--error-on-unmatched','--no-timestamp','-D',str(gen),str(schema/'config.proto')])
    flags=['-O2','-Wall','-Wextra','-Werror','-Wno-unused-function','-Wno-non-c-typedef-for-linkage']+([] if default else ['-fshort-enums'])
    for inc in [ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/include',gen,NANOPB,ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',ROOT/'config/glyph/glyph_mk6/include',ROOT/'src',HOST]:flags+=['-I',str(inc)]
    objects=[]
    for source in [NANOPB/'pb_common.c',NANOPB/'pb_encode.c',NANOPB/'pb_decode.c',gen/'config.pb.c']:
        obj=temp/(source.stem+'.o');run(['cc','-std=c11',*flags,'-c',str(source),'-o',str(obj)]);objects.append(str(obj))
    oracle=temp/'legacy.o';run(['c++','-std=c++17','-DUltimate=LegacyUltimate','-I',str(HOST/'frozen'),'-I',str(ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/frozen'),*flags,'-c',str(ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/legacy_ultimate.cpp'),'-o',str(oracle)])
    sources=['src/modes/Ultimate.cpp','src/modes/UltimateNativeProfile.cpp','src/modes/UltimateNativeEvaluator.cpp','src/core/ControllerMode.cpp','src/core/InputMode.cpp','src/core/socd.cpp']
    exe=temp/'native-runner';run(['c++','-std=c++17',*flags,str(HOST/'native_runner.cpp'),*[str(ROOT/s) for s in sources],str(oracle),*objects,'-o',str(exe)])
    return exe


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--default-enum',action='store_true');a=parser.parse_args()
    import glyph_serial_config_tool as writer
    pb,jf,_=writer.load_runtime_proto_modules(ROOT)
    context=pb.GameModeConfig(mode_id=pb.MODE_ULTIMATE)
    with tempfile.TemporaryDirectory(prefix='native-ultimate-') as directory:
        temp=Path(directory);exe=compile_runner(temp,a.default_enum)
        rows=[json.loads(x) for x in (HOST/'independent_legacy/short-expected.jsonl').read_text().splitlines()]
        for row in rows:
            config=pb.Config();config.ParseFromString((HOST/'independent_legacy/corpus'/(row['id']+'.pb')).read_bytes())
            native,metadata=convert(config.ultimate_profiles[0],context,pb,'historical_compatibility')
            wire=temp/(row['id']+'.pb');wire.write_bytes(native.SerializeToString(deterministic=True))
            result=run([str(exe),str(wire),row['input']]).split()
            require(result==[row['buttons'],*map(str,row['axes'])],f"independent native mismatch {row['id']}: {result} expected {row}")
        print(f'PASS independent legacy/native full-output corpus={len(rows)}')
        config,_=writer.encode_artifact_payload(make_v3_artifact(),pb,jf)
        for version in (1,2,3):
            sample=pb.Config();sample.CopyFrom(config)
            p=sample.ultimate_profiles[0];p.schema_version=version
            if version<3:p.ClearField('output_program')
            if version==1:
                for field in ('roles','routing_slots','table_rules','default_table_id'):p.ClearField(field)
            native,_=convert(p,context,pb,'historical_compatibility')
            wire=temp/('ordinary'+str(version)+'.pb');wire.write_bytes(native.SerializeToString());legacy=temp/'legacy.pb';legacy.write_bytes(sample.SerializeToString())
            print(f'v{version}: '+run([str(exe),str(wire),'matrix',str(legacy)]),end='')
    return 0
if __name__=='__main__':raise SystemExit(main())
