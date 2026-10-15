# Current compact Config persistence proof

Run `python3 tools/check_glyph_profile_store_config_persistence.py` from the
repository; set `GLYPH_PROFILE_STORE_SANITIZERS=1` for ASan/UBSan.

The checker compiles current `HAL/pico/src/core/Persistence.cpp` and its current
header, tracked generated Config schema, real Nanopb, CRC32 and Arduino stream
adapter, plus production generic Config semantic/extent validators. It does not
extract a historical Persistence body. Named-file host doubles inject definite
open/read/write/remove/rename failures. Tests assert selected durable Config,
legacy bytes, caller state and generation behavior as applicable, including a
prior-only recovery anchor and interrupted current-to-prior rotation.

The successful-publication case deliberately refuses every file open after the
successful staged-to-current rename. The save must still report success and
publish its generation; after clearing that injected read outage, reboot load
must reconstruct the new Config. The staged bytes must have passed readback
before this publication point.

Host `size_t` can add padding to ConfigHeader. Expected newly encoded records
compare header fields and the exact protobuf body, rather than unspecified
padding. Existing durable/prior/legacy records are compared byte for byte.

This proves observable source behavior under these host doubles. It does not
emulate target LittleFS allocation, power loss, sync/close outcomes, ambiguous
rename acknowledgements, target ABI, controller runtime output, or hardware
acceptance. A definite failed rename in the double performs no mutation.
