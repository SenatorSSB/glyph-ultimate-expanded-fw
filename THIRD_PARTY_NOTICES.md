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

| platform = atmelavr | unversioned / observed package | [Apache-2.0](https://dl.registry.platformio.org/download/platformio/platform/atmelavr/5.3.0/atmelavr-5.3.0.tar.gz) |
| framework = arduino under avr_base | unversioned / observed package | [LGPL-2.1-or-later (inspected source component)](https://raw.githubusercontent.com/arduino/ArduinoCore-avr/1.8.6/cores/arduino/Arduino.h) |
| avr_base lib_deps = Wire | unversioned / observed package | [LGPL-2.1-or-later (inspected source component)](https://raw.githubusercontent.com/arduino/ArduinoCore-avr/1.8.6/libraries/Wire/src/Wire.cpp) |

## Unresolved export inputs

`glyph_nuker` is invoked by the retained CI workflow. Its exact executable was
distributed in official LimitLabs/FW-Glyph, whose [pinned README line 15](https://github.com/LimitLabs/FW-Glyph/blob/9a78c7eeec87527b68644573e4c29fbdfb543239/README.md#L15)
declares the project GPL Version 3 and links its root GPLv3 LICENSE. GitHub
identifies this repository as a direct fork of that project. The
[lineage record](docs/runtime_config/glyph_nuker_source_lineage.md) and
[G2F receipt](docs/runtime_config/fixtures/glyph_nuker_release_rights_g2f.v1.json)
record official binary identity, account-associated authorship and the combined
engineering release-policy assessment.

Exact corresponding source is GregTurbo/glyph-nuker revision
`b583d53ea71347f2721d40bf3b55933190bdc87a`. G2D reproduced the 23,336-byte
executable byte-for-byte with Zig 0.15.2 and
`zig build -Dtarget=x86_64-linux -Doptimize=ReleaseSmall` (x86-64 baseline CPU)
in Debian 12 amd64 Linux. This tested recipe is not historical maintainer
attestation. Both inspected standalone source revisions lack a separate LICENSE
or explicit source-license declaration. That fact remains a provenance caveat;
the owner-directed engineering policy considers the official GPLv3 project
distribution, direct fork, authorship linkage and exact source correspondence
together. It does not assert a standalone source-license file or a final legal
opinion.

The missing-external-source blocker is retired. The remaining obligation is
**GLYPH_NUKER_CORRESPONDING_SOURCE_PACKAGING_REQUIRED**: provide the exact matching
Corresponding Source and build instructions and preserve applicable GPLv3,
copyright, upstream notices and attribution. The existing **REVIEW_REQUIRED**
classification remains until that packaging is satisfied; public export is still
blocked and diagnostic staging omits the executable. Source incorporation is
deferred to H-stage release preparation. No overall release clearance, executable
replacement or hardware acceptance follows.

The unversioned AVR selector was separately observed as `atmelavr5.3.0` (Apache-2.0) selecting `framework-arduino-avr~5.4.0`. The framework5.4.0 Arduino and built-in Wire headers match ArduinoCore-avr1.8.6 and state LGPL-2.1-or-later. These observations do not lock a future unversioned resolution.

The deterministic [export policy](tools/fixtures/glyph_public_export_policy.v1.json) records selectors, evidence locators, bundled-notice obligations and remaining review gates. Fresh-history validation is a separate gate.
