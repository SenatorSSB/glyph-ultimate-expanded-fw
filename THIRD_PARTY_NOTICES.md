# Third-party notices

This community firmware fork builds on HayBox by JonnyHaystack and the Glyph work by Limit Labs and contributors. The retained Glyph metadata names `GregTurbo/Haybox-Glyph` revision `05a7d2b` ([metadata](config/glyph/meta.yaml)); that upstream locator was unavailable during this inventory. Original authorship and notices remain with their contributors.

The repository retains [GNU GPL version 3](LICENSE) and [Glyph GPLv3 text](config/glyph/LICENSE). Bundled components retain their own terms; this inventory does not replace those notices or claim a complete corresponding-source bundle for any firmware binary.

## Bundled source

- [Glyph Joybus PIO license](lib/glyph-joybus-pio/LICENSE) and [provenance/local changes](lib/glyph-joybus-pio/UPSTREAM.md): LGPLv3 text, vendored commit `f2f59c0aee07aea58cdd03616439bc3c6a8cbd8a`.
- TUCompositeHID TUGamepad: MIT notices remain in [header](lib/TUCompositeHID/include/TUGamepad.hpp) and [source](lib/TUCompositeHID/src/TUGamepad.cpp).
- Host fixtures retain Nanopb [license](tools/fixtures/gp_config012_button_host/LICENSE.nanopb.txt), [additional schema license](tools/fixtures/custom_modifier_cache_host/schema/LICENSE.nanopb.txt), and [generated-fixture license](tools/fixtures/mode_selection_host/generated/LICENSE.nanopb.txt).
- Recovery/selector fixtures retain [CRC32](tools/fixtures/gp_config021_persisted_recovery/dependencies/LICENSE.CRC32.md), [nanopb-arduino notice](tools/fixtures/gp_config021_persisted_recovery/dependencies/NOTICE.nanopb-arduino.txt), [Joybus](tools/fixtures/gp_config021_persisted_recovery/dependencies/joybus/LICENSE), [NES PIO](tools/fixtures/gp_config021_persisted_recovery/dependencies/nes/LICENSE), and [failed-selector dependency](tools/fixtures/gamecube_selector_liveness/failed_dependency/LICENSE) notices.

## Declared external build inputs

Declarations are in [PlatformIO](platformio.ini) and [Glyph environments](config/glyph/env.ini). Commit selectors identify source snapshots; version tags and ranges can move or resolve differently. License evidence for a range is the inspected named version, not a lock of future resolutions. Frameworks bundle additional component notices. Wire is provided by the selected Arduino framework.

