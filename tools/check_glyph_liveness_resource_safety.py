#!/usr/bin/env python3
"""Offline ELF/diagnostic safety gate. Never opens a device or rebuilds firmware."""
import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BANKS = ((0x20041000, 0x20042000), (0x20040000, 0x20041000))


def sections_and_symbols(blob):
    assert blob[:6] == b'\x7fELF\x01\x01', 'Expected little-endian ELF32'
    header = struct.unpack_from('<16sHHIIIIIHHHHHH', blob)
    offset, size, count, names_index = header[6], header[11], header[12], header[13]
    headers = [struct.unpack_from('<10I', blob, offset + i * size) for i in range(count)]
    names = headers[names_index]
    strings = blob[names[4]:names[4] + names[5]]
    string = lambda data, start: data[start:data.index(b'\0', start)].decode()
    sections = [dict(name=string(strings, h[0]), type=h[1], flags=h[2], addr=h[3],
                     offset=h[4], size=h[5], link=h[6], entsize=h[9]) for h in headers]
    symbols = {}
    for section in sections:
        if section['type'] != 2:
            continue
        names = sections[section['link']]
        strings = blob[names['offset']:names['offset'] + names['size']]
        for offset in range(section['offset'], section['offset'] + section['size'], section['entsize']):
            name, value, length, info, other, index = struct.unpack_from('<IIIBBH', blob, offset)
            symbols[string(strings, name)] = dict(value=value, size=length, index=index)
    return sections, symbols


def safe_sections(sections):
    for section in sections:
        if not section['size'] or section['name'] in ('.stack_dummy', '.stack1_dummy'):
            continue
        for lower, upper in BANKS:
            assert not (section['addr'] < upper and section['addr'] + section['size'] > lower), section


def check_calls(disassembly):
    allowed = {'InitializeResourceDiagnosticsCore()': set(), 'SampleResourceDiagnostics()': set(),
               'ReadResourceDiagnostics()': {'__wrap_memset', 'memset'}, '__wrap__sbrk': {'_sbrk'},
               '_sbrk': set()}
    result = {}
    for name, permitted in allowed.items():
        match = re.search(r'^([0-9a-f]+) <' + re.escape(name) + r'>:\n(.*?)(?=\n\n)', disassembly, re.M | re.S)
        assert match, name
        body = match[2]
        calls = re.findall(r'\bbl\s+[0-9a-f]+ <([^>]+)>', body)
        assert not re.search(r'\bblx\b', body), (name, 'indirect call')
        assert set(calls) <= permitted, (name, calls)
        if name == '__wrap__sbrk':
            assert calls == ['_sbrk', '_sbrk'], calls
        result[name] = calls
    return result


def check_elf(path, objdump):
    blob = path.read_bytes()
    sections, symbols = sections_and_symbols(blob)
    safe_sections(sections)
    expected = {'__StackTop': 0x20042000, '__StackOneTop': 0x20041000, '__StackLimit': 0x20040000}
    for name, value in expected.items():
        assert symbols[name]['value'] == value, (name, symbols[name])
    separate = symbols['core1_separate_stack']
    section = sections[separate['index']]
    assert section['type'] == 8 or blob[section['offset'] + separate['value'] - section['addr']] == 0
    assert not any(name.startswith('__atomic_') for name in symbols), 'Unexpected atomic library helper'
    disassembly = subprocess.check_output([str(objdump), '-d', '-C', str(path)], text=True)
    calls = check_calls(disassembly)
    negative_count = 0
    for lower, _ in BANKS:
        try:
            safe_sections(sections + [dict(name='.scratch.regression', addr=lower, size=4)])
        except AssertionError:
            negative_count += 1
    try:
        check_calls(disassembly.replace('<_sbrk>\n', '<__wrap__sbrk>\n', 1))
    except AssertionError:
        negative_count += 1
    assert negative_count == 3
    return dict(elf_sha256=hashlib.sha256(blob).hexdigest(), stack_banks=BANKS,
                heap_capacity=0x20040000-symbols['end']['value'], direct_calls=calls,
                adversarial_negative_controls=negative_count)


