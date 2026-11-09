#!/usr/bin/env python3
"""Candidate-only USB lifecycle proof and bounded host seam."""
from pathlib import Path
import argparse
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--elf', type=Path)
    args = parser.parse_args()
    header = (ROOT / 'include/core/RecoveryUsbBringup.hpp').read_text()
    source = ROOT / 'HAL/pico/src/core/RecoveryUsbBringup.cpp'
    config = (ROOT / 'config/glyph/common/src/config.cpp').read_text()
    backend = (ROOT / 'HAL/pico/src/comms/ConfiguratorBackend.cpp').read_text()
    ini = (ROOT / 'platformio.ini').read_text()

    assert 'constexpr uint32_t kMountBudgetMs = 2000;' in header
    assert 'TinyUSBDevice.mounted()' in config
    assert 'void service() override { TinyUSB_Device_Task(); }' in config
    assert 'void wait(uint32_t milliseconds) override { delay(milliseconds); }' in config
    assert 'recovery_usb::WaitForMount(usb_lifecycle)' in config
    assert 'DiagnosticUsbState::Starting: display.println("USB starting")' in config
    assert 'DiagnosticUsbState::Ready: display.println("Configurator ready")' in config
    assert 'DiagnosticUsbState::Unavailable: display.println("USB unavailable")' in config
    assert 'SetRecoveryUsbReady(usb_ready)' in config
    assert 'if (_recovery_service && !_recovery_usb_ready) return;' in backend
    assert '#if !GLYPH_CONFIG_BIN_READONLY_DIAGNOSTIC\n    TinyUSBDevice.setID(0x2E8A, 0x1092);' in backend
    assert 'board_build.arduino.earlephilhower.usb_vid = 0x2E8A' in ini
    assert 'board_build.arduino.earlephilhower.usb_pid = 0x1092' in ini
    assert '-D USB_VID=' not in ini and '-D USB_PID=' not in ini
    recovery = config[config.index('void enter_recovery_configurator()'):config.index('\n}\n\n}  // namespace', config.index('void enter_recovery_configurator()'))]
    assert recovery.index('recovery_configurator = new ConfiguratorBackend') < recovery.index('recovery_usb::WaitForMount')
    assert recovery.index('recovery_usb::WaitForMount') < recovery.index('boot_diagnostics::Recovery(watchdog_hw->scratch[3],usb_ready)')

    harness = ROOT / 'tools/fixtures/recovery_usb_bringup/harness.cpp'
    with tempfile.TemporaryDirectory(prefix='recovery-usb-bringup-') as temporary:
        binary = Path(temporary) / 'harness'
        subprocess.run([
            'g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
            '-I', str(ROOT / 'include'), str(source), str(harness), '-o', str(binary)
        ], check=True)
        subprocess.run([str(binary)], check=True)

    if args.elf:
        image = args.elf.read_bytes()
        descriptor = bytes.fromhex('12010002000000408a2e9210000101020301')
        old_descriptor = bytes.fromhex('12010002000000408a2e0a00000101020301')
        assert image.count(descriptor) == 1, 'expected recovery USB descriptor missing or ambiguous'
        assert old_descriptor not in image, 'default Pico 0x000a descriptor remains linked'

    print('recovery_usb_bringup_source_and_lifecycle=PASS')

if __name__ == '__main__':
    main()