| Dependency / selector | Selector kind | Source-backed license evidence |
| --- | --- | --- |
| nanopb/Nanopb@^0.4.8 | version range | [Zlib](https://raw.githubusercontent.com/nanopb/nanopb/0.4.8/LICENSE.txt) |
| https://github.com/JonnyHaystack/HayBox-proto#5b2bb5d | immutable commit | [GPL-3.0-only (package metadata)](https://raw.githubusercontent.com/JonnyHaystack/HayBox-proto/5b2bb5d2c2a212647d5aaef7d5dc794be5197ecb/library.json) |
| https://github.com/GregTurbo/HayBox-proto#db4e2f6 | immutable commit | [GPL-3.0-only (package metadata)](https://raw.githubusercontent.com/GregTurbo/HayBox-proto/db4e2f68b5c4ddd407e7c11050a920c4b4ec54c8/library.json) |
| nicohood/Nintendo@^1.4.0 | version range | [MIT](https://raw.githubusercontent.com/NicoHood/Nintendo/1.4.0/LICENSE) |
| JonnyHaystack/arduino-nunchuk v1.0.1 | version or tag | [BSD-3-Clause](https://raw.githubusercontent.com/JonnyHaystack/arduino-nunchuk/v1.0.1/LICENSE.md) |
| JonnyHaystack/ArduinoJoystickLibrary v0.0.1 | version or tag | [LGPL-3.0 license text](https://raw.githubusercontent.com/JonnyHaystack/ArduinoJoystickLibrary/v0.0.1/LICENSE) |
| JonnyHaystack/ArduinoKeyboard 1.0.5 | version or tag | [LGPL-3.0 license text](https://raw.githubusercontent.com/JonnyHaystack/ArduinoKeyboard/1.0.5/LICENSE) |
| maxgerhardt/platform-raspberrypi#5e87ae34ca025274df25b3303e9e9cb6c120123c | immutable commit | [Apache-2.0](https://raw.githubusercontent.com/maxgerhardt/platform-raspberrypi/5e87ae34ca025274df25b3303e9e9cb6c120123c/LICENSE) |
| earlephilhower/arduino-pico#3.6.3 | version or tag | [LGPL-2.1 license text; bundled components have separate notices](https://raw.githubusercontent.com/earlephilhower/arduino-pico/3.6.3/LICENSE) |
| GregTurbo/nes-pio#422f16f | immutable commit | [LGPL-3.0 license text](https://raw.githubusercontent.com/GregTurbo/nes-pio/422f16f/LICENSE) |
| JonnyHaystack/Adafruit_TinyUSB_XInput#4b5617b | immutable commit | [MIT (actual XInput source/header notices)](https://raw.githubusercontent.com/JonnyHaystack/Adafruit_TinyUSB_XInput/4b5617b19294e808ce1d950a69e6e5cc96f4ec06/include/Adafruit_USBD_XInput.hpp) |
| FastLED/FastLED#6daa782 | immutable commit | [MIT](https://raw.githubusercontent.com/FastLED/FastLED/6daa782/LICENSE) |
| nanopb-arduino v1.1.1 | version or tag | [MIT (package metadata)](https://raw.githubusercontent.com/JonnyHaystack/nanopb-arduino/v1.1.1/library.json) |
| Adafruit GFX 1.12.6 | version or tag | [BSD-3-Clause](https://raw.githubusercontent.com/adafruit/Adafruit-GFX-Library/1.12.6/license.txt) |
| Adafruit SSD1306 ^2.5.9 | version range | [BSD-3-Clause](https://raw.githubusercontent.com/adafruit/Adafruit_SSD1306/2.5.9/license.txt) |
| PacketIO ^0.3.0 | version range | [MIT](https://raw.githubusercontent.com/eric-wieser/packet-io/0.3.0/LICENSE.txt) |
| CRC32 ^2.0.0 | version range | [MIT](https://raw.githubusercontent.com/bakercp/CRC32/2.0.0/LICENSE.md) |
| PCF8575 ^0.2.2 | version range | [MIT](https://raw.githubusercontent.com/RobTillaart/PCF8575/0.2.2/LICENSE) |
| Adafruit BusIO (transitive from display libraries; observed version 1.17.4) | transitive observation not lock | [MIT](https://raw.githubusercontent.com/adafruit/Adafruit_BusIO/1.17.4/LICENSE) |

## Unresolved export inputs

`glyph_nuker` is invoked by the retained CI workflow. Its [bounded lineage record](docs/runtime_config/glyph_nuker_source_lineage.md) leaves source, build recipe, license and byte transformation unknown. The export policy marks it **REVIEW_REQUIRED** and excludes it from diagnostic staging. This unresolved required input blocks an approved public export; no executable redistribution or firmware acceptance is implied.

The exported AVR declarations also name unversioned `atmelavr`, its Arduino framework and built-in Wire. Their exact resolved source/license inventory remains **REVIEW_REQUIRED**; Mk6 Arduino-Pico metadata does not clear AVR inputs.

The deterministic [export policy](tools/fixtures/glyph_public_export_policy.v1.json) records selectors, evidence locators, bundled-notice obligations and remaining review gates. Fresh-history validation is a separate gate.
