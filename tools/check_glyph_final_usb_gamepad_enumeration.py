#!/usr/bin/env python3
"""Exercise production backend selection/finalization against the pinned USB stack.

Physical electrical disconnect detection/Windows driver binding are not modeled.
The host cooperates with pull-up changes and issues real TinyUSB control requests.
"""
from pathlib import Path
import argparse
import hashlib
import os
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tools/fixtures/final_usb_gamepad'


def function(text, name, result):
    start = text.index(result + ' ' + name + '(')
    at = text.index('{', start) + 1
    depth = 1
    while depth:
        depth += (text[at] == '{') - (text[at] == '}')
        at += 1
    return text[start:at]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--framework', type=Path, default=Path.home()/'.platformio/packages/framework-arduinopico')
    parser.add_argument('--xinput', type=Path, default=ROOT/'.pio/libdeps/glyph_mk6/Adafruit_TinyUSB_XInput')
    args = parser.parse_args()
    usb = args.framework/'libraries/Adafruit_TinyUSB_Arduino/src'
    core=(args.framework/'cores/rp2040/main.cpp').read_text()
    api=(usb/'arduino/Adafruit_TinyUSB_API.cpp').read_text()
    assert core.index('TinyUSB_Device_Init(0);') < core.index('        setup();')
    assert 'TinyUSBDevice.begin(rhport);' in function(api,'TinyUSB_Device_Init','void')
    xinput = args.xinput
    external = [usb/path for path in ('tusb.c','device/usbd.c','device/usbd_control.c',
        'class/hid/hid_device.c','class/cdc/cdc_device.c','common/tusb_fifo.c',
        'arduino/Adafruit_USBD_Device.cpp','arduino/Adafruit_USBD_CDC.cpp','arduino/hid/Adafruit_USBD_HID.cpp')]
    assert hashlib.sha256(b''.join(p.read_bytes() for p in external)).hexdigest() == 'f7988ce4729455a2793b9ddd39c1118f54c1fba3292a8e98c35217dab5b2af01'
    xsource=xinput/'src/Adafruit_USBD_XInput.cpp'
    # Pin checked XInput translation unit independently of Git-cache availability.
    xhash=hashlib.sha256(xsource.read_bytes()).hexdigest()
    assert hashlib.sha256((xinput/'include/Adafruit_USBD_XInput.hpp').read_bytes()).hexdigest() == '0e60e1e91e52bcbde1519aa49a57a5b3dc7f4cd9dfb95e1e3992eb370af1fd3c'
    assert xhash == 'ea35e3cbec69d1a60ab980a5bbce1350be16ae9faf83bc15e59112e68067491f'
    config=(ROOT/'config/glyph/common/src/config.cpp').read_text()
    setup=function(config,'setup','void')
    assert setup.index('InitializeBootBackends()') > setup.index('MigrateBootLegacyConfiguration()')
    for required in ('persistence.ValidateConfig(', 'persistence.LoadConfigChecked(',
                     'profile_store.Begin(', 'profile_store.ValidateCompactReceipt(',
                     'package_ownership::SupportedLayout('):
        assert setup.index(required) < setup.index('InitializeBootBackends()')
    boot=function(config,'InitializeBootBackends','bool')
    backend=(ROOT/'HAL/pico/src/comms/backend_init.cpp').read_text()
    # Keep every production selection/constructor dispatch body; remove includes only.
    assert 'tud_disconnect' not in backend and 'tud_connect' not in backend
    backend='\n'.join(line for line in backend.splitlines() if not line.startswith('#include'))
    includes=[FIXTURE/'include', usb, usb/'arduino', xinput/'include', ROOT/'lib/TUCompositeHID/include',
        ROOT/'tools/fixtures/profile_store_cdc_rx_progress/include',
        ROOT/'tools/fixtures/switch_readiness/include',
        ROOT/'tools/fixtures/stage_c_ultimate_profiles_host/include',
        ROOT/'tools/fixtures/gp_config012_button_host/generated',
        ROOT/'tools/fixtures/gp_config012_button_host/nanopb',
        ROOT/'include',ROOT/'HAL/pico/include',ROOT/'config/glyph/common/include',
        ROOT/'tools/fixtures/switch_readiness/usb_host']
    sources=external+[xsource]+[ROOT/p for p in (
        'lib/TUCompositeHID/src/TUCompositeHID.cpp','lib/TUCompositeHID/src/TUGamepad.cpp',
        'lib/TUCompositeHID/src/TUKeyboard.cpp','HAL/pico/src/comms/NintendoSwitchBackend.cpp',
        'HAL/pico/src/comms/XInputBackend.cpp','HAL/pico/src/comms/DInputBackend.cpp',
        'src/core/CommunicationBackend.cpp','src/core/InputSource.cpp','src/core/config_usb_default_validation.cpp')]
    with tempfile.TemporaryDirectory(prefix='glyph-final-usb-') as temp:
        tmp=Path(temp)
        (tmp/'comms').mkdir()
        # Clang rejects GCC's parameter-name lookup in this existing default.
        h=(ROOT/'HAL/pico/include/comms/backend_init.hpp').read_text()
        assert h.count('detect_console_t detect_console = &detect_console')==1
        (tmp/'comms/backend_init.hpp').write_text(h.replace('detect_console_t detect_console = &detect_console',
            'detect_console_t detect_console = &::detect_console'))
        (tmp/'backend_selection.inc').write_text(backend)
        (tmp/'boot_finalization.inc').write_text(boot)
        objects=[]
        common=['-fshort-enums','-DGLYPH_MK6_FINAL_USB_GAMEPAD_REENUMERATION=1',
            '-DCFG_TUSB_CONFIG_FILE="host_config.h"','-DUSBDevice=TinyUSBDevice',
            '-DSerial=SerialTinyUSB','-DUSB_VID=0x2e8a','-DUSB_PID=0x000a',
            *['-I'+str(p) for p in [tmp,*includes]]]
        def compile_source(source, obj):
            cpp=source.suffix=='.cpp'
            subprocess.run([os.environ.get('CXX','c++') if cpp else os.environ.get('CC','cc'),
                '-std=gnu++17' if cpp else '-std=gnu11',*common,*(['-include',str(FIXTURE/'include/hardware/timer.h'),'-include','Adafruit_TinyUSB.h'] if cpp else []),'-c',str(source),'-o',str(obj)],check=True)
        for i,source in enumerate(sources):
            if source.name=='Adafruit_USBD_Device.cpp':
                text=source.read_text()
                for token in ('((uint32_t)language_id)','((uint32_t)USB_LANGUAGE)','((uint32_t)_desc_str_arr[STRID_LANGUAGE])'):
                    assert text.count(token)==1
                    text=text.replace(token,token.replace('uint32_t','uintptr_t'))
                source=tmp/source.name
                source.write_text(text)
            obj=tmp/f'{i}.o'
            compile_source(source,obj)
            objects.append(obj)
        def build_lifecycle():
            obj=tmp/'lifecycle.o'
            compile_source(FIXTURE/'lifecycle.cpp',obj)
            binary=tmp/'enumeration'
            subprocess.run([os.environ.get('CXX','c++'),*map(str,objects),str(obj),'-o',str(binary)],check=True)
            return binary
        binary=build_lifecycle()
        # Enum values are read from the actual nanopb declarations, not duplicated.
        header=(ROOT/'tools/fixtures/gp_config012_button_host/generated/config.pb.h').read_text()
        ids={name:int(value) for name,value in re.findall(r'COMMS_BACKEND_(\w+) = (\d+)',header)}
        cases=[(name,False,name,False) for name in ('XINPUT','DINPUT','NINTENDO_SWITCH','CONFIGURATOR','GAMECUBE','N64','NES','SNES')]
        cases += [(usb_name,True,retro,False) for usb_name in ('XINPUT','DINPUT','NINTENDO_SWITCH') for retro in ('GAMECUBE','N64','NES','SNES')]
        cases += [(name,True,name,False) for name in ('XINPUT','DINPUT','NINTENDO_SWITCH')]
        cases += [('XINPUT',True,'UNSPECIFIED',False),('XINPUT',False,'XINPUT',True)]
        for selected,provisional,detected,invalid in cases:
            subprocess.run([str(binary),str(ids[selected]),str(int(provisional)),str(ids[detected]),str(int(invalid))],check=True,timeout=5)
        # Regression control: retain precisely the old Switch-only decision.
        needle='requires_final_usb_gamepad_reenumeration(backends[0]->BackendId())'
        normalized=re.sub(r'\s+',' ',boot)
        assert needle in normalized
        mutant=re.sub(r'requires_final_usb_gamepad_reenumeration\(\s*backends\[0\]->BackendId\(\)\s*\)',
            '(backends[0]->BackendId() == COMMS_BACKEND_NINTENDO_SWITCH)',boot)
        assert mutant!=boot
        (tmp/'boot_finalization.inc').write_text(mutant)
        binary=build_lifecycle()
        for name in ('XINPUT','DINPUT'):
            result=subprocess.run([str(binary),str(ids[name]),'0',str(ids[name]),'0'],capture_output=True,timeout=5)
            assert result.returncode!=0, f'Switch-only mutant escaped {name}'
            assert b'disconnects==unsigned(usb_gamepad)' in result.stderr, result.stderr.decode(errors='replace')
            print(f'PASS Switch-only mutant rejected by {name}',flush=True)
        print(f'PASS {len(cases)} production selection/finalization cases; 2 independent mutant controls; pinned XInput {xhash}')

if __name__=='__main__':
    main()
