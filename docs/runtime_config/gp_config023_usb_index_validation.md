# GP-CONFIG-023 USB default index host proof

This bounded proof exercises the exact production index predicate and semantic
validator, plus source-extracted `initialize_backends` and default selector
bodies, against the generated C013/C022 configuration layout. It does not
change schema, defaults, or decoder behavior.

The host matrix covers all 4,096 combinations of counts 0–15 and index bytes
0–255. It accepts exactly 120 combinations where `1 <= index <= count`, using
the generated array extent of 15. Counts 16–255 are separately rejected as
outside that actual extent. Five invalid entry states reject before any
selector, getter, detector, initializer, secondary-backend callback, or save.
A selector-created invalid index rejects after the selector and before every
downstream callback. The valid route checks cover GameCube, USB XInput,
Keyboard through DInput, and a watchdog DInput selection with a saved mode
update.

The production semantic validator rejects an invalid SET-style Config without
changing its caller bytes. The harness does not run `ConfiguratorBackend` packet
decoding or the persistence implementation, so it does not claim byte-retention
or saved-file recovery behavior. Startup display and recovery UI are also not
executed. Peripheral constructors and host/device behavior are callback stubs.

Separate source-bound callsite checks verify that `HandleSetConfig` invokes the
shared validator before saving and publishing, `LoadConfigChecked` validates
before publishing, and Glyph's adapter calls `validate_config_semantics`. They
also verify that invalid startup selection reaches refusal before mode-binding
setup and zero-backend fallback, and that the secondary core gates normal menu
construction after refusal. These are source-order checks, not runtime UI or
storage simulations.

The adopted standalone C021 checker was attempted with
`python3 tools/check_glyph_gp_config021_persisted_recovery.py`; it stopped at
its exact C021 base/parent gate because this is the C023 candidate branch. The
adopted C022 checker was attempted with
`python3 tools/check_glyph_gp_config022_rgb_target_validation.py --output
/private/tmp/gp-config023-cross-c022`; it stopped because its frozen input
hash for `HAL/pico/src/comms/backend_init.cpp` differs from the authorized C023
source. The C023 checker instead authenticates and executes the current
initializer and selector fragments directly.

The checker compiles the actual production validation sources and two exact
source fragments in both the default and short-enum ABIs with AddressSanitizer
and UndefinedBehaviorSanitizer. This is host-only evidence: hardware acceptance
is **NOT_CLAIMED**, Nunchuk remains **NOT_TESTED**, and root cause remains
**UNPROVEN**.
