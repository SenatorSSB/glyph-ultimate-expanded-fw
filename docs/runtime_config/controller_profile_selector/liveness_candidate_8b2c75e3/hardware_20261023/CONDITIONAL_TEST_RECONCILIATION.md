# Conditional no-poll physical test applicability

The original owner objective (OWNER_OBJECTIVE.md, Hardware continuation gates)
says repeat a physical no-poll selection “if the approved test setup can safely
create that condition”. Its11 numbered acceptance criteria require source and
regression bounded progress plus normal exact physical workflows/preservation;
they do not impose an unconditional physical no-poll setup.

The assistant-prepared OWNER_PACKET.md strengthened that conditional clause to
an unconditional acceptance gate. That additional restriction did not come from
the original objective. Later owner explicitly reports no established method
and says one likely will not be provided unless other work fails. The final
XInput output/reboot/responsiveness question was answered “Yes, all matched”.

Applicability correction: no-poll physical row is NOT_TESTED because the safe
setup condition is not met. This is not a physical PASS and does not prove
physical response under absent polling. Original source/old-vs-new regression,
normal GameCube/XInput physical tests and post-test preservation requirements
remain mandatory and are supported by their separate evidence. The original
conditional scope governs this result; no new cable/adapter/power experiment
is authorized. No further setup request is pending from this repair.

The preserved earlier Stage B review reports accurately describe the gaps at
their own time; latest confirmations and acceptance audit supersede those
current-gap classifications. Exact historical failure, root cause UNPROVEN and
Nunchuk NOT_TESTED remain unchanged. Source-free HEP is evidence only; canonical
queue/governance and tested-source integration remain separate.
