# Final USB gamepad publication host fixture

Run `python3 tools/check_glyph_final_usb_gamepad_enumeration.py` from the repository.
The optional `--framework` and `--xinput` paths locate existing pinned build caches;
the checker does not download dependencies or touch a device.

The checker compiles the pinned Arduino-Pico 3.6.3 Adafruit TinyUSB device core,
CDC/HID implementations and pinned Adafruit XInput implementation with actual
Glyph XInput, DInput and Nintendo Switch backend constructors and TUCompositeHID.
It executes complete production `backend_init.cpp` selection/constructor dispatch
bodies (only includes removed), plus the actual extracted `InitializeBootBackends`
body and production classification helper. The pinned stack handles host requests,
configuration, class opens and endpoint claims. Early Pico CDC enumeration occurs
before backend construction, and the host subsequently enumerates the completed
interface only after the final reconnect. Actual XInput VID/PID, vendor interface
readiness, Switch VID/PID, and combined DInput gamepad/keyboard HID descriptors
are checked. The existing Switch readiness/USB-host fixtures remain separate.

The 25 cases cover each of eight final stock backends, each of three provisional
USB gamepad constructors followed by four final retro backends, all three ordinary
provisional USB-to-final-USB paths, failed console detection, and refused invalid
USB default with recovery entry. Each USB case requires one disconnect, one 10 ms
delay and one connect; other routes require zero. A Switch-only mutant must fail
XInput and DInput separately. The helper is also checked over all 256 IDs.

Explicit boundaries: console electrical detection returns a scripted identity;
retro backend and Configurator constructors carry identity only; persistent
storage, mode activation and recovery rendering are doubles. The production
selection code itself is executed. Separate repository Configurator, recovery,
ProfileStore and GameCube liveness fixtures cover those affected consumers. Source
checks establish that the pinned core attaches before `setup`, that validation,
storage and selection gates precede finalization, and that backend selection has
no independent reconnect call.

Native-only adaptations: the language-ID pointer casts in the pinned device
implementation are widened to `uintptr_t`; the existing GCC-style `detect_console`
default argument is explicitly namespace-qualified for Clang; Arduino's Serial
alias is exposed; hardware time/IRQ/endpoint boundaries use deterministic doubles.
The XInput source and header and the stack translation-unit set are hash-pinned.

This does not measure electrical disconnect duration, Windows driver binding,
actual receiver recognition or controller behavior. The host cooperates with
pull-up changes. The 10 ms argument is checked as policy, not proven universally
sufficient by simulation. Exact-candidate owner hardware acceptance is required.
