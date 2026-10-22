#!/usr/bin/env python3
"""Compile literal old/new Joybus and backend bodies against finite peripherals.

Only #include directives are elided in the generated translation unit. The
production headers, PIO C-SDK init helpers, joybus.c, GamecubeConsole.cpp and
GamecubeBackend.cpp bodies execute unchanged. This does not simulate electrical
hardware, prove linked resource budgets, or replace physical acceptance.
"""
import re
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "4898951994bcabcaef2846145de2922a674656f8"
FIX = ROOT / "tools/fixtures/gamecube_selector_liveness"
FAILED_DEP = FIX / 'failed_dependency'


def run(args):
    p = subprocess.run([str(x) for x in args], cwd=ROOT, text=True,
                       capture_output=True, timeout=60)
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    return p.stdout


def strip_includes(s):
    return re.sub(r"^\s*#include[^\n]*", "", s, flags=re.M)


def old_source(path):
    return run(["git", "show", f"{OLD}:{path}"])


def pio_parts(s):
    asm, sdk = s.split("% c-sdk {", 1)
    labels = {}
    ins = []
    constants = {}
    for line in asm.splitlines():
        line = line.split(";", 1)[0].strip()
        if not line:
            continue
        if line.startswith(".define public "):
            _, _, name, value = line.split()
            constants[name] = int(value)
        elif line.startswith("."):
            continue
        elif line.endswith(":"):
            labels[line.removeprefix("public ")[:-1]] = len(ins)
        else:
            ins.append(line)
    return labels, constants, ins, sdk.rsplit("%}", 1)[0]


def pio_proof(old, new):
    ol, oc, oi, _ = pio_parts(old)
    nl, nc, ni, _ = pio_parts(new)
    assert oc == nc and len(ni) == len(oi) + 1 == 24
    # The sole new instruction is before IN. All remaining receiver and sender
    # instructions, including relative label jumps, are literally preserved.
    assert oi[:ol['read_loop']] == ni[:nl['read_loop']]
    assert oi[ol['read_loop'] + 1:] == ni[nl['read_loop'] + 2:]
    assert oi[ol['read_loop']].startswith('wait 0 pin 0 [')
    assert ni[nl['read_loop']] == 'wait 0 pin 0'
    assert ni[nl['read_loop']+1].startswith('irq set 4 rel [')
    def cycles(instruction):
        delay = re.search(r'\[(.*)\]', instruction)
        return 1 + (int(eval(delay[1], {'__builtins__': {}}, nc)) if delay else 0)
    assert cycles(oi[ol['read_loop']]) == sum(map(cycles,ni[nl['read_loop']:nl['read_loop']+2])) == 20
    assert nl['write'] == ol['write'] + 1
    def words(path):
        header=path.read_text().split('joybus_program_instructions[] = {',1)[1].split('};',1)[0]
        return [int(x,16) for x in re.findall(r'^\s*(0x[0-9a-fA-F]+)',header,re.M)]
    ow=words(FAILED_DEP/'include/joybus.pio.h')
    nw=words(ROOT/'lib/glyph-joybus-pio/include/joybus.pio.h')
    assert len(ow)==23 and len(nw)==24
    assert (ow[1]&~0x1f00)==nw[1]  # remove old WAIT delay bits
    assert nw[2] == 0xd214  # irq set 4 rel [18]
    for index,word in enumerate(ow):
        if index==1:
            continue
        if word>>13==0:  # assembler JMP absolute target relocates around insertion
            target=word&31
            if target>=2:
                word=(word&~31)|(target+1)
        assert nw[index+(index>=2)]==word
    print('PIO: identical bit-sample cycles and remaining wire instructions; relocated write label PASS')


