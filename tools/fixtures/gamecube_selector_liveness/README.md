# GameCube selector liveness regression

Run `python3 tools/check_glyph_gamecube_selector_liveness.py` from the repository.
The checker compiles production Joybus C, GamecubeConsole C++, backend C++,
headers, and PIO C-SDK helper bodies, eliding only include directives to supply
deterministic host peripheral doubles. It tests both enum ABIs with ASan/UBSan.
The integrated variant links the real selector mailbox, actual extracted
application service, and actual Persistence implementation through an opaque
cross-translation-unit callback. Existing menu and persistence regressions run
alongside it. The bridge's accepted and refused transaction assertions remain
owned by the existing controller selector fixture.

The failed dependency is retained verbatim with its upstream commit and file
SHA-256 manifest. The old backend body comes from exact failed candidate
`4898951994bcabcaef2846145de2922a674656f8`. The old literal blocking receive
exceeds a finite simulated hardware bound when a request arrives without a
command. No implementation control flow is replaced by a liveness model.

The hardware doubles model FIFO events, pending TX completion, sticky receive
activity, GPIO raw edge events, PC state and elapsed time. They do not execute
the RP2040 instruction engine or establish physical timing. The separate PIO
checks compare literal source instructions, bit-sample cycles, generated opcode
words and all relocated JMP operands. Report and command responses are checked
byte-for-byte through the actual old and repaired protocol bodies.

The simulated admission bound is a regression assertion, not a measured device
latency. Electrical correctness, linked stack/resource budgets and exact-artifact
hardware acceptance remain separate required gates. A permanently stalled active
partial command is deliberately protected against false idle admission.