def watermark_stress():
    source = r'''#include "core/StackWatermark.hpp"
#include "core/ResourceDiagnostics.hpp"
#include <cassert>
int main() {
  uint32_t words[1026]{};
  for (unsigned pass=0; pass<10000; ++pass) {
    words[0]=0x11223344; words[1025]=0x55667788;
    glyph_resource::fill_stack_watermark(words+1, words+1025);
    assert(glyph_resource::scan_stack_watermark(words+1, words+1025)==4096);
    unsigned first=pass%1024;
    words[first+1]=0;
    for(unsigned repeat=0;repeat<4;++repeat)
      assert(glyph_resource::scan_stack_watermark(words+1, words+1025)==first*4);
    assert(words[0]==0x11223344 && words[1025]==0x55667788);
  }
  assert(!ReadResourceDiagnostics().resource_diagnostics_enabled);
}'''
    with tempfile.TemporaryDirectory(prefix='glyph-liveness-resource-') as directory:
        path = Path(directory)
        (path/'stress.cpp').write_text(source)
        subprocess.run(['c++','-std=c++17','-O2','-fsanitize=address,undefined','-I',str(ROOT/'include'),
                        str(path/'stress.cpp'),'-o',str(path/'stress')], check=True)
        subprocess.run([str(path/'stress')], check=True, timeout=60)
    return dict(fill_cycles=10000, scans=50000, maximum_words_per_scan=1024, sanitizer='ASan+UBSan', disabled_control=True)


def retained_samples(directory, output):
    keys = ['core0_stack_min_free_bytes','core1_stack_min_free_bytes','heap_arena_current_bytes',
            'heap_arena_peak_bytes','heap_arena_capacity_bytes','store_generation','count']
    rows=[]
    def visit(value, file, object_path=''):
        if isinstance(value, dict):
            if value.get('resource_diagnostics_enabled'):
                row = dict(mtime_utc=datetime.datetime.fromtimestamp(file.stat().st_mtime,datetime.timezone.utc).isoformat(),
                           phase=file.stem,file=str(file.relative_to(directory)),object=object_path)
                row.update({key:value.get(key,'NOT_REPORTED') for key in keys})
                row['source_sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
                rows.append(row)
            for key, child in value.items(): visit(child,file,object_path+'/'+key)
        elif isinstance(value,list):
            for i, child in enumerate(value): visit(child,file,object_path+'/'+str(i))
    for file in directory.rglob('*.json'):
        try: value=json.loads(file.read_text())
        except (ValueError,UnicodeError): continue
        visit(value,file)
    rows.sort(key=lambda row:(row['mtime_utc'],row['file'],row['object']))
    assert rows, 'No diagnostic samples found'
    with (output/'all-retained-resource-samples.csv').open('w') as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return dict(sample_count=len(rows),first=rows[0],last=rows[-1],
                observed_values={key:sorted({int(row[key]) for row in rows if row[key]!='NOT_REPORTED'}) for key in keys},
                chronology='Retained file modification time, not a firmware timestamp. count is NOT_REPORTED unless present.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--objdump',type=Path,default=Path.home()/'.platformio/packages/toolchain-rp2040-earlephilhower/bin/arm-none-eabi-objdump')
    parser.add_argument('--hardware-evidence',type=Path)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    result=dict(elf=check_elf(args.elf,args.objdump),watermark=watermark_stress())
    if args.hardware_evidence: result['retained_samples']=retained_samples(args.hardware_evidence,args.output_dir)
    result['status']='PASS';result['physical_root_cause']='UNPROVEN'
    (args.output_dir/'resource-safety.json').write_text(json.dumps(result,indent=2)+'\n')
    print('glyph_liveness_resource_safety=PASS ELF gates, 3 negative controls, 10000 fill cycles/50000 bounded scans; physical cause UNPROVEN')

if __name__=='__main__':main()
