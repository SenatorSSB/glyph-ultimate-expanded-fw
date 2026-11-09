#!/usr/bin/env python3
"""Compile and inspect the candidate extraction against synthetic NOR only."""
from pathlib import Path
import argparse,hashlib,os,struct,subprocess,tempfile,zlib

ROOT=Path(__file__).resolve().parents[1]
def run(argv):
    p=subprocess.run(list(map(str,argv)),capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout

def packets(path):
    data=path.read_bytes();at=0;result=[]
    while at<len(data):
        n,=struct.unpack_from('<I',data,at);at+=4
        p=data[at:at+n];at+=n
        assert len(p)==n and p[:5]==b'GCB1\x01' and p[8:16]==bytes.fromhex('0807060504030201')
        result.append(p)
    assert at==len(data)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--framework',type=Path,default=Path.home()/'.platformio/packages/framework-arduinopico');args=ap.parse_args()
    fw=args.framework/'libraries/LittleFS';here=ROOT/'tools/fixtures/config_bin_readonly_diagnostic'
    with tempfile.TemporaryDirectory(prefix='config-bin-readonly-') as directory:
        out=Path(directory);inc=out/'include';inc.mkdir()
        (inc/'Arduino.h').write_text('#pragma once\nunsigned long millis();\n')
        includes=['-I'+str(p) for p in [inc,ROOT/'include',fw/'lib/littlefs']]
        flags=['-g','-O1','-fno-omit-frame-pointer','-fsanitize=address,undefined','-DGLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC=1','-DGLYPH_PACKAGE_V1=1','-DGLYPH_CHECKED_STORAGE_TEST_MOUNT=1','-DLFS_NAME_MAX=32']
        objects=[]
        for source in [fw/'src/lfs.c',fw/'src/lfs_util.c']:
            obj=out/(source.stem+'.o');run([os.environ.get('CC','cc'),'-std=c11',*flags,*includes,'-Dmalloc=DiagnosticTestMalloc','-Dlfs_file_read=DiagnosticRealRead','-Dlfs_file_size=DiagnosticRealSize','-Dlfs_file_close=DiagnosticRealClose','-c',source,'-o',obj]);objects.append(obj)
        binary=out/'diagnostic'
        run([os.environ.get('CXX','c++'),'-std=c++17',*flags,*includes,'-Dlfs_file_read=DiagnosticTestRead','-Dlfs_file_size=DiagnosticTestSize','-Dlfs_file_close=DiagnosticTestClose',here/'harness.cpp',ROOT/'HAL/pico/src/core/ConfigBinReadOnlyDiagnostic.cpp',*objects,'-o',binary])
        print(run([binary,out]),end='')
        fixtures={'empty':b'','short':b'bad','header':bytes(8),'body':bytes((i*31+7)&255 for i in range(70008))}
        for name,expected in fixtures.items():
            ps=packets(out/(name+'.wire'));assert ps[0][5]==1 and len(ps[0])==24 and struct.unpack_from('<II',ps[0],16)==(len(expected),128)
            assembled=bytearray()
            for p in ps[1:-1]:
                assert p[5]==2 and p[6:8]==b'\0\0' and p[22:24]==b'\0\0'
                offset,count=struct.unpack_from('<IH',p,16);assert offset==len(assembled) and count==len(p)-24 and 0<count<=128
                assembled+=p[24:]
            assert assembled==expected
            final=ps[-1];assert final[5]==3 and len(final)==116 and final[6:8]==b'\0\0'
            size,sent,declared,stored,actual,crc=struct.unpack_from('<6I',final,16)
            body=expected[8:];header=expected[:8];full_header=len(header)==8
            assert (size,sent,actual,crc)==(len(expected),len(expected),len(body),zlib.crc32(body))
            assert final[40]==len(header) and final[44:52]==header.ljust(8,b'\0') and final[42:44]==b'\0\0'
            assert final[52:84]==hashlib.sha256(expected).digest() and final[84:116]==hashlib.sha256(body).digest()
            assert (declared,stored)==(struct.unpack('<II',header) if full_header else (0,0))
            flags=24|int(full_header)
            if full_header and declared==len(body):flags|=2
            if full_header and stored==zlib.crc32(body):flags|=4
            assert final[41]==flags
        failures={'missing':4,'read-failure':7,'oversize':6,'size-drift':7,'close-failure':8,'deadline':9}
        for name,status in failures.items():
            final=packets(out/(name+'.wire'))[-1]
            assert final[5]==3 and len(final)==116 and struct.unpack_from('<H',final,6)[0]==status
            assert final[52:116]==bytes(64)
        assert not packets(out/'tx-start.wire')
        assert len(packets(out/'tx-chunk.wire'))==2
        print('config_bin_readonly_diagnostic_wire=PASS (synthetic only)')

if __name__=='__main__':main()
