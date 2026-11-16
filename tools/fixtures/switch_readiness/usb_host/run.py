"""Replay host enumeration with the production backend and the Mk6's pinned TinyUSB stack."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", type=Path, default=Path.home() / ".platformio/packages/framework-arduinopico")
    args = parser.parse_args()
    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    fixture = Path(__file__).resolve().parent
    usb = args.framework / "libraries/Adafruit_TinyUSB_Arduino/src"
    includes = [fixture, usb, usb / "arduino", root / "lib/TUCompositeHID/include",
                root / "tools/fixtures/profile_store_cdc_rx_progress/include",
                root / "tools/fixtures/switch_readiness/include",
                root / "tools/fixtures/stage_c_ultimate_profiles_host/include",
                root / "tools/fixtures/gp_config012_button_host/generated",
                root / "tools/fixtures/gp_config012_button_host/nanopb",
                root / "include", root / "HAL/pico/include"]
    sources = [usb / path for path in (
        "tusb.c", "device/usbd.c", "device/usbd_control.c", "class/hid/hid_device.c",
        "class/cdc/cdc_device.c", "common/tusb_fifo.c", "arduino/Adafruit_USBD_Device.cpp",
        "arduino/Adafruit_USBD_CDC.cpp", "arduino/hid/Adafruit_USBD_HID.cpp")]
    # Byte-identify the external translation units (including the source before host adaptation).
    digest = hashlib.sha256(b"".join(source.read_bytes() for source in sources)).hexdigest()
    if digest != "f7988ce4729455a2793b9ddd39c1118f54c1fba3292a8e98c35217dab5b2af01":
        raise ValueError("Expected the Arduino-Pico 3.6.3 Adafruit TinyUSB source set")
    sources += [root / path for path in (
        "lib/TUCompositeHID/src/TUCompositeHID.cpp", "HAL/pico/src/comms/NintendoSwitchBackend.cpp",
        "src/core/CommunicationBackend.cpp", "src/core/InputSource.cpp")]
    sources.append(fixture / "enumeration.cpp")
    with tempfile.TemporaryDirectory() as temp:
        objects = []
        for source in sources:
            if source.name == "Adafruit_USBD_Device.cpp":
                # The pinned board stores its numeric language ID in a pointer slot.
                # Widen only those casts for a 64-bit host compiler.
                device = source.read_text()
                for token in ("((uint32_t)language_id)", "((uint32_t)USB_LANGUAGE)",
                              "((uint32_t)_desc_str_arr[STRID_LANGUAGE])"):
                    assert device.count(token) == 1
                    device = device.replace(token, token.replace("uint32_t", "uintptr_t"))
                source = Path(temp) / source.name
                source.write_text(device)
            cxx = source.suffix == ".cpp"
            compiler = os.environ.get("CXX", "c++") if cxx else os.environ.get("CC", "cc")
            obj = Path(temp) / (source.name + ".o")
            subprocess.run([compiler, "-std=gnu++17" if cxx else "-std=gnu11", "-fshort-enums",
                            '-DCFG_TUSB_CONFIG_FILE="host_config.h"', "-DUSBDevice=TinyUSBDevice",
                            "-DUSB_VID=0x2e8a", "-DUSB_PID=0x000a",
                            *["-I" + str(folder) for folder in includes], "-c", source, "-o", obj], check=True)
            objects.append(obj)
        binary = Path(temp) / "enumeration"
        subprocess.run([os.environ.get("CXX", "c++"), *objects, "-o", binary], check=True)
        for host in ["early-configured", "early-descriptor-only", "late"]:
            subprocess.run([binary, host], check=True, timeout=5)


if __name__ == "__main__":
    main()
