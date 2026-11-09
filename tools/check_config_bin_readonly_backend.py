#!/usr/bin/env python3
"""Actual backend COBS and candidate guards, bounded synthetic inputs only."""
from pathlib import Path
import argparse,hashlib,os,struct,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
def cobs(data):
    frames=[]
    for raw in data.split(b'\0'):
        if not raw:continue
        at=0;out=bytearray()
        while at<len(raw):
            n=raw[at];assert n and at+n<=len(raw);at+=1
            out+=raw[at:at+n-1];at+=n-1
            if n<255 and at<len(raw):out.append(0)
        frames.append(bytes(out))
    return frames

def function(text,name):
    start=text.index(name);start=text.index('{',start);depth=1;at=start+1
    while depth:
        depth+=(text[at]=='{')-(text[at]=='}');at+=1
    return text[start:at]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--framework',type=Path,default=Path.home()/'.platformio/packages/framework-arduinopico');ap.add_argument('--libdeps',required=True,type=Path);args=ap.parse_args()
    backend=ROOT/'HAL/pico/src/comms/ConfiguratorBackend.cpp';text=backend.read_text()
    old=subprocess.check_output(['git','show','c7e2386f45fbde44ed1bec0b56d1fe033115462e:HAL/pico/src/comms/ConfiguratorBackend.cpp'],cwd=ROOT,text=True)
    for name in ['bool ConfiguratorBackend::HandleRuntimeIdentity()','bool ConfiguratorBackend::CompleteStatusDispatch()','bool ConfiguratorBackend::RespondProfileStore()']:
        assert function(text,name)==function(old,name),name+' changed'
    assert '#define GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC 0' in (ROOT/'include/core/ConfigBinReadOnlyDiagnostic.hpp').read_text()
    persistence=(ROOT/'HAL/pico/src/core/Persistence.cpp').read_text()
    constructor=function(persistence,'Persistence::Persistence()')
    assert constructor.index('InstallReadOnlyMount()')<constructor.index('LittleFS.begin()')
    config=(ROOT/'config/glyph/common/src/config.cpp').read_text()
    setup=function(config,'void setup()')
    assert setup.index('#if GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC')<setup.index('persistence.LoadConfigChecked(config)')
    module=(ROOT/'HAL/pico/src/core/ConfigBinReadOnlyDiagnostic.cpp').read_text()
    assert module.count('"/config.bin"')==1
    for forbidden in ['lfs_file_write(','lfs_remove(','lfs_rename(','lfs_format(','LoadConfig','BeginRecovery','PackageStorageFence::']:
        assert forbidden not in module
    builder=ROOT/'tools/fixtures/glyph_package_v1/transaction/build.py'
    source=builder.read_text()
    def replace(a,b):
        nonlocal source
        assert source.count(a)==1,(a,source.count(a));source=source.replace(a,b)
    replace("here=Path(__file__).resolve().parent","here=Path(__file__).resolve().parent\n dependencies=Path("+repr(str(args.libdeps.resolve()))+")")
    # Reuse only the established actual-source compilation recipe, never a
    # retained corpus or its scenarios. All input bytes come from backend.cpp.
    source=source.replace("repo/'.pio/libdeps/glyph_mk6/PacketIO/src'","dependencies/'PacketIO/src'")
    replace("cpp=[here/'harness.cpp',","cpp=[repo/'tools/fixtures/config_bin_readonly_diagnostic/backend.cpp',repo/'HAL/pico/src/core/ConfigBinReadOnlyDiagnostic.cpp',")
    replace("'-DGLYPH_PACKAGE_V1=1',","'-DGLYPH_PACKAGE_V1=1','-DGLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC=1',")
    scope={'__file__':str(builder),'__name__':'config_bin_diagnostic_backend_builder'};exec(compile(source,str(builder),'exec'),scope)
    with tempfile.TemporaryDirectory(prefix='config-bin-backend-') as directory:
        out=Path(directory)
        binary=scope['build'](ROOT,out/'build',args.framework,args.libdeps/'Nanopb',True)
        p=subprocess.run([str(binary),str(out)],capture_output=True,text=True)
        if p.returncode:raise RuntimeError(p.stdout+p.stderr)
        print(p.stdout,end='')
        expected=bytes((i*31+7)&255 for i in range(70008))
        statuses={'recovery-once':[0,2],'not-recovery':[1],'no-storage':[3,2],'malformed-then-valid':[0]}
        for name,wanted in statuses.items():
            frames=cobs((out/(name+'.cobs')).read_bytes());identity=frames[-1]
            assert len(identity)==73 and identity[0]==10 and identity[17]==(2 if name=='not-recovery' else 3) and identity[18]==8
            assert identity[25:]==bytes(48)
            finals=[p[1:] for p in frames if p[0]==126 and p[6]==3]
            assert [struct.unpack_from('<H',p,6)[0] for p in finals]==wanted
            if wanted[0]==0:
                chunks=[p[25:] for p in frames if p[0]==126 and p[6]==2]
                assert b''.join(chunks)==expected
                assert finals[0][52:84]==hashlib.sha256(expected).digest()
        print('config_bin_readonly_backend_protocol_and_source_guards=PASS (synthetic only)')

if __name__=='__main__':main()
