#!/usr/bin/env python3
"""Extract actual DWARF producer/compilation-unit provenance from an immutable ELF."""
from pathlib import Path
import sys,subprocess,json,hashlib
elf=Path(sys.argv[1]); out=Path(sys.argv[2])
assert elf.is_file() and not elf.is_symlink() and not out.exists()
reader=Path('/private/tmp/glyph-profile-native-20261020/.platformio-home/packages/toolchain-rp2040-earlephilhower/bin/arm-none-eabi-readelf')
units=[]; unit=None
p=subprocess.Popen([str(reader),'--debug-dump=info',str(elf)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
for line in p.stdout:
    if 'Compilation Unit @ offset' in line:
        if unit and 'producer' in unit: units.append(unit)
        unit={'header':line.strip()}
    elif unit is not None:
        for attr,key in [('DW_AT_producer','producer'),('DW_AT_name','name'),('DW_AT_comp_dir','comp_dir')]:
            if attr in line and key not in unit:
                unit[key]=line.split(attr,1)[1].lstrip(' :').rstrip()
if unit and 'producer' in unit: units.append(unit)
stderr=p.stderr.read(); assert p.wait()==0,stderr
counts={}
for u in units: counts[u['producer']]=counts.get(u['producer'],0)+1
result={'kind':'EXACT_ELF_DWARF_PRODUCER_EXTRACTION','elf':{'path':str(elf),'bytes':elf.stat().st_size,'sha256':hashlib.sha256(elf.read_bytes()).hexdigest()},'extractor_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'readelf_sha256':hashlib.sha256(reader.read_bytes()).hexdigest(),'command':[str(reader),'--debug-dump=info',str(elf)],'producer_counts':counts,'units':units,'qualification':'Actual emitted DWARF compiler producer/option records. These do not contain a complete command argv, all preprocessor macros, include search paths, link flags or source/dependency archive. Use alongside exact build/dependency/script provenance, not as a substitute.'}
out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'output':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'units':len(units),'producer_variants':len(counts),'stderr':stderr},indent=2))
