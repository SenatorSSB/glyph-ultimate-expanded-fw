"""Fail-closed source authority for the two-stage cold recovery candidate.

No vendor source is copied or rewritten. The descriptor-only preparation uses
original Adafruit begin() plus the existing external port wrapper. This module
pins that external-call boundary and the ordinary core startup source.
"""
from hashlib import sha256
import json
from pathlib import Path

COLD_DEFINE = "GLYPH_RT2_COLD_RECOVERY_CANDIDATE"
WRAP_SYMBOLS = ("TinyUSB_Device_Task", "TinyUSB_Device_FlushCDC")
WRAP_FLAGS = tuple("-Wl,--wrap=" + name for name in WRAP_SYMBOLS)
PINS = {'main': {'installed': 'cores/rp2040/main.cpp',
          'sha256': 'c715e100f362b7520ed11348b9e446d9f451432a2fabce07766b14dd9f5f0fe3',
          'bytes': 5490},
 'support': {'installed': 'cores/rp2040/RP2040Support.h',
             'sha256': 'f9aebd5a7e47ca82a6ff2f38f5bde74f048f8cac668e02df84752c29ccb01412',
             'bytes': 8789},
 'api': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/arduino/Adafruit_TinyUSB_API.cpp',
         'sha256': 'd3ccfba32fe1eac05d86a471720368b0a5ebbda85ac8a36c55b9d34486a326d0',
         'bytes': 2878},
 'api_header': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/arduino/Adafruit_TinyUSB_API.h',
                'sha256': '848eca20e4232e82f914ca7733ced987f989dbdf5e3519fbb9e07364c47cff32',
                'bytes': 2882},
 'device': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/arduino/Adafruit_USBD_Device.cpp',
            'sha256': 'eec9057db61afaf73768df4a4fad020d1f28ca7d62cfbbfafa6b118776494597',
            'bytes': 17806},
 'cdc': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/arduino/Adafruit_USBD_CDC.cpp',
         'sha256': '497dfa3ee62693f9187ea6e909bb92830b4e792d19773fdf3f55c0ecc3304ec8',
         'bytes': 7486},
 'port': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/src/arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp',
          'sha256': 'ac9a2397254aafc498ad1d1eb59d0a8291c6943f9261369b8c49b09c19691c3a',
          'bytes': 4652},
 'delay': {'installed': 'cores/rp2040/delay.cpp',
           'sha256': '1f12e590c041dea9231dd45b0f5c42b90ccb3000373f50570d2bdeccdf233454',
           'bytes': 1647},
 'watchdog': {'installed': 'pico-sdk/src/rp2_common/hardware_watchdog/watchdog.c',
              'sha256': '199db806a6844a638ae505383083ce7942f8a7bfd746f218a7499e49999fd014',
              'bytes': 3283},
 'watchdog_regs': {'installed': 'pico-sdk/src/rp2040/hardware_regs/include/hardware/regs/watchdog.h',
                   'sha256': 'd2020b6f62d175f3879151e7cafb39d8b5f40f83b67eec9bcad888c0b01b9900',
                   'bytes': 11068},
 'sdk_version': {'installed': 'include/pico_base/pico/version.h',
                 'sha256': '28f4397e73b20ee0e167958297da3e4433d77734a7d5a81c289e9e4c4eefda68',
                 'bytes': 439},
 'framework_version': {'installed': 'package.json',
                       'sha256': '0aa78013e54caef261f2fd38b12ac84ce16c8f1e5dcba5660be6846e888c8960',
                       'bytes': 401},
 'adafruit_version': {'installed': 'libraries/Adafruit_TinyUSB_Arduino/library.properties',
                      'sha256': '5d2bb442f356ca002791a435be291be741ef5f1923c9c20dcec9a7a4371c45fe',
                      'bytes': 385}}


def _text(data):
    return data.decode("utf-8").replace("\r\n", "\n")


def _once(text, anchor, label):
    if text.count(anchor) != 1:
        raise ValueError("cold recovery exact source anchor changed: " + label)


