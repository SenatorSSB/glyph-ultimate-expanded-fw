# GP-CONFIG-019 ordinary USB name-selection characterization

H1 host-only evidence at canonical base `d2f78cd3a3fa38c60d04dab54236ee630ead379e`.
Integration waits for separately implemented GP-VAL-041 strict DONE. This report
selects no naming policy and authorizes no firmware change or beta restriction.

The production selector compares all eighteen name bytes. At its first matching
Config row it disconnects USB, delays 500 ms, writes the matching one-based row
index to watchdog scratch[1], writes the selected one-based backend index to
scratch[0], delays 30 ms and calls reboot. Its scan does not consult current row
identity, mode ID, Keyboard flag or backend applicability. With a terminating
host reboot double, an ordinary menu action on a later duplicate selects the
earlier matching profile. The returning double is a separate diagnostic: it
continues the scan and writes later matches. Physical continuation is UNKNOWN.

Source defaults contain twelve unique nonempty names and one sole empty
Keyboard name. The exact default initializer and copy function are compiled.
The constructed-current-mode control checks each default against each USB
option its constructor offers, including profiles whose ordinary USB profile
availability is restricted. This does not claim all default profiles are USB
reachable. Controller USB options are XInput/DInput/Switch; a current Keyboard
profile offers DInput alone. The Glyph profile-menu applicability/Keyboard
exception and SetDefaultMode reboot route are separately hash-bound source
routes, not physically executed menu navigation.

Actual generated schema and Nanopb decode bytes are the accepted GP-PROV-014 /
GP-CONFIG-012 tracked closure. Name wire lengths 0, 16 and 17 decode; length18
rejects. All eighteen comparison positions matter, including bytes after an
embedded NUL. The all-nonzero eighteen-byte buffers and detached-current-profile
no-match case are injected, with physical reachability UNKNOWN. Negative backend
indices are unrepresentable by the uint8_t parameter; indices count through255
return without effects.

Production HandleSetConfig admits duplicate and empty names in otherwise valid
wire Configs when the SaveConfig success spy succeeds. Production LoadConfig
also decodes those wire Configs under the explicit valid-header/CRC assumption.
These are independent acceptance-route proofs, not a filesystem save/load
roundtrip: the host LoadConfig reads the incoming wire. The real encoder may
normalize bytes after embedded NUL; this report makes no persistence-preservation
claim for them. Save failure, flash behavior and CRC validation are outside this
experiment. No live same-session coherence claim follows.

Accepted controller duplicate names produce first-row scratch selection even
when the current row is later. With accepted empty controller/Keyboard names,
Keyboard's offered DInput action chooses the earlier controller row. With an
earlier Keyboard and later controller sharing a name, the controller's ordinary
XInput/Switch action writes the Keyboard row. Exact initialize_backends consumes
the scratch values and passes that row to a set_mode spy, updating backend
default mode and invoking SaveConfig. Actual set_mode restricts Keyboard to
DInput; controller output and actual mode activation remain UNKNOWN. Direct
Keyboard-to-XInput selector invocation is injected because that option is not
offered by the ordinary Keyboard USB menu.

The checker binds exact production/default/menu/acceptance/startup/build and
schema/decoder bytes, literal extracted fragments, and both host files. It
compiles unchanged production fragments with address/undefined sanitizers and
the authorized one-byte Button ABI. Omission, byte substitution, fixture hash
substitution and executable-mode record negatives reject. The finite new paths
are the report, JSON fixture, checker, main.cpp and include/host_stubs.hpp.
The host paths are outside PlatformIO source filters, include roots and builder
extra-script inputs. No firmware/build inputs change.

This is source-backed evidence of ambiguous ordinary name selection. A minimum
repair or nonblocking disposition requires its separate authorized decision;
duplicate custom naming is not automatically a release blocker. Hardware
acceptance is NOT_CLAIMED. Nunchuk remains NOT_TESTED; root cause remains unproven.
