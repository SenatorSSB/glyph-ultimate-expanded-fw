# GP-KBD-001 Keyboard pipeline characterization

Status: candidate characterization; integration waits for GP-VAL-040 DONE.
Risk: H1. Classification: INACTIVE_GENERATOR_OR_FIXTURE.

## Scope and identity

The authorized base is `328c6a1bfb09eb035c2065d0de080283307f34d6`.
The executable fixture binds exact production and dependency bytes to that
commit and to SHA-256 values. The candidate identity, tree, complete raw path,
blob and mode inventory, validation and independent conformance receipt belong
to the later source-free candidate handoff. This report does not self-certify
its own Git identity or authorize integration.

Production firmware, defaults, schema, decoder and build inputs remain unchanged.
No firmware build, artifact, device write or physical test is part of this work.
The host executable is temporary test machinery only.

## Source-supported path

The current Glyph defaults contain thirteen profiles. Keyboard is profile 13;
the older numbered comment in the defaults is not an index authority.
`config/glyph/common/include/glyph_overrides.hpp` binds its keyboard configuration
and SOCD pairs. `HAL/pico/src/display/DefaultConfigMenu.cpp` exposes the Profile
selection path and forces the DInput backend for a keyboard profile before
writing the watchdog selections, disconnecting and rebooting.
`HAL/pico/src/comms/backend_init.cpp` registers the keyboard descriptor for
DInput. `src/core/mode_selection.cpp` requires DInput for `MODE_KEYBOARD` and
selects `CustomKeyboardMode`. `config/glyph/common/src/config.cpp` then calls
`current_kb_mode->SendReport(backends[0]->GetInputs())` from the loop. These are
source-route observations, not evidence
of a completed physical menu/reboot or host enumeration.

## Observed pipeline

`HAL/pico/src/core/KeyboardMode.cpp::SendReport` copies the input, calls
`HandleRemap` and `HandleSocd` on the copy, then calls `UpdateKeys(inputs)` with
the original input. `src/modes/CustomKeyboardMode.cpp::UpdateKeys` reads that
original button mask for each configured key. The temporary host program
compiles these complete production bodies together with production
`InputMode.cpp`, `socd.cpp`, state headers and state utilities. Its observer
calls the production remap and SOCD methods and records their results; it does
not substitute an implementation of those transformations.

The TUKeyboard double observes method calls and key state. HID key names in
literal default initializers use distinct host tokens. Their numeric token
values are not USB usage codes and establish no descriptor, rollover, USB
packet, timing, OS or application behavior. Every test object receives
`SetConfig` before a report; unconfigured-object behavior is outside this proof.

## Supported finding and disposition boundary

The original-versus-transformed seam is present on the source-supported ordinary
Keyboard profile path. A transformed SOCD state can differ from the original
button state while keyboard mapping still reads the original. This evidence
must remain visible in release adjudication; excluding Keyboard because it is
outside the GC controller path would omit an ordinary USB path.

Default remaps concern MB buttons that have no default keyboard key binding.
Any injected remap that creates a visible key difference is a separate host
control, not a claim about an unchanged default physical input. The existing
default count and initializer mismatch must not silently be repaired here.

No desired SOCD rule, remap repair, gameplay semantics, backend repair or
nonblocking release judgment is chosen. A subsequent bounded Curator packet
must disposition the demonstrated supported-path finding and, if a repair is
selected, authorize its exact source change and hardware validation. GP-VAL-040
only authenticates finite source-free host paths; it grants no firmware fix.

## Validation and limits

The focused proof passes 103 input observations and eight constructor/destructor
cycles in ordinary and AddressSanitizer/UndefinedBehaviorSanitizer runs. It rejects
118 identity negatives and five executable behavior mutants: replacing original
input with the copy, omitting remapping, omitting SOCD, omitting releaseAll, and
omitting destructor sendState. A mutant compilation failure cannot count as a
passing behavioral negative.

Run `python3 tools/check_glyph_gp_kbd_001_keyboard_pipeline.py` for the literal
source proof, behavioral controls and negative checks. The fixture records the
closed source dependencies and exact host case expectations. Candidate-phase
aggregate results and independent review are recorded in the handoff after
execution. Expected unknown-path correspondence rejection is the named
GP-VAL-040 gate, not permission to weaken correspondence or integrate early.

Hardware status: NOT_TESTED. Nunchuk remains NOT_TESTED. Root cause remains
unproven. No controller acceptance, source repair or public release is claimed.