def aggregate(old=False, bridge=False):
    vendor = 'lib/glyph-joybus-pio/'
    def source(rel):
        if old:
            # Dependency bytes are exact pinned failed-candidate checkout inputs,
            # not reconstructed implementation bodies.
            return (FAILED_DEP / rel).read_text()
        return (ROOT / vendor / rel).read_text()
    pio = source('src/joybus.pio')
    labels, constants, _, sdk = pio_parts(pio)
    # Old PIO did not export read_loop, but its local label has the same address.
    defs = '\n'.join(f'constexpr uint {k}={v};' for k,v in
                     [(f'joybus_offset_{k}',v) for k,v in labels.items()] +
                     [(f'joybus_{k}',v) for k,v in constants.items()])
    defs = 'using uint=unsigned;\n' + defs
    mailbox = (ROOT/'src/core/profile_selection.cpp').read_text()
    mailbox = mailbox[mailbox.index('namespace profile_selection {'):mailbox.index('\nbool IsUsb(')] + '\n}\n'
    config=(ROOT/'config/glyph/common/src/config.cpp').read_text()
    gate_start=config.index('\n',config.index('    if (backends == nullptr || backend_count == 0 || backends[0] == nullptr) return;'))+1
    gate_end=config.index('    select_mode(backends, backend_count, config);',gate_start)
    gate='void application_service_gate(CommunicationBackend **backends, void (*service_profile_selection)()) {\n'+config[gate_start:gate_end]+'}\n'
    if not old:
        assert 'profile_selection::Pending' not in gate, 'empty-mailbox race may bypass receiver admission'
    parts = [defs,(FIX/'hardware.cpp').read_text(),source('include/gamecube_definitions.h'),
             source('include/joybus.h'), sdk, source('include/GamecubeConsole.hpp'),
             mailbox,old_source('HAL/pico/include/comms/GamecubeBackend.hpp') if old else
             (ROOT/'HAL/pico/include/comms/GamecubeBackend.hpp').read_text(),
             source('src/joybus.c'),source('src/GamecubeConsole.cpp'),
             old_source('HAL/pico/src/comms/GamecubeBackend.cpp') if old else
             (ROOT/'HAL/pico/src/comms/GamecubeBackend.cpp').read_text(),
             '' if old else gate,(FIX/'scenarios.cpp').read_text()]
    if bridge:
        # Separate namespace avoids coupling the peripheral doubles to Config,
        # Persistence, enums and private globals in the existing service fixture.
        includes='\n'.join(x for x in parts[1].splitlines() if x.startswith('#include'))
        parts[6]='namespace profile_selection = ::profile_selection;'
        unit='\n'.join(strip_includes(x) for x in parts[:-1])
        return includes + '''
namespace profile_selection { bool Request(uint32_t); uint32_t Pending(); void Complete(); }
namespace gc_liveness {
''' + unit + '''
}
extern "C" void run_gc_idle_then(void (*service)()) {
 using namespace gc_liveness;
 now_us=0;limit_us=2000;tx_end=0;hw={};bank={};pin_high=true;irq_disabled=false;
 updates=pauses=resumes=resets=starts=0;rx.clear();tx.clear();events.clear();on_disable={};
 fast_scans=0;on_fast_scan={};
 if(::profile_selection::Pending())throw std::runtime_error("expected prior application service opportunity");
 InputState inputs;GamecubeBackend backend(inputs,nullptr,0,0);
 CommunicationBackend *backends[]={&backend};
 application_service_gate(backends,service); // actual initial service point
 if(!::profile_selection::Request(1001))throw std::runtime_error("pre-wait request refused");
 hw.marker=true;
 application_service_gate(backends,service);
 if(::profile_selection::Pending()!=1001)throw std::runtime_error("actual service bypassed partial-first-byte gate");
 hw.marker=false;hw.pc=joybus_offset_write;tx_end=100;
 application_service_gate(backends,service);
 if(::profile_selection::Pending()!=1001)throw std::runtime_error("actual service bypassed pending-TX gate");
 ::profile_selection::Complete();hw.pc=joybus_offset_read_loop;tx_end=0;
 event(10,[]{if(!::profile_selection::Request(1001))throw std::runtime_error("request during idle wait refused");});
 backend.SendReport();
 if(now_us>60 || hw.enabled || updates || !tx.empty() || ::profile_selection::Pending()!=1001)
  throw std::runtime_error("source backend did not yield safely for selector service");
 application_service_gate(backends,service);
 std::cout<<"GC no-poll request -> bounded return -> actual selector service PASS\\n";
}
'''
    return '\n'.join(strip_includes(x) if i>1 else x for i,x in enumerate(parts))


def main():
    manifest=json.loads((FAILED_DEP/'manifest.json').read_text())
    assert manifest['upstream_commit']=='f2f59c0aee07aea58cdd03616439bc3c6a8cbd8a'
    for rel,digest in manifest['files'].items():
        assert hashlib.sha256((FAILED_DEP/rel).read_bytes()).hexdigest()==digest
    old_pio=(FAILED_DEP/'src/joybus.pio').read_text()
    pio_proof(old_pio,(ROOT/'lib/glyph-joybus-pio/src/joybus.pio').read_text())
    with tempfile.TemporaryDirectory(prefix='glyph-gc-liveness-') as d:
        d=Path(d)
        for old in (True,False):
            for abi in ('-fshort-enums','-fno-short-enums'):
                src=d/'test.cpp';src.write_text(aggregate(old));exe=d/'test'
                run(['c++','-std=c++17','-O1','-g',abi,'-fsanitize=address,undefined',
                     '-fno-omit-frame-pointer',*(['-DOLD_SOURCE'] if old else []),src,'-o',exe])
                print(('old' if old else 'new'),abi,run([exe]),end='')
    print('Scope: source/peripheral proof plus integrated actual Persistence; exact build/resource/hardware acceptance remains separate.')
    print(run(['python3',ROOT/'tools/check_glyph_controller_profile_selector.py','--gamecube-liveness']),end='')


if __name__=='__main__':
    main()
