#!/usr/bin/env python3
"""Source-backed selected LittleFS + exact wrapper path validation host probe."""
import hashlib, pathlib, re, subprocess
root=pathlib.Path(__file__).resolve().parents[1]; out=root.parent/'storage-recovery-v2'/'verification'
library=root/'.platformio-home/packages/framework-arduinopico/libraries/LittleFS'
header=(library/'src/LittleFS.h').read_text()
start=header.index('    static bool pathValid('); end=header.index('\n    // The actual flash',start)
literal=header[start:end]
(out/'actual_path_valid.hpp').write_text(literal)
def run(command):
    result=subprocess.run(command,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if result.returncode: raise RuntimeError(result.stdout)
    return result.stdout
flags=['-O1','-g','-DNDEBUG','-DLFS_NAME_MAX=32','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-I'+str(library/'lib/littlefs'),'-I'+str(out)]
objects=[]
for name in ['lfs','lfs_util']:
    source=library/'src'/(name+'.c'); obj=out/(name+'.o');objects.append(str(obj))
    run(['clang','-std=c99',*flags,'-c',str(source),'-o',str(obj)])
exe=out/'actual-littlefs-probe'
run(['clang++','-std=gnu++17',*flags,str(root/'friend/tests/littlefs_probe.cpp'),*objects,'-o',str(exe)])
helper=(root/'config/glyph/common/include/friend_profile_provisioning.hpp').read_text()
marker=re.search(r'kMarkerPath\[\] = "([^"]+)"',helper).group(1)
output=run([str(exe),'/friend_ultimate_20261011_applied.flag',marker,str(out/'baked-short.pb')])
output+='literal pathValid SHA-256='+hashlib.sha256(literal.encode()).hexdigest()+'\n'
for path in ['src/lfs.c','src/lfs_util.c','src/LittleFS.h','src/LittleFS.cpp','lib/littlefs/lfs.c','lib/littlefs/lfs.h']:
    output+=path+' SHA-256='+hashlib.sha256((library/path).read_bytes()).hexdigest()+'\n'
(out/'actual-littlefs.log').write_text(output);print(output)
