# USB source audit

Baseline `59870835e7cd8e7c52bd3742e4910a7083cd21f5`; stock Limit Labs Glyph
v1.0.7 `9a78c7eeec87527b68644573e4c29fbdfb543239`. Stock
[`glyph_overrides.hpp`](https://github.com/LimitLabs/FW-Glyph/blob/9a78c7eeec87527b68644573e4c29fbdfb543239/config/glyph/common/include/glyph_overrides.hpp)
communication_backend_configs contains exactly these eight protocols (617–659):

| Backend enum suffix (`COMMS_BACKEND_`) | Transport | Final gamepad reconnect |
| --- | --- | --- |
| XINPUT | USB vendor-specific XUSB, expected 0738:4726 | Yes |
| DINPUT | USB composite HID gamepad + keyboard | Yes |
| NINTENDO_SWITCH | USB 0f0d:0092 HORI/Pokkén simple HID | Yes |
| CONFIGURATOR | Early USB CDC reused, late 2e8a:1092 | No |
| GAMECUBE | Console Joybus | No |
| N64 | Console signalling / Joybus family | No |
| NES | Console data/clock/latch | No |
| SNES | Console data/clock/latch | No |

The USB-C socket is a physical connector, not protocol authority. Existing report
serializers and retro-console source remain unchanged. Switch retains its 86-byte
HID descriptor and eight-byte report, without Pro Controller, 0x30/subcommand,
HD-rumble or IMU behavior. Profile applicable_backends is a separate product concept.

## Exact publication boundary

Pinned dependencies: Arduino-Pico 3.6.3
`32e74d024e5e3ee5e7ec9593f5a4101641c61897`, bundled Adafruit TinyUSB 2.3.0
`e2918652339aa3986f66b32c0a592c1aa72aabc8`, XInput
`4b5617b19294e808ce1d950a69e6e5cc96f4ec06`.

1. Arduino-Pico [`main.cpp`](https://github.com/earlephilhower/arduino-pico/blob/32e74d024e5e3ee5e7ec9593f5a4101641c61897/cores/rp2040/main.cpp)
   calls TinyUSB_Device_Init(0) before application setup().
2. [`Adafruit_TinyUSB_API.cpp`](https://github.com/adafruit/Adafruit_TinyUSB_Arduino/blob/e2918652339aa3986f66b32c0a592c1aa72aabc8/src/arduino/Adafruit_TinyUSB_API.cpp)
   calls TinyUSBDevice.begin().
3. [`Adafruit_USBD_Device.cpp`](https://github.com/adafruit/Adafruit_TinyUSB_Arduino/blob/e2918652339aa3986f66b32c0a592c1aa72aabc8/src/arduino/Adafruit_USBD_Device.cpp)
   begin() clears config, establishes initial identity, registers CDC, then calls
   TinyUSB_Port_InitDevice(). Pico board defaults are 2e8a:000a / product Pico.
4. [`RP2040 port`](https://github.com/adafruit/Adafruit_TinyUSB_Arduino/blob/e2918652339aa3986f66b32c0a592c1aa72aabc8/src/arduino/ports/rp2040/Adafruit_TinyUSB_rp2040.cpp)
   invokes tud_init(), then DCD initialization connects the pull-up.
5. Glyph [setup](../../../config/glyph/common/src/config.cpp) validates defaults,
   stored Config, ProfileStore, receipts/migration/layout before InitializeBootBackends().
6. [initialize_backends](../../../HAL/pico/src/comms/backend_init.cpp) invokes
   PrepareBackendPhase(); when detection is needed, it constructs the provisional
   default USB backend **before** detect_console_at_boot(). This is not finalization.
7. Detection chooses final backend; init_primary_backend() constructs/retains it.
   Retro selection deletes/replaces the provisional primary. FinishBackendPhase()
   produces backends[], applies mode, and returns zero on failed detection.
8. InitializeBootBackends() rechecks USB-default validity, binds normal modes, then
   finalizes only positive initialized count and the executing backends[0]->BackendId().
   It disconnects, waits 10 ms, connects once, before normal startup publication.
   Refused storage never reaches this call; invalid USB-default returns to recovery;
   zero detection count cannot pass the reconnect guard. Recovery bypasses this path.

The pinned [USBD](https://github.com/adafruit/Adafruit_TinyUSB_Arduino/blob/e2918652339aa3986f66b32c0a592c1aa72aabc8/src/device/usbd.c)
SET_CONFIGURATION path does not reopen newly added endpoints when the configuration
number is unchanged. A host that retained the first device/configuration descriptor
has no obligation to fetch late descriptors. Reconnect offers a fresh enumeration;
the host must issue its reset and control requests. No generic USB reset API is added.

## Backend audits

[XInputBackend](../../../HAL/pico/src/comms/XInputBackend.cpp) calls Serial.end() (clears the existing configuration), then
_xinput.begin(), Serial.begin(), and setID(0738,4726). Pinned
[`Adafruit_USBD_XInput::begin()`](https://github.com/JonnyHaystack/Adafruit_TinyUSB_XInput/blob/4b5617b19294e808ce1d950a69e6e5cc96f4ec06/src/Adafruit_USBD_XInput.cpp)
adds the interface, sets version0210 and records the instance; it does not snapshot
VID/PID. setID() writes live _desc_device returned by tud_descriptor_device_cb().
Ordering is valid and retained. Missing final publication is a concrete source defect;
the owner's Pico-only identity is consistent with it. Exact physical cause remains
unproven pending candidate retest; no website-only diagnosis or universal Mac XInput
compatibility claim follows.

DInput init_primary_backend() registers TUGamepad then TUKeyboard before constructing
[DInputBackend](../../../HAL/pico/src/comms/DInputBackend.cpp). Each registration calls
[TUCompositeHID::addDescriptor](../../../lib/TUCompositeHID/src/TUCompositeHID.cpp),
which concatenates report bytes and calls setReportDescriptor(). The constructor
calls _gamepad.begin() → shared _usb_hid.begin() → TinyUSBDevice.addInterface().
Live configuration length/interface count therefore changes after early CDC attach.
This confirms the same late-enumeration defect class. Final reconnect covers it
without making DInput profile eligibility a requirement for host coverage.

[NintendoSwitchBackend](../../../HAL/pico/src/comms/NintendoSwitchBackend.cpp)
registers HID and sets manufacturer/product/serial and 0f0d:0092 before shared HID
begin(). Its existing physically accepted final reconnect is generalized unchanged.

[ConfiguratorBackend](../../../HAL/pico/src/comms/ConfiguratorBackend.cpp) reuses
CDC; it adds no USB interface. It does late-set 2e8a:1092, so early/final identities
are **not identical**. Source plus working owner CDC evidence does not establish a
need to re-enumerate for CDC service. Keep it excluded and preserve uncertainty
about host-displayed identity. Recovery uses the same CDC/constructor route.

## Interval evidence and limits

The pinned RP2040 DCD disconnect/connect toggles the pull-up without rebuilding
interfaces. Keep the prior Switch-qualified 10 ms as one bounded common candidate
interval. [Microchip disconnect detection](https://support.microchip.com/s/article/USB-Device-Disconnect-Detection)
describes full/low-speed detach after SE0 longer than 2.5 µs; this electrical fact is
not a guarantee for every host. [Microsoft enumeration](https://techcommunity.microsoft.com/blog/microsoftusbblog/how-does-usb-stack-enumerate-a-device/270685/)
places at least 100 ms stable-connect debounce after attachment; that is not a
larger device-side disconnect minimum. No Windows-specific larger minimum was
established. The pinned examples do not establish a particular hold time. Windows
XInput and applicable DInput physical success remain required observations. No
startup optimization or arbitrary interval increase is part of this repair.
