# Managed profile selection candidate

Owner host campaign of 2026-11-13. Hardware acceptance pending. The ordinary
Mk6 Profile menu lists eligible configured modes and native profiles already
bound to an eligible Ultimate row. Native entries are ordered by display rank
with stable directory-order ties. A managed pair must agree on its record ID,
owned row and RGB slot. A legacy native record may appear when exactly one row
binds it on the executing backend. An unbound record is still available to the
separate G6 reference-management protocol. Navigation reads directory metadata
only; the left pane shows the highlighted name and the plate from that row.

The menu submits the logical ID to core0. Core0 reloads durable Config, resolves
the eligible pair, reads the actual native wrapper and checks its preprocessing
against that exact row. Checked Config publication changes only the destination
for the selected backend and its saved backend-family default. A committed
one-shot destination selects it on watchdog reboot. Normal boot uses the saved
destination. Activation chords and managed USB route selection use the same
publication path. This choice preserves the existing 30-row Config and avoids
an additional on-disk selector, reference edit, shared native record or live
runtime replacement.

The production-NOR test creates Lark and Wren with different native tables,
remaps, SOCD, plates, ranks and routes. It selects on GameCube, XInput and
Switch USB, starts a new process from saved NOR for each accepted selection and
checks exact native bytes, all Config fields and the complete namespace. Missing
and corrupt pairs and unsupported routes refuse. The selector checker also
exercises menu rendering and button actions on both host enum ABIs.

    python3 tools/check_glyph_controller_profile_selector.py --gamecube-liveness
    python3 tools/fixtures/glyph_package_v1/transaction/build.py --repo . --out BUILD
    python3 tools/fixtures/glyph_package_v1/transaction/managed_selection.py --corpus SENSCOPE/contracts/glyph-package-v1 --binary BUILD/package-fault-harness --out RESULTS

Later hardware acceptance needs the exact built candidate. Check the GC adapter
menu, read the two names and plates, switch both ways, and compare the executing
identity and preprocessing after reboot. USB routes require separate observations.