def validate_anchors(blobs):
    """Also callable by negative controls without weakening the full hash gate."""
    texts = {key: _text(value) for key, value in blobs.items()}
    main = texts["main"]
    _once(main, "    TinyUSB_Device_Init(0);", "core early init")
    if not (main.index("    rp2040.begin();") < main.index("    initVariant();") <
            main.index("    TinyUSB_Device_Init(0);") <
            main.index("                multicore_launch_core1(main1);") < main.index("        setup();")):
        raise ValueError("cold recovery original core startup order changed")
    _once(texts["api_header"], "void TinyUSB_Device_Init(uint8_t rhport) __attribute__((weak));", "weak C ABI declaration")
    _once(texts["api"], "void TinyUSB_Device_Init(uint8_t rhport) {\n  // Init USB Device controller and stack\n  TinyUSBDevice.begin(rhport);\n}", "original init body")
    _once(texts["device"], """bool Adafruit_USBD_Device::begin(uint8_t rhport) {
  clearConfiguration();

  // Serial is always added by default
  // Use Interface Association Descriptor (IAD) for CDC
  // As required by USB Specs IAD's subclass must be common class (2) and
  // protocol must be IAD (1)
  _desc_device.bDeviceClass = TUSB_CLASS_MISC;
  _desc_device.bDeviceSubClass = MISC_SUBCLASS_COMMON;
  _desc_device.bDeviceProtocol = MISC_PROTOCOL_IAD;

  SerialTinyUSB.begin(115200);

  // Init device hardware and call tusb_init()
  TinyUSB_Port_InitDevice(rhport);

  return true;
}""", "unchanged descriptor prefix and external port boundary")
    _once(texts["port"], "void TinyUSB_Port_InitDevice(uint8_t rhport) {\n  mutex_init(&__usb_mutex);\n\n  tud_init(rhport);", "one original port initialization")
    _once(texts["cdc"], "  _instance = _instance_count++;\n  this->setStringDescriptor(\"TinyUSB Serial\");\n  TinyUSBDevice.addInterface(*this);", "CDC descriptor preparation")
    _once(texts["delay"], "    void yield() {\n#ifdef USE_TINYUSB\n        TinyUSB_Device_Task();\n        TinyUSB_Device_FlushCDC();\n#endif\n    }", "pre-port yield task and flush")
    _once(texts["support"], "        watchdog_reboot(0, 0, 10);", "existing firmware reboot")
    _once(texts["watchdog"], "void watchdog_reboot(uint32_t pc, uint32_t sp, uint32_t delay_ms)", "SDK reboot authority")


def verify_installed(framework):
    framework = Path(framework).resolve()
    records, blobs = {}, {}
    for key, pin in PINS.items():
        path = framework / pin["installed"]
        data = path.read_bytes()
        digest = sha256(data).hexdigest()
        if digest != pin["sha256"] or len(data) != pin["bytes"]:
            raise ValueError("cold recovery exact installed source pin mismatch: " + key)
        records[key] = dict(pin, path=str(path))
        blobs[key] = data
    validate_anchors(blobs)
    return records


def _object_names(source):
    path = Path(source)
    return {path.name + ".o", path.stem + ".o"}


def validate_graph(paths, root, framework, linkflags):
    """Source-graph gate; final ELF binding/call proof remains a separate check."""
    root, framework = Path(root).resolve(), Path(framework).resolve()
    paths = {Path(path).resolve() for path in paths}
    if any("rt2-recovery-reinit" in str(path) or "rt2_recovery_reinit" in str(path) for path in paths):
        raise ValueError("cold recovery graph contains superseded warm-reset replacement")
    objects = {path for path in paths if path.suffix == ".o"}
    selected = {}
    for key in ("main", "api", "device", "cdc", "port", "delay"):
        found = {path for path in objects if path.name in _object_names(PINS[key]["installed"])}
        if len(found) != 1:
            raise ValueError("cold recovery graph requires one original object: " + key)
        installed = framework / PINS[key]["installed"]
        if installed not in paths:
            raise ValueError("cold recovery graph lacks original source: " + key)
        selected[key] = [str(path) for path in sorted(found)]
    for name in ("ColdRecoveryBoot.cpp", "ColdRecoveryUsbInit.c"):
        expected = root / "HAL/pico/src/core" / name
        found = {path for path in objects if path.name in _object_names(name)}
        if expected not in paths or len(found) != 1:
            raise ValueError("cold recovery graph requires one owned source/object: " + name)
        selected[name] = [str(path) for path in sorted(found)]
    dcd = {path for path in objects if path.name in _object_names("dcd_rp2040.c")}
    if len(dcd) != 1 or not all("rt2-private-dcd" in str(path) for path in dcd):
        raise ValueError("cold recovery graph requires existing S0/S1 DCD replacement only")
    flags = list(map(str, linkflags))
    for flag in WRAP_FLAGS:
        if flags.count(flag) != 1:
            raise ValueError("cold recovery requires one functional wrapper link flag: " + flag)
    selected["dcd"] = [str(path) for path in sorted(dcd)]
    return selected


def write_receipt(path, records, **details):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dict(status="SOURCE_PINS_PASS", framework_sources_unchanged=True,
                vendor_copies=0, source_pins=records, **details)
    path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
    return body
