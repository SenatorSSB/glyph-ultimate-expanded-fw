# GP-CONFIG-009 config-menu invalid-state characterization

This is bounded H1 host evidence for the exact current Glyph menu bodies. The
harness literally includes and compiles `ConfigMenu.cpp`, `DefaultConfigMenu.cpp`,
and `GlyphConfigMenu.cpp`; dependency doubles cover only host display, input,
backend/mode, config, platform, bitmap, persistence, and reboot symbols.

Observed host cases:

- A null `CurrentGameMode` with one configured XInput backend triggers the
  exact `DefaultConfigMenu` null dereference under UBSan/ASan.
- A source-shaped filtered empty page constructs and completes the bounded
  empty-child display path in the host run.
- A synthetic `highlighted == items_count` state aborts under ASan/UBSan when
  the exact production `HandleControls` body indexes the selected item.

The synthetic index case is explicitly injected; its physical reachability is
UNKNOWN. Host sanitizer output is not evidence of device crash, display output,
controller behavior, dual-core timing, or hardware acceptance. No firmware
repair or empty-page product policy is selected.
